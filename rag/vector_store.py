from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path
import os

class CareerKnowledgeBase:
    """RAG system for career knowledge"""
    
    def __init__(self, documents_dir="rag/documents"):
        self.documents_dir = Path(documents_dir)
        
        # Initialize embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client()
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.create_collection(
                name="career_knowledge",
                metadata={"description": "Career and job role knowledge base"}
            )
        except:
            # Collection already exists
            self.collection = self.chroma_client.get_collection("career_knowledge")
    
    def load_documents(self):
        """Load all documents from the documents directory"""
        documents = []
        metadatas = []
        ids = []
        
        doc_id = 0
        for file_path in self.documents_dir.glob("*.txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Split into chunks (simple paragraph-based splitting)
                chunks = [p.strip() for p in content.split('\n\n') if p.strip()]
                
                for chunk in chunks:
                    documents.append(chunk)
                    metadatas.append({
                        "source": file_path.stem,
                        "filename": file_path.name
                    })
                    ids.append(f"doc_{doc_id}")
                    doc_id += 1
        
        return documents, metadatas, ids
    
    def build_index(self):
        """Build vector index from documents"""
        print("Loading documents...")
        documents, metadatas, ids = self.load_documents()
        
        print(f"Found {len(documents)} document chunks")
        print("Creating embeddings...")
        
        # Add to ChromaDB
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print("✅ Index built successfully!")
        return len(documents)
    
    def search(self, query, n_results=3):
        """Search for relevant documents"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return {
            'documents': results['documents'][0],
            'metadatas': results['metadatas'][0],
            'distances': results['distances'][0] if 'distances' in results else None
        }
    
    def get_relevant_context(self, query, n_results=3):
        """Get relevant context as formatted string"""
        results = self.search(query, n_results)
        
        context = "\n\n---\n\n".join([
            f"Source: {meta['source']}\n{doc}"
            for doc, meta in zip(results['documents'], results['metadatas'])
        ])
        
        return context