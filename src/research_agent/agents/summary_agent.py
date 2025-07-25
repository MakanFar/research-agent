from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from ..utils.paper_processor import PaperProcessor
from ..agents.prompts import PromptManager
from pathlib import Path
from ..utils.validators import metaAnalysisModel, FilterModel, SystematicReviewModel
import asyncio
from ..logger.logger import Logger
from rich.console import Console
import typer

console = Console()

# Initialize logger
logger = Logger().get_logger()
log_timer = Logger().log_execution_time

class SummaryAgent:
    def __init__(self, api_key, meta_data):
        self.util = util()
        self.api_key = api_key
        self.meta_data = meta_data
        self.model_name = "gpt-4o"
        self.MetaAnalysisModel= metaAnalysisModel() 
        self.SystematicReviewModel = SystematicReviewModel()
        
        # Initialize  LLM instance for concurrent processing
        self.llm = ChatOpenAI(
                temperature=0,
                model=self.model_name,
                openai_api_key=api_key,
                max_retries=2,
                request_timeout=30
                )
        
        self.paper_processor = PaperProcessor(api_key)

    @log_timer
    async def filter_single_paper(self, paper,objective):
        """filter a single paper according to abstract"""
        try:
            """
            if type=="local":
                processed_abstract =  self.paper_processor.process_article(abstract,True) 
            else:
                processed_abstract =  self.paper_processor.process_abstract_online(abstract)  
            """
            processed_abstract =  self.paper_processor.process_abstract_online(paper.metadata["title/abstract"])

            parser = PydanticOutputParser(pydantic_object=FilterModel)
            
            
            prompt = PromptTemplate(
            template=PromptManager.filter_prompt(),
            input_variables=["questions","paper"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()},
            )
        
            chain = prompt | self.llm | parser

            output = await chain.ainvoke({
                "questions": objective,
                "paper": processed_abstract
            })
            return output
        
        except Exception as e:
            logger.exception("Error during filtering single paper: error: {}, Paper: {}".format(str(e),paper.metadata["title"]))
            console.print("[red]Error during filtering paper titled {}".format(paper.metadata["title"]))
            return {
                "error": str(e),
                "file": paper.metadata["title"]
            }
        
    async def proccess_with_semaphore(self,query,*args, **kwargs):
        semaphore = asyncio.Semaphore(3)
        async with semaphore:
            return await query(*args, **kwargs)
    
    @log_timer
    async def meta_analysis_single(self, article):
        """Analyze a single paper and return structured summary"""
        
        processed_article =  self.paper_processor.process_abstract_online(article)   
        
        parser = PydanticOutputParser(pydantic_object=self.MetaAnalysisModel)

        prompt = PromptTemplate(
        template=PromptManager.meta_analysis_prompt(),
        input_variables=["paper"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.llm | parser

        output = await chain.ainvoke({
            "paper": processed_article,
        })
        return output
    
    @log_timer
    async def systematic_review_single(self, article):
        """Analyze a single paper and return structured summary"""
        
        processed_article =  self.paper_processor.process_abstract_online(article)   
        
        parser = PydanticOutputParser(pydantic_object=self.SystematicReviewModel)

        prompt = PromptTemplate(
        template=PromptManager.systematic_review_prompt(),
        input_variables=["paper"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.llm | parser

        output = await chain.ainvoke({
            "paper": processed_article,
        })
        return output
        
                
       
    def obj_questions(self, objective):

        prompt = PromptTemplate(
            template=PromptManager.generate_objective_prompt(),
            input_variables=["objective"],

            )
        
        chain = prompt | self.llm 

        output =  chain.invoke({
            "objective": objective,
        })
        return output
        
    @log_timer
    async def filter_papers(self, papers,objective):
        """Analyze multiple papers sequentially and return structured summaries"""

        try:
            filter_results = []
            relevant_results = []

            obj_questions = self.obj_questions(objective)

            tasks = [self.proccess_with_semaphore(self.filter_single_paper, 
                    p, obj_questions.content) for p in papers]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            

            for i, result in enumerate(results):
                paper = papers[i]

                if isinstance(result, Exception):
                    logger.exception("An exception happend while screening paper: error {}, paper{}".format(str(result),paper.metadata["title"]))
                    console.print("[red]Error: An exception happend while screening paper titled {}".format(paper.metadata["title"]))
                    filter_results.append({
                        "error": str(result),
                        "file": paper.metadata["title"]
                    })
                    continue

                result_dict = result.dict() if hasattr(result, "dict") else result

                result_dict["pmc"] = paper.metadata["pmc"]
                result_dict["url"] = paper.metadata["url"]
                result_dict["title"] = paper.metadata["title"]
                result_dict["Author"] = paper.metadata["first_author"]
                result_dict["year"] = paper.metadata["year"]
                result_dict["journal"] = paper.metadata["journal"]

                filter_results.append(result_dict)

                if result_dict.get("relevant") is True:
                    relevant_results.append(paper)
                else:
                    logger.info(f"Abstract not relevant. Skipping paper: {paper.metadata.get('title', paper)}")
                    console.print(f"[yellow]Warning: Abstract doesn't match. Skipping paper:", paper.metadata.get("title", paper))

            return filter_results, relevant_results
    
        except Exception as e:
            logger.exception("Error during filtering papers: error: {}".format(str(e)))
            console.print(f"[red]Error during filtering papers")
            return {
                "error": str(e),
            }
        
    @log_timer
    async def meta_analysis(self, papers):
        try:
            tasks = [self.proccess_with_semaphore(self.meta_analysis_single, p) for p in papers]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            final_results = []
            for i, result in enumerate(results):
                paper = papers[i]

                if isinstance(result, Exception):
                    logger.exception("An exception happend while meta analyzing paper: error {}, paper{}".format(str(result),paper.metadata["title"]))
                    console.print("[red]Error: An exception happend while analyzing paper titled {}".format(paper.metadata["title"]))
                    final_results.append({
                        "error": str(result),
                        "file": paper.metadata["title"]
                    })
                    continue

                result_dict = result.dict() if hasattr(result, "dict") else result

                result_dict["pmc"] = paper.metadata["pmc"]
                result_dict["url"] = paper.metadata["url"]
                result_dict["title"] = paper.metadata["title"]
                result_dict["Author"] = paper.metadata["first_author"]
                result_dict["year"] = paper.metadata["year"]
                result_dict["journal"] = paper.metadata["journal"]

                final_results.append(result_dict)

            return final_results
        except Exception as e:
            logger.exception("Error during meta-analysis: Error {}".format(str(e)))
            console.print(f"[red]Error during meta-analysis")
            return {"error": str(e)}
    @log_timer   
    async def systematic_review(self, papers):
        try:
            tasks = [self.proccess_with_semaphore(self.systematic_review_single, p) for p in papers]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            final_results = []
            for i, result in enumerate(results):
                paper = papers[i]

                if isinstance(result, Exception):
                    logger.exception("An exception happend while analyzing paper: error {}, paper{}".format(str(e),paper.metadata["title"]))
                    console.print("[red]Error: An exception happend while analyzing paper titled {}".format(paper.metadata["title"]))
                    final_results.append({
                        "error": str(result),
                        "file": paper.metadata["title"]
                    })
                    continue

                result_dict = result.dict() if hasattr(result, "dict") else result

                existing_meta = result_dict.get("meta_data", {})
                new_meta = dict(list(paper.metadata.items())[:-1])

                existing_meta.update(new_meta)
                result_dict["meta_data"] = existing_meta

                final_results.append(result_dict)

            return final_results
        except Exception as e:
            logger.exception("Error during systematic review: error: {}".format(str(e)))
            console.print("[red]Error during systematic review")
            return {"error": str(e)}

    
    
       