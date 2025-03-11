from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

class PDFProcessor:
    def __init__(self, api_key):
        self.embeddings = OllamaEmbeddings(model="deepseek")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ";", " ", ""]
        )
    
    def process(self, file_path):
        """Process a PDF file and return chunked text with embeddings"""
        try:
            # Skip supplementary URLs that aren't actual PDFs
            if '/s1' in file_path or file_path.endswith('/s1'):
                return {
                    'chunks': [],
                    'vectorstore': None,
                    'error': 'Skipped supplementary URL'
                }

            loader = PyPDFLoader(file_path)
            
            # Handle potential stream errors
            try:
                pages = loader.load()
            except Exception as page_error:
                if "Stream has ended unexpectedly" in str(page_error):
                    # Try alternative loading method or return partial content
                    return {
                        'chunks': [],
                        'vectorstore': None,
                        'error': f'PDF loading error: {str(page_error)}'
                    }
                raise page_error

            # Clean and validate text before chunking
            cleaned_pages = []
            for page in pages:
                if hasattr(page, 'page_content'):
                    # Remove vertical text artifacts and normalize spaces
                    cleaned_text = ' '.join(page.page_content.split())
                    page.page_content = cleaned_text
                    cleaned_pages.append(page)

            # Clean and validate text before chunking
            cleaned_pages = []
            for page in pages:
                if hasattr(page, 'page_content'):
                    # Remove vertical text artifacts and normalize spaces
                    cleaned_text = ' '.join(page.page_content.split())
                    page.page_content = cleaned_text
                    cleaned_pages.append(page)

            chunks = self.text_splitter.split_documents(cleaned_pages)

            if not chunks:
                return {
                    'chunks': [],
                    'vectorstore': None,
                    'error': 'No content extracted from PDF'
                }

            # Create vector store from the chunks
            vectorstore = FAISS.from_documents(chunks, self.embeddings)
            
            return {
                'chunks': chunks,
                'vectorstore': vectorstore
            }
        except Exception as e:
            return {
                'chunks': [],
                'vectorstore': None,
                'error': f"Error processing PDF {file_path}: {str(e)}"
            }
