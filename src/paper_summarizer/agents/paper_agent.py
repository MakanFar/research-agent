import json
from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from ..tools.pdf_processor import PDFProcessor
from ..tools.paper_analyzer import PaperAnalyzer
import re
class PaperAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4-turbo",
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
    
    def _extract_json(self, text):
        """Extract JSON string from text output"""
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            return text[start_idx:end_idx]
        return None

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
                # Process the PDF and get chunks with embeddings
                processed_data = self.pdf_processor.process(path)
                chunks = processed_data['chunks']
                vectorstore = processed_data['vectorstore']
                
                # Define important section queries
                queries = {
                    "title abstract authors affiliations": 5,
                    "introduction background objective": 4,
                    "methods methodology algorithm model": 5,
                    "data dataset preprocessing cleaning": 4,
                    "results performance metrics evaluation": 4,
                    "discussion findings implications": 3,
                    "conclusion future work": 3
                }
                
                # Get relevant chunks for each section
                section_chunks = []
                for query, k in queries.items():
                    results = vectorstore.similarity_search(query, k=k)
                    section_chunks.extend(results)
                
                # Map phase - analyze each section
                mapped_results = []
                for chunk in section_chunks:
                    map_prompt = self.paper_analyzer._map_chunk(chunk)
                    map_result = self.agent_executor.invoke({
                        "input": map_prompt
                    })
                    if isinstance(map_result, dict) and 'output' in map_result:
                        try:
                            json_str = self._extract_json(map_result['output'])
                            if json_str:
                                mapped_results.append(json.loads(json_str))
                        except json.JSONDecodeError:
                            continue
                
                # Reduce phase - combine results
                reduce_prompt = self.paper_analyzer._reduce_results(mapped_results)
                analysis = self.agent_executor.invoke({
                    "input": reduce_prompt
                })
                
                
                # Use the agent to extract structured information
                result = self.agent_executor.invoke({
                    "input": f"""
                    Based on the following paper analysis, extract the requested information in JSON format:
                    {analysis}
                    """
                })
                
                # Extract JSON from the final analysis
                if isinstance(analysis, dict) and 'output' in analysis:
                    json_str = self._extract_json(analysis['output'])
                    if json_str:
                        return json.loads(json_str)
                    else:
                        return {"error": "No JSON found in output", "file": path}
                else:
                    return {"error": "Unexpected output format", "file": path}
                    
            except Exception as e:
                return {
                    "error": str(e),
                    "file": path
                }
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
