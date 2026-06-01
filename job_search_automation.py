import pandas as pd
import time
import subprocess
import re
import os
import smtplib
from email.message import EmailMessage
from jobspy import scrape_jobs

# 1. Your Profile for Matching
MY_PROFILE = {
    'education': ['PhD', 'Master', 'International Relations', 'Governance'],
    'skills': ['Research', 'Environmental Policy', 'Policy Analysis', 'German B1'],
    'keywords': ['Climate', 'Sustainability', 'Foreign Policy', 'Development']
}

def calculate_match(row):
    score = 0
    text = f"{row['title']} {row.get('location', '')}".lower()
    for edu in MY_PROFILE['education']: 
        if edu.lower() in text: score += 3
    for kw in MY_PROFILE['keywords'] + MY_PROFILE['skills']:
        if kw.lower() in text: score += 1
    return score

def send_email(file_path):
    sender = os.environ.get('EMAIL_USER')
    pwd = os.environ.get('EMAIL_PASSWORD')
    if not sender or not pwd: return

    msg = EmailMessage()
    msg['Subject'] = f'Job Search: Match Report {pd.Timestamp.now().date()}'
    msg['From'] = sender
    msg['To'] = sender
    msg.set_content("Attached is your 4-day automated job report, ranked by your professional skills.")

    with open(file_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=file_path)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, pwd)
        smtp.send_message(msg)

def run_pipeline():
    print("Starting Scraper...")
    job_titles = ["Researcher", "Consultant", "Manager", "Specialist"]
    locations = ["Bonn, Germany", "Freiburg, Germany", "Basel, Switzerland"]
    all_jobs = []

    # Scrape LinkedIn
    for loc in locations:
        for title in job_titles:
            try:
                jobs = scrape_jobs(site_name=["linkedin"], search_term=title, location=loc, results_wanted=5, distance=50)
                if not jobs.empty:
                    all_jobs.append(jobs)
                time.sleep(2)
            except Exception: continue

    if all_jobs:
        df = pd.concat(all_jobs, ignore_index=True)
        df['match_score'] = df.apply(calculate_match, axis=1)
        df = df.sort_values('match_score', ascending=False)
        
        # Generate the missing file
        file_name = 'Latest_Job_Report.xlsx'
        df.to_excel(file_name, index=False)
        
        # Send it
        send_email(file_name)
        print(f"Pipeline finished. File {file_name} created and emailed.")
    else:
        print("No jobs found during this run.")

if __name__ == '__main__':
    run_pipeline()
