AI powered Literature review tool in order to quickly summarise findings from multiple sources, compare key results, and understand complex relationships across studies.
The pipeline is currently split into 2 sections; NER and RAG, with a 3rd section for Claude integration on its way.
 
User queries are considered, expanded, and then relevant papers from PubMed and Semantic Scholar would be cached for RAG analysis and Claude integration for reasoning.
 
Section 1. Named Entity Recognition (NER)
Extracts the most relevant biological terms, attempts to understand biological relationships between terms so we can next expand search terms for PubMed API requests.
 
Section 2. Information Retrieval
Takes titles and PMIDs and processes them in order to get the relevant PDF’s.
