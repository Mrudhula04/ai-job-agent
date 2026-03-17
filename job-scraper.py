#!/usr/bin/env python3
"""
Real Job Scraper - Fetches actual job postings
"""

import json
import os
import re
import time
from datetime import datetime
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup

class JobScraper:
    def __init__(self):
        self.profile_file = "my_profile.json"
        self.jobs_file = "daily_jobs.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}
    
    def scrape_linkedin_jobs(self, profile):
        """Scrape LinkedIn job postings"""
        jobs = []
        role = profile.get('desired_role', 'Software Engineer')
        skills = ' '.join(profile.get('skills', [])[:2])
        location = profile.get('location', '')
        
        # LinkedIn job search URL with date filter (f_TPR=r86400 = past 24 hours)
        keywords = f"{role} {skills}"
        url = f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(keywords)}&location={quote_plus(location)}&f_TPR=r86400&sortBy=DD"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='base-card')[:10]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h3', class_='base-search-card__title')
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        location_elem = card.find('span', class_='job-search-card__location')
                        link_elem = card.find('a', class_='base-card__full-link')
                        
                        if title_elem and company_elem and link_elem:
                            # Try to get posting date
                            time_elem = card.find('time')
                            posted_date = time_elem.get('datetime', '') if time_elem else ''
                            
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else 'Remote',
                                'url': link_elem.get('href', ''),
                                'platform': 'LinkedIn',
                                'posted_date': posted_date
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"LinkedIn scraping error: {str(e)}")
        
        return jobs
    
    def scrape_indeed_jobs(self, profile):
        """Scrape Indeed job postings (last 24 hours)"""
        jobs = []
        role = profile.get('desired_role', 'Software Engineer')
        skills = ' '.join(profile.get('skills', [])[:2])
        location = profile.get('location', '')
        
        # Indeed with date filter (fromage=1 = last 1 day)
        keywords = f"{role} {skills}"
        url = f"https://www.indeed.com/jobs?q={quote_plus(keywords)}&l={quote_plus(location)}&fromage=1&sort=date"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='job_seen_beacon')[:10]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        company_elem = card.find('span', {'data-testid': 'company-name'})
                        location_elem = card.find('div', {'data-testid': 'text-location'})
                        
                        if title_elem:
                            link = title_elem.find('a')
                            if link and company_elem:
                                job_id = link.get('data-jk', '')
                                # Try to get posting date
                                date_elem = card.find('span', class_='date')
                                posted_date = date_elem.text.strip() if date_elem else 'Today'
                                
                                job = {
                                    'title': title_elem.text.strip(),
                                    'company': company_elem.text.strip(),
                                    'location': location_elem.text.strip() if location_elem else 'Remote',
                                    'url': f"https://www.indeed.com/viewjob?jk={job_id}",
                                    'platform': 'Indeed',
                                    'posted_date': posted_date
                                }
                                jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Indeed scraping error: {str(e)}")
        
        return jobs
    
    def search_google_jobs(self, profile):
        """Use Google to find job postings (last 24 hours)"""
        jobs = []
        role = profile.get('desired_role', 'Software Engineer')
        skills = profile.get('skills', [])[:2]
        
        # Search for specific job boards with date filter
        queries = [
            f"{role} {skills[0]} site:linkedin.com/jobs/view",
            f"{role} {skills[0]} site:wellfound.com",
            f"{role} {skills[0]} site:indeed.com/viewjob"
        ]
        
        for query in queries:
            try:
                # Add date filter: tbs=qdr:d (past day)
                url = f"https://www.google.com/search?q={quote_plus(query)}&num=5&tbs=qdr:d"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find search results
                    results = soup.find_all('div', class_='g')[:5]
                    
                    for result in results:
                        try:
                            link_elem = result.find('a')
                            title_elem = result.find('h3')
                            
                            if link_elem and title_elem:
                                url = link_elem.get('href', '')
                                if 'linkedin.com/jobs/view' in url or 'indeed.com/viewjob' in url or 'wellfound.com' in url:
                                    # Extract company from snippet
                                    snippet = result.find('div', class_='VwiC3b')
                                    company = 'Unknown'
                                    if snippet:
                                        text = snippet.text
                                        # Try to extract company name
                                        if ' at ' in text:
                                            company = text.split(' at ')[1].split('.')[0].strip()
                                    
                                    platform = 'LinkedIn' if 'linkedin' in url else 'Indeed' if 'indeed' in url else 'Wellfound'
                                    
                                    job = {
                                        'title': title_elem.text.strip(),
                                        'company': company,
                                        'location': 'See posting',
                                        'url': url,
                                        'platform': platform,
                                        'posted_date': 'Last 24 hours'
                                    }
                                    jobs.append(job)
                        except Exception as e:
                            continue
                
                time.sleep(2)  # Be respectful with requests
                
            except Exception as e:
                print(f"Google search error: {str(e)}")
                continue
        
        return jobs
    
    def display_jobs(self, all_jobs, profile):
        """Display formatted job listings"""
        print("\n" + "="*80)
        print(f"📅 DAILY JOB POSTINGS - {datetime.now().strftime('%B %d, %Y')}")
        print("="*80)
        
        print(f"\n👤 YOUR PROFILE:")
        print(f"   Role: {profile.get('desired_role')}")
        print(f"   Skills: {', '.join(profile.get('skills', [])[:4])}")
        print(f"   Location: {profile.get('location')}")
        
        if not all_jobs:
            print("\n⚠️  No jobs found. This could be due to:")
            print("   - Website blocking automated requests")
            print("   - Network issues")
            print("   - Need to use manual search")
            print("\n💡 Try running the manual search version instead:")
            print("   python3 job-finder-simple.py")
            return
        
        print(f"\n🎯 FOUND {len(all_jobs)} JOB POSTINGS:\n")
        
        for i, job in enumerate(all_jobs, 1):
            print(f"{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Platform: {job['platform']}")
            if job.get('posted_date'):
                print(f"   Posted: {job['posted_date']}")
            print(f"   🔗 {job['url']}")
            print()
        
        print("="*80)
        print("\n💡 NEXT STEPS:")
        print("   1. Click each link above to view full job details")
        print("   2. Apply to 3-5 jobs that match your profile")
        print("   3. Customize your resume for each application")
        print("   4. Track your applications in a spreadsheet\n")
    
    def save_jobs(self, jobs, profile):
        """Save jobs to JSON file"""
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "profile": {
                "role": profile.get('desired_role'),
                "skills": profile.get('skills'),
                "location": profile.get('location')
            },
            "jobs": jobs,
            "total_jobs": len(jobs)
        }
        
        with open(self.jobs_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def run(self):
        """Main execution"""
        print("\n🤖 AI Job Scraper Starting...")
        print(f"⏰ {datetime.now().strftime('%I:%M %p')}")
        
        profile = self.load_profile()
        if not profile:
            print("\n❌ Error: my_profile.json not found")
            return
        
        print("\n🔍 Searching for real job postings...")
        print("   📅 Filtering: Jobs posted in the last 24 hours only")
        print("   This may take 30-60 seconds...\n")
        
        all_jobs = []
        
        # Try Google search first (most reliable)
        print("   → Searching via Google...")
        google_jobs = self.search_google_jobs(profile)
        all_jobs.extend(google_jobs)
        
        # Try LinkedIn
        print("   → Searching LinkedIn...")
        linkedin_jobs = self.scrape_linkedin_jobs(profile)
        all_jobs.extend(linkedin_jobs)
        
        # Try Indeed
        print("   → Searching Indeed...")
        indeed_jobs = self.scrape_indeed_jobs(profile)
        all_jobs.extend(indeed_jobs)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        self.display_jobs(unique_jobs, profile)
        self.save_jobs(unique_jobs, profile)
        
        print(f"✅ Results saved to {self.jobs_file}\n")

if __name__ == "__main__":
    scraper = JobScraper()
    scraper.run()
