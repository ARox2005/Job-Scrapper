import requests
from datetime import datetime
from datetime import date as dt
import pandas as pd
import re
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction import text
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

data_df = pd.read_csv('all_ibm_jobs.csv',
                 low_memory=False)

def all_jobs_quals_extract(data):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    quals = []

    for job in data:
        driver.get(job['_source']['url']) 
        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        field_label_ed = soup.find("div", class_="article__content__view__field__label", string=re.compile(r"Required education", re.I))
        field_label_tech = soup.find("div", class_="article__content__view__field__label", string=re.compile(r"Required technical and professional expertise", re.I))
        if field_label_ed:
            value_div_ed = field_label_ed.find_next("div", class_="article__content__view__field__value")
            # if value_div:
            print(value_div_ed.get_text(strip=True, separator="\n"))
        if field_label_tech:
            value_div_tech = field_label_tech.find_next("div", class_="article__content__view__field__value")
            # if value_div:
            print(value_div_tech.get_text(strip=True, separator="\n"))

        if value_div_ed and value_div_tech:
            quals.append({
                "Date Posted": job['_source']['dcdate'], 
                "Job Name": job['_source']['title'], 
                "Required Education": value_div_ed, 
                "Required Skills": value_div_tech,
                "Job Link": job['_source']['url']})
        elif value_div_tech and not value_div_ed:
            quals.append({
                "Date Posted": job['_source']['dcdate'], 
                "Job Name": job['_source']['title'], 
                "Required Education": None, 
                "Required Skills": value_div_tech,
                "Job Link": job['_source']['url']})

    driver.quit()
    return quals

def matcher(resume_text, job_ed_html, job_html):
    if job_ed_html:
        soup = BeautifulSoup(job_ed_html, "html.parser")
        job_ed = soup.get_text(separator=" ")
    soup = BeautifulSoup(job_html, "html.parser")
    job_description = soup.get_text(separator=" ")

    def clean(text_input):
        text_input = text_input.lower()
        text_input = re.sub(r'[^a-z0-9\s\+\#]', ' ', text_input)
        return " ".join([w for w in text_input.split() if len(w) > 2])

    resume_clean = clean(resume_text)
    job_ed_clean = clean(job_ed)
    job_clean = clean(job_description)

    degree_keywords = [
        "btech", "b.tech", "bachelor", "bachelors", "b.sc", "bsc", "be", "mtech",
        "m.tech", "master", "msc", "m.sc", "phd", "doctorate", "associate", "none", None
    ]

    resume_lower = resume_clean.lower()
    job_lower = job_ed_clean.lower()

    meets_education = any(kw in resume_lower for kw in degree_keywords) and \
                    any(kw in job_lower for kw in degree_keywords)

    print("✅ Meets education requirement:", meets_education)

    stop_words = set(text.ENGLISH_STOP_WORDS)
    extra_stopwords = {
        "experience", "skills", "knowledge", "responsibilities",
        "ability", "requirements", "must", "preferred",
        "proficient", "understanding", "good", "excellent"
    }
    custom_stopwords = stop_words.union(extra_stopwords)

    if not meets_education:
        match_percent = 0.0
        common_keywords = None
        return 0
    else:
        vectorizer = TfidfVectorizer(stop_words=list(custom_stopwords))
        vectors = vectorizer.fit_transform([resume_clean, job_clean])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        match_percent = round(similarity * 100, 2)

        resume_words = set(resume_clean.split()) - custom_stopwords
        job_words = set(job_clean.split()) - custom_stopwords
        common_keywords = sorted(resume_words & job_words)

    print("\n🧠 Match Score:", match_percent, "%")
    return len(common_keywords)

