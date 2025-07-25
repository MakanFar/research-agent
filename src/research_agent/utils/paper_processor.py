from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from pathlib import Path

class PaperProcessor:
    def __init__(self, api_key):
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,  
            chunk_overlap=200,  
            separators=["\n\n", "\n", ".", "!", "?", ";", " ", ""]
        )

    def convert2doc(self,parsed_articles):
        docs = []
        for article in parsed_articles:
            content="None"

            if article['body'] is not None:

                content = f"{article['title']}\n\nAbstract:\n{article['abstract']}\n\nFull Text:\n{article['body']}"

            pmc = article["pmc"]
            metadata = {
                "pmc": pmc,
                "url": article["url"],
                "title": article["title"],
                "journal": article.get("journal"),
                "first_author": article.get("first_author"),
                "year": article.get("year"),
                "abstract": article["abstract"],
                "title/abstract": f"{article['title']}\n\nAbstract:\n{article['abstract']}"
            }
            doc = Document(page_content=content, metadata=metadata)
            docs.append(doc)

        return docs
    
    def process_article(self, article,only_abstract=False):
        """Process a PDF file and return chunked text with embeddings"""
                
        try:
            if isinstance(article, Path):
                loader = PyPDFLoader(article)
                article = loader.load()

            chunks = self.text_splitter.split_documents(article)

            # Create vector store from the chunks
            vectorstore = FAISS.from_documents(chunks, self.embeddings)

            unique_chunks = set()
            result_chunks = []

            # Get the first chunk for context (if available)

            if chunks:
                first_chunk = chunks[0].page_content
                unique_chunks.add(first_chunk)
                result_chunks.append(first_chunk)

           

            if only_abstract:
                 # abstract
                abstract_quries = {
                    "introduction background objective abstract": 4,    # Context
                }
                # Batch process abstract queries at once
        
                
                for query, k in abstract_quries.items():
                    search_results = vectorstore.similarity_search(query, k=k)
                    # Add only new chunks
                    for doc in search_results:
                        content = doc.page_content
                        if content not in unique_chunks:
                            unique_chunks.add(content)
                            result_chunks.append(content)

      
            else:

                # Key sections in body to extract with their importance
                context_queries = {
                    "introduction background objective abstract": 4,    # Context
                    "dataset": 3,                                      # Data
                    "methods methodology algorithm model": 4,         # Technical details
                    "preprocessing normalization augmentation": 3,    # Data handling
                    "sensitivity specificity precision recall f1 score AUC Accuracy": 3,
                    "performance restults metrics": 4,         
                    "discussion limitations": 4,                      # Interpretations
                    "conclusion future work": 4                       # Final remarks
                }
                    

                
                # Batch process all queries at once
        
                
                for query, k in context_queries.items():
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
        
            return f"Error processing PDF {article}: {str(e)}"
        
    

    def process_abstract_online(self, abstract):
        try:
            chunks = self.text_splitter.split_documents(abstract)            
            # Return chunks
            return chunks
    
        except Exception as e:
        
            return f"Error processing abstract {abstract}: {str(e)}"
        

    
        
def convert2doc(parsed_articles):
        docs = []
        for article in parsed_articles:
            content="None"

            if article['body'] is not None:

                content = f"{article['title']}\n\nAbstract:\n{article['abstract']}\n\nFull Text:\n{article['body']}"

            pmc = article["pmc"]
            metadata = {
                "pmc": pmc,
                "url": article["url"],
                "title": article["title"],
                "journal": article.get("journal"),
                "first_author": article.get("first_author"),
                "year": article.get("year"),
                "abstract": article["abstract"],
                "title/abstract": f"{article['title']}\n\nAbstract:\n{article['abstract']}"
            }
            doc = Document(page_content=content, metadata=metadata)
            docs.append(doc)

        return docs

        

         

            
       
