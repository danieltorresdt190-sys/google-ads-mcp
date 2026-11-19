
"""Herramientas de Google Search Console para el MCP."""

import json
from datetime import date
from urllib.parse import quote
from urllib.request import Request, urlopen

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

search_console_mcp = FastMCP("search_console")


def call_google_api(method, url, payload=None):
    token = get_access_token()

    if not token or not token.token:
        raise RuntimeError(
            "Debes autorizar Google desde ChatGPT."
        )

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Accept": "application/json",
    }

    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")

    request = Request(
        url, data=body, headers=headers, method=method
    )

    with urlopen(request, timeout=30) as response:
        return json.load(response)


@search_console_mcp.tool()
def list_sites() -> dict:
    """Lista las propiedades disponibles en Search Console."""
    return call_google_api(
        "GET",
        "https://www.googleapis.com/webmasters/v3/sites",
    )


@search_console_mcp.tool()
def search_performance(
    site_url: str,
    start_date: str,
    end_date: str,
    dimension: str = "query",
    row_limit: int = 100,
) -> dict:
    """Consulta clics, impresiones, CTR y posición SEO."""

    allowed = {"query", "page", "date", "country", "device"}
    if dimension not in allowed:
        raise ValueError("Dimensión no permitida")

    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    if start > end:
        raise ValueError("La fecha inicial supera la final")

    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": [dimension],
        "rowLimit": max(1, min(row_limit, 25000)),
    }

    property_url = quote(site_url, safe="")
    endpoint = (
        "https://www.googleapis.com/webmasters/v3/sites/"
        f"{property_url}/searchAnalytics/query"
    )

    return call_google_api("POST", endpoint, payload)
