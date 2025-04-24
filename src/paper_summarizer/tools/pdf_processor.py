import os
import urllib.parse
from pathlib import Path
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
            # Ensure we have a valid local file path
            file_path = os.path.abspath(file_path)
            
            # Verify the file exists before attempting to load it
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            chunks = self.text_splitter.split_documents(pages)
            
            # Create vector store from the chunks
            vectorstore = FAISS.from_documents(chunks, self.embeddings)
            
            # Return both chunks and vectorstore for semantic search
            return {
                'chunks': chunks,
                'vectorstore': vectorstore
            }
        except Exception as e:
            raise Exception(f"Error processing PDF {file_path}: {str(e)}")
