#!/usr/bin/env python3
"""
Test script for the MCP server HTTP endpoint with proper session management
"""

import asyncio
import aiohttp
import json
import sys
import argparse
import re


def parse_sse_messages(text: str):
    """Parse Server-Sent Events format"""
    messages = []
    current_event = {}

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            if current_event.get("data"):
                try:
                    messages.append(json.loads(current_event["data"]))
                except json.JSONDecodeError:
                    pass
                current_event = {}
            continue

        if line.startswith("data:"):
            data = line[5:].strip()
            current_event["data"] = current_event.get("data", "") + data
        elif line.startswith("event:"):
            current_event["event"] = line[6:].strip()

    # Handle last message
    if current_event.get("data"):
        try:
            messages.append(json.loads(current_event["data"]))
        except json.JSONDecodeError:
            pass

    return messages


async def test_mcp_tool(base_url: str, tool_name: str, arguments: dict):
    """Test an MCP tool via HTTP with proper session management"""

    # Remove trailing slash if present
    base_url = base_url.rstrip("/")

    async with aiohttp.ClientSession() as session:
        # Step 1: Initialize the MCP session
        print(f"🔄 Initializing MCP session at {base_url}/mcp...")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1,
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        try:
            async with session.post(
                f"{base_url}/mcp",
                json=init_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json,text/event-stream",
                },
            ) as response:
                if response.status != 200:
                    print(f"❌ Initialize failed with status {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return False

                # Get session ID from response headers (check lowercase too)
                session_id = (
                    response.headers.get("mcp-session-id")
                    or response.headers.get("X-Mcp-Session-Id")
                    or response.headers.get("X-Session-Id")
                    or response.headers.get("Session-Id")
                )

                if not session_id:
                    print("❌ No session ID in headers")
                    print("Available headers:")
                    for key, value in response.headers.items():
                        print(f"   {key}: {value}")
                    return False

                # Parse SSE response
                response_text = await response.text()
                messages = parse_sse_messages(response_text)

                if not messages:
                    print(f"❌ No messages parsed from SSE response")
                    return False

                init_response = messages[0] if messages else {}
                print(f"✅ Session initialized: {session_id}")
                print(
                    f"   Server: {init_response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}"
                )

        except Exception as e:
            print(f"❌ Initialize error: {e}")
            return False

        # Step 2: Call the tool
        print(f"\n🔄 Calling tool '{tool_name}'...")
        tool_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 2,
            "params": {"name": tool_name, "arguments": arguments},
        }

        try:
            async with session.post(
                f"{base_url}/mcp",
                json=tool_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json,text/event-stream",
                    "mcp-session-id": session_id,
                },
            ) as response:
                if response.status != 200:
                    print(f"❌ Tool call failed with status {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return False

                # Parse SSE response
                response_text = await response.text()
                messages = parse_sse_messages(response_text)

                if not messages:
                    print(f"❌ No messages parsed from SSE response")
                    print(f"Raw response:\n{response_text}")
                    return False

                result = messages[0] if messages else {}
                print(f"✅ Tool call successful!")
                print(f"\n📄 Result:")
                print(json.dumps(result, indent=2))

                # Also print the content if available
                if "result" in result and "content" in result["result"]:
                    content = result["result"]["content"]
                    if isinstance(content, list) and len(content) > 0:
                        print(f"\n📝 Tool Output:")
                        for item in content:
                            if item.get("type") == "text":
                                print(item.get("text", ""))

                return True

        except Exception as e:
            print(f"❌ Tool call error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Test MCP server HTTP endpoint")
    parser.add_argument(
        "--url",
        default="https://mcp-server-aap.apps.cluster-5ffmt.5ffmt.sandbox1919.opentlc.com",
        help="Base URL of the MCP server",
    )
    parser.add_argument("--tool", default="get_projects", help="Tool name to call")
    parser.add_argument("--args", default="{}", help="Tool arguments as JSON string")

    args = parser.parse_args()

    try:
        arguments = json.loads(args.args)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in arguments: {e}")
        sys.exit(1)

    print("🚀 Testing MCP Server HTTP Endpoint")
    print("=" * 60)
    print(f"URL: {args.url}")
    print(f"Tool: {args.tool}")
    print(f"Arguments: {json.dumps(arguments, indent=2)}")
    print("=" * 60)

    success = asyncio.run(test_mcp_tool(args.url, args.tool, arguments))

    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
