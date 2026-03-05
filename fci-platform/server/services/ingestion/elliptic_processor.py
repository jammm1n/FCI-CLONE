"""
Elliptic API Screening Processor.

Async wrapper around the synchronous EllipticScreener from the
toolkit. Screens wallet addresses via the Elliptic AML API (or
demo mode) and returns structured markdown output.

The toolkit's EllipticScreener is synchronous (uses httpx sync client).
All calls are wrapped with asyncio.to_thread() to avoid blocking
the FastAPI event loop.
"""

import asyncio
import logging

from ..icr.elliptic_api import EllipticScreener

logger = logging.getLogger(__name__)


def _run_screening_sync(addresses: list[str], customer_id: str) -> dict:
    """
    Synchronous screening via the toolkit's EllipticScreener.

    The screener reads ELLIPTIC_API_KEY, ELLIPTIC_API_SECRET, and
    ELLIPTIC_DEMO_MODE from environment variables directly.

    Returns:
        Dict with keys: status, summary, results, markdown, demo_mode.
        On configuration error: {status: 'not_configured', message: ...}
    """
    screener = EllipticScreener()

    if not screener.is_configured():
        return {
            'status': 'not_configured',
            'message': (
                'Elliptic API credentials not configured. '
                'Set ELLIPTIC_API_KEY and ELLIPTIC_API_SECRET environment '
                'variables, or set ELLIPTIC_DEMO_MODE=true.'
            ),
        }

    report = screener.screen_and_report(addresses, customer_id)
    return report


async def screen_addresses(addresses: list[str], customer_id: str) -> dict:
    """
    Screen wallet addresses via the Elliptic API.

    Offloads the synchronous HTTP calls to a thread pool.

    Args:
        addresses: List of blockchain address strings.
        customer_id: The subject UID (used as customer reference
                     in the Elliptic API).

    Returns:
        Dict with keys:
            status      'complete' or 'not_configured'
            output      Markdown report string (when complete)
            summary     {total_screened, high_risk, medium_risk,
                         low_risk, errors}
            demo_mode   Whether demo mode was used
    """
    if not addresses:
        return {
            'status': 'complete',
            'output': 'No wallet addresses to screen.',
            'summary': {
                'total_screened': 0,
                'high_risk': 0,
                'medium_risk': 0,
                'low_risk': 0,
                'errors': 0,
            },
            'demo_mode': False,
        }

    result = await asyncio.to_thread(_run_screening_sync, addresses, customer_id)

    if result.get('status') == 'not_configured':
        return result

    return {
        'status': result.get('status', 'complete'),
        'output': result.get('markdown', ''),
        'summary': result.get('summary', {}),
        'demo_mode': result.get('demo_mode', False),
    }
