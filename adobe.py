import re
import json
import requests
from datetime import datetime, date, time
import os
from dotenv import load_dotenv
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction import text
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

all_jobs=pd.read_csv('all_adoobe_jobs.csv')

# def matcher(jobs_skills, resume_text):
#     if resume_text is None or not jobs_skills:
#         return 0
    
#     def clean(text):
#         text = re.sub(r'[^a-zA-Z0-9\s\+\#]', ' ', text.lower())
#         return " ".join([w for w in text.split() if len(w)>2])
    
#     resume_clean = clean(resume_text)
#     job_clean = clean(jobs_skills)
    
#     stop_words = set(text.ENGLISH_STOP_WORDS)
#     extra_stopwords = {
#         "experience", "skills", "knowledge", "responsibilities",
#         "ability", "requirements", "must", "preferred",
#         "proficient", "understanding", "good", "excellent"
#     }
#     custom_stopwords = stop_words.union(extra_stopwords)

#     resume_words = set(resume_clean.split()) - custom_stopwords
#     job_words = set(job_clean.split())

#     print(job_words)

#     common_keywords = resume_words & job_words
#     match_percent = round(len(common_keywords) / len(job_words) * 100, 2) if job_words else 0

#     print("\n🧠 Match Score:", match_percent, "%")
#     return len(common_keywords)

import json

def matcher(resume_text, job_text):
    prompt = f"""
    You are a job-matching assistant.
    Resume:
    {resume_text}

    Job Skills:
    {job_text}

    Task:
    - Give a match percentage (0–100).
    - List missing skills.
    - Summarize strengths.
    Respond in JSON only with this schema:
        {{
          "match": <int>,
          "missing_skills": [<string>],
          "strengths": [<string>]
        }}
    """
    
    config = {
        "responseMimeType" : "application/json"
    }

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents=prompt,
        config=config
    )

    raw = response.text

    try:
        result = json.loads(raw)
        print("\n🧠 Match Score:", result['match'])
        return result['match']
    except json.JSONDecodeError:
        return "Failed, try again"

def adobe_scraper(data_df=all_jobs, resume_text=None):
    if not os.path.exists('all_adoobe_jobs.csv') or os.stat('all_adoobe_jobs.csv').st_size == 0:
        all_jobs = pd.DataFrame()
    else:
        all_jobs=pd.read_csv('all_adoobe_jobs.csv')

    if all_jobs.empty:
        lastDate = date(2003, 5, 20)
        lastTime = time(0, 0, 0, 0)
    else:
        lastDate = datetime.fromisoformat(all_jobs['postedDate'].iloc[0]).date()
        lastTime = datetime.fromisoformat(all_jobs['postedDate'].iloc[0]).time()

    tdatetime = datetime.now().isoformat()
    tdate = datetime.fromisoformat(tdatetime).date()
    ttime = datetime.fromisoformat(tdatetime).time()

    data=[]

    start=0
    while (tdate-lastDate).days>0 or (ttime>lastTime):
        url = f"https://careers.adobe.com/us/en/search-results?from={start}&s=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        }
        html = requests.get(url, headers=headers).text

        pattern = r'phApp\.ddo\s*=\s*(\{.*?\});'
        match = re.search(pattern, html, re.S)

        if match:
            json_str = match.group(1)
            ndata = json.loads(json_str)['eagerLoadRefineSearch']['data']['jobs']
            if not ndata:
                break
            # tot = json.loads(json_str)['eagerLoadRefineSearch']['totalHits']
            # print(data.keys())
        else:
            print("phApp.ddo not found")

        for item in ndata:
            dt = datetime.fromisoformat(item['postedDate']).date()
            t = datetime.fromisoformat(item['postedDate']).time()
            if (tdate-dt).days>7 or (dt-lastDate).days<0:
                continue
            if (dt-lastDate).days==0 and t<=lastTime:
                continue
            
            data.append(item)

        start+=10

    new_ext_jobs = pd.DataFrame(data)
    if not new_ext_jobs.empty:
        all_jobs = pd.concat([new_ext_jobs, all_jobs], ignore_index=True)
        all_jobs.sort_values(by='postedDate', ascending=False, inplace=True)
        date2 = datetime.fromisoformat(all_jobs['postedDate'].iloc[-1]).date()
        while (tdate-date2).days > 7:
            all_jobs = all_jobs[:-1]
            date2 = datetime.fromisoformat(all_jobs['postedDate'].iloc[-1]).date()
        all_jobs.to_csv('all_adoobe_jobs.csv', index=False)

    job_data = []

    for item in all_jobs.itertuples(index=False):
        try:
            match = matcher(item, resume_text)
            if(match>50):
                job_data.append({ "Date Posted" : item.postedDate, 
                            "Job ID": item.jobId, 
                            "Title": item.title,
                            "Job Page": item.applyUrl,
                            "relevance": match})
        except:
            print(f"Not Found: {html}")
            continue

    return job_data