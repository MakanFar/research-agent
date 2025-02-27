from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from ..tools.pdf_processor import PDFProcessor
from ..tools.paper_analyzer import PaperAnalyzer

class PaperAgent:
    def __init__(self, api_key):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4",
            openai_api_key=api_key
        )
        self.pdf_processor = PDFProcessor()
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
            ("user", "{input}")
        ])
        return prompt
    
    def analyze_papers(self, paper_paths):
        """Analyze multiple papers and return structured summaries"""
        results = []
        for path in paper_paths:
            try:
                result = self.agent_executor.invoke({
                    "input": f"Analyze the paper at {path} and extract key information"
                })
                results.append(result)
            except Exception as e:
                print(f"Error processing {path}: {str(e)}")
        return results
