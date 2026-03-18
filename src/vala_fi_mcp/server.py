"""
Vala-Fi MCP Server

Gives AI assistants (Claude, Cursor, Windsurf) direct access to the Vala-Fi
financial knowledge graph — company relationships extracted from SEC 10-K filings.

Think of it as a Bloomberg Terminal you can talk to.
"""

import os
import httpx
from mcp.server.fastmcp import FastMCP

API_URL = os.environ.get("VALAFI_API_URL", "https://api.valafi.dev")
API_KEY = os.environ.get("VALAFI_API_KEY", "")

mcp = FastMCP(
    "Vala-Fi",
    description="Financial knowledge graph — company relationships from SEC 10-K filings",
)

def _headers() -> dict[str, str]:
    if not API_KEY:
        raise ValueError(
            "VALAFI_API_KEY not set. Get a free key at https://valafi.dev/signup"
        )
    return {"X-API-Key": API_KEY}


async def _get(path: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(base_url=API_URL, timeout=30) as client:
        resp = await client.get(path, headers=_headers(), params=params)
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def get_company(ticker: str) -> dict:
    """
    Get company profile by ticker symbol.

    Returns basic company information including name, sector, industry,
    country, and exchange. Use this to look up any company in the graph.

    Example: get_company("AAPL") -> Apple Inc., Technology, Consumer Electronics
    """
    return await _get(f"/v1/company/{ticker.upper()}")


@mcp.tool()
async def get_supply_chain(
    ticker: str,
    hops: int = 1,
    direction: str = "upstream",
) -> dict:
    """
    Get the supply chain for a company.

    Traverses the knowledge graph to find suppliers, customers, or both.
    Each relationship includes SEC 10-K citation evidence.

    Args:
        ticker: Stock ticker (e.g. "AAPL", "TSLA")
        hops: Depth of traversal (1 = direct relationships, 2 = second-degree). Free tier: max 2.
        direction: "upstream" (suppliers), "downstream" (customers), or "both"

    Example: get_supply_chain("AAPL", hops=2, direction="both")
    -> Shows Apple's suppliers, their suppliers, and Apple's customers
    """
    return await _get(
        f"/v1/company/{ticker.upper()}/supply-chain",
        params={"hops": hops, "direction": direction},
    )


@mcp.tool()
async def get_customers(ticker: str) -> dict:
    """
    Get all known customers of a company.

    Returns companies that list the queried company as a supplier in their
    SEC 10-K filings. Each relationship includes citation evidence.

    Example: get_customers("TSM") -> Apple, NVIDIA, AMD, Qualcomm...
    """
    return await _get(f"/v1/company/{ticker.upper()}/customers")


@mcp.tool()
async def get_competitors(ticker: str) -> dict:
    """
    Get all known competitors of a company.

    Competitors are identified from SEC 10-K filings where companies
    explicitly name their competitive landscape.

    Example: get_competitors("AAPL") -> Microsoft, Samsung, Google...
    """
    return await _get(f"/v1/company/{ticker.upper()}/competitors")


@mcp.tool()
async def find_path(ticker_a: str, ticker_b: str) -> dict:
    """
    Find the shortest path between two companies in the knowledge graph.

    Discovers how two companies are connected through supplier, customer,
    and competitor relationships. Great for finding hidden connections.

    Example: find_path("AAPL", "NVDA")
    -> Apple -> TSMC -> NVIDIA (connected through shared semiconductor supplier)
    """
    return await _get(f"/v1/path/{ticker_a.upper()}/{ticker_b.upper()}")


@mcp.tool()
async def get_exposure(ticker: str) -> dict:
    """
    Get supply chain exposure and concentration risk analysis.

    Identifies shared suppliers/customers across peer companies and
    flags single-source dependencies. Returns an exposure score.

    Example: get_exposure("AAPL")
    -> Shows TSMC as a high-risk sole supplier, shared suppliers with peers
    """
    return await _get(f"/v1/exposure/{ticker.upper()}")


@mcp.tool()
async def get_sector_graph(
    sector: str,
    relationship_types: str | None = None,
) -> dict:
    """
    Get the full relationship subgraph for an entire sector.

    Returns all companies and edges within the specified sector.
    Note: This endpoint requires a paid tier.

    Args:
        sector: Sector name (e.g. "Technology", "Healthcare", "Energy",
                "Financial Services", "Consumer Cyclical", "Industrials",
                "Communication Services", "Consumer Defensive",
                "Basic Materials", "Real Estate", "Utilities")
        relationship_types: Optional comma-separated filter (e.g. "supplier,customer")

    Example: get_sector_graph("Technology", relationship_types="supplier")
    """
    params = {}
    if relationship_types:
        params["relationship_types"] = relationship_types
    return await _get(f"/v1/sector/{sector}/graph", params=params or None)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
