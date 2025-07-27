import time
from typing import List, Tuple, Iterator, Optional
from uuid import uuid4
from contextlib import contextmanager

from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from src.config import settings
from src.utils.logger import logger
from src.utils.exceptions import URLProcessingError, VectorStoreError, LLMError
from src.utils.validators import validate_urls, validate_query

class RAGService:
    """
    RAG service for processing URLs and answering questions
    """
    
    def __init__(self):
        self._llm: Optional[ChatGroq] = None
        self._vector_store: Optional[Chroma] = None
        self._embeddings: Optional[HuggingFaceEmbeddings] = None
        self._initialized = False

    @property
    def llm(self) -> ChatGroq:
        """Lazy initialization of LLM"""
        if self._llm is None:
            try:
                self._llm = ChatGroq(
                    model=settings.groq_model,
                    temperature=settings.llm_temperature,
                    max_tokens=settings.llm_max_tokens
                )
                logger.info(f"Initialized LLM with model: {settings.groq_model}")
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {str(e)}")
                raise LLMError(f"LLM initialization failed: {str(e)}")
        return self._llm
    
    @property
    def embeddings(self) -> HuggingFaceEmbeddings:
        """Lazy initialization of embeddings"""
        if self._embeddings is None:
            try:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=settings.embedding_model,
                    model_kwargs={"trust_remote_code": True}
                )
                logger.info(f"Initialized embeddings with model: {settings.embedding_model}")
            except Exception as e:
                logger.error(f"Failed to initialize embeddings: {str(e)}")
                raise VectorStoreError(f"Embeddings initialization failed: {str(e)}")
        return self._embeddings
    
    @property
    def vector_store(self) -> Chroma:
        """Lazy initialization of vector store"""
        if self._vector_store is None:
            try:
                self._vector_store = Chroma(
                    collection_name=settings.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(settings.vectorstore_dir)
                )
                logger.info(f"Initialized vector store at: {settings.vectorstore_dir}")
            except Exception as e:
                logger.error(f"Failed to initialize vector store: {str(e)}")
                raise VectorStoreError(f"Vector store initialization failed: {str(e)}")
        return self._vector_store
    
    def initialize(self) -> None:
        """Initialize all components"""
        if self._initialized:
            return
        
        logger.info("Initializing RAG service components...")
        
        # Initialize components (lazy loading will handle actual initialization) 
        _ = self.llm
        _ = self.embeddings
        _ = self.vector_store
        
        self._initialized = True
        logger.info("RAG service initialization completed")

    @contextmanager
    def error_handler(self, operation: str):
        """Context manager for error handling"""
        try:
            logger.info(f"Starting operation: {operation}")
            start_time = time.time()
            yield
            end_time = time.time()
            logger.info(f"Completed operation: {operation} in {end_time - start_time:.2f}s")
        except Exception as e:
            logger.error(f"Operation failed: {operation} - {str(e)}")
            raise

    def process_urls(self, urls: List[str]) -> Iterator[str]:
        """
        Process URLs and store in vector database
        
        Args:
            urls: List of URLs to process
            
        Yields:
            Status messages
            
        Raises:
            URLProcessingError: If URL processing fails
            VectorStoreError: If vector store operations fail
        """
        try:
            # Validate URLs
            valid_urls = validate_urls(urls)
            logger.info(f"Processing {len(valid_urls)} URLs")
            
            yield "🔧 Initializing components..."
            self.initialize()
            
            yield "🔄 Resetting vector store..."
            with self.error_handler("reset_collection"):
                self.vector_store.reset_collection()
            
            yield "📥 Loading data from URLs..."
            with self.error_handler("load_urls"):
                loader = UnstructuredURLLoader(urls=valid_urls)
                documents = loader.load()
                
            if not documents:
                raise URLProcessingError("No documents were loaded from the provided URLs")
            
            logger.info(f"Loaded {len(documents)} documents")
            
            yield "✂️ Splitting text into chunks..."
            with self.error_handler("split_documents"):
                text_splitter = RecursiveCharacterTextSplitter(
                    separators=["\n\n", "\n", ".", " "],
                    chunk_size=settings.chunk_size,
                    chunk_overlap=settings.chunk_overlap
                )
                chunks = text_splitter.split_documents(documents)
            
            logger.info(f"Created {len(chunks)} text chunks")
            
            yield "🗃️ Adding chunks to vector database..."
            with self.error_handler("add_to_vectorstore"):
                uuids = [str(uuid4()) for _ in range(len(chunks))]
                self.vector_store.add_documents(chunks, ids=uuids)
            
            yield "✅ Successfully processed all URLs!"
            logger.info("URL processing completed successfully")
            
        except Exception as e:
            error_msg = f"URL processing failed: {str(e)}"
            logger.error(error_msg)
            if isinstance(e, (URLProcessingError, VectorStoreError)):
                raise
            raise URLProcessingError(error_msg)
        
    def generate_answer(self, query: str) -> Tuple[str, str]:
        """
        Generate answer for a query using RAG
        
        Args:
            query: User query
            
        Returns:
            Tuple of (answer, sources)
            
        Raises:
            LLMError: If answer generation fails
            VectorStoreError: If vector store is not initialized
        """
        try:
            # Validate query
            clean_query = validate_query(query)
            logger.info(f"Processing query: {clean_query[:100]}...")
            
            if not self._initialized or self._vector_store is None:
                raise VectorStoreError("Vector store not initialized. Please process URLs first.")
            
            with self.error_handler("generate_answer"):
                # Create retrieval chain
                chain = RetrievalQAWithSourcesChain.from_llm(
                    llm=self.llm,
                    retriever=self.vector_store.as_retriever()
                )
                
                # Generate answer
                result = chain.invoke(
                    {"question": clean_query},
                    return_only_outputs=True
                )
                
                answer = result.get("answer", "No answer generated")
                sources = result.get("sources", "No sources found")
                
                logger.info("Answer generated successfully")
                return answer, sources
                
        except Exception as e:
            error_msg = f"Answer generation failed: {str(e)}"
            logger.error(error_msg)
            if isinstance(e, (LLMError, VectorStoreError)):
                raise
            raise LLMError(error_msg)
        
        
    def get_collection_info(self) -> dict:
        """
        Get information about the current collection
        
        Returns:
            Dictionary with collection information
        """
        try:
            if not self._initialized or self._vector_store is None:
                return {"status": "not_initialized", "count": 0}
            
            collection = self.vector_store._collection
            count = collection.count()
            
            return {
                "status": "initialized",
                "count": count,
                "collection_name": settings.collection_name
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return {"status": "error", "error": str(e)}


    def health_check(self) -> dict:
        """
        Perform health check on all components
        
        Returns:
            Dictionary with health status
        """
        health = {
            "llm": "unknown",
            "embeddings": "unknown", 
            "vector_store": "unknown",
            "overall": "unknown"
        }
        
        try:
            # Check LLM
            try:
                _ = self.llm
                health["llm"] = "healthy"
            except Exception:
                health["llm"] = "unhealthy"
            
            # Check embeddings
            try:
                _ = self.embeddings
                health["embeddings"] = "healthy"
            except Exception:
                health["embeddings"] = "unhealthy"
            
            # Check vector store
            try:
                _ = self.vector_store
                health["vector_store"] = "healthy"
            except Exception:
                health["vector_store"] = "unhealthy"
            
            # Overall health
            all_healthy = all(status == "healthy" for status in health.values() if status != "unknown")
            health["overall"] = "healthy" if all_healthy else "unhealthy"
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            health["overall"] = "error"
        
        return health


# Global service instance
rag_service = RAGService()


if __name__ == "__main__":
    urls = ["https://huggingface.co/blog/Kseniase/mcp"]
    try:
        # Process URLs
        for status in rag_service.process_urls(urls):
            print(status)
        
        # Generate answer
        query = "when AI agents and agentic workflows became major buzzwords?"
        answer, sources = rag_service.generate_answer(query)
        print(f"Answer: {answer}")
        print(f"Sources: {sources}")
        
    except Exception as e:
        print(f"Error: {str(e)}")