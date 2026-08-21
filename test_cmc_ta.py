import os
import sys
import asyncio
import json
import traceback
import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


CMC_MCP_URL = "https://mcp.coinmarketcap.com/mcp"

TOOL_NAME = "get_crypto_technical_analysis"

# Bitcoin CMC ID
BTC_ID = "1"


async def main():
    api_key = os.getenv("CMC_API_KEY")

    if not api_key:
        print("ERROR: CMC_API_KEY is not set.")
        sys.exit(1)

    print("=" * 70)
    print("CoinMarketCap Technical Analysis Test")
    print("=" * 70)

    headers = {
        "X-CMC-MCP-API-KEY": api_key,
        "Accept": "application/json, text/event-stream",
    }

    try:
        timeout = httpx.Timeout(
            connect=30.0,
            read=120.0,
            write=30.0,
            pool=30.0,
        )

        async with httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        ) as http_client:

            print("Connecting to CoinMarketCap MCP...")

            async with streamable_http_client(
                CMC_MCP_URL,
                http_client=http_client,
            ) as streams:

                read_stream, write_stream, _ = streams

                async with ClientSession(
                    read_stream,
                    write_stream,
                ) as session:

                    print("Initializing MCP...")
                    await session.initialize()

                    print("MCP CONNECTION: OK")
                    print()

                    # --------------------------------------------------
                    # Get available tools
                    # --------------------------------------------------

                    print("Loading available tools...")

                    tools_result = await session.list_tools()

                    tools = tools_result.tools

                    target_tool = None

                    for tool in tools:
                        if tool.name == TOOL_NAME:
                            target_tool = tool
                            break

                    if target_tool is None:
                        print()
                        print("ERROR:")
                        print(f"Tool '{TOOL_NAME}' was not found.")

                        print()
                        print("Available tools:")

                        for tool in tools:
                            print(f"- {tool.name}")

                        sys.exit(1)

                    print(f"FOUND TOOL: {TOOL_NAME}")
                    print()

                    # --------------------------------------------------
                    # Show tool input schema
                    # --------------------------------------------------

                    print("=" * 70)
                    print("TECHNICAL ANALYSIS TOOL SCHEMA")
                    print("=" * 70)

                    try:
                        schema = target_tool.inputSchema

                        print(
                            json.dumps(
                                schema,
                                indent=2,
                                ensure_ascii=False,
                            )
                        )

                    except Exception:
                        print(
                            "Could not display input schema."
                        )

                    print()

                    # --------------------------------------------------
                    # IMPORTANT:
                    # First inspect schema before making the call.
                    # --------------------------------------------------

                    print("=" * 70)
                    print("BTC DAILY TECHNICAL ANALYSIS")
                    print("=" * 70)

                    print(
                        "Bitcoin CMC ID:",
                        BTC_ID,
                    )

                    print(
                        "Requested timeframe: Daily"
                    )

                    print()

                    # --------------------------------------------------
                    # Try the most likely CMC parameter structure.
                    #
                    # If CMC rejects it, the returned error will expose
                    # the exact expected parameters.
                    # --------------------------------------------------

                    arguments = {
                        "id": BTC_ID,
                        "timeframe": "1d",
                    }

                    print("Calling Technical Analysis tool...")
                    print()

                    result = await session.call_tool(
                        TOOL_NAME,
                        arguments=arguments,
                    )

                    # --------------------------------------------------
                    # Print result
                    # --------------------------------------------------

                    print("=" * 70)
                    print("RAW CMC TECHNICAL ANALYSIS RESPONSE")
                    print("=" * 70)

                    if result.content:

                        for index, item in enumerate(
                            result.content,
                            start=1,
                        ):
                            print()
                            print(f"CONTENT ITEM #{index}")
                            print("-" * 70)

                            if hasattr(item, "text"):
                                print(item.text)

                            else:
                                print(str(item))

                    else:
                        print("CMC returned an empty response.")

                    # --------------------------------------------------
                    # Structured content if available
                    # --------------------------------------------------

                    if getattr(result, "structuredContent", None):

                        print()
                        print("=" * 70)
                        print("STRUCTURED CONTENT")
                        print("=" * 70)

                        print(
                            json.dumps(
                                result.structuredContent,
                                indent=2,
                                ensure_ascii=False,
                                default=str,
                            )
                        )

                    print()
                    print("=" * 70)
                    print("TECHNICAL ANALYSIS TEST FINISHED")
                    print("=" * 70)

    except Exception:
        print()
        print("=" * 70)
        print("CMC TECHNICAL ANALYSIS TEST: FAILED")
        print("=" * 70)

        print()
        print("FULL ERROR DETAILS:")
        print()

        traceback.print_exc()

        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
