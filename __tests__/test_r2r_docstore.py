"""Tests for R2R docstore."""
import pytest
from r2r import R2RClient
from llmcompiler.src.docstore.r2r_rag import R2RDocstore, R2RExplorer

def test_integration_r2r_client_init():
    """Test d'intégration : Test that we can initialize the R2R client."""
    client = R2RClient()
    client.set_api_key("pk_5KuMwg5EcJv6ZPG8.sk_fsvwgKXy5esF7EVtu99PdoeEbAvNVoLw")
    assert client is not None

def test_integration_r2r_default_collection():
    """Test d'intégration : Test that we can access the default collection."""
    client = R2RClient()
    client.set_api_key("pk_5KuMwg5EcJv6ZPG8.sk_fsvwgKXy5esF7EVtu99PdoeEbAvNVoLw")
    # Essayons de faire une recherche simple dans la collection par défaut
    results = client.retrieval.search("test")
    assert results is not None
    # Vérifions que c'est un objet valide
    assert hasattr(results, 'results') or hasattr(results, 'data')

def test_integration_r2r_search_structure():
    """Test d'intégration : Test pour explorer la structure des résultats de recherche."""
    client = R2RClient()
    client.set_api_key("pk_5KuMwg5EcJv6ZPG8.sk_fsvwgKXy5esF7EVtu99PdoeEbAvNVoLw")
    
    # Faire une recherche avec des paramètres explicites
    results = client.retrieval.search(
        query="test",
        search_mode="basic",
        search_settings={"limit": 5}
    )
    
    # Afficher la structure complète des résultats
    print("\nType of results:", type(results))
    print("\nDir of results:", dir(results))
    
    # Explorer les attributs
    if hasattr(results, 'results'):
        print("\nResults attribute:", results.results)
    if hasattr(results, 'data'):
        print("\nData attribute:", results.data)
    if hasattr(results, 'items'):
        print("\nItems attribute:", results.items)
    
    # Vérifier si c'est itérable
    try:
        for item in results:
            print("\nItem in results:", item)
            print("Item type:", type(item))
            print("Item attributes:", dir(item))
    except:
        print("\nResults is not iterable")

@pytest.mark.asyncio
async def test_integration_r2r_explorer_list_documents():
    """Test d'intégration : vérifier que nous pouvons lister les documents R2R."""
    # Initialiser le docstore et l'explorer
    docstore = R2RDocstore()
    explorer = R2RExplorer(docstore)
    
    # Lister les documents
    results = await explorer.list_documents()
    
    # Afficher les résultats
    print("\n=== Documents R2R ===")
    print(results)
    print("===================\n")
    
    # Vérifier que nous avons des résultats
    assert results is not None
    assert isinstance(results, str)
    
    # Vérifier que ce n'est pas un message d'erreur
    assert not results.startswith("Erreur")
    assert "Aucun document trouvé" not in results

@pytest.mark.asyncio
async def test_integration_r2r_explorer_list_documents_error():
    """Test d'intégration : vérifier la gestion d'erreur avec une clé API invalide."""
    # Créer un docstore sans clé API pour forcer une erreur
    docstore = R2RDocstore()
    docstore.client.set_api_key("invalid_key")
    explorer = R2RExplorer(docstore)
    
    # Lister les documents devrait retourner un message d'erreur
    results = await explorer.list_documents()
    assert "Erreur lors de la récupération" in results

@pytest.mark.asyncio
async def test_integration_r2r_semantic_search():
    """Test d'intégration : vérifier que la recherche sémantique fonctionne."""
    # Initialiser le docstore et l'explorer
    docstore = R2RDocstore()
    explorer = R2RExplorer(docstore)
    
    # Faire une recherche sémantique
    query = "maçonnerie"
    results = await explorer.search(query, top_k=1)  # Un seul résultat
    
    # Afficher les résultats
    print("\n=== Résultats de la recherche sémantique ===")
    print(f"Query: {query}")
    print(results)
    print("===================\n")
    
    # Vérifier que nous avons une réponse
    assert results is not None
    assert isinstance(results, str)
    assert len(results) > 0
    assert "Erreur" not in results

@pytest.mark.asyncio
async def test_integration_r2r_semantic_search_no_results():
    """Test d'intégration : vérifier la recherche sémantique avec une requête invalide."""
    # Initialiser le docstore et l'explorer
    docstore = R2RDocstore()
    explorer = R2RExplorer(docstore)
    
    # Faire une recherche qui ne devrait rien trouver
    query = "xyzabc123"
    results = await explorer.search(query, top_k=2)
    
    # Vérifier que nous avons une réponse
    assert results is not None
    assert isinstance(results, str)
    assert len(results) > 0
