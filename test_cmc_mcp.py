import os
import sys
import asyncio
import traceback
import httpx

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


CMC_MCP_URL = "https://mcp.coinmarketcap.com/mcp"


async def main():
    api_key = os.getenv("CMC_API_KEY")

    if not api_key:
        print("ERROR: CMC_API_KEY is not set.")
        sys.exit(1)

    print("=" * 60)
    print("CoinMarketCap MCP Connection Test")
    print("=" * 60)

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

        print("Creating HTTP client...")

        async with httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        ) as http_client:

            print("Connecting to CMC MCP...")

            async with streamable_http_client(
                CMC_MCP_URL,
                http_client=http_client,
            ) as streams:

                read_stream, write_stream, _ = streams

                print("HTTP connection established.")

                async with ClientSession(
                    read_stream,
                    write_stream,
                ) as session:

                    print("Initializing MCP session...")

                    init_result = await session.initialize()

                    print("MCP INITIALIZE: OK")
                    print()

                    if init_result.serverInfo:
                        print(
                            f"SERVER: "
                            f"{init_result.serverInfo.name}"
                        )

                        print(
                            f"VERSION: "
                            f"{init_result.serverInfo.version}"
                        )

                    print()
                    print("Requesting available tools...")

                    result = await session.list_tools()

                    tools = result.tools

                    print(f"TOOLS FOUND: {len(tools)}")
                    print()

                    for tool in tools:
                        print(f"- {tool.name}")

                    print()

                    technical_analysis_found = any(
                        tool.name == "get_crypto_technical_analysis"
                        for tool in tools
                    )

                    if technical_analysis_found:
                        print(
                            "TECHNICAL ANALYSIS TOOL: FOUND"
                        )
                        print(
                            "get_crypto_technical_analysis"
                        )
                    else:
                        print(
                            "TECHNICAL ANALYSIS TOOL: NOT FOUND"
                        )
                        sys.exit(1)

                    print()
                    print("=" * 60)
                    print("CMC MCP TEST: SUCCESS")
                    print("=" * 60)

    except Exception:
        print()
        print("=" * 60)
        print("CMC MCP TEST: FAILED")
        print("=" * 60)
        print()
        print("FULL ERROR DETAILS:")
        print()

        traceback.print_exc()

        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
