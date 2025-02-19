import asyncio
from llmcompiler.src.docstore.r2r_rag import R2RDocstore, R2RExplorer

async def main():
    # Initialiser le docstore avec la collection par défaut
    docstore = R2RDocstore(collection_name="default")
    
    # Créer l'explorateur
    explorer = R2RExplorer(docstore)
    
    # Lister les documents
    print("=== Liste des documents dans la collection par défaut ===")
    docs = await explorer.list_documents()
    print(docs)
    print("\n===================")

if __name__ == "__main__":
    asyncio.run(main())
