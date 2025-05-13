import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from ..tools.pdf_processor import PDFProcessor
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
        self.prompt = self._create_prompt()
    
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
        - first_author: First listed author's name on paper
        - publication_date: Year that paper was published
        - title: Paper title
        - data_type: Type of data used in the study such as radiology, clinicopathologic, or text
        - species_breed: Target species
        - ml_algorithm: Types Model used in the study
        - ai_goal: Clinical objective of the study
        - clinical_implementation: Boolean. Set true if study was actually deployed and adopted in real life.
        - external_training_data: Boolean. Set True if external datasets such as data from multiple sources are used
        - external_validation_data: Boolean. Set to True if the model has been evaluated using external datasets or data from other sources. 
        - small_dataset: Boolean. Set to True if the paper mentions lack of data OR if the data used to train the model is less than 1000 samples
        - small_dataset_techniques: In cases of limited data, mention methods that authors use to mitigate the issue—such as transfer learning, data augmentation, and similar techniques.
        - data_heterogeneity: Mention of the authors use heterogeneous data or attempt to add variability through different types of data, data from various sources, different collection processes, or any other methods that could increase heterogeneity.
        - preprocessing: Data preprocessing techniques used to to handel the noise, or missing data, or class imbalance
        - regularization: regularization techniques used to stop model from overfiting such as early stopping, dropout or l1 and l2 regularization
        - black_box_status: Boolean. Set to True if the model lacked explainability methods such as feature importance, Grad-CAM, or other means of providing interpretability.
        - evaluation_metrics: Performance metrics used for evaluting the model
        - performance_results: Key final performance results
        - ethics: Ethical implications discussed by the authors
        
        Return concise JSON only, no explanations.
        """),
            ("user", "{input}"),
        ])
        return prompt
    
    def analyze_single_paper(self, path):
        """Analyze a single paper and return structured summary"""
        try:
           
            combined_text =  self.pdf_processor.process(path)
            
            formatted_prompt = self.prompt.invoke({"input": combined_text})
            # Use the agent to extract structured information
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
 
    def analyze_papers(self, paper_paths):
        """Analyze multiple papers sequentially and return structured summaries"""
        results = []
        for path in paper_paths:
            try:
                path = Path(path).resolve()
                result = self.analyze_single_paper(path)
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "file": path
                })
        
        return results