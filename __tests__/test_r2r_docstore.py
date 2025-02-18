"""Tests for R2R docstore."""
import pytest
from r2r import R2RClient
from shared.api.models.base import R2RResults

def test_r2r_client_init():
    """Test that we can initialize the R2R client."""
    client = R2RClient()
    client.set_api_key("pk_5KuMwg5EcJv6ZPG8.sk_fsvwgKXy5esF7EVtu99PdoeEbAvNVoLw")
    assert client is not None

def test_r2r_default_collection():
    """Test that we can access the default collection."""
    client = R2RClient()
    client.set_api_key("pk_5KuMwg5EcJv6ZPG8.sk_fsvwgKXy5esF7EVtu99PdoeEbAvNVoLw")
    # Essayons de faire une recherche simple dans la collection par défaut
    results = client.retrieval.search("test")
    assert results is not None
    # Vérifions que c'est bien un R2RResults
    assert isinstance(results, R2RResults)
