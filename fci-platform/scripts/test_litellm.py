"""
Test script for LiteLLM proxy connectivity.

Run on the Binance network with SAFU API credentials:
    ANTHROPIC_API_KEY=sk-ts02... ANTHROPIC_BASE_URL=https://litellm.safuapi.secfdg.net python scripts/test_litellm.py

Or set these in your .env file and run:
    python scripts/test_litellm.py

Tests:
  1. Basic non-streaming message (connectivity + auth)
  2. Streaming message (SSE proxy)
  3. Prompt caching (cache_control header support)
"""

import asyncio
import os
import sys

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anthropic import AsyncAnthropic


async def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "")
    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    if not api_key:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
        print(f"Using proxy: {base_url}")
    else:
        print("Using direct Anthropic API (no base_url set)")

    print(f"Model: {model}")
    print(f"Key prefix: {api_key[:10]}...")
    print()

    client = AsyncAnthropic(**kwargs)

    # ── Test 1: Basic non-streaming ──────────────────────────────
    print("Test 1: Non-streaming message...")
    try:
        response = await client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "Respond with exactly: OK"}],
        )
        text = response.content[0].text
        print(f"  Response: {text}")
        print(f"  Tokens: input={response.usage.input_tokens}, output={response.usage.output_tokens}")
        print("  PASS")
    except Exception as e:
        print(f"  FAIL: {e}")
        print()
        print("If the model name was rejected, try prefixing with 'anthropic/':")
        print(f"  ANTHROPIC_MODEL=anthropic/{model} python scripts/test_litellm.py")
        return

    # ── Test 2: Streaming ────────────────────────────────────────
    print()
    print("Test 2: Streaming message...")
    try:
        chunks = []
        async with client.messages.stream(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "Count from 1 to 5."}],
        ) as stream:
            async for chunk in stream:
                if chunk.type == "content_block_delta" and chunk.delta.type == "text_delta":
                    chunks.append(chunk.delta.text)

            final = await stream.get_final_message()

        text = "".join(chunks)
        print(f"  Response: {text}")
        print(f"  Chunks received: {len(chunks)}")
        print(f"  Tokens: input={final.usage.input_tokens}, output={final.usage.output_tokens}")
        print("  PASS")
    except Exception as e:
        print(f"  FAIL: {e}")

    # ── Test 3: Prompt caching ───────────────────────────────────
    print()
    print("Test 3: Prompt caching (two calls with same system prompt)...")
    long_system = "You are a helpful assistant. " * 100  # ~600 tokens, needs to exceed cache minimum

    try:
        # First call — should create cache
        r1 = await client.messages.create(
            model=model,
            max_tokens=20,
            system=[{"type": "text", "text": long_system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": "Say hello."}],
        )
        cache_created_1 = getattr(r1.usage, "cache_creation_input_tokens", 0) or 0
        cache_read_1 = getattr(r1.usage, "cache_read_input_tokens", 0) or 0
        print(f"  Call 1: input={r1.usage.input_tokens}, cache_created={cache_created_1}, cache_read={cache_read_1}")

        # Second call — should read from cache
        r2 = await client.messages.create(
            model=model,
            max_tokens=20,
            system=[{"type": "text", "text": long_system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": "Say goodbye."}],
        )
        cache_created_2 = getattr(r2.usage, "cache_creation_input_tokens", 0) or 0
        cache_read_2 = getattr(r2.usage, "cache_read_input_tokens", 0) or 0
        print(f"  Call 2: input={r2.usage.input_tokens}, cache_created={cache_created_2}, cache_read={cache_read_2}")

        if cache_read_2 > 0:
            print("  PASS — cache is working")
        elif cache_created_1 > 0:
            print("  PARTIAL — cache was created but not read on second call (may need larger prompt)")
        else:
            print("  WARNING — no caching headers returned (proxy may not support cache_control)")
    except Exception as e:
        print(f"  FAIL: {e}")

    print()
    print("Done. If all tests passed, set these in your .env and start the app.")


if __name__ == "__main__":
    asyncio.run(main())
