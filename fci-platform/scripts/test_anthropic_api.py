"""
FCI Platform — Anthropic API Validation Script

Run this BEFORE building any backend logic. It confirms that all four
API capabilities the platform depends on actually work:

  1. Basic chat (send message, get response)
  2. Tool use (define tool, trigger it, complete the loop)
  3. Image input (send base64 image, get description)
  4. Streaming (SSE chunks arrive incrementally)

Usage:
    # Set your API key first
    export ANTHROPIC_API_KEY=sk-ant-...

    # Run all tests
    python scripts/test_anthropic_api.py

    # Run a specific test
    python scripts/test_anthropic_api.py --test chat
    python scripts/test_anthropic_api.py --test tools
    python scripts/test_anthropic_api.py --test images
    python scripts/test_anthropic_api.py --test streaming

Exit codes:
    0 = all tests passed
    1 = one or more tests failed
"""

import os
import sys
import json
import base64
import argparse
import time

import anthropic


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-4-6"  # Sonnet for dev/testing
MAX_TOKENS = 1024


def get_client() -> anthropic.Anthropic:
    """Create and return an Anthropic client."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Test 1: Basic Chat
# ---------------------------------------------------------------------------

def test_basic_chat(client: anthropic.Anthropic) -> bool:
    """
    Send a simple message, confirm we get a text response back.
    Validates: API connectivity, auth, basic message structure.
    """
    print("\n" + "=" * 60)
    print("TEST 1: Basic Chat")
    print("=" * 60)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": "Reply with exactly: VALIDATION_OK"
                }
            ],
        )

        # Check response structure
        assert response.stop_reason == "end_turn", \
            f"Expected stop_reason 'end_turn', got '{response.stop_reason}'"
        assert len(response.content) > 0, "Response content is empty"
        assert response.content[0].type == "text", \
            f"Expected text block, got '{response.content[0].type}'"

        text = response.content[0].text
        print(f"  Response: {text[:100]}")
        print(f"  Stop reason: {response.stop_reason}")
        print(f"  Input tokens: {response.usage.input_tokens}")
        print(f"  Output tokens: {response.usage.output_tokens}")
        print(f"  Model: {response.model}")
        print("  ✅ PASSED")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False


# ---------------------------------------------------------------------------
# Test 2: Tool Use
# ---------------------------------------------------------------------------

def test_tool_use(client: anthropic.Anthropic) -> bool:
    """
    Define a tool, send a message that should trigger it, handle the
    tool call, send the result back, and get a final text response.

    This validates the EXACT loop the backend uses for reference
    document retrieval (PRD Section 6.3).
    """
    print("\n" + "=" * 60)
    print("TEST 2: Tool Use (get_reference_document pattern)")
    print("=" * 60)

    # Define a tool that mimics our reference document retrieval
    tools = [
        {
            "name": "get_reference_document",
            "description": (
                "Retrieve a reference document from the knowledge base. "
                "Use this when you need detailed procedural guidance."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The unique identifier of the reference document."
                    }
                },
                "required": ["document_id"]
            }
        }
    ]

    messages = [
        {
            "role": "user",
            "content": (
                "You have a reference document available called 'scam-fraud-sop' "
                "that covers scam investigation procedures. Please retrieve it "
                "using the get_reference_document tool, then summarise what "
                "you received in one sentence."
            )
        }
    ]

    try:
        # --- First API call: expect tool_use ---
        print("  Step 1: Sending message that should trigger tool call...")
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=messages,
            tools=tools,
        )

        print(f"  Stop reason: {response.stop_reason}")

        # The model should request the tool
        assert response.stop_reason == "tool_use", \
            f"Expected stop_reason 'tool_use', got '{response.stop_reason}'"

        # Find the tool_use block
        tool_use_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_use_block = block
                break

        assert tool_use_block is not None, "No tool_use block found in response"
        assert tool_use_block.name == "get_reference_document", \
            f"Expected tool name 'get_reference_document', got '{tool_use_block.name}'"

        print(f"  Tool called: {tool_use_block.name}")
        print(f"  Tool input: {json.dumps(tool_use_block.input)}")
        print(f"  Tool use ID: {tool_use_block.id}")

        # --- Second API call: send tool result, get final response ---
        print("  Step 2: Sending tool result back...")

        # Append the assistant's response (including the tool_use block)
        messages.append({"role": "assistant", "content": response.content})

        # Append the tool result
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": (
                        "# Scam & Fraud Investigation SOP\n\n"
                        "This document covers first-party and third-party scam "
                        "classification, victim vs willing participant determination, "
                        "romance scam patterns, and evidence thresholds for escalation."
                    )
                }
            ]
        })

        response2 = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=messages,
            tools=tools,
        )

        assert response2.stop_reason == "end_turn", \
            f"Expected stop_reason 'end_turn' after tool result, got '{response2.stop_reason}'"

        # Extract text from final response
        final_text = ""
        for block in response2.content:
            if block.type == "text":
                final_text += block.text

        assert len(final_text) > 0, "Final response after tool result is empty"

        print(f"  Final response: {final_text[:150]}...")
        print(f"  Input tokens (call 2): {response2.usage.input_tokens}")
        print(f"  Output tokens (call 2): {response2.usage.output_tokens}")
        print("  ✅ PASSED — Full tool call loop works")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Test 3: Image Input
# ---------------------------------------------------------------------------

def test_image_input(client: anthropic.Anthropic) -> bool:
    """
    Send a base64-encoded image with a text message.
    Validates that the vision capability works for KYC document
    screenshots and other image-based evidence.

    We generate a minimal valid PNG programmatically so this test
    has no external dependencies.
    """
    print("\n" + "=" * 60)
    print("TEST 3: Image Input (Vision)")
    print("=" * 60)

    try:
        # Generate a minimal 2x2 red PNG (no external file needed)
        # This is the smallest valid PNG that the API will accept
        png_bytes = _create_minimal_png()
        b64_image = base64.standard_b64encode(png_bytes).decode("utf-8")

        print(f"  Image size: {len(png_bytes)} bytes")
        print(f"  Base64 length: {len(b64_image)} chars")

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": b64_image,
                            }
                        },
                        {
                            "type": "text",
                            "text": "Describe what you see in this image in one sentence."
                        }
                    ]
                }
            ],
        )

        assert response.stop_reason == "end_turn", \
            f"Expected stop_reason 'end_turn', got '{response.stop_reason}'"
        assert len(response.content) > 0, "Response content is empty"

        text = response.content[0].text
        print(f"  Response: {text[:150]}")
        print(f"  Input tokens: {response.usage.input_tokens}")
        print("  ✅ PASSED — Image input works")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def _create_minimal_png() -> bytes:
    """
    Create a minimal valid 8x8 red PNG image.
    No external dependencies — pure Python using zlib.
    """
    import struct
    import zlib

    width, height = 8, 8

    def create_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)
        length = struct.pack(">I", len(data))
        return length + chunk + crc

    # PNG signature
    signature = b"\x89PNG\r\n\x1a\n"

    # IHDR chunk: width, height, bit depth 8, color type 2 (RGB)
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = create_chunk(b"IHDR", ihdr_data)

    # IDAT chunk: image data (red pixels)
    raw_data = b""
    for _ in range(height):
        raw_data += b"\x00"  # filter byte (none)
        for _ in range(width):
            raw_data += b"\xff\x00\x00"  # RGB red

    compressed = zlib.compress(raw_data)
    idat = create_chunk(b"IDAT", compressed)

    # IEND chunk
    iend = create_chunk(b"IEND", b"")

    return signature + ihdr + idat + iend


# ---------------------------------------------------------------------------
# Test 4: Streaming
# ---------------------------------------------------------------------------

def test_streaming(client: anthropic.Anthropic) -> bool:
    """
    Send a message with streaming enabled. Confirm that:
    - We receive incremental text chunks
    - The final message is complete
    - We get usage stats at the end

    This validates the SSE streaming the frontend depends on.
    """
    print("\n" + "=" * 60)
    print("TEST 4: Streaming")
    print("=" * 60)

    try:
        chunks_received = 0
        full_text = ""
        first_chunk_time = None
        start_time = time.time()

        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Write a brief 3-sentence summary of what a "
                        "financial crime investigator does."
                    )
                }
            ],
        ) as stream:
            for text in stream.text_stream:
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                chunks_received += 1
                full_text += text

        end_time = time.time()

        # Get the final message for usage stats
        final_message = stream.get_final_message()

        assert chunks_received > 1, \
            f"Expected multiple chunks, got {chunks_received}"
        assert len(full_text) > 0, "Streamed text is empty"

        time_to_first = (first_chunk_time - start_time) if first_chunk_time else 0
        total_time = end_time - start_time

        print(f"  Chunks received: {chunks_received}")
        print(f"  Full text length: {len(full_text)} chars")
        print(f"  Time to first chunk: {time_to_first:.2f}s")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Input tokens: {final_message.usage.input_tokens}")
        print(f"  Output tokens: {final_message.usage.output_tokens}")
        print(f"  Text preview: {full_text[:150]}...")
        print("  ✅ PASSED — Streaming works")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Test 5: System Prompt + Tool Use Combined (Integration)
# ---------------------------------------------------------------------------

def test_system_prompt_with_tools(client: anthropic.Anthropic) -> bool:
    """
    Send a message with a system prompt AND tools defined.
    This mirrors the actual production payload structure:
    system prompt (core KB) + messages + tool definitions.

    Validates that all three work together without conflicts.
    """
    print("\n" + "=" * 60)
    print("TEST 5: System Prompt + Tools (Integration)")
    print("=" * 60)

    system_prompt = (
        "You are an AI investigation assistant for financial crime cases. "
        "You have access to reference documents via the get_reference_document tool. "
        "Always be concise. When you receive case data, begin with an assessment.\n\n"
        "## REFERENCE DOCUMENT INDEX\n"
        "- **scam-fraud-sop**: Covers scam classification, victim determination\n"
        "- **block-unblock-guidelines**: Covers account blocking criteria\n"
    )

    tools = [
        {
            "name": "get_reference_document",
            "description": (
                "Retrieve a reference document from the knowledge base."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "The document ID from the reference index."
                    }
                },
                "required": ["document_id"]
            }
        }
    ]

    # Simulate the initial case data injection + first AI assessment
    messages = [
        {
            "role": "user",
            "content": (
                "[CASE DATA]\n"
                "Case ID: CASE-TEST-001\n"
                "Type: Scam\n"
                "Subject: BIN-12345678\n"
                "Summary: Suspected romance scam. 5 outbound transfers totalling "
                "$45,000 to 3 flagged counterparties over 2 months.\n\n"
                "Please provide your initial assessment of this case."
            )
        }
    ]

    try:
        print("  Sending case data with system prompt and tools...")
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=messages,
            tools=tools,
        )

        print(f"  Stop reason: {response.stop_reason}")
        print(f"  Input tokens: {response.usage.input_tokens}")
        print(f"  Output tokens: {response.usage.output_tokens}")

        # The model might respond with text, or it might request a tool first.
        # Either is valid — we just need to confirm no errors.
        text_parts = []
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(block.name)

        if text_parts:
            print(f"  Text response: {' '.join(text_parts)[:150]}...")
        if tool_calls:
            print(f"  Tool calls made: {tool_calls}")

        print("  ✅ PASSED — System prompt + tools work together")
        return True

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TEST_MAP = {
    "chat": ("Basic Chat", test_basic_chat),
    "tools": ("Tool Use", test_tool_use),
    "images": ("Image Input", test_image_input),
    "streaming": ("Streaming", test_streaming),
    "integration": ("System Prompt + Tools", test_system_prompt_with_tools),
}


def main():
    parser = argparse.ArgumentParser(
        description="Validate Anthropic API capabilities for FCI Platform"
    )
    parser.add_argument(
        "--test",
        choices=list(TEST_MAP.keys()),
        help="Run a specific test (default: all)",
        default=None,
    )
    args = parser.parse_args()

    client = get_client()

    print(f"Model: {MODEL}")
    print(f"Max tokens: {MAX_TOKENS}")

    if args.test:
        tests_to_run = {args.test: TEST_MAP[args.test]}
    else:
        tests_to_run = TEST_MAP

    results = {}
    for key, (name, test_fn) in tests_to_run.items():
        results[name] = test_fn(client)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n  All tests passed. Backend can be built on these capabilities.")
    else:
        print("\n  Some tests failed. Fix before proceeding with backend development.")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()