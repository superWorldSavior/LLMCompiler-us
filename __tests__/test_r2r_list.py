import asyncio
from r2r import R2RClient

async def main():
    # Initialiser le client R2R directement
    client = R2RClient()
    client.set_api_key("pk_5KuMwg5EcJv6ZPG8.sk_fsvwgKXy5esF7EVtu99PdoeEbAvNVoLw")
    
    # ID de la collection Default
    default_collection_id = "8283f90a-ba4f-54bc-8b4f-3cea2fa300d1"
    
    print(f"Listing documents de la collection Default...")
    
    try:
        # Lister les documents de la collection Default
        docs = client.collections.list_documents(default_collection_id)
        print("\n=== Documents de la collection Default ===")
        if hasattr(docs, 'results'):
            for doc in docs.results:
                print(f"\nDocument:")
                print(f"- ID: {doc.id if hasattr(doc, 'id') else 'No ID'}")
                # Afficher tous les attributs disponibles pour debug
                for attr in dir(doc):
                    if not attr.startswith('_'):  # Ignorer les attributs privés
                        try:
                            value = getattr(doc, attr)
                            print(f"- {attr}: {value}")
                        except:
                            pass
    except Exception as e:
        print(f"Erreur lors de la récupération des documents : {e}")
    
    print("\n===================")

if __name__ == "__main__":
    asyncio.run(main())
