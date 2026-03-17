#!/usr/bin/env python3
"""
Smart Job Scraper - Uses Claude to analyze job descriptions
Filters jobs based on experience requirements and profile match
"""

import json
import os
import re
import time
from datetime import datetime
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class SmartJobScraper:
    def __init__(self):
        self.profile_file = "my_profile.json"
        self.jobs_file = "daily_jobs.json"
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # LinkedIn authentication cookies (optional)
        self.linkedin_cookies = {}
        li_at = os.environ.get('LINKEDIN_LI_AT')
        jsessionid = os.environ.get('LINKEDIN_JSESSIONID')
        
        if li_at and jsessionid:
            self.linkedin_cookies = {
                'li_at': li_at,
                'JSESSIONID': jsessionid
            }
            print("   ✅ LinkedIn authentication enabled (more results!)")
        else:
            print("   ℹ️  LinkedIn authentication not configured (limited results)")
        
    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}
    
    def fetch_job_description(self, url):
        """Fetch full job description from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to find job description
                # LinkedIn
                if 'linkedin.com' in url:
                    desc = soup.find('div', class_='description__text')
                    if desc:
                        return desc.get_text(strip=True, separator=' ')
                
                # Indeed
                elif 'indeed.com' in url:
                    desc = soup.find('div', id='jobDescriptionText')
                    if desc:
                        return desc.get_text(strip=True, separator=' ')
                
                # Fallback: get all text
                return soup.get_text(strip=True, separator=' ')[:5000]
        except Exception as e:
            print(f"   ⚠️  Could not fetch description: {str(e)[:50]}")
            return None
    
    def analyze_job_match(self, job, job_description, profile):
        """Analyze if job matches profile using Claude or smart fallback"""
        if not job_description:
            return False, "Could not fetch job description"
        
        profile_summary = f"""
Experience: {profile.get('experience_years', 0)} years
Skills: {', '.join(profile.get('skills', []))}
Desired Role: {profile.get('desired_role', '')}
Minimum Annual Salary: ${profile.get('salary_min_annual', 0):,}
Minimum Hourly Rate: ${profile.get('salary_min_hourly', 0)}/hour
"""
        
        prompt = f"""You are a job matching assistant. Analyze if this job is a good match for the candidate.

CANDIDATE PROFILE:
{profile_summary}

JOB POSTING:
Title: {job['title']}
Company: {job['company']}

FULL JOB DESCRIPTION:
{job_description[:3000]}

ANALYSIS REQUIRED:
1. Does the required experience match? (Candidate has {profile.get('experience_years', 0)} years)
2. Do the required skills match the candidate's skills?
3. Is this an appropriate level role (not too senior, not too junior)?
4. Does the salary meet minimum requirements?
   - For annual salary jobs: Must be at least ${profile.get('salary_min_annual', 0):,}/year
   - For hourly jobs: Must be at least ${profile.get('salary_min_hourly', 0)}/hour
   - If EITHER requirement is met, the salary is acceptable

Respond in this EXACT format:
MATCH: YES or NO
REASON: One sentence explanation
EXPERIENCE_REQUIRED: X years (extract from description)
CONFIDENCE: High/Medium/Low

