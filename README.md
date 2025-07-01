# NPI Registry MCP Server

A Model Context Protocol (MCP) server for searching the National Provider Identifier (NPI) registry. This server provides tools to search and retrieve information about healthcare providers and organizations in the United States.

## Overview

NPI is a unique identification number for covered health care providers in the United States. This MCP server allows Claude and other MCP-compatible clients to search the official NPI registry maintained by the Centers for Medicare & Medicaid Services (CMS), and integrates the results into an LLM context for enhanced analysis and insights.

### Features

- **Search by Provider Name**: Find individual healthcare providers by first name, last name, or both
- **Search by Organization**: Look up healthcare organizations by name
- **Search by NPI Number**: Direct lookup using a specific 10-digit NPI
- **Location-based Search**: Filter results by city, state, or postal code
- **Specialty Search**: Find providers by their specialty or taxonomy description
- **Comprehensive Data**: Returns detailed information including addresses, practice locations, specialties, and other identifiers

### Use Cases

- Verify healthcare provider credentials
- Find provider contact information and addresses
- Look up organization details and authorized officials
- Validate NPI numbers
- Research provider specialties and taxonomies
- Find providers in specific geographic areas

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Development Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/eliotk/npi-registry-mcp-server.git
   cd npi-registry-mcp-server
   ```

2. **Install uv** (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create a virtual environment and install dependencies**:

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

4. **Run the server directly** (for testing):
   ```bash
   uv run python -m npi_registry_mcp.server
   # or using the entry point:
   uv run npi-registry-mcp-server
   ```

### Production Installation

Install from PyPI (once published):

```bash
uv pip install npi-registry-mcp-server
```

Or install from source:

```bash
uv pip install git+https://github.com/eliotk/npi-registry-mcp-server.git
```

## Usage

### Available Tools

#### `search_npi_registry`

Search the NPI registry with various criteria:

**Parameters:**

- `first_name` (optional): Provider's first name
- `last_name` (optional): Provider's last name
- `organization_name` (optional): Organization name
- `npi` (optional): Specific 10-digit NPI number
- `city` (optional): City name
- `state` (optional): State abbreviation (e.g., 'CA', 'NY')
- `postal_code` (optional): ZIP/postal code (supports wildcards)
- `specialty` (optional): Provider specialty or taxonomy
- `limit` (optional): Maximum results to return (1-200, default: 10)

**Examples:**

```python
# Search for a specific provider by name
search_npi_registry(first_name="John", last_name="Smith", state="CA")

# Look up a specific NPI
search_npi_registry(npi="1234567890")

# Find organizations in a city
search_npi_registry(organization_name="Hospital", city="Los Angeles", state="CA")

# Search by specialty
search_npi_registry(specialty="cardiology", state="NY", limit=20)

# Find providers in a specific ZIP code area
search_npi_registry(postal_code="902*", state="CA")
```

### Response Format

The search returns a structured response with:

```json
{
  "success": true,
  "count": 5,
  "results": [
    {
      "npi": "1234567890",
      "entity_type": "Individual",
      "is_organization": false,
      "status": "A",
      "enumeration_date": "2010-05-05",
      "last_updated": "2023-01-15",
      "name": {
        "first": "John",
        "last": "Smith",
        "credential": "MD"
      },
      "addresses": [...],
      "practice_locations": [...],
      "taxonomies": [...],
      "identifiers": [...]
    }
  ]
}
```

## Claude Desktop Configuration

To use this MCP server with Claude Desktop, add the following configuration to your Claude Desktop config file:

### macOS

Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows

Location: `%APPDATA%/Claude/claude_desktop_config.json`

### Configuration

```json
{
  "mcpServers": {
    "npi-registry": {
      "command": "uv", # may need full path to executable
      "args": [
        "--directory",
        "/path/to/npi-registry-mcp-server",
        "run",
        "npi-registry-mcp-server"
      ]
    }
  }
}
```

### Verification

1. Save the configuration file
2. Restart Claude Desktop completely
3. Look for the 🔧 icon in Claude Desktop to verify the server is connected
4. Try asking Claude: "Search for doctors named Smith in California"

## Development

### Project Structure

```
npi-registry-mcp-server/
├── src/
│   └── npi_registry_mcp/
│       ├── __init__.py
│       └── server.py
├── tests/
├── pyproject.toml
├── README.md
└── .gitignore
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
# Format code
uv run black src/ tests/

# Sort imports
uv run isort src/ tests/

# Lint
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

### Building the Package

```bash
uv build
```

## API Reference

This server uses the official NPI Registry API provided by CMS:

- **Base URL**: https://npiregistry.cms.hhs.gov/api/
- **Documentation**: https://npiregistry.cms.hhs.gov/registry/help-api
- **Rate Limits**: The API has reasonable rate limits for normal usage

### Data Sources

All data comes directly from the official NPI Registry maintained by:

- Centers for Medicare & Medicaid Services (CMS)
- U.S. Department of Health and Human Services

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `uv run pytest`
5. Format your code: `uv run black src/ tests/`
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Additional documentation available in the `/docs` directory
- **API Questions**: Refer to the official NPI Registry API documentation

## Changelog

### v0.1.0

- Initial release
- Basic NPI registry search functionality
- Support for individual and organization searches
- Location and specialty filtering
- Comprehensive provider data retrieval

---

For more information about the Model Context Protocol, visit: https://modelcontextprotocol.io/
