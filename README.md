# UniProt MCP Server

A Python-based server that provides tools to interact with the UniProt database using the Model Context Protocol (MCP) architecture.

> **⚠️ DISCLAIMER: This project remains in a development and experimental phase. All features, APIs, and documentation may evolve and change without advance warning. ⚠️**

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tools](#tools)
- [Running MCP Server Using Docker](#running-mcp-server-using-docker)
- [Tech Stack](#tech-stack)
- [Local Development](#local-development-and-running-without-docker)
- [Architecture](#architecture)
- [External APIs](#external-apis)
- [Authors](#authors)
- [License](#license)

## Overview

This repository contains code to build a UniProt MCP server that allows users to:
- Search the UniProt database with various filtering criteria
- Find orthology information for UniProtKB entries
- Access enzyme data and descriptions

The server leverages the UniProt REST APIs and Alliance Genome API to provide comprehensive protein information in a structured format.


## Features

### 1. **UniProt Search**
Search the UniProt database with customizable filters like function, organism, gene name, and review status.

### 2. **Orthology Queries**
Find orthologous proteins across species by providing a UniProtKB accession.

### 3. **Fetch UniProt Entry by Accession(s)**
Retrieve detailed UniProt entries using one or more UniProtKB accessions.

### 4. **EC Number Replacement Prompt**
Replace EC numbers in protein search results with descriptions from an enzyme data file.

### 5. **Enzyme Data Access**
Access enzyme data from a local database, mapping EC numbers to enzyme descriptions and integrating them with protein search results.

---

## Tools

### `search_uniprot`
- **Description**: Search the UniProt database with optional filters (e.g., function, organism, gene name, etc.).
- **Parameters**:
  - `function_query`: Concise protein function (e.g., "kinase").
  - `organism_id`: Taxonomy ID (e.g., 9606 for human).
  - `size`: Number of results to return.
  - `gene_name`: Gene name for query (partial or exact match).
  - `gene_exact`: Exact match for gene name.
  - `reviewed`: Filter by review status (True/False/None).

---

### `orthology_query`
- **Description**: Retrieve orthologs for a given UniProtKB accession across different species using the Alliance Genome API.
- **Parameters**:
  - `accession`: UniProtKB accession for the protein.

---

### `fetch_uniprot_entry_by_accession`
- **Description**: Retrieve UniProt entries using one or more UniProtKB accessions.
- **Parameters**:
  - `accession`: One or more UniProtKB accessions (comma-separated).

---

### `summary`
- **Description**: Replace EC numbers with descriptions from an enzyme data file, displaying the results in a table format.
- **Input**: UniProt search fields and EC numbers.
- **Output**: Protein accession with EC number and corresponding description in a table.

---

### `enzyme_dat`
- **Description**: Provides enzyme descriptions from a local enzyme data file (e.g., `enzyme.dat`).
- **Output**: EC number mapped to enzyme description.

---

## Running MCP Server Using Docker

You can run the server using the official Docker image:

1. **Pull the latest Docker image from GitHub Container Registry:**
   ```bash
   docker pull ghcr.io/ebi-uniprot/uniprot-mcp-server:latest 
   ```

2. **Run the Docker container and expose port 8000 on the host machine:**
    ```bash
   docker run -p 8000:8000 ghcr.io/ebi-uniprot/uniprot-mcp-server:latest
   ```
---

3. **Configure LLM Client (Example: Claude Desktop)**

> **Warning**: This step will **not work with the free-tier Claude**.

   - Open **Claude Desktop** and go to the settings then Connectors
   - Click on Add custom connector
   - Enter name e.g. uniprot-mcp-server
   - Remote MCP server URL : `http://localhost:8000`

4. **Test the Connection**:
   - In your LLM client, test the connection to ensure that it can communicate with the MCP server at `http://localhost:8000`.
   - Once connected, you can start querying and interacting with the server using your LLM client.

   > **Note**: This example uses **Claude Desktop**, but you can configure any LLM client to interact with the server in the same way.

---

## Tech Stack

- **Python**: Core programming language
- **uv**: Package manager
- **FastMCP**: Framework for building Model Context Protocol servers
- **Pydantic**: Data validation and settings management
- **Requests**: HTTP library for API interactions
- **CSV**: Module for handling tabular data
---

## Local Development and Running (Without Docker)

### Set up
1. Clone the repository:
   ```bash
   git clone https://github.com/ebi-uniprot/uniprot-mcp-server.git
   cd uniprot-mcp-server
   ```

2. Install dependencies:
   ```bash
   uv pip install -r pyproject.toml
   ```

3. Run tests:
   ```bash
   pytest
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

### Starting the Server

Run the server using:

```bash
uv run -m src.uniprot.tools.server
```

### Starting the MCP Inspector for debugging

Run the MCP Inspector using:

```bash
npx @modelcontextprotocol/inspector
```
---

## Architecture

The project follows the Model Context Protocol (MCP) architecture.
---

## External APIs

- [UniProt REST API](https://rest.uniprot.org)
- [Alliance Genome API](https://www.alliancegenome.org/api)

---

## Authors

- **Vishal Joshi**
- **Shadab Ahmad**
- **Supun Wijerathne**

---
## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](https://github.com/ebi-uniprot/uniprot-mcp-server/blob/main/LICENSE) file for details.

---