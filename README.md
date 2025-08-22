# UniProt MCP Server

A Python-based server that provides tools to interact with the UniProt database using the Model Context Protocol (MCP) architecture.

## Overview

This repository contains code to build a UniProt MCP (Model Context Protocol) server that allows users to:
- Search the UniProt database with various filtering criteria
- Find orthology information for UniProtKB entries
- Access enzyme data and descriptions

The server leverages the UniProt REST API and Alliance Genome API to provide comprehensive protein information in a structured format.

## Tech Stack

- **Python**: Core programming language
- **FastMCP**: Framework for building Model Context Protocol servers
- **Pydantic**: Data validation and settings management
- **Requests**: HTTP library for API interactions
- **CSV**: Module for handling tabular data

## Features

### 1. UniProt Search

Search the UniProt database with various filtering options:
- Function query
- Organism/taxonomy ID
- Gene name (exact or partial matching)
- Review status (SwissProt/TrEMBL)
- Customizable result size

### 2. Orthology Queries

Find orthologous proteins across different species:
- Input a UniProtKB accession
- Retrieve orthology information via Alliance Genome API
- Get corresponding UniProt entries for orthologous genes

### 3. Enzyme Data Access

Access enzyme data from a local database:
- Map EC numbers to enzyme descriptions
- Integrate enzyme information with protein search results

## Installation

1. Clone the repository:
   ```bash
   git clone https://gitlab.ebi.ac.uk/uniprot/aa/llm/uniprot-mcp-server.git
   cd uniprot-mcp-server
   ```
   
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install fastmcp pydantic requests
   ```
4. **Update your Claude configuration file** (e.g. `claude.config.json`) to include the following MCP server entry:

```json
{
  "mcpServers": {
    "uniprot-mcp": {
      "command": "<path-to-project>/venv/bin/python",
      "args": [
        "<path-to-project>/src/uniprot/tools/server.py"
      ],
      "env": {
        "PYTHONPATH": "<path-to-project>/src"
      }
    }
  }
}
```


5. Configure the enzyme data file path in `src/uniprot/tools/server.py` if needed.

## Usage

### Starting the Server

Run the server using:

```bash
python -m src.uniprot.tools.server
```

### Starting the MCP Inspector

Run the MCP Inspector using:

```bash
npx @modelcontextprotocol/inspector
```

## Architecture

The project follows the Model Context Protocol (MCP) architecture.

## External APIs

- [UniProt REST API](https://rest.uniprot.org)
- [Alliance Genome API](https://www.alliancegenome.org/api)

## Author

- **Vishal Joshi**
- Created: June 2025

## License

[Specify your license here]