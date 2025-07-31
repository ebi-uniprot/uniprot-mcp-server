import csv
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

uniprot_search_url = 'https://rest.uniprot.org/uniprotkb/search'


@mcp.tool(
    name="search_uniprot",
    description="Search the UniProt database using the REST API with mandatory filtering criteria",
    tags={"search"}
)
def search_uniprot(function_query: Annotated[Optional[str], Field(description="concise function in the user query",
                                                                  examples=["kinase"])],
                   organism_id: Annotated[Optional[int],
                                Field(default=None,
                                      description="taxonomy id of organism/taxonomy to filter queries on",
                                      examples=[9606, 2])],
                   size: Annotated[Optional[int],
                                Field(default=2,
                                      description="number of protein entries to return",
                                      examples=[2, 4])],
                   gene_name: Annotated[Optional[str],
                                   Field(default=None,
                                         description="gene name of the entries to query",
                                         examples=["app", "YDJ1"])],
                   gene_exact: Annotated[Optional[str],
                                   Field(default=None,
                                         description="exact gene name of the entries to query and not allowing any"
                                                     " variations e.g Lists all entries for proteins encoded by gene"
                                                     " HPSE, but excluding variations like HPSE2 or HPSE_0.",
                                         examples=["app", "YDJ1"])],
                   reviewed: Annotated[Optional[bool],
                                   Field(default=None,
                                         description="if set to True, it will return UniProtKB/SwissProt; "
                                                     "if set to False, it will return UniProtKB/TrEMBL which are"
                                                     " unreviewed set of proteins; "
                                                     "if set to None which is its default value, it will return all"
                                                     " UniProtKB entries")]
                   ):

    params = {'query': function_query}

    if organism_id is not None:
        params['query'] = f"{function_query} AND organism_id={organism_id}"

    if gene_name is not None:
        exiting_query = params['query']
        params['query'] = f"{exiting_query} AND gene={gene_name}"

    if gene_exact is not None:
        exiting_query = params['query']
        params['query'] = f"{exiting_query} AND gene_exact={gene_exact}"

    if reviewed is not None:
        exiting_query = params['query']
        params['query'] = f"{exiting_query} AND reviewed={reviewed}"

    params['size'] = size or 2
    params['format'] = 'json'
    params['fields'] = 'accession,ec,organism_name,gene_names,protein_name,cc_function,cc_catalytic_activity'
    try:
        response = requests.get(uniprot_search_url, params=params)
        response.raise_for_status()
        return {"status": "ok", "body": response.json()}
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}


@mcp.tool(
    name="orthology_query",
    description="find orthology of the given uniprotkb accession",
    tags={"orthologs"}
)
def orthology(accession: Annotated[Optional[str],
                                   Field(default=None, description="UniProt kb accession which uniquely identifies"
                                                                   " a uniprotKB record")]):
    url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    response = requests.get(url)

    if response.status_code == 200:
        entry = response.json()
        agr_xref = None
        for xref in entry['uniProtKBCrossReferences']:
            if xref['database'] == 'AGR':
                agr_xref = xref['id']
                break

        if agr_xref is not None:
            limit = 10
            stringency_level = "stringent"  # could be strict, moderate, no filter
            alliance_url = f"https://www.alliancegenome.org/api/gene/{agr_xref}/orthologs"
            params = {
                "filter.stringency": stringency_level,
                "limit": limit
            }
            try:
                alliance_response = requests.get(alliance_url, params)
                alliance_response.raise_for_status()
                if alliance_response.status_code == 200:
                    alliance_response_json = alliance_response.json()
                    gene_taxa = []
                    for item in alliance_response_json.get("results", []):
                        object_gene = item["geneToGeneOrthologyGenerated"]["objectGene"]
                        gene_name = object_gene["geneSymbol"]["displayText"]
                        taxon_id = object_gene["taxon"]["curie"].split(":")[1]
                        gene_taxa.append((gene_name, taxon_id))

                    query_parts = [f"(gene:{gene} AND taxonomy_id:{tax_id})" for gene, tax_id in gene_taxa]
                    uniprot_query = " OR ".join(query_parts)
                    search_params = {
                        "query": uniprot_query,
                        "format": "json",
                        "fields": "accession,ec,organism_name,gene_names,protein_name,cc_function,cc_catalytic_activity"
                    }
                    try:
                        search_response = requests.get(uniprot_search_url, search_params)
                        if search_response.status_code == 200:
                            search_response.raise_for_status()
                            return {"status": "ok", "body": search_response.json()}
                        else:
                            search_error_message = (f"Error {search_response.status_code}: Unable to search for"
                                                    f" query:{query_parts}")
                            print(search_error_message)
                            return {"status": "error", "message": search_error_message}
                    except requests.RequestException as e:
                        return {"status": "error", "message": str(e)}
                else:
                    alliance_error_message = f"Error {response.status_code}: Unable to fetch orthologs for {accession}"
                    print(alliance_error_message)
                    return {"status": "error", "message": alliance_error_message}
            except requests.RequestException as e:
                return {"status": "error", "message": str(e)}
        else:
            agr_error_message = f"no AGR xref found for {accession}"
            print(agr_error_message)
            return {"status": "error", "message": agr_error_message}
    else:
        error_message = f"Error {response.status_code}: Unable to fetch entry for {accession}"
        print(error_message)
        return {"status": "error", "message": error_message}


@mcp.resource(uri="resource://enzymedat",
              name="Enzyme dat file reader",     # Custom name
              description="Provides the current enzyme dat file.", # Custom description
              mime_type="application/json" # Explicit MIME type
              )
def enzyme_dat():
    path="/Users/vjoshi/Documents/sample_enzyme.dat"
    with open(path, newline='', encoding='utf‑8') as f:
        reader = csv.reader(f, delimiter='\t')
        # build dict; later duplicates overwrite earlier ones
        return {key: value for key, value in reader}


@mcp.prompt
def summary() -> str:
    return (f"You will search uniprot with provided fields and then replace ec numbers with description provided in enzyme dat."
            f"if the EC number is not found in the file, say 'Information not available'"
            f"Finally, the output should be Protein accession: accession -----> ec: ec description all in a table format")


if __name__ == "__main__":
    mcp.run()