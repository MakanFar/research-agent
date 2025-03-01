import json
from langchain.chains import MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document

class PaperAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4-turbo",
            openai_api_key=api_key
        )
        self.schema = {
            "first_author": {"type": "string", "description": "First author's name"},
            "publication_date": {"type": "string", "description": "Date of publication"},
            "title": {"type": "string", "description": "Title of the paper"},
            "journal": {"type": "string", "description": "Name of the journal"},
            "external_training_data": {"type": "boolean", "description": "Whether external datasets were used for training"},
            "external_evaluation_data": {"type": "boolean", "description": "Whether external datasets were used for evaluation"},
            "small_dataset_techniques": {"type": "string", "description": "Techniques used to mitigate small dataset issues"},
            "data_heterogeneity": {"type": "string", "description": "Description of data heterogeneity and management methods"},
            "preprocessing": {"type": "string", "description": "Data preprocessing and noise handling steps"},
            "black_box_status": {"type": "boolean", "description": "Whether the model is considered a black box"},
            "evaluation_metrics": {"type": "string", "description": "Metrics used to evaluate model performance"},
            "species_breed": {"type": "string", "description": "Target species or breed, if applicable"},
            "ml_algorithm": {"type": "string", "description": "Machine learning algorithm or model type used"},
            "data_type": {"type": "string", "description": "Type of data used in the study"},
            "ai_goal": {"type": "string", "description": "Purpose of the AI system and target disease"},
            "clinical_implementation": {"type": "boolean", "description": "Whether the model has been implemented clinically or commercially"}
        }
    
    def analyze(self, text_chunks):
        """Analyze paper content using MapReduce approach"""
        # Create a simplified schema for the prompts
        simple_schema = {k: v["description"] for k, v in self.schema.items()}
        
        # Map prompt - analyze individual chunks
        map_template = """Extract key information from this research paper section.
        Focus on finding specific details that match these categories:
        {schema}
        
        Text section:
        {text}
        
        Return ONLY a valid JSON object with any found information, no additional text.
        Only include fields where you found relevant information.
        """
        
        map_prompt = PromptTemplate(
            input_variables=["text", "schema"],
            template=map_template
        )
        
        # Reduce prompt - combine all findings
        reduce_template = """Combine these separate paper analysis results into a single coherent summary.
        Resolve any conflicts by choosing the most specific or detailed information.
        
        Required format: Return a JSON object with these exact fields:
        {schema}
        
        Analysis sections:
        {text}
        
        Guidelines:
        1. Merge all found metadata, keeping most complete information
        2. Combine all preprocessing steps and techniques
        3. List all evaluation metrics found
        4. Use most detailed algorithm descriptions
        5. Set boolean fields true if any section indicates true
        
        Return ONLY a valid JSON object, no additional text.
        """
        
        reduce_prompt = PromptTemplate(
            input_variables=["text", "schema"],
            template=reduce_template
        )
        
        # Create the map and reduce chains
        map_chain = LLMChain(llm=self.llm, prompt=map_prompt)
        reduce_chain = LLMChain(llm=self.llm, prompt=reduce_prompt)
        
        # Create combine documents chain
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain,
            document_variable_name="text",
        )
        
        # Create the MapReduce chain
        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            combine_documents_chain=combine_documents_chain,
            document_variable_name="text",
            return_intermediate_steps=False
        )
        
        try:
            # Convert text chunks to Documents if needed
            documents = []
            for chunk in text_chunks:
                if isinstance(chunk, Document):
                    documents.append(chunk)
                else:
                    documents.append(Document(page_content=str(chunk)))
            
            # Run the MapReduce chain
            result = map_reduce_chain.run(
                input_documents=documents,
                schema=json.dumps(simple_schema, indent=2)
            )
            
            return result
            
        except Exception as e:
            raise Exception(f"Error analyzing paper content: {str(e)}")
