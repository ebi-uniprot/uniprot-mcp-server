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

#### Note — Always activate the virtual environment before running the server (and the inspector, if needed). See the instructions above on how to activate the virtual environment.

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

### Using Docker

You can also run the server using Docker:

```bash
docker pull registry.gitlab.com/[your-group]/uniprot-mcp-server:latest
docker run -p 8000:8000 registry.gitlab.com/[your-group]/uniprot-mcp-server:latest
```

Replace `[your-group]` with your GitLab group path.

## CI/CD Pipeline

This repository includes a GitLab CI/CD pipeline that automatically builds, pushes Docker images, and can trigger Kubernetes deployments.

### Pipeline Behavior

The pipeline consists of two stages: `build` and `deploy`.

#### Build Stage (`docker-build`)

- Builds a Docker image and pushes it to the GitLab registry.
- Runs automatically on the `main` branch or can be triggered manually on any branch.
- Creates two Docker image tags:
    - `latest` – always points to the most recent successful build
    - `[commit-sha]` – unique tag based on the commit SHA for versioning and rollback

#### Deploy Stage (`k8s-deploy`)

- Triggers a Kubernetes deployment(uniprot/deployment/unp.ci.api.k8s) in the `dev` environment using the `latest` Docker image.
- Runs automatically after a successful build on the `main` branch or can be triggered manually on any branch.
- Uses variables like `CI_PIPELINE_TASKS`, `MCP_TAG`, `DC`, `K8S_ENV`, and `ARTIFACT` for deployment configuration.

### Manually Triggering a Build

To manually trigger a build:

1. Go to your GitLab repository
2. Navigate to CI/CD > Pipelines
3. Click "Run pipeline"
4. Select the branch you want to build
5. Click "Run pipeline"

## Architecture

The project follows the Model Context Protocol (MCP) architecture.

## External APIs

- [UniProt REST API](https://rest.uniprot.org)
- [Alliance Genome API](https://www.alliancegenome.org/api)

## Authors

- **Vishal Joshi**
- **Shadab Ahmad**
## Created
- June 2025

## License

[Specify your license here]
