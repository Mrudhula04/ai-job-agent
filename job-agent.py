#!/usr/bin/env python3
"""
Autonomous AI Job Agent
Goal: Get job interviews by finding and recommending optimal job opportunities daily

This agent:
- Searches multiple sources (avoiding throttling)
- Uses Claude AI for intelligent filtering
- Makes autonomous decisions
- Learns from results
- Runs daily automatically
"""

import json
import os
import time
from datetime import datetime, timedelta
from anthropic import Anthropic
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import random

load_dotenv()

class JobAgent:
    """
    Autonomous AI Agent for Job Hunting
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.profile_file = "my_profile.json"
        self.state_file = "agent_state.json"
        self.jobs_file = "daily_jobs.json"
        
        # Agent's goal
        self.goal = "Find optimal job opportunities and get interviews"
        
        # Load state and profile
        self.state = self.load_state()
        self.profile = self.load_profile()
        
        # Job sources (diversified to avoid throttling)
        self.sources = ['google_jobs', 'company_sites', 'job_boards']
        
        # Top 25 US Tech Companies
        self.companies = [
            {'name': 'Google', 'url': 'https://careers.google.com/jobs/results/'},
            {'name': 'Amazon', 'url': 'https://www.amazon.jobs/en/search'},
            {'name': 'Microsoft', 'url': 'https://careers.microsoft.com/us/en/search-results'},
            {'name': 'Apple', 'url': 'https://jobs.apple.com/en-us/search'},
            {'name': 'Meta', 'url': 'https://www.metacareers.com/jobs'},
            {'name': 'Netflix', 'url': 'https://jobs.netflix.com/search'},
            {'name': 'Salesforce', 'url': 'https://salesforce.wd1.myworkdayjobs.com/External_Career_Site'},
            {'name': 'Oracle', 'url': 'https://careers.oracle.com/jobs/'},
            {'name': 'Adobe', 'url': 'https://careers.adobe.com/us/en/search-results'},
            {'name': 'IBM', 'url': 'https://www.ibm.com/careers/search'},
            {'name': 'Stripe', 'url': 'https://stripe.com/jobs/search'},
            {'name': 'Airbnb', 'url': 'https://careers.airbnb.com/positions/'},
            {'name': 'Uber', 'url': 'https://www.uber.com/us/en/careers/list/'},
            {'name': 'Lyft', 'url': 'https://www.lyft.com/careers'},
            {'name': 'DoorDash', 'url': 'https://careers.doordash.com/jobs/'},
            {'name': 'Coinbase', 'url': 'https://www.coinbase.com/careers/positions'},
            {'name': 'Robinhood', 'url': 'https://robinhood.com/us/en/careers/'},
            {'name': 'Cisco', 'url': 'https://jobs.cisco.com/jobs/SearchJobs/'},
            {'name': 'Intel', 'url': 'https://jobs.intel.com/en/search-jobs'},
            {'name': 'VMware', 'url': 'https://careers.vmware.com/main/jobs'},
            {'name': 'Databricks', 'url': 'https://www.databricks.com/company/careers'},
            {'name': 'Snowflake', 'url': 'https://careers.snowflake.com/us/en/search-results'},
            {'name': 'Atlassian', 'url': 'https://www.atlassian.com/company/careers/all-jobs'},
            {'name': 'Twilio', 'url': 'https://www.twilio.com/company/jobs'},
            {'name': 'Slack', 'url': 'https://slack.com/careers'},
        ]
        
        print("🤖 AI Job Agent Initialized")
        print(f"📋 Goal: {self.goal}")
        print(f"🧠 Day {self.state.get('days_active', 0)} of operation")
        print()
    
    def load_profile(self):
        """Load user profile"""
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_state(self):
        """Load agent's memory"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        
        return {
            'days_active': 0,
            'total_jobs_found': 0,
            'jobs_shown_to_user': 0,
            'user_applied': 0,
            'interviews_gotten': 0,
            'last_run': None,
            'successful_sources': [],
            'learning_log': []
        }
    
    def save_state(self):
        """Save agent's memory"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def think(self):
        """Agent thinks about what to do today"""
        situation = f"""
Today is day {self.state['days_active']} of my operation.

MY STATS:
- Jobs found so far: {self.state['total_jobs_found']}
- Jobs shown to user: {self.state['jobs_shown_to_user']}
- User applied to: {self.state['user_applied']}
- Interviews gotten: {self.state['interviews_gotten']}

USER PROFILE:
- Role: {self.profile.get('desired_role')}
- Experience: {self.profile.get('experience_years')} years
- Skills: {', '.join(self.profile.get('skills', [])[:5])}

MY GOAL: {self.goal}

What should I focus on today?
1. Search aggressively for more jobs?
2. Be more selective with quality?
3. Try different job sources?

