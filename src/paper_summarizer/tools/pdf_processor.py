import os
import urllib.parse
from pathlib import Path
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import tiktoken

class PDFProcessor:
    def __init__(self, api_key):
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Reduced chunk size
            chunk_overlap=100,  # Reduced overlap
            separators=["\n\n", "\n", ".", "!", "?", ";", " ", ""]
        )
        # Initialize tokenizer for GPT-4
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
        
    def num_tokens(self, text):
        """Count the number of tokens in a text string"""
        return len(self.tokenizer.encode(text))
    
    def process(self, file_path):
        """Process a PDF file and return chunked text with embeddings"""
        try:
            # Ensure we have a valid local file path
            
            loader = PyPDFLoader(file_path)
            pages = loader.load()

            chunks = self.text_splitter.split_documents(pages)
            
            # Count total tokens in all chunks
            total_tokens = sum(self.num_tokens(chunk.page_content) for chunk in chunks)
            
            # Create vector store from the chunks
            vectorstore = FAISS.from_documents(chunks, self.embeddings)
            
            # Return both chunks and vectorstore for semantic search
            return {
                'chunks': chunks,
                'vectorstore': vectorstore,
                'total_tokens': total_tokens
            }
        except Exception as e:
            raise Exception(f"Error processing PDF {file_path}: {str(e)}")
