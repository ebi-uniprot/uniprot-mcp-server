import requests
from unittest.mock import patch, Mock
import pytest

import src.uniprot.tools.server as uniprot_mcp_server


class TestSearchUniProt:
    def test_search_uniprot_no_criteria(self):
        result = uniprot_mcp_server.search_uniprot(
            function_query=None,
            organism_id=None,
            size=2,
            gene_name=None,
            gene_exact=None,
            reviewed=None,
        )
        assert result["status"] == "error"
        assert "At least one search criteria" in result["message"]

    @patch("src.uniprot.tools.server.requests.get")
    def test_search_uniprot_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": [{"accession": "P12345"}]}
        mock_get.return_value = mock_response

        result = uniprot_mcp_server.search_uniprot(
            function_query="kinase",
            organism_id=9606,
            size=1,
            gene_name=None,
            gene_exact=None,
            reviewed=True,
        )
        assert result["status"] == "ok"
        assert "body" in result
        assert result["body"]["results"][0]["accession"] == "P12345"
        mock_get.assert_called_once()

    @patch("src.uniprot.tools.server.requests.get")
    def test_search_uniprot_request_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("Network error")
        result = uniprot_mcp_server.search_uniprot(
            function_query="kinase",
            organism_id=None,
            size=2,
            gene_name=None,
            gene_exact=None,
            reviewed=None,
        )
        assert result["status"] == "error"
        assert "Network error" in result["message"]


class TestFetchAgrXref:
    def test_fetch_agr_xref_found(self):
        entry = {
            "uniProtKBCrossReferences": [
                {"database": "OTHER", "id": "X1"},
                {"database": "AGR", "id": "AGR:123"},
            ]
        }
        result = uniprot_mcp_server._uniprot_mcp_server__fetch_agr_xref(entry)
        assert result == "AGR:123"

    def test_fetch_agr_xref_not_found(self):
        entry = {"uniProtKBCrossReferences": []}
        result = uniprot_mcp_server._uniprot_mcp_server__fetch_agr_xref(entry)
        assert result is None


class TestGetUniProtEntry:
    def test_get_uniprot_entry_no_accession(self):
        result = uniprot_mcp_server.get_uniprot_entry(None)
        assert result["status"] == "error"

    @patch("src.uniprot.tools.server.requests.get")
    def test_get_uniprot_entry_success(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [{"accession": "P12345"}]}
        mock_get.return_value = mock_response

        result = uniprot_mcp_server.get_uniprot_entry("P12345")
        assert result["status"] == "ok"
        assert "body" in result
        mock_get.assert_called_once()

    @patch("src.uniprot.tools.server.requests.get")
    def test_get_uniprot_entry_request_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("Network error")
        result = uniprot_mcp_server.get_uniprot_entry("P12345")
        assert result["status"] == "error"
        assert "Network error" in result["message"]


class TestOrthology:
    @patch("src.uniprot.tools.server.requests.get")
    def test_orthology_entry_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = uniprot_mcp_server.orthology("P12345")
        assert result["status"] == "error"
        assert "Unable to fetch entry" in result["message"]

    @patch("src.uniprot.tools.server.requests.get")
    def test_orthology_happy_path(self, mock_get):
        # 1. Mock UniProt entry response
        mock_uniprot = Mock()
        mock_uniprot.status_code = 200
        mock_uniprot.json.return_value = {
            "uniProtKBCrossReferences": [{"database": "AGR", "id": "AGR:001"}]
        }

        # 2. Mock Alliance orthologs response
        mock_alliance = Mock()
        mock_alliance.status_code = 200
        mock_alliance.json.return_value = {
            "results": [
                {"geneToGeneOrthologyGenerated": {"objectGene": {"geneSymbol": {"displayText": "GENE1"}, "taxon": {"curie": "NCBITaxon:9606"}}}},
                {"geneToGeneOrthologyGenerated": {"objectGene": {"geneSymbol": {"displayText": "GENE2"}, "taxon": {"curie": "NCBITaxon:10090"}}}}
            ]
        }

        # 3. Mock UniProt search for generated query
        mock_search = Mock()
        mock_search.status_code = 200
        mock_search.json.return_value = {"results": [{"accession": "P12345"}]}

        # Sequence of requests.get calls: UniProt -> Alliance -> UniProt search
        mock_get.side_effect = [mock_uniprot, mock_alliance, mock_search]

        result = uniprot_mcp_server.orthology("P12345")

        assert result["status"] == "ok"
        assert "body" in result
        assert result["body"]["results"][0]["accession"] == "P12345"


class TestParalogy:
    @patch("src.uniprot.tools.server.requests.get")
    def test_paralogy_entry_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = uniprot_mcp_server.paralogy("P12345")
        assert result["status"] == "error"
        assert "Unable to fetch entry" in result["message"]

    @patch("src.uniprot.tools.server.requests.get")
    def test_paralogy_happy_path(self, mock_get):
        # 1. Mock UniProt entry response
        mock_uniprot = Mock()
        mock_uniprot.status_code = 200
        mock_uniprot.json.return_value = {
            "uniProtKBCrossReferences": [{"database": "AGR", "id": "AGR:002"}]
        }

        # 2. Mock Alliance paralogs response
        mock_alliance = Mock()
        mock_alliance.status_code = 200
        mock_alliance.json.return_value = {
            "results": [
                {"geneToGeneParalogy": {"objectGene": {"geneSymbol": {"displayText": "GENE3"}, "taxon": {"curie": "NCBITaxon:9606"}}}},
                {"geneToGeneParalogy": {"objectGene": {"geneSymbol": {"displayText": "GENE4"}, "taxon": {"curie": "NCBITaxon:10090"}}}}
            ]
        }

        # 3. Mock UniProt search for generated query
        mock_search = Mock()
        mock_search.status_code = 200
        mock_search.json.return_value = {"results": [{"accession": "P67890"}]}

        # Sequence of requests.get calls: UniProt -> Alliance -> UniProt search
        mock_get.side_effect = [mock_uniprot, mock_alliance, mock_search]

        result = uniprot_mcp_server.paralogy("P12345")

        assert result["status"] == "ok"
        assert "body" in result
        assert result["body"]["results"][0]["accession"] == "P67890"
