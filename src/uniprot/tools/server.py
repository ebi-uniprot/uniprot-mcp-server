import csv
from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field
import requests
import importlib.resources

"""
Author: Vishal Joshi
Date: 2025-06-25
This is main entry point for UniProt MCP server
"""
mcp = FastMCP("UniProt MCP Server")

uniprot_search_url = 'https://rest.uniprot.org/uniprotkb/search'


@mcp.tool(
    name="search_uniprot",
    description="Search the UniProt database using the REST API with optional filtering criteria. Can search by function, gene, organism, or any combination."
)
def search_uniprot(function_query: Annotated[Optional[str], 
                   Field(default=None,
                         description="concise function in the user query", 
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
    # Build query parts dynamically
    query_parts = []
    
    if function_query:
        query_parts.append(function_query)
    
    if organism_id:
        query_parts.append(f"organism_id={organism_id}")
    
    if gene_name:
        query_parts.append(f"gene={gene_name}")
    
    if gene_exact:
        query_parts.append(f"gene_exact={gene_exact}")
    
    if reviewed is not None: # False is valid value for reviewed
        query_parts.append(f"reviewed={reviewed}")
    
    # If no query parts are provided, return an error
    if not query_parts:
        return {"status": "error", "message": "At least one search criteria must be provided (function_query, gene_name, gene_exact, organism_id, or reviewed)"}
    
    # Join query parts with AND
    params = {'query': ' AND '.join(query_parts)}
    params['size'] = size or 2
    params['format'] = 'json'
    params['fields'] = 'accession,ec,organism_name,gene_names,protein_name,cc_function,cc_catalytic_activity'
    
    try:
        response = requests.get(uniprot_search_url, params=params)
        response.raise_for_status()
        return {"status": "ok", "body": response.json()}
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}


def __fetch_agr_xref(entry):
    agr_xref = None
    for xref in entry['uniProtKBCrossReferences']:
        if xref['database'] == 'AGR':
            agr_xref = xref['id']
            break
    return agr_xref


@mcp.tool(
    name="orthology_query",
    description="find orthologs of the given uniprotkb accession"
)
def orthology(accession: Annotated[Optional[str],
Field(default=None, description="UniProt kb accession which uniquely identifies"
                                " a uniprotKB record")]):
    url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    response = requests.get(url)

    if response.status_code == 200:
        entry = response.json()
        agr_xref = __fetch_agr_xref(entry)

        if agr_xref is not None:
            alliance_url = f"https://www.alliancegenome.org/api/gene/{agr_xref}/orthologs"
            params = {
                "filter.stringency": "all",
                "limit": 10
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


@mcp.tool(
    name="paralogy_query",
    description="find paralogs of the given uniprotkb accession"
)
def paralogy(accession: Annotated[Optional[str],
                    Field(default=None, description="UniProt kb accession which uniquely identifies"
                                " a uniprotKB record")]):
    url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    response = requests.get(url)

    if response.status_code == 200:
        entry = response.json()
        agr_xref = __fetch_agr_xref(entry)

        if agr_xref is not None:
            alliance_url = f"https://www.alliancegenome.org/api/gene/{agr_xref}/paralogs"
            params = {
                "filter.stringency": "all",
                "limit": 10
            }
            try:
                alliance_response = requests.get(alliance_url, params)
                alliance_response.raise_for_status()
                if alliance_response.status_code == 200:
                    alliance_response_json = alliance_response.json()
                    gene_taxa = []
                    for item in alliance_response_json.get("results", []):
                        object_gene = item["geneToGeneParalogy"]["objectGene"]
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
                            return {"status": "ok", "body": search_response.json()}
                        else:
                            search_error_message = (f"Error {search_response.status_code}: Unable to search for"
                                                    f" query:{query_parts}")
                            print(search_error_message)
                            return {"status": "error", "message": search_error_message}
                    except requests.RequestException as e:
                        return {"status": "error", "message": str(e)}
                else:
                    alliance_error_message = f"Error {response.status_code}: Unable to fetch paralogs for {accession}"
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


@mcp.prompt()
def summary() -> str:
    return (f"You will search uniprot with provided fields and then replace ec numbers with description"
            f" provided in enzyme dat."
            f"if the EC number is not found in the file, say 'Information not available'"
            f"Finally, the output should be Protein accession: "
            f"accession -----> ec: ec description all in a table format")


@mcp.tool(
    name="fetch_uniprot_entry_by_accession",
    description="this will retrieve uniprot entry by accession, it will not being used for search"
                " based on other parameters"
)
def get_uniprot_entry(accession: Annotated[Optional[str],
                    Field(default=None,
                          description="UniProt kb accession(s) which uniquely identifies a uniprotKB record. "
                                    "Can be a single accession or multiple accessions separated by commas")]):
    if not accession:
        return {"status": "error", "message": "No accession provided"}
    
    # Clean and validate accessions
    accessions = [acc.strip() for acc in accession.split(',') if acc.strip()]
    
    if not accessions:
        return {"status": "error", "message": "No valid accessions provided"}
    
    # Use accessions endpoint which supports comma-separated accessions
    url = "https://rest.uniprot.org/uniprotkb/accessions"
    params = {
        "accessions": ",".join(accessions)
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            return {"status": "ok", "body": data}
        else:
            error_message = f"Error {response.status_code}: Unable to fetch entries"
            print(error_message)
            return {"status": "error", "message": error_message}
            
    except requests.RequestException as e:
        error_message = f"Request failed: {str(e)}"
        print(error_message)
        return {"status": "error", "message": error_message}


@mcp.resource(uri="resource://enzymedat",
              name="Enzyme dat file reader",  # Custom name
              description="Provides the current enzyme dat file.",  # Custom description
              mime_type="application/json"  # Explicit MIME type
              )
def enzyme_dat():
    enzyme_cache = {}
    with importlib.resources.files("uniprot.resources").joinpath("enzyme.dat").open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("ID"):
                key = line[5:].strip()
            elif line.startswith("DE"):
                value = line[5:]. strip()
                enzyme_cache[key] = value
    return enzyme_cache


if __name__ == "__main__":
    mcp.run()