def ibm_scraper(data_df=data_df, resume_text=None):
    url = 'https://www-api.ibm.com/search/api/v2'
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    payload ={"appId":"careers","scopes":["careers2"],"query":{"bool":{"must":[]}},"aggs":{"field_keyword_172":{"filter":{"match_all":{}},"aggs":{"field_keyword_17":{"terms":{"field":"field_keyword_17","size":6}},"field_keyword_17_count":{"cardinality":{"field":"field_keyword_17"}}}},"field_keyword_083":{"filter":{"match_all":{}},"aggs":{"field_keyword_08":{"terms":{"field":"field_keyword_08","size":6}},"field_keyword_08_count":{"cardinality":{"field":"field_keyword_08"}}}},"field_keyword_184":{"filter":{"match_all":{}},"aggs":{"field_keyword_18":{"terms":{"field":"field_keyword_18","size":6}},"field_keyword_18_count":{"cardinality":{"field":"field_keyword_18"}}}},"field_keyword_055":{"filter":{"match_all":{}},"aggs":{"field_keyword_05":{"terms":{"field":"field_keyword_05","size":1000}},"field_keyword_05_count":{"cardinality":{"field":"field_keyword_05"}}}}},"size":100,"from":0,"sort":[{"dcdate": "desc"}, {"_score":"desc"}],"lang":"zz","localeSelector":{},"p":"2","sm":{"query":"","lang":"zz"},"_source":["_id","title","url","dcdate","description","language","entitled","field_keyword_17","field_keyword_08","field_keyword_18","field_keyword_19"]}

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Preview:", response.text[:300])

    data = []
    date3 = int(data_df['Date Posted'][0].replace("-", ""))
    date1 = int(response.json()['hits']['hits'][0]['_source']['dcdate'].replace("-", ""))
    date2 = int(response.json()['hits']['hits'][0]['_source']['dcdate'].replace("-", ""))
    print(date1, date2, date3)

    # total_data = int(response.json()['hits']['total']["value"])
    i=0
    while date2>date3 and date1-date2<=7 and date1-date2>=0:
        payload ={"appId":"careers","scopes":["careers2"],"query":{"bool":{"must":[]}},"aggs":{"field_keyword_172":{"filter":{"match_all":{}},"aggs":{"field_keyword_17":{"terms":{"field":"field_keyword_17","size":6}},"field_keyword_17_count":{"cardinality":{"field":"field_keyword_17"}}}},"field_keyword_083":{"filter":{"match_all":{}},"aggs":{"field_keyword_08":{"terms":{"field":"field_keyword_08","size":6}},"field_keyword_08_count":{"cardinality":{"field":"field_keyword_08"}}}},"field_keyword_184":{"filter":{"match_all":{}},"aggs":{"field_keyword_18":{"terms":{"field":"field_keyword_18","size":6}},"field_keyword_18_count":{"cardinality":{"field":"field_keyword_18"}}}},"field_keyword_055":{"filter":{"match_all":{}},"aggs":{"field_keyword_05":{"terms":{"field":"field_keyword_05","size":1000}},"field_keyword_05_count":{"cardinality":{"field":"field_keyword_05"}}}}},"size":100,"from":i,"sort":[{"dcdate": "desc"}, {"_score":"desc"}],"lang":"zz","localeSelector":{},"p":"2","sm":{"query":"","lang":"zz"},"_source":["_id","title","url","dcdate","description","language","entitled","field_keyword_17","field_keyword_08","field_keyword_18","field_keyword_19"]}

        response = requests.post(url, headers=headers, json=payload)

        print("Status:", response.status_code)
        print("Content-Type:", response.headers.get("Content-Type"))
        print("Preview:", response.text[:300])

        newdata = response.json()['hits']['hits']
        for items in newdata:
            date2 = int(items['_source']['dcdate'].replace("-", ""))
            print(date1, date2, date3)
            if date2<date3 or date1-date2<0 or date1-date2>7:
                break
            if(date1-date2<=7):
                data.append(items)
        
        i+=100
    
    # print(data)
    quals = all_jobs_quals_extract(data)

    all_jobs = pd.DataFrame(quals)
    data_ibm_alljobs = pd.concat([all_jobs, data_df], ignore_index=True)
    data_ibm_alljobs.sort_values(by="Date Posted", ascending=False, inplace=True)
    date1 = int(dt.today().strftime("%Y%m%d"))
    date2 = int(data_ibm_alljobs['Date Posted'].iloc[-1].replace("-", ""))
    while date1-date2 > 7:
        data_ibm_alljobs = data_ibm_alljobs[:-1]
        date2 = int(data_ibm_alljobs['Date Posted'].iloc[-1].replace("-", ""))
    data_ibm_alljobs.to_csv('all_ibm_jobs.csv', index=False)

    relevant_data = []

    for items in quals:
        date = items['Date Posted']
        title = items['Job Name']
        job_ed_html = str(items['Required Education'])
        job_html = str(items["Required Skills"])
        url = items["Job Link"]
        try:
            match = matcher(resume_text, job_ed_html, job_html)
            if(match>5):
                relevant_data.append({ "Date Posted" : date, 
                            "Title": title,
                            "Job Page": url,
                            "relevance": match})
        except:
            print(f"Not Found: {job_html}")
            continue

    return relevant_data
