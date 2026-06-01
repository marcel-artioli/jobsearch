import pandas as pd
import time
import subprocess
import re
import os
import smtplib
from email.message import EmailMessage
from jobspy import scrape_jobs

# Your Profile for Matching
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
    sender = os.environ.get('cecelartioli10@gmail.com')
    pwd = os.environ.get('$Chulum8&rg&r89')
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
    # (Placeholder for the scraping logic previously defined)
    # After combined_jobs is created:
    # combined_jobs['match_score'] = combined_jobs.apply(calculate_match, axis=1)
    # combined_jobs = combined_jobs.sort_values('match_score', ascending=False)
    # combined_jobs.to_excel('Latest_Job_Report.xlsx', index=False)
    
    if os.path.exists('Latest_Job_Report.xlsx'):
        send_email('Latest_Job_Report.xlsx')

if __name__ == '__main__':
    run_pipeline()
