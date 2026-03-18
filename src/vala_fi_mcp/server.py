"""
Vala-Fi MCP Server

Gives AI assistants (Claude, Cursor, Windsurf) direct access to the Vala-Fi
financial knowledge graph — company relationships extracted from SEC 10-K filings.

Think of it as a Bloomberg Terminal you can talk to.
"""

import os
import re
import httpx
from mcp.server.fastmcp import FastMCP

API_URL = os.environ.get("VALAFI_API_URL", "https://api.valafi.dev")
API_KEY = os.environ.get("VALAFI_API_KEY", "")

mcp = FastMCP(
    "Vala-Fi",
    instructions="Financial knowledge graph — company relationships from SEC 10-K filings",
)

_TICKER_RE = re.compile(r"^[A-Z0-9.\-]{1,10}$")


def _validate_ticker(ticker: str) -> str:
    """Validate and sanitize ticker input to prevent path traversal."""
    cleaned = ticker.strip().upper()
    if not _TICKER_RE.match(cleaned):
        raise ValueError(f"Invalid ticker symbol: {ticker!r}")
    return cleaned


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
async def get_company_profile(ticker: str) -> dict:
    """
    Get company profile by ticker symbol.

    Returns basic company information including name, sector, industry,
    country, and exchange. Use this to look up any company in the graph.

    Example: get_company_profile("AAPL") -> Apple Inc., Technology, Consumer Electronics
    """
    return await _get(f"/v1/company/{_validate_ticker(ticker)}")


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
        f"/v1/company/{_validate_ticker(ticker)}/supply-chain",
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
    return await _get(f"/v1/company/{_validate_ticker(ticker)}/customers")


@mcp.tool()
async def get_competitors(ticker: str) -> dict:
    """
    Get all known competitors of a company.

    Competitors are identified from SEC 10-K filings where companies
    explicitly name their competitive landscape.

    Example: get_competitors("AAPL") -> Microsoft, Samsung, Google...
    """
    return await _get(f"/v1/company/{_validate_ticker(ticker)}/competitors")


@mcp.tool()
async def find_path(ticker_a: str, ticker_b: str) -> dict:
    """
    Find the shortest path between two companies in the knowledge graph.

    Discovers how two companies are connected through supplier, customer,
    and competitor relationships. Great for finding hidden connections.

    Example: find_path("AAPL", "NVDA")
    -> Apple -> TSMC -> NVIDIA (connected through shared semiconductor supplier)
    """
    return await _get(f"/v1/path/{_validate_ticker(ticker_a)}/{_validate_ticker(ticker_b)}")


@mcp.tool()
async def get_exposure(ticker: str) -> dict:
    """
    Get supply chain exposure and concentration risk analysis.

    Identifies shared suppliers/customers across peer companies and
    flags single-source dependencies. Returns an exposure score.

    Example: get_exposure("AAPL")
    -> Shows TSMC as a high-risk sole supplier, shared suppliers with peers
    """
    return await _get(f"/v1/exposure/{_validate_ticker(ticker)}")


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
    if sector not in SECTORS:
        raise ValueError(f"Unknown sector: {sector!r}. Valid: {', '.join(SECTORS)}")
    params = {}
    if relationship_types:
        params["relationship_types"] = relationship_types
    return await _get(f"/v1/sector/{sector}/graph", params=params or None)


# ── Resources ──────────────────────────────────────────────────────────

SECTORS = [
    "Technology", "Healthcare", "Financial Services", "Energy",
    "Consumer Cyclical", "Industrials", "Communication Services",
    "Consumer Defensive", "Basic Materials", "Real Estate", "Utilities",
]


@mcp.resource("valafi://sectors")
def list_sectors() -> str:
    """List all sectors covered in the Vala-Fi knowledge graph."""
    return "\n".join(SECTORS)


@mcp.resource("valafi://api-info")
def api_info() -> str:
    """Vala-Fi API overview and free tier limits."""
    return "\n".join([
        "Vala-Fi Financial Knowledge Graph API",
        f"Endpoint: {API_URL}",
        "Coverage: 5,200+ companies, 8,000+ relationships, 11 sectors",
        "Data source: SEC 10-K annual filings",
        "",
        "Free tier limits:",
        "  - 50 requests/day",
        "  - 10 unique tickers/day",
        "  - 5 results per query",
        "  - 2-hop max supply chain depth",
        "  - Full strength scores and SEC citations",
        "  - Sector graph endpoint: paid only",
        "",
        "Docs: https://valafi.dev/docs",
        "Get API key: https://valafi.dev/signup",
    ])


# ── Prompts ────────────────────────────────────────────────────────────


@mcp.prompt()
def analyze_supply_chain(ticker: str) -> str:
    """Deep-dive into a company's supply chain with risk analysis."""
    return f"""Analyze the full supply chain for {ticker.upper()}:

1. Use get_supply_chain("{ticker.upper()}", hops=2, direction="both") to map suppliers and customers
2. Use get_competitors("{ticker.upper()}") to identify competitive landscape
3. Use get_exposure("{ticker.upper()}") to assess concentration risk

For each key relationship, note the SEC 10-K citation evidence.
Highlight any single-source dependencies or high-risk suppliers.
Summarize with an overall supply chain health assessment."""


@mcp.prompt()
def compare_companies(ticker_a: str, ticker_b: str) -> str:
    """Compare two companies' relationships and find connections."""
    return f"""Compare {ticker_a.upper()} and {ticker_b.upper()}:

1. Use get_company_profile for both to compare sectors and profiles
2. Use find_path("{ticker_a.upper()}", "{ticker_b.upper()}") to discover how they're connected
3. Use get_supply_chain for both to compare their supplier networks
4. Use get_competitors for both to see if they compete or share competitors

Summarize: How are these companies related? Do they share suppliers?
Are they competitors? What's the shortest path between them?"""


@mcp.prompt()
def portfolio_risk_check(tickers: str) -> str:
    """Assess supply chain risk across a portfolio of stocks."""
    ticker_list = [t.strip().upper() for t in tickers.split(",")]
    steps = []
    for t in ticker_list:
        steps.append(f'- get_exposure("{t}") for concentration risk')
        steps.append(f'- get_supply_chain("{t}", direction="upstream") for supplier dependencies')

    return f"""Analyze supply chain risk for this portfolio: {', '.join(ticker_list)}

For each company:
{chr(10).join(steps)}

Then cross-reference:
- Which suppliers appear across multiple portfolio companies? (shared risk)
- Are there any single-source dependencies?
- Which sectors have the most concentration risk?

Provide a risk summary table and flag the top 3 risks."""


@mcp.prompt()
def due_diligence(ticker: str) -> str:
    """Run a due diligence check on a company using SEC filing data."""
    return f"""Run due diligence on {ticker.upper()} using SEC 10-K filing data:

1. get_company_profile("{ticker.upper()}") — basic profile
2. get_supply_chain("{ticker.upper()}", hops=2, direction="both") — full supplier/customer map
3. get_competitors("{ticker.upper()}") — competitive landscape
4. get_exposure("{ticker.upper()}") — supply chain risks

For each finding, include the SEC filing citation.
Structure the output as a due diligence memo:
- Company Overview
- Key Relationships (suppliers, customers)
- Competitive Position
- Supply Chain Risks
- Summary Assessment"""


def main():
    mcp.run()


if __name__ == "__main__":
    main()
