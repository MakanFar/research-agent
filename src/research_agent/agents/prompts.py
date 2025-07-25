

class PromptManager:


    @staticmethod
    def meta_analysis_prompt():
       
         return   """
            You are an expert at analyzing academic papers. Extract meta data accurately. Be thorough and precise in your analysis.
            
            Don't add any knowledge from yourself. Only rely on the information provided in the paper.
            Be thorough and precise in your analysis.
            Write the results concisely.
            Look for information in all sections.
            If information is not found in the paper, return "unknown", but only after a thorough search.
            Return JSON in the specified format:
            {format_instructions}

            Here is the paper:
            {paper}
            """
    

    def systematic_review_prompt():
       
         return   """
            You are an expert at analyzing academic papers. Extract both meta-data and in-depth information about the paper accurately. Be thorough and precise in your analysis, look for information in all sections, and write the results concisely.

            Only for meta-data:
            Don't add any knowledge from yourself. Only rely on the information provided in the paper.            
            If information is not found in the paper, return "unknown", but only after a thorough search.

            Only for in-depth infromation:
            If a something is not directly discussed, try to infer it based on:
                - Study design
                - Data characteristics (e.g., number of samples, single vs. multi-institution)
                - Methods (e.g., only internal validation, no explainability technique)
                - Evaluation metrics (e.g., no external AUC reported)
            If there is not enough information to confirm or deny, label it as "unknown".
            Your goal is to evaluate quality and completeness of the study, not just extract what is reported.

            Return a JSON object with two main sections: "meta_data" and "in_depth" with these fields:

            {format_instructions}

            Here is the paper:
            {paper}
            """

    def filter_prompt():
       
         return   """
            You are an expert research assistant helping a researcher find the most relevant academic papers for a specific research goal. Your job is to analyze paper abstracts and titles and decide whether they are relevant to the user's objective.

            Instructions:
            - Carefully read the user's objective and the abstract.
            - Determine whether the abstract is highly relevant to the user's stated goal.
            - Be strict and conservative in your judgment—only return True if the abstract clearly aligns with the research objective.
            - Do not make assumptions beyond what's written in the abstract.

            You will be given an abstract of a scientific paper. Your task is to analyze it carefully and answer the following:
            ### Questions:
            {questions}

            ### Final Decision:
            Based on your answers above, decide:
            *Does this paper meet the criteria?** 

            - Return a JSON object like this:
            {format_instructions}

            Here is the paper:
            {paper}
            """
    
    def generate_objective_prompt():
                
                return """
                {objective}

                Based on the objective described above, generate 5 questions for an expert research assistant tasked with answering them after reading a paper.
                Generate only questions. Nothing else!
                Generate only 5 questions.
                Each question should be phrased so it can be answered with Yes or No.
                You may also include an example for each question ONLY if it helps clarify what the question is asking.

                Here is an example of an objective and how the questions should look like:

                        Objective:
                        Review on AI in veterinary medicine diagnstics.

                        Questions:

                        1. **Is this a primary research paper?** (Yes/No)  
                        *Exclude reviews, editorials, perspectives, books, theses, and non-research papers.*

                        2. **Does the study apply AI (machine learning, deep learning, or related techniques)?** (Yes/No)

                        3. **Is the goal of the AI application focused on**:
                        - Diagnosis of a disease?
                        - Prediction of a disease outcome?
                        - Classification of disease type or severity?
                        *(Answer Yes only if at least one of these is the focus)*

                        4. **Is the focus clearly on veterinary medicine (i.e., animals like dogs, cats, cattle, horses, etc.)?** (Yes/No)
                
                """
    
   
    