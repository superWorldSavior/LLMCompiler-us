"""Wrapper around R2R Cloud API."""
import os
import time
from typing import List, Optional, Dict, Any, Union
from langchain_community.docstore.base import Docstore
from langchain_community.docstore.document import Document
from r2r import R2RClient
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class R2RDocstore(Docstore):
    """Wrapper around R2R Cloud API."""

    def __init__(
        self,
        collection_name: str = "default",
        benchmark: bool = False,
        char_limit: Optional[int] = None
    ) -> None:
        """Initialize R2R Cloud docstore.
        
        Args:
            collection_name: Name of the collection to use, defaults to "default"
            benchmark: Whether to collect performance metrics
            char_limit: Maximum number of characters to return per document
        """
        self.collection_name = collection_name
        self.char_limit = char_limit
        self.benchmark = benchmark
        self.all_times = []
        
        # Initialize R2R client
        try:
            self.client = R2RClient()
            # Configure API key from environment variable
            api_key = os.getenv("R2R_API_KEY")
            if not api_key:
                raise ValueError("R2R_API_KEY environment variable is not set")
            self.client.set_api_key(api_key)
            logger.info(f"Initialized R2R client with collection: {collection_name}")
        except Exception as e:
            raise ValueError(f"Failed to initialize R2R client: {str(e)}")

    def reset(self) -> None:
        """Reset performance metrics."""
        self.all_times = []

    def get_stats(self) -> Dict[str, List[float]]:
        """Get performance statistics."""
        return {
            "all_times": self.all_times,
        }

    async def asearch(
        self, 
        query: str, 
        top_k: int = 5,
        return_raw: bool = False
    ) -> Union[str, List[Document]]:
        """Search documents in R2R Cloud.
        
        Args:
            query: Search query
            top_k: Number of results to return
            return_raw: If True, return raw Document objects instead of formatted string
            
        Returns:
            Either formatted string of results or list of Document objects
        """
        start_time = time.time()
        try:
            # Perform semantic search
            results = await self.client.search(
                query=query,
                top_k=top_k,
                collection=self.collection_name
            )
            
            if not results:
                return [] if return_raw else f"Aucun résultat trouvé pour '{query}'."
            
            # Convert to Documents
            documents = []
            for result in results:
                doc = Document(
                    page_content=result.text,
                    metadata={
                        "score": result.score,
                        "collection": self.collection_name
                    }
                )
                documents.append(doc)
            
            if return_raw:
                return documents
            
            # Format results for display
            formatted_results = []
            for doc in documents:
                content = doc.page_content
                if self.char_limit:
                    content = content[:self.char_limit] + ("..." if len(content) > self.char_limit else "")
                metadata = f"(Score: {doc.metadata['score']:.2f})"
                formatted_results.append(f"{content}\n{metadata}")
            
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            error_msg = f"Erreur lors de la recherche R2R : {str(e)}"
            logger.error(error_msg)
            return [] if return_raw else error_msg
        finally:
            if self.benchmark:
                self.all_times.append(time.time() - start_time)

    def search(self, search_term: str) -> List[Document]:
        """Search for documents (required by Docstore interface).
        
        Args:
            search_term: Search query
            
        Returns:
            List of matching documents
        """
        try:
            results = self.client.retrieval.search(
                query=search_term,
                collection=self.collection_name
            )
            
            documents = []
            for result in results.chunk_search_results:
                doc = Document(
                    page_content=result.text,
                    metadata={
                        "score": result.score,
                        "collection": self.collection_name
                    }
                )
                documents.append(doc)
            
            return documents
        except Exception as e:
            logger.error(f"Error in sync search: {str(e)}")
            return []

    async def add_documents(self, documents: List[Dict[str, str]]) -> None:
        """Add documents to R2R Cloud.
        
        Args:
            documents: List of documents to add
                Each document should have:
                - text: str
                - metadata: Dict[str, str] (optional)
        """
        start_time = time.time()
        try:
            # Add documents to collection
            await self.client.add_documents(documents, collection=self.collection_name)
            logger.info(f"Added {len(documents)} documents to collection {self.collection_name}")
        except Exception as e:
            logger.error(f"Error adding documents to R2R: {str(e)}")
            raise
        finally:
            if self.benchmark:
                self.all_times.append(time.time() - start_time)


