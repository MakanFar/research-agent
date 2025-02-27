import json
from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from ..tools.pdf_processor import PDFProcessor
from ..tools.paper_analyzer import PaperAnalyzer

class PaperAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",
            openai_api_key=api_key
        )
        self.pdf_processor = PDFProcessor(api_key)
        self.paper_analyzer = PaperAnalyzer()
        
        self.tools = [
            Tool(
                name="process_pdf",
                func=self.pdf_processor.process,
                description="Process a PDF file and extract its text content"
            ),
            Tool(
                name="analyze_paper",
                func=self.paper_analyzer.analyze,
                description="Analyze paper content and extract structured information"
            )
        ]
        
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self._create_prompt()
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
    
    def _create_prompt(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert at analyzing academic papers. Extract key information accurately."),
            ("user", "{input}"),
            ("user", "{agent_scratchpad}")
        ])
        return prompt
    
    def analyze_papers(self, paper_paths):
        """Analyze multiple papers and return structured summaries"""
        from concurrent.futures import ThreadPoolExecutor
        import threading

        thread_local = threading.local()
        results = []

        def analyze_single_paper(path):
            try:
                # First process the PDF and get chunks with embeddings
                processed_data = self.pdf_processor.process(path)
                chunks = processed_data['chunks']
                vectorstore = processed_data['vectorstore']
                
                # Only use the most relevant chunks from specific sections
                queries = {
                    "title abstract": 1,
                    "methods": 1,
                    "results conclusion": 1
                }
                
                all_chunks = []
                for query, k in queries.items():
                    results = vectorstore.similarity_search(query, k=k)
                    all_chunks.extend([doc.page_content for doc in results])
                
                # Keep only unique chunks
                unique_chunks = list(set(all_chunks))
                
                # Limit total text length
                combined_text = " ".join(unique_chunks)
                if len(combined_text) > 3000:
                    unique_chunks = [combined_text[:3000]]
                
                analysis = self.paper_analyzer.analyze(unique_chunks)
                
                # Use the agent to extract structured information
                result = self.agent_executor.invoke({
                    "input": f"""
                    Based on the following paper analysis, extract the requested information in JSON format:
                    {analysis}
                    """
                })
                
                # Extract the actual result from the agent's output
                if isinstance(result, dict) and 'output' in result:
                    try:
                        # Try to parse JSON from the output
                        parsed_result = json.loads(result['output'])
                        results.append(parsed_result)
                    except json.JSONDecodeError:
                        # If not valid JSON, use the raw output
                        results.append(result['output'])
                else:
                    results.append(result)
                    
            except Exception as e:
                print(f"Error processing {path}: {str(e)}")
                results.append({
                    "error": str(e),
                    "file": path
                })
        def process_paper(path):
            try:
                return analyze_single_paper(path)
            except Exception as e:
                return {
                    "error": str(e),
                    "file": path
                }

        # Process papers in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(process_paper, paper_paths))

        return results
