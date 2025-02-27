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
                
                # Get information from specific sections
                queries = {
                    "title page header authors": 3,  # More chunks for metadata
                    "methodology machine learning algorithm": 2,
                    "results evaluation metrics": 2,
                    "data preprocessing dataset": 2
                }
                
                essential_sections = []
                for query, k in queries.items():
                    results = vectorstore.similarity_search(query, k=k)
                    essential_sections.extend(results)
                
                # Process chunks more intelligently
                all_chunks = []
                seen_content = set()
                
                for doc in essential_sections:
                    content = doc.page_content.strip()
                    # Only add non-empty, unique content
                    if content and content not in seen_content:
                        seen_content.add(content)
                        all_chunks.append(content)
                
                # Prioritize first chunks which likely contain metadata
                combined_text = " ".join(all_chunks)
                if len(combined_text) > 1500:
                    # Keep first chunk (likely metadata) and trim the rest
                    first_chunk = all_chunks[0]
                    remaining_text = " ".join(all_chunks[1:])[:1500 - len(first_chunk)]
                    unique_chunks = [first_chunk + " " + remaining_text]
                else:
                    unique_chunks = [combined_text]
                
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