Respond with: STRATEGY: [aggressive|balanced|selective]
REASONING: [one sentence]
"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": situation}]
            )
            
            decision = response.content[0].text
            
            if 'aggressive' in decision.lower():
                return 'aggressive', decision
            elif 'selective' in decision.lower():
                return 'selective', decision
            else:
                return 'balanced', decision
                
        except Exception as e:
            return 'balanced', 'Default strategy'
    
    def search_google_jobs(self, keywords, location):
        """Search using Google Jobs (no throttling)"""
        jobs = []
        
        # Google Jobs search
        query = f"{keywords} jobs {location}"
        url = f"https://www.google.com/search?q={quote_plus(query)}&ibp=htl;jobs"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for job listings in Google Jobs
                job_elements = soup.find_all('div', class_='PwjeAc')
                
                for elem in job_elements[:20]:
                    try:
                        title = elem.find('div', class_='BjJfJf')
                        company = elem.find('div', class_='vNEEBe')
                        
                        if title and company:
                            jobs.append({
                                'title': title.get_text(strip=True),
                                'company': company.get_text(strip=True),
                                'url': f"https://www.google.com/search?q={quote_plus(title.get_text())}+{quote_plus(company.get_text())}+jobs",
                                'source': 'Google Jobs'
                            })
                    except:
                        continue
        except:
            pass
        
        return jobs
    
    def search_company_sites(self, keywords):
        """Search company career pages"""
        jobs = []
        
        print(f"   → Searching {len(self.companies)} company career sites...")
        
        for company in self.companies:
            try:
                response = requests.get(company['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for job links
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        text = link.get_text(strip=True).lower()
                        href = link.get('href', '')
                        
                        # Check if it looks like a job posting
                        if any(kw in text for kw in ['software', 'engineer', 'developer', 'java', 'typescript']):
                            # Make full URL
                            if not href.startswith('http'):
                                if href.startswith('/'):
                                    base = '/'.join(company['url'].split('/')[:3])
                                    href = base + href
                                else:
                                    continue
                            
                            jobs.append({
                                'title': link.get_text(strip=True),
                                'company': company['name'],
                                'url': href,
                                'source': f"{company['name']} Careers"
                            })
                            
                            if len([j for j in jobs if j['company'] == company['name']]) >= 5:
                                break  # Max 5 per company
            except:
                pass
            
            time.sleep(1)  # Rate limiting
        
        print(f"      Company Sites: {len(jobs)} found")
        return jobs
        """Search alternative job boards"""
        jobs = []
        
        # Try RemoteOK (no throttling, API-friendly)
        try:
            url = "https://remoteok.com/api"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for job in data[1:21]:  # Skip first item (metadata)
                    try:
                        if isinstance(job, dict):
                            title = job.get('position', '')
                            company = job.get('company', '')
                            
                            # Check if matches keywords
                            if any(kw.lower() in title.lower() for kw in keywords.split()):
                                jobs.append({
                                    'title': title,
                                    'company': company,
                                    'url': job.get('url', ''),
                                    'source': 'RemoteOK'
                                })
                    except:
                        continue
        except:
            pass
        
        return jobs
    
    def search_all_sources(self, strategy):
        """Search multiple sources based on strategy"""
        print(f"🔍 Searching for jobs (Strategy: {strategy})...")
        
        role = self.profile.get('desired_role', 'Software Engineer')
        skills = self.profile.get('skills', [])[:3]
        location = self.profile.get('location', 'USA')
        
        all_jobs = []
        
        # Search queries based on strategy
        if strategy == 'aggressive':
            queries = [
                f"{role}",
                f"Junior {role}",
                f"{skills[0]} Developer" if skills else role,
                f"{skills[1]} Engineer" if len(skills) > 1 else role,
            ]
        elif strategy == 'selective':
            queries = [
                f"{role} {skills[0]} {skills[1]}" if len(skills) > 1 else role,
            ]
        else:  # balanced
            queries = [
                f"{role}",
                f"{skills[0]} Developer" if skills else role,
            ]
        
        for query in queries:
            print(f"   → Searching: {query[:50]}...")
            
            # Google Jobs (reliable, no throttling)
            google_jobs = self.search_google_jobs(query, location)
            all_jobs.extend(google_jobs)
            print(f"      Google Jobs: {len(google_jobs)} found")
            
            # Job Boards
            board_jobs = self.search_job_boards(query, location)
            all_jobs.extend(board_jobs)
            print(f"      Job Boards: {len(board_jobs)} found")
            
            # Company Sites (every 2nd query to avoid too many requests)
            if queries.index(query) % 2 == 0:
                company_jobs = self.search_company_sites(query)
                all_jobs.extend(company_jobs)
            
            time.sleep(2)  # Respectful rate limiting
        
        # Remove duplicates
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = f"{job['title']}_{job['company']}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        print(f"\n   ✅ Found {len(unique_jobs)} unique jobs")
        return unique_jobs
    
    def evaluate_job(self, job):
        """Use Claude to evaluate if job matches profile"""
        prompt = f"""Evaluate this job for the candidate.

JOB:
Title: {job['title']}
Company: {job['company']}

CANDIDATE:
Experience: {self.profile.get('experience_years', 0)} years
Skills: {', '.join(self.profile.get('skills', [])[:5])}
Role: {self.profile.get('desired_role')}

Is this a good match?
- Check experience requirements (reject if needs 5+ years for 1 year candidate)
- Check if title matches level (reject Senior/Lead/Staff for junior)
- Check skill alignment

Respond: MATCH: YES or NO
REASON: [one sentence]
CONFIDENCE: [High/Medium/Low]"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            is_match = 'YES' in result.upper()
            
            return is_match, result
            
        except Exception as e:
            # Fallback: simple keyword check
            title_lower = job['title'].lower()
            if any(word in title_lower for word in ['senior', 'sr.', 'lead', 'staff', 'principal']):
                return False, "Senior role (fallback check)"
            return True, "Potential match (fallback)"
    
    def run_daily(self):
        """Main daily execution"""
        print("🚀 Starting Daily Job Hunt\n")
        
        # Update state
        self.state['days_active'] += 1
        self.state['last_run'] = datetime.now().isoformat()
        
        # Step 1: Think about strategy
        print("🤔 Agent thinking about today's strategy...")
        strategy, reasoning = self.think()
        print(f"   Strategy: {strategy.upper()}")
        print(f"   Reasoning: {reasoning[:100]}...\n")
        
        # Step 2: Search for jobs
        jobs = self.search_all_sources(strategy)
        self.state['total_jobs_found'] += len(jobs)
        
        if not jobs:
            print("\n⚠️  No jobs found today. Will try again tomorrow.")
            self.save_state()
            return
        
        # Step 3: Evaluate jobs with AI
        print(f"\n🧠 Evaluating {len(jobs)} jobs with Claude AI...\n")
        
        matched_jobs = []
        for i, job in enumerate(jobs, 1):
            print(f"   [{i}/{len(jobs)}] {job['title'][:50]}...", end=' ')
            
            is_match, reason = self.evaluate_job(job)
            job['evaluation'] = reason
            
            if is_match:
                print("✅")
                matched_jobs.append(job)
            else:
                print("❌")
            
            time.sleep(0.5)  # Rate limiting
        
        # Step 4: Show results to user
        print("\n" + "="*70)
        print("📊 TODAY'S JOB RECOMMENDATIONS")
        print("="*70)
        print(f"\nDate: {datetime.now().strftime('%B %d, %Y')}")
        print(f"Jobs Searched: {len(jobs)}")
        print(f"Jobs Matched: {len(matched_jobs)}")
        
        if matched_jobs:
            print(f"\n✅ JOBS TO APPLY TODAY ({len(matched_jobs)}):")
            print("="*70 + "\n")
            
            for i, job in enumerate(matched_jobs, 1):
                print(f"{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Source: {job['source']}")
                print(f"   🔗 {job['url']}")
                print()
            
            self.state['jobs_shown_to_user'] += len(matched_jobs)
        else:
            print("\n⚠️  No matches today. All jobs were too senior or didn't match your profile.")
            print("💡 The agent will adjust strategy tomorrow.")
        
        # Step 5: Save results
        results = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'strategy': strategy,
            'jobs_searched': len(jobs),
            'jobs_matched': len(matched_jobs),
            'matched_jobs': matched_jobs,
            'all_jobs': jobs
        }
        
        with open(self.jobs_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Step 6: Agent learning
        self.state['learning_log'].append({
            'day': self.state['days_active'],
            'strategy': strategy,
            'jobs_found': len(jobs),
            'jobs_matched': len(matched_jobs),
            'match_rate': f"{(len(matched_jobs)/len(jobs)*100):.1f}%" if jobs else "0%"
        })
        
        # Keep only last 30 days of logs
        self.state['learning_log'] = self.state['learning_log'][-30:]
        
        # Step 7: Show agent stats
        print("\n" + "="*70)
        print("🤖 AGENT STATISTICS")
        print("="*70)
        print(f"\nDays Active: {self.state['days_active']}")
        print(f"Total Jobs Found: {self.state['total_jobs_found']}")
        print(f"Jobs Shown to You: {self.state['jobs_shown_to_user']}")
        print(f"Current Strategy: {strategy}")
        
        if self.state['learning_log']:
            recent = self.state['learning_log'][-3:]
            print(f"\nRecent Performance:")
            for log in recent:
                print(f"   Day {log['day']}: {log['jobs_matched']} matches from {log['jobs_found']} jobs ({log['match_rate']})")
        
        print("\n" + "="*70)
        
        # Save state
        self.save_state()
        
        print(f"\n✅ Results saved to {self.jobs_file}")
        print("✅ Agent state saved")
        print("\n💡 Apply to the jobs above and update agent_state.json when you get interviews!")
        print("🔄 Run again tomorrow for fresh jobs\n")

if __name__ == "__main__":
    agent = JobAgent()
    agent.run_daily()
