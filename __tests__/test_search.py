import asyncio
import logging
from llmcompiler.src.docstore.r2r_rag import R2RDocstore, R2RExplorer

# Désactiver TOUS les logs
logging.getLogger().setLevel(logging.CRITICAL)

async def main():
    # Initialiser le docstore et l'explorer
    docstore = R2RDocstore()
    explorer = R2RExplorer(docstore)
    
    # Lister les documents
    print("\n=== Documents disponibles ===")
    docs = await explorer.list_documents()
    if isinstance(docs, str):
        print(docs.strip())
    print("===================\n")
    
    # Faire une recherche RAG comme dans la doc
    query = "Expliquez-moi ce qu'est le béton désactivé et le ragréage en termes simples."
    raw_results = explorer.docstore.client.retrieval.rag(
        query=query,
        search_settings={
            "use_semantic_search": True,
            "limit": 10,
            "chunk_settings": {
                "limit": 20
            }
        },
        rag_generation_config={
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 150
        }
    )
    
    # Afficher les résultats
    print("\n=== Réponse RAG ===")
    if hasattr(raw_results, 'results') and hasattr(raw_results.results, 'generated_answer'):
        print(raw_results.results.generated_answer)
    else:
        print("Pas de résultats")
    print("===================\n")

if __name__ == "__main__":
    asyncio.run(main())
