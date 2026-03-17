#!/usr/bin/env python3
"""
Company Career Page Scraper
Searches directly on tech company career websites - bypasses LinkedIn/Indeed throttling
"""

import json
import os
import time
from datetime import datetime
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class CompanyCareerScraper:
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.profile_file = "my_profile.json"
        self.jobs_file = "company_jobs.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Top US Tech Companies with career pages
        self.companies = [
            # FAANG+
            {'name': 'Google', 'url': 'https://careers.google.com/jobs/results/', 'api': 'greenhouse'},
            {'name': 'Amazon', 'url': 'https://www.amazon.jobs/en/search.json', 'api': 'amazon'},
            {'name': 'Microsoft', 'url': 'https://careers.microsoft.com/us/en/search-results', 'api': 'microsoft'},
            {'name': 'Apple', 'url': 'https://jobs.apple.com/en-us/search', 'api': 'apple'},
            {'name': 'Meta', 'url': 'https://www.metacareers.com/jobs', 'api': 'meta'},
            
            # Tech Giants
            {'name': 'Netflix', 'url': 'https://jobs.netflix.com/search', 'api': 'greenhouse'},
            {'name': 'Salesforce', 'url': 'https://salesforce.wd1.myworkdayjobs.com/External_Career_Site', 'api': 'workday'},
            {'name': 'Oracle', 'url': 'https://careers.oracle.com/jobs/', 'api': 'oracle'},
            {'name': 'Adobe', 'url': 'https://careers.adobe.com/us/en/search-results', 'api': 'adobe'},
            {'name': 'IBM', 'url': 'https://www.ibm.com/careers/search', 'api': 'ibm'},
            
            # Unicorns & High-Growth
            {'name': 'Stripe', 'url': 'https://stripe.com/jobs/search', 'api': 'greenhouse'},
            {'name': 'Airbnb', 'url': 'https://careers.airbnb.com/positions/', 'api': 'greenhouse'},
            {'name': 'Uber', 'url': 'https://www.uber.com/us/en/careers/list/', 'api': 'uber'},
            {'name': 'Lyft', 'url': 'https://www.lyft.com/careers', 'api': 'greenhouse'},
            {'name': 'DoorDash', 'url': 'https://careers.doordash.com/jobs/', 'api': 'greenhouse'},
            {'name': 'Coinbase', 'url': 'https://www.coinbase.com/careers/positions', 'api': 'greenhouse'},
            {'name': 'Robinhood', 'url': 'https://robinhood.com/us/en/careers/', 'api': 'greenhouse'},
            
            # Enterprise
            {'name': 'Cisco', 'url': 'https://jobs.cisco.com/jobs/SearchJobs/', 'api': 'cisco'},
            {'name': 'Intel', 'url': 'https://jobs.intel.com/en/search-jobs', 'api': 'intel'},
            {'name': 'VMware', 'url': 'https://careers.vmware.com/main/jobs', 'api': 'vmware'},
            
            # Startups & Scale-ups
            {'name': 'Databricks', 'url': 'https://www.databricks.com/company/careers', 'api': 'greenhouse'},
            {'name': 'Snowflake', 'url': 'https://careers.snowflake.com/us/en/search-results', 'api': 'snowflake'},
            {'name': 'Atlassian', 'url': 'https://www.atlassian.com/company/careers/all-jobs', 'api': 'atlassian'},
            {'name': 'Twilio', 'url': 'https://www.twilio.com/company/jobs', 'api': 'greenhouse'},
            {'name': 'Slack', 'url': 'https://slack.com/careers', 'api': 'greenhouse'},
        ]
    
    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}
    
    def search_company_generic(self, company, keywords):
        """Generic search for company career pages"""
        jobs = []
        
        try:
            # Try to fetch the career page
            response = requests.get(company['url'], headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for common job listing patterns
                job_links = soup.find_all('a', href=True)
                
                for link in job_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    
                    # Check if it looks like a job posting
                    if any(keyword in text for keyword in ['software', 'engineer', 'developer', 'java', 'typescript']):
                        # Make sure it's a full URL
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                base_url = '/'.join(company['url'].split('/')[:3])
                                href = base_url + href
                            else:
                                continue
                        
                        jobs.append({
                            'title': link.get_text(strip=True),
                            'company': company['name'],
                            'url': href,
                            'platform': 'Company Website'
                        })
                        
                        if len(jobs) >= 10:  # Limit per company
                            break
        
        except Exception as e:
            pass
        
        return jobs
    
    def evaluate_job(self, job, profile):
        """Use Claude to evaluate if job matches profile"""
        prompt = f"""Quick evaluation: Does this job match the candidate?

JOB: {job['title']} at {job['company']}

CANDIDATE:
- Experience: {profile.get('experience_years', 0)} years
- Skills: {', '.join(profile.get('skills', [])[:5])}

Respond: YES or NO
If YES, give 1 sentence why.
If NO, give 1 sentence why not."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            
            decision = response.content[0].text
            is_match = 'YES' in decision.upper()
            
            return is_match, decision
            
        except Exception as e:
            # Fallback: check title for senior keywords
            title_lower = job['title'].lower()
            if any(word in title_lower for word in ['senior', 'sr.', 'lead', 'staff', 'principal']):
                return False, "Senior role"
            return True, "Potential match"
    
    def run(self):
        """Main execution"""
        print("\n🏢 Company Career Page Scraper")
        print(f"⏰ {datetime.now().strftime('%I:%M %p')}")
        print(f"🎯 Searching {len(self.companies)} top tech companies\n")
        
        profile = self.load_profile()
        if not profile:
            print("❌ No profile found")
            return
        
        role = profile.get('desired_role', 'Software Engineer')
        skills = profile.get('skills', [])[:3]
        keywords = f"{role} {' '.join(skills)}"
        
        print(f"👤 Profile: {role} with {profile.get('experience_years', 0)} years experience")
        print(f"🔍 Keywords: {keywords}\n")
        
        all_jobs = []
        matched_jobs = []
        
        print("="*70)
        print("SEARCHING COMPANIES")
        print("="*70 + "\n")
        
        for i, company in enumerate(self.companies, 1):
            print(f"[{i}/{len(self.companies)}] {company['name']}...", end=' ', flush=True)
            
            jobs = self.search_company_generic(company, keywords)
            all_jobs.extend(jobs)
            
            print(f"({len(jobs)} jobs found)")
            
            # Rate limiting
            time.sleep(2)
        
        print(f"\n✅ Found {len(all_jobs)} total jobs across {len(self.companies)} companies")
        
        if not all_jobs:
            print("\n⚠️  No jobs found. Companies may have changed their website structure.")
            print("💡 Try visiting the company career pages directly:")
            for company in self.companies[:5]:
                print(f"   • {company['name']}: {company['url']}")
            return
        
        # Evaluate jobs with Claude
        print(f"\n🧠 Evaluating jobs with Claude AI...\n")
        
        for i, job in enumerate(all_jobs, 1):
            print(f"   [{i}/{len(all_jobs)}] {job['title'][:50]}...", end=' ')
            
            is_match, reason = self.evaluate_job(job, profile)
            job['match_reason'] = reason
            
            if is_match:
                print("✅")
                matched_jobs.append(job)
            else:
                print("❌")
            
            time.sleep(0.5)  # Rate limiting
        
        # Display results
        print("\n" + "="*70)
        print(f"📊 RESULTS")
        print("="*70)
        print(f"\nTotal Jobs Found: {len(all_jobs)}")
        print(f"Matched Jobs: {len(matched_jobs)}")
        print(f"Match Rate: {(len(matched_jobs)/len(all_jobs)*100):.1f}%")
        
        if matched_jobs:
            print(f"\n✅ JOBS TO APPLY ({len(matched_jobs)}):")
            print("="*70 + "\n")
            
            for i, job in enumerate(matched_jobs, 1):
                print(f"{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   🔗 {job['url']}")
                print()
        
        # Save results
        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_jobs': len(all_jobs),
            'matched_jobs': matched_jobs,
            'all_jobs': all_jobs
        }
        
        with open(self.jobs_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Results saved to {self.jobs_file}\n")

if __name__ == "__main__":
    scraper = CompanyCareerScraper()
    scraper.run()
