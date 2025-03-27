# -*- coding: utf-8 -*-
"""InformationRetrieval.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fAWm86TYwW8HfZMNQxQUzPO3UEr49-uX
"""

#Clean and prepare both sets
clean_entities = [e.strip().lower() for e in entities]
clean_expanded_terms = [e.strip().lower() for e in final_expanded_terms]

#Create the PubMed query, original entitiy to use AND terms, to prioritise the import terms
mandatory_query = " AND ".join(clean_entities)

#Add expanded terms to broaden add them as "OR", these will help expand API
optional_query = " OR ".join(clean_expanded_terms)

#Final query combining both for mandatory and optional terms
final_pubmed_query = f"({mandatory_query}) AND ({optional_query})"

#Final formatted query ready for PubMed API request
print("Formatted PubMed Query:", final_pubmed_query)

import requests

#Define the PubMed query with the free full text filter
final_pubmed_query = final_pubmed_query + " AND \"free full text\"[filter]"

#PubMed E-utilities URL for the search
pubmed_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

#Define the parameters for the request
params = {
    'db': 'pubmed',
    'term': final_pubmed_query,
    'retmax': '15',
    'usehistory': 'y'
}

#Make the request to PubMed
response = requests.get(pubmed_url, params=params)

#Check if the request was successful
if response.status_code == 200:
    # Parse the XML response to get the PubMed IDs
    from xml.etree import ElementTree
    root = ElementTree.fromstring(response.text)

    #Extract the list of PubMed IDs
    pmids = [id.text for id in root.findall(".//Id")]

    #Print the PubMed IDs of the articles
    print("PubMed IDs of the articles:", pmids)
else:
    print(f"Error retrieving data from PubMed: {response.status_code}")

import requests
import xml.etree.ElementTree as ET

#Function to convert pmids to PMCS
def get_pmcid_from_pmid(pmid):
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=my_tool&email=myemail@example.com&ids={pmid}"
    response = requests.get(url)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        record = root.find("record")
        if record is not None and "pmcid" in record.attrib:
            return record.attrib["pmcid"]
    return None

pmid_list = pmids
pmc_ids = {pmid: get_pmcid_from_pmid(pmid) for pmid in pmid_list}

print("PMID to PMCID Mapping:", pmc_ids)

from Bio import Entrez
import xml.etree.ElementTree as ET

# NCBI Entrez API
Entrez.email = "your_email@example.com"

def get_free_full_text_links(pmid_list):
    """Fetches free full-text links for a list of PubMed IDs."""
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    free_links = {}

    for pmid in pmid_list:
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="text")
            records = handle.read()
            handle.close()

            #Convert bytes to string if needed
            if isinstance(records, bytes):
                records = records.decode("utf-8")

            #Parse XML
            root = ET.fromstring(records)

            #Look for PubMedCentral (PMC) ID
            pmc_link = None
            for article_id in root.findall(".//ArticleIdList/ArticleId"):
                if article_id.get("IdType") == "pmc":
                    pmc_link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id.text}/"
                    break

            #Look for DOI
            doi_link = None
            for article_id in root.findall(".//ArticleIdList/ArticleId"):
                if article_id.get("IdType") == "doi":
                    doi_link = f"https://doi.org/{article_id.text}"
                    break

            #Decide which link to use
            if pmc_link:
                free_links[pmid] = pmc_link
            elif doi_link:
                free_links[pmid] = doi_link
            else:
                free_links[pmid] = f"No free full-text link found. Check manually: {base_url}{pmid}/"

        except Exception as e:
            free_links[pmid] = f"Error fetching data: {str(e)}"

    return free_links

#Example usage
#pmid_list =
full_text_links = get_free_full_text_links(pmids)

#Print results
for pmid, link in full_text_links.items():
    print(f"PMID: {pmid} -> {link}")

import requests
import os

#Function to download a PDF given a URL with headers
def download_pdf(url, file_name):
    """Downloads a PDF from the given URL and saves it to a file."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        #Save the content as a PDF file
        with open(file_name, 'wb') as f:
            f.write(response.content)

        print(f"Downloaded {file_name} successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

def get_free_full_text_links_and_download(pmid_list):
    """Fetches free full-text links for PubMed IDs and downloads PDFs if available."""
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    free_links = {}

    for pmid in pmid_list:
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="text")
            records = handle.read()
            handle.close()

            #Convert bytes to string if needed
            if isinstance(records, bytes):
                records = records.decode("utf-8")

            #Parse XML
            root = ET.fromstring(records)

            #Look for PubMedCentral (PMC) ID
            pmc_link = None
            for article_id in root.findall(".//ArticleIdList/ArticleId"):
                if article_id.get("IdType") == "pmc":
                    pmc_link = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{article_id.text}/pdf/"
                    break

            #Look for DOI
            doi_link = None
            for article_id in root.findall(".//ArticleIdList/ArticleId"):
                if article_id.get("IdType") == "doi":
                    doi_link = f"https://doi.org/{article_id.text}"
                    break

            #Decide which link to use
            if pmc_link:
                free_links[pmid] = pmc_link
                pdf_filename = f"{pmid}_article.pdf"
                download_pdf(pmc_link, pdf_filename)
            elif doi_link:
                free_links[pmid] = doi_link
                print(f"DOI link found for {pmid}, but no PDF download implemented for DOI links.")
            else:
                free_links[pmid] = f"No free full-text link found. Check manually: {base_url}{pmid}/"

        except Exception as e:
            free_links[pmid] = f"Error fetching data: {str(e)}"

    return free_links


pmid_list = pmids
full_text_links = get_free_full_text_links_and_download(pmid_list)

#Print results
for pmid, link in full_text_links.items():
    print(f"PMID: {pmid} -> {link}")