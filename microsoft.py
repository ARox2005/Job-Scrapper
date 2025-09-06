import requests
from datetime import datetime
import pandas as pd
import re
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction import text

data_df = pd.read_csv('microsoft_scraped_jobs.csv',
                 low_memory=False)

def html_extract(jobs):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        }

    quals_html = []

    for items in jobs:
        url = f"https://gcsservices.careers.microsoft.com/search/api/v1/job/{items['jobId']}?lang=en_us"

        response = requests.get(url, headers=headers)
        if response.headers.get("Content-Type") == "application/json":
            quals_html.append([items['postingDate'], items['jobId'], items['title'], response.json()['operationResult']['result']['qualifications']])

    return quals_html

def matcher(resume_text, job_html):
    if(resume_text!=None):
        soup = BeautifulSoup(job_html, "html.parser")
        job_description = soup.get_text(separator=" ")

        def clean(text):
            text = re.sub(r'[^a-zA-Z0-9\s\+\#]', ' ', text.lower())
            return " ".join([w for w in text.split() if len(w) > 2])

        resume_clean = clean(resume_text)
        job_clean = clean(job_description)

        stop_words = set(text.ENGLISH_STOP_WORDS)

        extra_stopwords = {
            "experience", "skills", "knowledge", "responsibilities",
            "ability", "requirements", "must", "preferred",
            "proficient", "understanding", "good", "excellent"
        }

        custom_stopwords = stop_words.union(extra_stopwords)
        vectorizer = TfidfVectorizer(stop_words=list(custom_stopwords))

        vectors = vectorizer.fit_transform([resume_clean, job_clean])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        match_percent = round(similarity * 100, 2)

        resume_words = set(resume_clean.split()) - custom_stopwords
        job_words = set(job_clean.split()) - custom_stopwords
        common_keywords = resume_words & job_words

        print("\n🧠 Match Score:", match_percent, "%")
        return len(common_keywords)
    
    return None

def microsoft_scraper(data_df=data_df, resume_text=None):
    url = "https://gcsservices.careers.microsoft.com/search/api/v1/search?l=en_us&pg=1&pgSz=20&o=Recent&flt=true"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Preview:", response.text[:300])
    if response.headers.get("Content-Type") == "application/json":
        latest_data = response.json()['operationResult']['result']['jobs']
    pg=0

    date1 = datetime.fromisoformat(data_df["Date Posted"][0])
    date2 = datetime.fromisoformat(latest_data[0]['postingDate'])

    print(date2.date(), date1.date())

    data = []
    while (date2.date()-date1.date()).days<=7 and (date2.date()-date1.date()).days>=0:
        pg+=1
        url = f"https://gcsservices.careers.microsoft.com/search/api/v1/search?l=en_us&pg={pg}&pgSz=20&o=Recent&flt=true"
        response = requests.get(url, headers=headers)

        print("Status:", response.status_code)
        print("Content-Type:", response.headers.get("Content-Type"))
        print("Preview:", response.text[:300])

        if response.headers.get("Content-Type") == "application/json":
            newdata = response.json()['operationResult']['result']['jobs']
            if not newdata:
                break
            for items in newdata:
                date2 = datetime.fromisoformat(items['postingDate'])
                if((date2.date()-date1.date()).days==0):
                    if(date2.time()<=date1.time()):
                        break
                if((date2.date()-date1.date()).days<0):
                    break
                data.append(items)

    quals_html = html_extract(data)

    job_data = []

    for items in quals_html:
        date = items[0]
        id = items[1]
        title = items[2]
        html = items[3]
        try:
            match = matcher(resume_text, html)
            if(match>5):
                job_data.append({ "Date Posted" : date, 
                            "Job ID": id, 
                            "Title": title,
                            "Job Page": f"https://jobs.careers.microsoft.com/global/en/job/{id}",
                            "relevance": match})
        except:
            print(f"Not Found: {html}")
            continue

    return job_data