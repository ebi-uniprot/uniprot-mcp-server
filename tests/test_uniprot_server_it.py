import pytest
from uniprot.tools.server import (
    search_uniprot,
    orthology,
    paralogy,
    get_uniprot_entry,
    enzyme_dat
)

@pytest.mark.integration
def test_search_uniprot_integration():
    """Integration test for search_uniprot"""
    result = search_uniprot(
        function_query="kinase",
        organism_id=9606,  # Human
        size=1,
        gene_name=None,
        gene_exact=None,
        reviewed=True
    )
    assert result["status"] == "ok"
    body = result.get("body")
    assert body is not None
    assert "results" in body
    assert len(body["results"]) > 0
    first_result = body["results"][0]
    assert "comments" in first_result

@pytest.mark.integration
def test_get_uniprot_entry_integration():
    """Integration test for fetching a UniProt entry by accession"""
    result = get_uniprot_entry("P31749")  # AKT1 Human
    assert result["status"] == "ok"
    body = result.get("body")
    assert "results" in body
    assert len(body["results"]) > 0
    assert body["results"][0]["primaryAccession"] == "P31749"

@pytest.mark.integration
def test_orthology_integration():
    """Integration test for orthology query"""
    result = orthology("P31749")  # AKT1 Human
    # Orthology may not return results for every gene
    assert "status" in result
    assert result["status"] in ["ok", "error"]
    if result["status"] == "ok":
        body = result.get("body")
        assert "results" in body

@pytest.mark.integration
def test_paralogy_integration():
    """Integration test for paralogy query"""
    result = paralogy("P31749")  # AKT1 Human
    # Paralogy may not return results for every gene
    assert "status" in result
    assert result["status"] in ["ok", "error"]
    if result["status"] == "ok":
        body = result.get("body")
        assert "results" in body

@pytest.mark.integration
def test_enzyme_dat_resource():
    """Integration test for enzyme.dat resource"""
    enzyme_cache = enzyme_dat()
    assert isinstance(enzyme_cache, dict)
    # Check that at least one EC number exists
    assert any(enzyme_cache.values())
