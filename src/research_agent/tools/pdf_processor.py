from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

class PDFProcessor:
    def __init__(self, api_key):
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,  
            chunk_overlap=200,  
            separators=["\n\n", "\n", ".", "!", "?", ";", " ", ""]
        )


    
    def process(self, file_path):
        """Process a PDF file and return chunked text with embeddings"""
                
        try:

            loader = PyPDFLoader(file_path)
            pages = loader.load()
    

            chunks = self.text_splitter.split_documents(pages)

            # Create vector store from the chunks
            vectorstore = FAISS.from_documents(chunks, self.embeddings)

                        
            # Define key sections to extract with their importance (number of chunks)
            section_queries = {
                "introduction background objective abstract": 4,    # Context
                "dataset": 3,                                      # Data
                "methods methodology algorithm model": 4,         # Technical details
                "preprocessing normalization augmentation": 4,    # Data handling
                "sensitivity specificity precision recall f1 score AUC Accuracy": 3,
                "performance restults metrics": 4,         
                "discussion limitations": 4,                      # Interpretations
                "conclusion future work": 4                       # Final remarks
            }
            
            # Get the first chunk for context (if available)
            unique_chunks = set()
            result_chunks = []
            
            if chunks:
                first_chunk = chunks[0].page_content
                unique_chunks.add(first_chunk)
                result_chunks.append(first_chunk)
            
            # Batch process all queries at once
            for query, k in section_queries.items():
                search_results = vectorstore.similarity_search(query, k=k)
                
                # Add only new chunks
                for doc in search_results:
                    content = doc.page_content
                    if content not in unique_chunks:
                        unique_chunks.add(content)
                        result_chunks.append(content)

            # Count tokens in the combined chunks
            combined_text = " ".join(result_chunks)
            
            
            # Return both chunks and vectorstore for semantic search
            return combined_text
    
        except Exception as e:
        
            return f"Error processing PDF {file_path}: {str(e)}"
            
       
