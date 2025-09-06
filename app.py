import streamlit as st
import pandas as pd
import scraper

st.title("📄 Job Scraper Dashboard")

resume_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

if resume_file:
    microsoft_data_df = pd.read_csv('microsoft_scraped_jobs.csv',
                 low_memory=False)
    ibm_data_df = pd.read_csv('all_ibm_jobs.csv',
                    low_memory=False)

    with open("temp_resume.pdf", "wb") as f:
        f.write(resume_file.read())
    resume_text = scraper.extract_text_from_pdf("temp_resume.pdf")

    companies = ["Microsoft", "IBM", "Oracle", "Adobe"]
    selected_companies = []
    st.subheader("Select Companies")
    for comp in companies:
        if st.checkbox(comp):
            selected_companies.append(comp)

    if st.button("Run Scraper"):
        if not selected_companies:
            st.warning("Please select at least one company.")
        else:
            for company in selected_companies:
                data_df_new = scraper.run_scraper(resume_text, company)
                st.subheader(company)

                st.success(f"✅ Scraping done! {len(data_df_new)} total jobs found.")
                # data_df_new['Job Page'] = data_df_new['Job Page'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
                # st.markdown(data_df_new.to_html(escape=False), unsafe_allow_html=True)
                st.dataframe(
                    data_df_new,
                    column_config={
                        "Job Page": st.column_config.LinkColumn("Job Link")
                    },
                    height=300  # Height of scrollable box
                )