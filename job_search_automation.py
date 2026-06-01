import pandas as pd
import time
import subprocess
import re
from jobspy import scrape_jobs

def run_pipeline():
    print("Starting automation pipeline...")

    # 1. Scraping LinkedIn
    job_titles = ["Researcher", "Consultant", "Manager", "Specialist", "Programme Manager", "Project Manager"]
    locations = ["Bonn, Germany", "Freiburg im Breisgau, Germany", "Frankfurt, Germany", "Basel, Switzerland"]
    all_linkedin = []

    for loc in locations:
        for title in job_titles:
            try:
                jobs = scrape_jobs(site_name=["linkedin"], search_term=title, location=loc, results_wanted=10, distance=50, job_type="fulltime")
                if not jobs.empty:
                    jobs = jobs[['title', 'company', 'location', 'job_url', 'date_posted']]
                    jobs['source'] = 'LinkedIn'
                    all_linkedin.append(jobs)
                time.sleep(5)
            except Exception as e: print(f"Error LinkedIn: {e}")

    # 2. Scraping UNJobs
    un_jobs = []
    search_urls = ["https://unjobs.org/duty_stations/germany", "https://unjobs.org/duty_stations/switzerland"]
    for url in search_urls:
        res = subprocess.run(['curl', '-s', '-L', '-A', 'Mozilla/5.0', url], capture_output=True, text=True)
        matches = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', res.stdout)
        for link, title_html in matches:
            title = re.sub('<[^<]+?>', '', title_html).strip()
            if any(kw in title.lower() for kw in ["research", "consultant", "manager"]):
                un_jobs.append({'title': title, 'company': 'UN Agency', 'location': 'International', 'job_url': f"https://unjobs.org{link}", 'source': 'UNJobs.org'})

    # 3. Combine and Save
    df1 = pd.concat(all_linkedin) if all_linkedin else pd.DataFrame()
    df2 = pd.DataFrame(un_jobs)
    combined = pd.concat([df1, df2]).drop_duplicates(subset=['job_url'])
    combined.to_excel('Latest_Job_Report.xlsx', index=False)
    print(f"Success! Saved {len(combined)} jobs.")

if __name__ == '__main__':
    run_pipeline()
