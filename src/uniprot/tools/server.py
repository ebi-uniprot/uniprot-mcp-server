from typing import Annotated, Optional

from fastmcp import FastMCP
from pydantic import Field
import requests

"""
Author: Vishal Joshi
Date: 2025-06-25
This is main entry point for UniProt MCP server
"""
mcp = FastMCP("UniProt MCP Server")


@mcp.tool(
    name="search_uniprot",
    description="Search the UniProt database using the REST API with mandatory filtering criteria",
    tags={"search"}
)
def search_uniprot(function_query: Annotated[Optional[str], Field(description="concise function in the user query", examples=["kinase"])],
                   organism_id: Annotated[Optional[int],
                                Field(default=None,
                                      description="taxonomy id of organism/taxonomy to filter queries on",
                                      examples=[9606, 2])],
                   size: Annotated[Optional[int],
                                Field(default=10,
                                      description="number of protein entries to return",
                                      examples=[10, 12])]):

    base_url = 'https://rest.uniprot.org/uniprotkb/search'
    params = {}

    if organism_id is not None:
        params['organism_id'] = organism_id
    params['query'] = function_query
    params['size'] = size
    params['format'] = 'json'
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return {"status": "ok", "body": response.json()}
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    mcp.run()