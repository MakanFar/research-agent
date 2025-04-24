import os
import urllib.parse
import time
import random
from pathlib import Path
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from openai import RateLimitError

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
        max_retries = 5
        base_delay = 1
        
        try:
            # Ensure we have a valid local file path
            file_path = os.path.abspath(file_path)
            
            # Verify the file exists before attempting to load it
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            chunks = self.text_splitter.split_documents(pages)
            
            # Create vector store from the chunks with retry logic
            for attempt in range(max_retries):
                try:
                    vectorstore = FAISS.from_documents(chunks, self.embeddings)
                    
                    # Return both chunks and vectorstore for semantic search
                    return {
                        'chunks': chunks,
                        'vectorstore': vectorstore
                    }
                except RateLimitError as e:
                    if attempt < max_retries - 1:
                        # Calculate exponential backoff with jitter
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        print(f"Rate limit hit, retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} attempts: {str(e)}")
                except Exception as e:
                    # For non-rate limit errors, don't retry
                    raise
                    
        except Exception as e:
            raise Exception(f"Error processing PDF {file_path}: {str(e)}")
