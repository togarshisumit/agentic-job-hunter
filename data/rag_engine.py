import os
import chromadb
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter

class PortfolioRetriever:
    """
    A production-grade RAG interface for querying a user's past experience.
    It builds a local vector database if one doesn't exist, or loads it if it does.
    """
    
    def __init__(self, data_dir: str = "data/documents", db_dir: str = "data/chroma_db"):
        self.data_dir = data_dir
        self.db_dir = db_dir
        self.collection_name = "portfolio_collection"
        
        # Configure global settings (Using local HuggingFace embeddings for free)
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        # Chunk size of 256 is perfect for capturing granular project details without exceeding context windows
        Settings.node_parser = SentenceSplitter(chunk_size=256, chunk_overlap=25)

        # Initialize ChromaDB client (Persistent local storage)
        self.db = chromadb.PersistentClient(path=self.db_dir)
        self.collection = self.db.get_or_create_collection(self.collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        self.index = self._initialize_index()

    def _initialize_index(self) -> VectorStoreIndex:
        """Loads existing index or builds a new one if the DB is empty."""
        if self.collection.count() > 0:
            print("📦 Loading existing portfolio vector database...")
            return VectorStoreIndex.from_vector_store(
                self.vector_store,
                storage_context=self.storage_context,
            )
        else:
            print("🔨 Vector database is empty. Ingesting documents...")
            return self.ingest_documents()

    def ingest_documents(self) -> VectorStoreIndex:
        """Reads all files in data/documents/ and embeds them into ChromaDB."""
        if not os.path.exists(self.data_dir) or not os.listdir(self.data_dir):
            raise FileNotFoundError(f"⚠️ No documents found in {self.data_dir}. Drop your resume/projects there.")
        
        documents = SimpleDirectoryReader(self.data_dir).load_data()
        print(f"📚 Loaded {len(documents)} document chunks. Embedding now...")
        
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=self.storage_context, 
            show_progress=True
        )
        return index

    def retrieve_relevant_experience(self, query: str, top_k: int = 5) -> str:
        """
        Queries the vector DB for the most relevant past experience.
        Returns a single concatenated string of context for the LLM.
        """
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query)
        
        if not nodes:
            return "No highly relevant past experience found in the database."
        
        # Combine the text from the top retrieved chunks
        context = "\n---\n".join([node.node.text for node in nodes])
        return context