Be strict: If job requires 5+ years and candidate has 1 year, say NO.
Be flexible: Accept job if it meets EITHER annual OR hourly minimum."""
        
        # Try Claude API first
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis = response.content[0].text
            
            # Parse response
            is_match = "MATCH: YES" in analysis
            reason_match = re.search(r'REASON: (.+?)(?:\n|$)', analysis)
            reason = reason_match.group(1) if reason_match else "Analysis completed"
            
            exp_match = re.search(r'EXPERIENCE_REQUIRED: (.+?)(?:\n|$)', analysis)
            exp_required = exp_match.group(1) if exp_match else "Not specified"
            
            return is_match, f"{reason} (Requires: {exp_required})"
            
        except Exception as e:
            # Enhanced fallback: Smart keyword analysis
            return self._smart_fallback_analysis(job, job_description, profile)
    
    def _smart_fallback_analysis(self, job, job_description, profile):
        """Enhanced fallback analysis without Claude API"""
        desc_lower = job_description.lower()
        title_lower = job['title'].lower()
        exp_years = profile.get('experience_years', 0)
        skills = [s.lower() for s in profile.get('skills', [])]
        
        # Extract experience requirements
        exp_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience',
            r'minimum\s+(?:of\s+)?(\d+)\s+years?',
            r'at least\s+(\d+)\s+years?',
            r'(\d+)\s+years?\s+minimum',
            r'(\d+)-(\d+)\s+years?'
        ]
        
        required_exp = None
        for pattern in exp_patterns:
            matches = re.findall(pattern, desc_lower)
            if matches:
                if isinstance(matches[0], tuple):
                    required_exp = int(matches[0][0])
                else:
                    required_exp = int(matches[0])
                break
        
        # Check title-based seniority
        if 'senior' in title_lower or 'sr.' in title_lower:
            if exp_years < 5:
                return False, f"Senior role typically requires 5+ years (you have {exp_years})"
        
        if 'lead' in title_lower or 'principal' in title_lower:
            if exp_years < 5:
                return False, f"Lead/Principal role requires 5+ years (you have {exp_years})"
        
        if 'staff' in title_lower:
            if exp_years < 7:
                return False, f"Staff role typically requires 7+ years (you have {exp_years})"
        
        if 'architect' in title_lower:
            if exp_years < 8:
                return False, f"Architect role requires 8+ years (you have {exp_years})"
        
        # Check explicit experience requirements
        if required_exp:
            if required_exp > exp_years + 1:  # Allow 1 year flexibility
                return False, f"Requires {required_exp}+ years experience (you have {exp_years})"
        
        # Check for entry-level indicators
        entry_keywords = ['entry level', 'junior', 'associate', 'early career', 'new grad', 'graduate']
        is_entry = any(keyword in desc_lower for keyword in entry_keywords)
        
        if exp_years <= 2 and not is_entry and required_exp and required_exp >= 5:
            return False, f"Requires {required_exp}+ years, not entry-level (you have {exp_years})"
        
        # Check skill match
        skill_matches = sum(1 for skill in skills if skill in desc_lower)
        skill_match_ratio = skill_matches / len(skills) if skills else 0
        
        if skill_match_ratio < 0.2:  # Less than 20% skill match
            return False, f"Low skill match ({skill_matches}/{len(skills)} skills matched)"
        
        # Positive indicators for junior/entry roles
        if exp_years <= 2:
            if is_entry:
                return True, f"Entry-level role, good match ({skill_matches}/{len(skills)} skills matched)"
            if not required_exp or required_exp <= 3:
                return True, f"Good match for your experience level ({skill_matches}/{len(skills)} skills matched)"
        
        # For 3-5 years experience
        if 3 <= exp_years <= 5:
            if required_exp and required_exp <= 5:
                return True, f"Experience requirement matches ({required_exp} years required, {skill_matches} skills matched)"
        
        # Default: if no red flags and decent skill match
        if skill_match_ratio >= 0.3:
            exp_note = f"~{required_exp} years" if required_exp else "not specified"
            return True, f"Reasonable match (Experience: {exp_note}, {skill_matches}/{len(skills)} skills matched)"
        
        return False, f"Not a strong match (only {skill_matches}/{len(skills)} skills matched)"
    
    def scrape_linkedin_jobs(self, profile):
        """Scrape LinkedIn job postings (last 7 days)"""
        jobs = []
        role = profile.get('desired_role', 'Software Engineer')
        skills = profile.get('skills', [])[:3]  # Use top 3 skills
        location = profile.get('location', '')
        
        # Search with different keyword combinations to get more results
        search_queries = [
            f"{role} {' '.join(skills[:2])}",  # Role + top 2 skills
            f"{role}",  # Just the role
            f"{skills[0]} developer",  # Primary skill + developer
            f"{skills[1]} {role}",  # Second skill + role
            f"entry level {role}",  # Entry level
            f"junior {role}",  # Junior roles
        ]
        
        seen_urls = set()
        
        for keywords in search_queries:
            # LinkedIn with date filter (f_TPR=r604800 = past 7 days)
            url = f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(keywords)}&location={quote_plus(location)}&f_TPR=r604800&sortBy=DD"
            
            try:
                print(f"      Searching: {keywords[:50]}...")
                # Use cookies if available for authenticated access
                response = requests.get(url, headers=self.headers, cookies=self.linkedin_cookies, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='base-card')[:50]  # Increased from 15 to 50
                    
                    for card in job_cards:
                        try:
                            title_elem = card.find('h3', class_='base-search-card__title')
                            company_elem = card.find('h4', class_='base-search-card__subtitle')
                            location_elem = card.find('span', class_='job-search-card__location')
                            link_elem = card.find('a', class_='base-card__full-link')
                            
                            if title_elem and company_elem and link_elem:
                                job_url = link_elem.get('href', '')
                                
                                # Skip duplicates
                                if job_url in seen_urls:
                                    continue
                                seen_urls.add(job_url)
                                
                                time_elem = card.find('time')
                                posted_date = time_elem.get('datetime', '') if time_elem else ''
                                
                                job = {
                                    'title': title_elem.text.strip(),
                                    'company': company_elem.text.strip(),
                                    'location': location_elem.text.strip() if location_elem else 'Remote',
                                    'url': job_url,
                                    'platform': 'LinkedIn',
                                    'posted_date': posted_date
                                }
                                jobs.append(job)
                        except Exception as e:
                            continue
                elif response.status_code == 429:
                    print(f"      ⚠️  Rate limited by LinkedIn, skipping remaining searches")
                    break
                else:
                    print(f"      ⚠️  LinkedIn returned status {response.status_code}")
                            
            except requests.Timeout:
                print(f"      ⚠️  Request timeout, skipping this search")
                continue
            except Exception as e:
                print(f"      ⚠️  Error: {str(e)[:50]}")
                continue
            
            time.sleep(2)  # Rate limiting between searches
        
        return jobs
    
    def scrape_indeed_jobs(self, profile):
        """Scrape Indeed job postings (last 7 days)"""
        jobs = []
        role = profile.get('desired_role', 'Software Engineer')
        skills = profile.get('skills', [])[:3]
        location = profile.get('location', '')
        
        # Search with different keyword combinations
        search_queries = [
            f"{role} {' '.join(skills[:2])}",
            f"{role}",
            f"{skills[0]} developer",
        ]
        
        seen_urls = set()
        
        for keywords in search_queries:
            # Indeed with date filter (fromage=7 = last 7 days)
            url = f"https://www.indeed.com/jobs?q={quote_plus(keywords)}&l={quote_plus(location)}&fromage=7&sort=date"
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='job_seen_beacon')[:50]  # Increased from 15 to 50
                    
                    for card in job_cards:
                        try:
                            title_elem = card.find('h2', class_='jobTitle')
                            company_elem = card.find('span', {'data-testid': 'company-name'})
                            location_elem = card.find('div', {'data-testid': 'text-location'})
                            
                            if title_elem:
                                link = title_elem.find('a')
                                if link and company_elem:
                                    job_id = link.get('data-jk', '')
                                    job_url = f"https://www.indeed.com/viewjob?jk={job_id}"
                                    
                                    # Skip duplicates
                                    if job_url in seen_urls:
                                        continue
                                    seen_urls.add(job_url)
                                    
                                    date_elem = card.find('span', class_='date')
                                    posted_date = date_elem.text.strip() if date_elem else 'Today'
                                    
                                    job = {
                                        'title': title_elem.text.strip(),
                                        'company': company_elem.text.strip(),
                                        'location': location_elem.text.strip() if location_elem else 'Remote',
                                        'url': job_url,
                                        'platform': 'Indeed',
                                        'posted_date': posted_date
                                    }
                                    jobs.append(job)
                        except Exception as e:
                            continue
                            
            except Exception as e:
                print(f"   ⚠️  Indeed error: {str(e)[:50]}")
            
            time.sleep(2)  # Rate limiting between searches
        
        return jobs
    
    def display_jobs(self, matched_jobs, rejected_jobs, profile):
        """Display formatted job listings"""
        print("\n" + "="*80)
        print(f"📅 SMART JOB MATCHING REPORT - {datetime.now().strftime('%B %d, %Y')}")
        print("="*80)
        
        print(f"\n👤 YOUR PROFILE:")
        print(f"   Role: {profile.get('desired_role')}")
        print(f"   Experience: {profile.get('experience_years')} years")
        print(f"   Skills: {', '.join(profile.get('skills', [])[:4])}")
        
        if matched_jobs:
            print(f"\n✅ MATCHED JOBS ({len(matched_jobs)}):\n")
            
            for i, job in enumerate(matched_jobs, 1):
                print(f"{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['location']}")
                print(f"   Platform: {job['platform']}")
                if job.get('posted_date'):
                    print(f"   Posted: {job['posted_date']}")
                if job.get('match_reason'):
                    print(f"   ✓ {job['match_reason']}")
                print(f"   🔗 {job['url']}")
                print()
        else:
            print("\n⚠️  No matching jobs found today.")
            print("   This is normal - not every day has perfect matches.")
        
        if rejected_jobs:
            print(f"\n❌ REJECTED JOBS ({len(rejected_jobs)}) - Not a good fit:\n")
            for i, job in enumerate(rejected_jobs[:5], 1):
                print(f"{i}. {job['title']} at {job['company']}")
                print(f"   Reason: {job.get('match_reason', 'Not a match')}")
                print()
        
        print("="*80)
        print("\n💡 NEXT STEPS:")
        print("   1. Click each matched job link to view full details")
        print("   2. Apply to all matched jobs (they're pre-filtered for you!)")
        print("   3. Customize your resume for each application")
        print("   4. Follow up after 1 week\n")
    
    def save_jobs(self, matched_jobs, rejected_jobs, profile):
        """Save jobs to JSON file"""
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "profile": {
                "role": profile.get('desired_role'),
                "experience_years": profile.get('experience_years'),
                "skills": profile.get('skills'),
                "location": profile.get('location')
            },
            "matched_jobs": matched_jobs,
            "rejected_jobs": rejected_jobs,
            "total_matched": len(matched_jobs),
            "total_rejected": len(rejected_jobs)
        }
        
        with open(self.jobs_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def run(self):
        """Main execution"""
        print("\n🤖 Smart AI Job Scraper with Claude Analysis")
        print(f"⏰ {datetime.now().strftime('%I:%M %p')}")
        
        profile = self.load_profile()
        if not profile:
            print("\n❌ Error: my_profile.json not found")
            return
        
        print("\n🔍 Step 1: Searching for job postings (last 7 days)...")
        
        all_jobs = []
        
        print("   → Searching LinkedIn...")
        linkedin_jobs = self.scrape_linkedin_jobs(profile)
        all_jobs.extend(linkedin_jobs)
        
        print("   → Searching Indeed...")
        indeed_jobs = self.scrape_indeed_jobs(profile)
        all_jobs.extend(indeed_jobs)
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        print(f"\n   Found {len(unique_jobs)} unique job postings")
        
        # Limit to first 50 jobs to keep analysis time reasonable
        if len(unique_jobs) > 50:
            print(f"   ⚡ Analyzing first 50 jobs (to save time)")
            unique_jobs = unique_jobs[:50]
        
        if not unique_jobs:
            print("\n⚠️  No jobs found today. Try again tomorrow!")
            return
        
        print(f"\n🧠 Step 2: Analyzing {len(unique_jobs)} jobs with Claude Sonnet 4 AI...")
        print(f"   (Checking experience requirements, skills match, etc.)")
        print(f"   ⏱️  This will take ~{len(unique_jobs) * 2} seconds (2 sec per job)\n")
        
        matched_jobs = []
        rejected_jobs = []
        
        for i, job in enumerate(unique_jobs, 1):
            print(f"   [{i}/{len(unique_jobs)}] {job['title'][:60]}...", end=' ')
            
            # Fetch job description
            job_description = self.fetch_job_description(job['url'])
            
            if job_description:
                # Analyze with Claude
                is_match, reason = self.analyze_job_match(job, job_description, profile)
                job['match_reason'] = reason
                
                if is_match:
                    matched_jobs.append(job)
                    print(f"✅")
                else:
                    rejected_jobs.append(job)
                    print(f"❌")
            else:
                # If can't fetch, be conservative and include it
                job['match_reason'] = "Could not analyze (included by default)"
                matched_jobs.append(job)
                print(f"⚠️")
            
            # Rate limiting - don't spam Claude API
            if i < len(unique_jobs):
                time.sleep(0.5)  # Reduced from 1 second
        
        self.display_jobs(matched_jobs, rejected_jobs, profile)
        self.save_jobs(matched_jobs, rejected_jobs, profile)
        
        print(f"✅ Results saved to {self.jobs_file}\n")

if __name__ == "__main__":
    scraper = SmartJobScraper()
    scraper.run()
