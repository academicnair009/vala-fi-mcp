# Vala-Fi MCP Server

**A Bloomberg Terminal you can talk to.** Query company relationships — suppliers, customers, competitors, supply chain paths — directly from Claude, Cursor, or any MCP-compatible AI assistant.

Every relationship is extracted from SEC 10-K filings. Every edge has a citation. No black boxes.

[![MCP Badge](https://lobehub.com/badge/mcp/academicnair009-vala-fi-mcp)](https://lobehub.com/mcp/academicnair009-vala-fi-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Why This Exists

Bloomberg Terminal costs $24,000/year. FactSet starts at $12,000. PitchBook won't even show you pricing without a sales call.

**Vala-Fi gives you the same company relationship data for free.**

We extract supplier, customer, and competitor relationships from SEC 10-K annual filings using AI — the same source of truth that institutional investors rely on. The difference: you get it as a structured API with graph traversal, not a 200-page PDF.

**5,200+ companies. 8,000+ relationships. 11 sectors. Free during beta.**

---

## Quick Start

### 1. Get a free API key

Sign up at [valafi.dev/signup](https://valafi.dev/signup) — takes 10 seconds, no credit card.

### 2. Configure your AI assistant

#### Remote Server (Recommended — zero install)

No packages to install. Just paste the config and go.

**Claude Desktop** — add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "vala-fi": {
      "url": "https://mcp.valafi.dev/mcp",
      "headers": {
        "X-API-Key": "vfi_your_key_here"
      }
    }
  }
}
```

**Cursor** — add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "vala-fi": {
      "url": "https://mcp.valafi.dev/mcp",
      "headers": {
        "X-API-Key": "vfi_your_key_here"
      }
    }
  }
}
```

**Windsurf / Claude Code** — same config format as above.

#### Local Server (Alternative — runs on your machine)

If you prefer running the server locally:

```json
{
  "mcpServers": {
    "vala-fi": {
      "command": "uvx",
      "args": ["vala-fi-mcp"],
      "env": {
        "VALAFI_API_KEY": "vfi_your_key_here"
      }
    }
  }
}
```

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

### 3. Start asking questions

That's it. Your AI assistant now has access to a financial knowledge graph.

---

## Available Tools

| Tool | Description |
|------|-------------|
| `get_company_profile` | Company name, sector, industry, exchange |
| `get_supply_chain` | Upstream/downstream relationships (1-3 hops) |
| `get_customers` | All known customers with SEC citations |
| `get_competitors` | All known competitors with SEC citations |
| `find_path` | Shortest path between two companies |
| `get_exposure` | Supply chain concentration risk analysis |
| `get_sector_graph` | Full sector relationship subgraph (paid tier) |

---

## Prompts

Pre-built prompt templates you can invoke directly:

| Prompt | Description |
|--------|-------------|
| `analyze_supply_chain` | Deep-dive a company's suppliers, customers, competitors, and concentration risk |
| `compare_companies` | Compare two companies — shared suppliers, paths, competitive overlap |
| `portfolio_risk_check` | Cross-portfolio supply chain risk assessment (pass comma-separated tickers) |
| `due_diligence` | Structured due diligence memo from SEC filing data |

---

## Resources

| Resource URI | Description |
|--------------|-------------|
| `valafi://sectors` | List of all 11 sectors covered in the knowledge graph |
| `valafi://api-info` | API overview, endpoint URL, and free tier limits |

---

## What You Can Do

Ask your AI assistant questions like:

- *"Who are Apple's top suppliers?"*
- *"Find the connection between Tesla and NVIDIA"*
- *"What companies depend on TSMC as a sole supplier?"*
- *"Show me all competitors of Microsoft mentioned in SEC filings"*
- *"What's the supply chain risk for my portfolio: AAPL, MSFT, GOOGL?"*

Every answer comes with the SEC filing citation so you can verify it yourself.

---

## Use Cases

### Solo Developer / Indie Hacker
You're building a stock analysis tool and need to understand company relationships without paying for a Bloomberg Terminal. Vala-Fi gives you structured supply chain data through a simple API.

### AI Agent Builder
You're building an autonomous research agent that needs to answer questions like "What happens to Apple if TSMC has a production issue?" Plug in Vala-Fi as an MCP tool and your agent can traverse the financial graph.

### Quantitative Researcher
You're modeling supply chain risk or building factor models that incorporate inter-company dependencies. Query the graph programmatically and get SEC-cited evidence for every relationship.

### Due Diligence Analyst
You're evaluating an acquisition target and need to quickly map their supplier/customer network. One API call gives you the full picture with citations.

### Financial Content Creator
You're writing analysis and need to verify company relationships. Instead of reading 10-K filings manually, query the graph and get the exact excerpt.

---

## Free Tier Limits

| Limit | Value |
|-------|-------|
| Requests per day | 50 |
| Unique tickers per day | 10 |
| Results per query | 5 |
| Max hop depth | 2 |
| Strength scores | Included |
| SEC citations | All results |
| Sector graph | Paid only |

Need more? [Contact us](https://valafi.dev/pricing).

---

## Example Session

```
You: Who are NVIDIA's main suppliers according to SEC filings?

Claude: Based on NVIDIA's SEC 10-K filings, here are their key suppliers:

1. **TSMC** (TSM) - Primary foundry partner manufacturing NVIDIA's GPUs
   "Taiwan Semiconductor Manufacturing Company Limited manufactures
   our GPUs and Tegra processors..." — NVIDIA 10-K

2. **Samsung Electronics** - Secondary foundry for certain chip production
   "Samsung manufactures different different different different..." — NVIDIA 10-K

3. **Amkor Technology** (AMKR) - Packaging and testing services
   "We use third-party foundries, including TSMC and Samsung,
   and packaging and test providers such as Amkor..." — NVIDIA 10-K
```

---

## Direct API Usage (Without MCP)

Don't need an AI assistant? Use the REST API directly:

```bash
# Get Apple's suppliers
curl -H "X-API-Key: vfi_your_key" \
  https://api.valafi.dev/v1/company/AAPL/supply-chain

# Find path between Tesla and NVIDIA
curl -H "X-API-Key: vfi_your_key" \
  https://api.valafi.dev/v1/path/TSLA/NVDA

# Get supply chain risk for a company
curl -H "X-API-Key: vfi_your_key" \
  https://api.valafi.dev/v1/exposure/AAPL
```

Full API documentation: [valafi.dev/docs](https://valafi.dev/docs)

---

## Data Source

All relationship data is extracted from **SEC 10-K annual filings** using AI. We do not scrape news, social media, or third-party databases.

- Source: [SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany)
- Coverage: 5,200+ public companies across 11 GICS sectors
- Update frequency: As new 10-K filings are published (primarily Q1 and Q3)
- Relationship types: supplier, customer, competitor, partner, and more

---

## Links

- **Website:** [valafi.dev](https://valafi.dev)
- **API Docs:** [valafi.dev/docs](https://valafi.dev/docs)
- **Get API Key:** [valafi.dev/signup](https://valafi.dev/signup)
- **Pricing:** [valafi.dev/pricing](https://valafi.dev/pricing)

---

## License

MIT — use it however you want.
