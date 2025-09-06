import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from datetime import date as dt
import microsoft
import ibm
import adobe
import pdfplumber
from PIL import Image
import pytesseract
import re
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

microsoft_data_df = pd.read_csv('microsoft_scraped_jobs.csv',
                 low_memory=False)
ibm_data_df = pd.read_csv('all_ibm_jobs.csv',
                 low_memory=False)
adobe_data_df = pd.read_csv('all_adoobe_jobs.csv',
                            low_memory=False)

pdf_path = 'Animesh_Combined_resume_2a.pdf'
resume_text = extract_text_from_pdf(pdf_path=pdf_path)
resume_text

companies = ["Microsoft", "IBM", "Oracle", "Adobe"]

def run_scraper(resume_text, company):
    print(company)
    if company == 'Microsoft':
        jobs_data = microsoft.microsoft_scraper(microsoft_data_df, resume_text)

        jobs_df = pd.DataFrame(jobs_data)
        # print(jobs_df)

        data_df_ms = pd.concat([microsoft_data_df, jobs_df], ignore_index=True)
        data_df_ms.sort_values(by="Date Posted", ascending=False, inplace=True)
        date1 = datetime.fromisoformat(datetime.now().isoformat()).date()
        date2 = datetime.fromisoformat(data_df_ms['Date Posted'].iloc[-1]).date()
        while (date1-date2).days > 7:
            data_df_ms = data_df_ms[:-1]
            date2 = datetime.fromisoformat(data_df_ms['Date Posted'].iloc[-1]).date()
        data_df_ms.to_csv("microsoft_scraped_jobs.csv", index=False)
        return data_df_ms
        
    if company == 'IBM':
        jobs_data = ibm.ibm_scraper(ibm_data_df, resume_text)
        jobs_df = pd.DataFrame(jobs_data)
        ibm_rel_df = pd.read_csv("relevant_ibm_jobs.csv", low_memory=False)
        data_df_ibm = pd.concat([ibm_rel_df, jobs_df], ignore_index=True)
        data_df_ibm.sort_values(by="Date Posted", ascending=False, inplace=True)
        date1 = int(dt.today().strftime("%Y%m%d"))
        date2 = int(data_df_ibm['Date Posted'].iloc[-1].replace("-", ""))
        while date1-date2 > 7:
            data_df_ibm = data_df_ibm[:-1]
            date2 = int(data_df_ibm['Date Posted'].iloc[-1].replace("-", ""))
        data_df_ibm.to_csv("relevant_ibm_jobs.csv", index=False)
        return data_df_ibm
    
    if company == "Adobe":
        jobs_data = adobe.adobe_scraper(adobe_data_df, resume_text)
        jobs_data = pd.DataFrame(jobs_data)
        return jobs_data

    return f"{company} not found"
        