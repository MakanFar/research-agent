import json
import tiktoken  # OpenAI's tokenizer library
from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from ..tools.pdf_processor import PDFProcessor
from ..tools.paper_analyzer import PaperAnalyzer
import re

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

    def _count_tokens(self, text, model="gpt-4o"):
        """
        Count tokens in a given text using OpenAI's tokenizer.
        """
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))

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
                # Process the PDF and extract text chunks
                processed_data = self.pdf_processor.process(path)
                
                if 'error' in processed_data:
                    return {"error": processed_data['error'], "file": path}
                
                chunks = processed_data['chunks']
                vectorstore = processed_data['vectorstore']
                
                if not chunks or not vectorstore:
                    return {"error": "No content extracted from PDF", "file": path}

                queries = {
                    "introduction background objective": 4,
                    "methods methodology algorithm model": 4,
                    "dataset": 2,
                    "preprocessing normalization augmentation noise missing data": 4,
                    "discussion limitations": 4,
                    "conclusion future work": 4
                }
                
                relevant_chunks = []
                for query, k in queries.items():
                    results = vectorstore.similarity_search(query, k=k)
                    relevant_chunks.extend([doc.page_content for doc in results])

                first_chunk_text = chunks[0].page_content if chunks else ""

                seen = set()
                unique_chunks = []

                if first_chunk_text not in seen:
                    unique_chunks.append(first_chunk_text)
                    seen.add(first_chunk_text)

                for chunk in relevant_chunks:
                    if chunk not in seen:
                        unique_chunks.append(chunk)
                        seen.add(chunk)

                analysis = self.paper_analyzer.analyze(unique_chunks)

                with open("test.txt", "w", encoding="utf-8") as file:
                        file.write(analysis)

                # Count input tokens before execution
                input_text = f"""{analysis}"""
                input_token_count = self._count_tokens(input_text)
                print(f"📊 Input Token Count: {input_token_count}")

                if input_token_count > 30000:
                    return {
                        "error": f"Input token count ({input_token_count}) exceeds GPT-4o limit (30000).",
                        "file": path
                    }

                # Use the agent executor
                result = self.agent_executor.invoke({"input": input_text})

                # Count output tokens
                if isinstance(result, dict) and 'output' in result:
                    output_text = result['output']
                    output_token_count = self._count_tokens(output_text)
                    print(f"📊 Output Token Count: {output_token_count}")

                    if output_token_count > 30000:
                        return {
                            "error": f"Output token count ({output_token_count}) exceeds GPT-4o limit (30000).",
                            "file": path
                        }

                    # Extract JSON from output
                    try:
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
                return {"error": str(e), "file": path}

        def process_paper(path):
            print(path)
            try:
                return analyze_single_paper(path)
            except Exception as e:
                return {"error": str(e), "file": path}

        # Process papers in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(process_paper, paper_paths))

        return results
