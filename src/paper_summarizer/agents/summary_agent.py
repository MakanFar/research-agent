import json
from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from ..tools.pdf_processor import PDFProcessor
from ..tools.paper_analyzer import PaperAnalyzer
from pathlib import Path

class SummaryAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o",
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
          
                # Process the PDF once and unpack results
                processed_data = self.pdf_processor.process(path)
                chunks = processed_data['chunks']
                vectorstore = processed_data['vectorstore']
                
                # Define key sections to extract with their importance (number of chunks)
                section_queries = {
                    "introduction background objective": 3,          # Context
                    "methods methodology algorithm model": 4,         # Technical details
                    "dataset": 2,                                    # Data
                    "preprocessing normalization augmentation": 4,    # Data handling
                    "discussion limitations": 3,                      # Interpretations
                    "conclusion future work": 3                       # Final remarks
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

                analysis = self.paper_analyzer.analyze(result_chunks)
                
                # Use the agent to extract structured information
                result = self.agent_executor.invoke({
                    "input": f"""{analysis}"""
                })
                
                # Extract the actual result from the agent's output
                if isinstance(result, dict) and 'output' in result:
                    try:
                        # Try to parse JSON from the output
                        # Remove any leading/trailing text around the JSON
                        output_text = result['output']
                        start_idx = output_text.find('{')
                        end_idx = output_text.rfind('}') + 1
                        if start_idx != -1 and end_idx != -1:
                            json_str = output_text[start_idx:end_idx]
                            parsed_result = json.loads(json_str)
                            return parsed_result
                        else:
                            return {"error": "No JSON found in output", "file": path}
                    except json.JSONDecodeError:
                        return {"error": "Invalid JSON in output", "file": path}
                else:
                    return {"error": "Unexpected output format", "file": path}
                    
            except Exception as e:
                return {
                    "error": str(e),
                    "file": path
                }
        def process_paper(path):
            try:
                path = Path(path).resolve()
                return analyze_single_paper(path)
            except Exception as e:
                return {
                    "error": str(e),
                    "file": path
                }

        # Process papers in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            #print("thisss", paper_paths)
            results = list(executor.map(process_paper, paper_paths))
        return results
