import os
import asyncio
import json
import httpx

from mcp import ClientSession
from mcp.client.streamable_http import (
    streamable_http_client,
)


CMC_MCP_URL = "https://mcp.coinmarketcap.com/mcp"
TOOL_NAME = "get_crypto_technical_analysis"
BTC_ID = "1"


class TechnicalAnalysisError(Exception):
    pass


def _extract_text(result):
    parts = []

    for item in getattr(result, "content", []) or []:
        if hasattr(item, "text"):
            parts.append(item.text)
        else:
            parts.append(str(item))

    return "\n".join(parts)


def _find_value(obj, names):
    """
    Recursively searches a JSON-like object for one of
    the requested field names.
    """

    wanted = {
        name.lower()
        for name in names
    }

    if isinstance(obj, dict):

        for key, value in obj.items():

            if key.lower() in wanted:
                return value

        for value in obj.values():

            found = _find_value(
                value,
                names,
            )

            if found is not None:
                return found

    elif isinstance(obj, list):

        for item in obj:

            found = _find_value(
                item,
                names,
            )

            if found is not None:
                return found

    return None


def _parse_result(result):
    structured = getattr(
        result,
        "structuredContent",
        None,
    )

    if structured:
        return structured

    text = _extract_text(result)

    if not text:
        return {}

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "raw_text": text,
        }


async def _get_ta_async():
    api_key = os.getenv("CMC_API_KEY")

    if not api_key:
        raise TechnicalAnalysisError(
            "CMC_API_KEY is not configured."
        )

    headers = {
        "X-CMC-MCP-API-KEY": api_key,
        "Accept": "application/json, text/event-stream",
    }

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

        async with streamable_http_client(
            CMC_MCP_URL,
            http_client=http_client,
        ) as streams:

            read_stream, write_stream, _ = streams

            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                tools_result = await session.list_tools()

                tool = None

                for item in tools_result.tools:
                    if item.name == TOOL_NAME:
                        tool = item
                        break

                if tool is None:
                    raise TechnicalAnalysisError(
                        f"{TOOL_NAME} was not found."
                    )

                schema = tool.inputSchema or {}

                properties = schema.get(
                    "properties",
                    {},
                )

                arguments = {}

                # CMC documentation says most tools use numeric
                # CMC IDs.
                if "id" in properties:
                    arguments["id"] = BTC_ID

                elif "crypto_id" in properties:
                    arguments["crypto_id"] = BTC_ID

                elif "coin_id" in properties:
                    arguments["coin_id"] = BTC_ID

                elif "symbol" in properties:
                    arguments["symbol"] = "BTC"

                # Daily timeframe if supported by the schema.
                if "timeframe" in properties:
                    arguments["timeframe"] = "1D"

                elif "interval" in properties:
                    arguments["interval"] = "1D"

                elif "time_frame" in properties:
                    arguments["time_frame"] = "1D"

                result = await session.call_tool(
                    TOOL_NAME,
                    arguments=arguments,
                )

                return _parse_result(result)


def get_btc_daily_ta():
    try:
        data = asyncio.run(
            _get_ta_async()
        )

    except Exception as exc:
        raise TechnicalAnalysisError(
            f"CMC Technical Analysis failed: {exc}"
        ) from exc

    # RSI
    rsi = _find_value(
        data,
        [
            "rsi",
            "RSI(14)",
            "rsi_14",
        ],
    )

    # EMA 330
    ema330 = _find_value(
        data,
        [
            "ema330",
            "ema_330",
            "EMA330",
            "ema 330",
        ],
    )

    # Stochastic is intentionally NOT calculated.
    #
    # CMC's documented TA tool currently lists RSI, moving
    # averages, MACD, Fibonacci and pivots, but not Stochastic.
    #
    # We therefore leave it unavailable until we connect
    # a second verified data source.

    return {
        "rsi": rsi,
        "ema330": ema330,
        "stoch_k": None,
        "stoch_d": None,
        "raw": data,
    }
