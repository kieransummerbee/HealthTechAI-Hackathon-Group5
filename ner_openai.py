# -*- coding: utf-8 -*-
"""NER-openai.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16Smv7dsjXP-RuGeufo62Xr3jKByzpu8U
"""

import openai
import requests

#OpenAI API key
openai.api_key = "INSERT API KEY"


#User query
text = "Acinetobacter lwoffii has been evolved in the lab to be resistant to which of these antibiotics."

#NER prompt
prompt = f"""
Extract all biomedical entities from the following text, including but not limited to: diseases, drugs, bacteria, antibiotic resistance, resistance mechanisms, genes, mutations, treatments, and related concepts.

The most important biomedical entity should be identified as the main subject (e.g., disease, organism, drug, gene, mutation) and should be included in the returned list of entities. If the primary entity is not recognized by the model, you should identify it based on the context and explicitly include it.

Additionally, extract any associated terms or concepts, including but not limited to: mutations, interactions, resistance mechanisms, genetic variations, and relationships between biomedical entities. When two or more terms appear together in a way that suggests they are conceptually related (e.g., a drug and its mechanism, a gene and its mutation, bacteria and antibiotic resistance), treat them as a single related entity.

Return a comma-separated list of entity names without descriptions.
"{text}"
"""

#API request
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # Use the chat model
    messages=[
        {"role": "system", "content": "You are a biomedical and research focused chat model"},
        {"role": "user", "content": prompt},
    ],
    max_tokens=200,
    temperature=0.5
)

#Parse the extracted entities into a set (lowercase for consistency)
entities = {e.strip().lower() for e in response['choices'][0]['message']['content'].strip().split(",")}
print("Extracted Entities:", entities)

#Store unique expanded terms
final_expanded_terms = set()

#Expanding terms for PubMedAPI to broaden search results
for entity in entities:
    expansion_prompt = f"""
    Given the extracted biomedical entity '{entity}', first check if this entity **forms a relationship** with any other extracted entity in the text. For example, if 'antibiotics' and 'resistance' appear together and form a **combined concept** like 'antibiotic resistance', treat them as a **single, combined entity**.

    If the entity forms a **relationship** with another entity (such as 'antibiotics' and 'resistance' forming 'antibiotic resistance'), expand **only the combined concept** by providing **exactly 5 distinct biologically relevant terms** (synonyms, related diseases, drugs, genes, etc.) that are **contextually appropriate** for the **combined concept**.

    If the entity does **not form a relationship** with any other entity, expand it **individually** and provide **5 distinct biologically relevant terms** (synonyms, related diseases, drugs, genes, etc.) that are **contextually appropriate** to the **single entity**.

    Ensure that the terms returned for any **combined concept** are **distinct** from those returned for individual entities.

    **Important**: If any expanded terms for an entity overlap with terms from any previously expanded entity (whether combined or individual), replace those overlapping terms with **new, distinct terms** that are **contextually relevant** but **do not repeat** from previously provided lists.

    Please return the output in the following **concise format**:
    - First, list the entity name.
    - Then, list the 5 expanded terms related to the entity, separated by commas.

    Do not include any extra text or explanations.
    """

    #openai API request
    expansion_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a biomedical and research focused chat model"},
            {"role": "user", "content": expansion_prompt},
        ],
        max_tokens=200,
        temperature=0.5
    )

    #Take expanded terms and clean up
    expanded_terms = expansion_response['choices'][0]['message']['content'].strip()

    #Remove unwanted characters, line breaks, or redundant entries
    expanded_terms = [term.strip().lower().replace('-', '').replace('\n', '') for term in expanded_terms.split(",")]

    # Add to the final set, to ensure there are no duplicates
    final_expanded_terms.update(expanded_terms)

#Clean up final terms by removing redundant terms
final_expanded_terms = {term.strip() for term in final_expanded_terms if term.strip()}

#Print expanded terms
print("Final unique expanded terms:", final_expanded_terms)