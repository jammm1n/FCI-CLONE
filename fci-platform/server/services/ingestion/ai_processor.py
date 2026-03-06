"""
AI Processor — Prompt-based narrative generation for C360 processor outputs.

Takes raw processor output text, sends it to the Anthropic API with a
dedicated prompt, and returns AI-generated narrative suitable for the
case file.

Key design decisions:
  - Non-streaming batch calls (not interactive chat)
  - Sequential processing (one prompt at a time)
  - Prompt files loaded once at first use, cached in memory
  - Global rules preamble prepended to every prompt
  - Does NOT reuse ai_client.py (too complex for simple batch calls)
"""

import logging
from pathlib import Path

from anthropic import AsyncAnthropic

from server.config import settings

logger = logging.getLogger(__name__)

# ── Prompt-to-Processor Mapping ──────────────────────────────────

PROCESSOR_PROMPT_MAP = {
    'tx_summary':   'prompt-01-transaction-analysis.md',
    'blocks':       'prompt-03-account-blocks.md',
    'ctm':          'prompt-06-ctm-alerts.md',
    'privacy_coin': 'prompt-07-privacy-coin.md',
    'fiat':         'prompt-08-failed-fiat.md',
    'counterparty': 'prompt-19-counterparty-ingestion.md',
    'device':       'prompt-17-device-ip-ingestion.md',
    'ftm':          'prompt-18-ftm-alerts-ingestion.md',
}

# Processors NOT in this map (user_profile, elliptic) get no AI processing.

# ── Text Section Prompt Map ─────────────────────────────────────
# Maps ingestion section keys to their prompt files.
# These are simple text-in / narrative-out sections (not C360 processors).

SECTION_PROMPT_MAP = {
    'hexa_dump':    'prompt-20-l1-referral.md',
    'raw_hex_dump': 'prompt-21-haoDesk-cleanup.md',
    'previous_icrs': 'prompt-04-prior-icr.md',
    'rfis':         'prompt-10-rfi-summary.md',
}

# ── Prompt Loading ───────────────────────────────────────────────

_GLOBAL_RULES = None
_PROMPT_CACHE = {}


def _load_prompts():
    """Load global rules + all prompt files. Called once at first use."""
    global _GLOBAL_RULES
    prompts_dir = Path(settings.KNOWLEDGE_BASE_PATH) / 'prompts'

    if not prompts_dir.exists():
        raise FileNotFoundError(
            f'Prompts directory not found: {prompts_dir}. '
            'Ensure knowledge_base/prompts/ exists with prompt files.'
        )

    _GLOBAL_RULES = (prompts_dir / '_global-rules.md').read_text(encoding='utf-8')

    all_mappings = {**PROCESSOR_PROMPT_MAP, **SECTION_PROMPT_MAP}
    for key, filename in all_mappings.items():
        prompt_path = prompts_dir / filename
        if not prompt_path.exists():
            logger.warning('Prompt file not found: %s', prompt_path)
            continue
        prompt_text = prompt_path.read_text(encoding='utf-8')
        _PROMPT_CACHE[key] = _GLOBAL_RULES + '\n\n' + prompt_text

    logger.info(
        'Loaded %d prompts from %s', len(_PROMPT_CACHE), prompts_dir,
    )


def _get_prompt(processor_id: str) -> str | None:
    """Get the cached prompt for a processor ID. Loads on first call."""
    if not _PROMPT_CACHE:
        _load_prompts()
    return _PROMPT_CACHE.get(processor_id)


# ── Variable Injection ───────────────────────────────────────────


def _inject_variables(prompt_text: str, variables: dict) -> str:
    """Replace [PLACEHOLDER] tokens in prompt text with actual values."""
    for key, value in variables.items():
        prompt_text = prompt_text.replace(f'[{key.upper()}]', str(value))
    return prompt_text


# ── API Client ───────────────────────────────────────────────────

_client = None


def _get_client() -> AsyncAnthropic:
    """Lazy-init the Anthropic async client."""
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


# ── Core Processing Function ─────────────────────────────────────


async def process_with_ai(
    processor_id: str,
    raw_content: str,
    variables: dict | None = None,
) -> dict:
    """
    Send raw processor output through AI with the mapped prompt.

    Args:
        processor_id: The processor ID (e.g., 'tx_summary', 'ctm').
        raw_content: The raw text output from the processor.
        variables: Optional dict of placeholder values to inject
                   (e.g., {'nationality': 'US', 'residence': 'UK'}).

    Returns:
        {
            'ai_output': str | None,   # The AI-generated narrative
            'prompt_file': str,        # Which prompt file was used
            'model': str,              # Which model was used
            'usage': dict,             # Token usage {input, output}
            'error': str | None,       # Error message if failed
        }
    """
    prompt_file = PROCESSOR_PROMPT_MAP.get(processor_id, '')
    model = settings.ANTHROPIC_MODEL
    result = {
        'ai_output': None,
        'prompt_file': prompt_file,
        'model': model,
        'usage': {},
        'error': None,
    }

    # Get the prompt
    prompt_text = _get_prompt(processor_id)
    if not prompt_text:
        result['error'] = f'No prompt found for processor: {processor_id}'
        logger.warning(result['error'])
        return result

    # Inject variables if provided
    if variables:
        prompt_text = _inject_variables(prompt_text, variables)

    # Call the API
    try:
        client = _get_client()
        response = await client.messages.create(
            model=model,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            system=prompt_text,
            messages=[
                {'role': 'user', 'content': raw_content},
            ],
        )

        # Extract the text response
        if response.content and len(response.content) > 0:
            result['ai_output'] = response.content[0].text

        result['usage'] = {
            'input': response.usage.input_tokens,
            'output': response.usage.output_tokens,
        }

        logger.info(
            'AI processing complete for %s: %d input, %d output tokens',
            processor_id,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )

    except Exception as e:
        result['error'] = str(e)
        logger.exception('AI processing failed for %s', processor_id)

    return result
