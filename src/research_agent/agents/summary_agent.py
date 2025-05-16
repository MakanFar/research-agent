import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from ..tools.paper_processor import PaperProcessor
from pathlib import Path

class SummaryAgent:
    def __init__(self, api_key, meta_data):
        self.api_key = api_key
        self.meta_data=meta_data
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o",
            openai_api_key=api_key
        )
        self.pdf_processor = PaperProcessor(api_key)
        self.prompt = self._create_prompt()
        self.prompt2 = self._create_filter_prompt()
    
    def _create_prompt(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
        f"""
        You are an expert at analyzing academic papers. Extract key information accurately. Be thorough and precise in your analysis. Search for both explicit and implicit information and follow the instructions.

        Instructions:
        - Don't add any knowledge from yourself, and don't make assumptions. Only rely on the information provided in the paper
        - Be thorough and precise in your analysis.
        - Write the results concise 
        - Look for information in all sections.
        - If information is not found in the paper, return "unknown", but only after a thorough search.
        - For boolean fields, default to False only if the information is confidently not mentioned.

        Extract key information from this paper excerpt. Return a JSON object with these fields:
        {self.meta_data}
        
        Return concise JSON only, no explanations.
        """),
            ("user", "{input}"),
        ])
        return prompt
    
    def _create_filter_prompt(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
            """
            You are an expert research assistant helping a researcher find the most relevant academic papers for a specific research goal. Your job is to analyze paper abstracts and decide whether they are relevant to the user's objective.

            Instructions:
            - Carefully read the user's objective and the abstract.
            - Determine whether the abstract is highly relevant to the user's stated goal.
            - Be strict and conservative in your judgment—only return True if the abstract clearly aligns with the research objective.
            - Do not make assumptions beyond what's written in the abstract.
            - Return a JSON object like this:
            
            
                "relevant": true or false,
                "confidence": "high" | "medium" | "low",
                "reason": "short explanation why the abstract matches or not"
            
            """),
            ("user", 
            """
            Research Objective:
            {objective}

            Abstract:
            {abstract}
            """)
        ])
        return prompt
    
    def analyze_single_paper(self, path,type,objective):
        """Analyze a single paper and return structured summary"""
        try:
            if type=="pdf":
                combined_text =  self.pdf_processor.process(path)
                
                formatted_prompt = self.prompt.invoke({"input": combined_text})
            else:
                # Use the agent to extract structured information
                combined_text =  self.pdf_processor.filter_(path)
                formatted_prompt = self.prompt2.invoke({"objective":objective,"abstract": combined_text})

            result = self.llm.invoke(formatted_prompt)
            
            try:
                # Extract the content from the AIMessage
                if hasattr(result, 'content'):
                    content = result.content  # For AIMessage objects
                elif isinstance(result, str):
                    content = result  # For string responses
                elif isinstance(result, dict) and 'output' in result:
                    content = result['output']  # For dictionary responses
                else:
                    content = str(result)  # Fallback to string conversion
                
                print(f"Raw content type: {type(content)}")
                print(f"Raw content snippet: {str(content)[:100]}...")
                
                # Try to parse JSON directly or extract JSON from text
                try:
                    # First see if the entire content is valid JSON
                    parsed_result = json.loads(content)
                    return parsed_result
                except json.JSONDecodeError:
                    # If not, try to extract JSON from the text
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx != -1 and end_idx != -1:
                        json_str = content[start_idx:end_idx]
                        try:
                            parsed_result = json.loads(json_str)
                            return parsed_result
                        except json.JSONDecodeError:
                            return {"error": f"Failed to parse extracted JSON: {json_str[:50]}...", "file": path}
                    else:
                        return {"error": "No JSON found in output", "file": path}
            except Exception as json_error:
                return {"error": f"Failed to parse result: {str(json_error)}", "file": path, "raw_output": str(result)[:200]}
                
        except Exception as e:
            return {
                "error": str(e),
                "file": path
            }
 
    def analyze_papers(self, papers, type,objective):
        """Analyze multiple papers sequentially and return structured summaries"""
        results = []
        if type=='pdf':
            for path in papers:
                try:
                    path = Path(path).resolve()
                    result = self.analyze_single_paper(path,type,None)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "error": str(e),
                        "file": path
                    })
        else:
            for paper in papers:
                try:
                    result = self.analyze_single_paper(paper['body'],type,objective)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "error": str(e),
                        "file": paper
                    })
        
        return results