class R2RExplorer:
    """Helper class for exploring R2R Cloud documents."""

    def __init__(
        self, 
        docstore: R2RDocstore,
        char_limit: Optional[int] = None
    ) -> None:
        """Initialize with a docstore.
        
        Args:
            docstore: R2R docstore instance
            char_limit: Maximum characters to display per document
        """
        self.docstore = docstore
        self.documents: List[Document] = []
        self.char_limit = char_limit
        self.last_query = ""

    async def search(self, query: str, top_k: int = 5) -> str:
        """Search for documents and format results using RAG.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            Generated response based on search results
        """
        try:
            # Faire une recherche RAG selon la doc
            results = self.docstore.client.retrieval.rag(
                query=query,
                search_settings={
                    "use_semantic_search": True,
                    "limit": top_k,
                    "chunk_settings": {
                        "limit": top_k * 2  # Plus de chunks pour plus de contexte
                    }
                },
                rag_generation_config={
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 150
                }
            )
            
            # Extraire la réponse générée
            if hasattr(results, 'results') and hasattr(results.results, 'generated_answer'):
                return results.results.generated_answer
            
            return f"Aucun résultat trouvé pour '{query}'."
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche R2R : {str(e)}")
            return f"Erreur lors de la recherche R2R : {str(e)}"

    def _format_results(self) -> str:
        """Format search results into a string.
        
        Returns:
            Formatted string with search results
        """
        formatted_results = []
        for i, doc in enumerate(self.documents, 1):
            result_parts = []
            
            # Extraire le contenu selon la structure disponible
            content = None
            if hasattr(doc, 'content'):
                content = doc.content
            elif hasattr(doc, 'text'):
                content = doc.text
            elif isinstance(doc, str):
                content = doc
            elif isinstance(doc, dict) and 'content' in doc:
                content = doc['content']
            elif isinstance(doc, dict) and 'text' in doc:
                content = doc['text']
            
            if content:
                # Limiter la longueur si nécessaire
                if self.char_limit and len(content) > self.char_limit:
                    content = content[:self.char_limit] + "..."
                result_parts.append(f"{i}. {content}")
            
            # Ajouter le score s'il est disponible
            score = None
            if hasattr(doc, 'score'):
                score = doc.score
            elif isinstance(doc, dict) and 'score' in doc:
                score = doc['score']
            
            if score is not None:
                result_parts.append(f"Score: {score:.3f}")
            
            formatted_results.append("\n".join(result_parts))
        
        if not formatted_results:
            return f"Aucun résultat trouvé pour '{self.last_query}'."
        
        return "\n\n".join(formatted_results)

    async def list_documents(self) -> str:
        """Liste tous les documents disponibles dans la collection par défaut.
        
        Returns:
            Chaîne formatée avec la liste des documents
        """
        try:
            # Obtenir la liste des documents de la collection par défaut
            docs = self.docstore.client.collections.list_documents("8283f90a-ba4f-54bc-8b4f-3cea2fa300d1")
            
            if not hasattr(docs, 'results') or not docs.results:
                return "Aucun document trouvé dans la collection par défaut."
            
            # Formater les résultats
            formatted_docs = []
            for doc in docs.results:
                doc_info = [
                    f"Document:",
                    f"- Titre: {doc.title}",
                    f"- ID: {doc.id}"
                ]
                formatted_docs.append("\n".join(doc_info))
            
            return "\n\n".join(formatted_docs)
        except Exception as e:
            return f"Erreur lors de la récupération des documents R2R : {str(e)}"
