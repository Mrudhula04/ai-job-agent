#!/usr/bin/env python3
"""
Autonomous AI Job Agent
Goal: Get job interviews for the user by finding and tracking relevant job opportunities
"""

import json
import os
from datetime import datetime, timedelta
from anthropic import Anthropic
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time

load_dotenv()

class AIJobAgent:
    """
    An autonomous AI agent with the goal of getting you job interviews.
    
    The agent:
    - Has a clear goal: Get job interviews
    - Makes decisions autonomously
    - Takes actions to achieve the goal
    - Learns from results
    - Adapts strategy over time
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.profile_file = "my_profile.json"
        self.state_file = "agent_state.json"
        self.applications_file = "applications_tracker.json"
        
        # Agent's goal
        self.goal = "Get job interviews for Software Engineer positions matching the user's profile"
        
        # Load agent state (memory)
        self.state = self.load_state()
        
        # Load user profile
        self.profile = self.load_profile()
        
        print("🤖 AI Job Agent Initialized")
        print(f"📋 Goal: {self.goal}")
        print(f"🧠 Agent State: Day {self.state.get('days_active', 0)}")
        print()
    
    def load_profile(self):
        """Load user profile"""
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_state(self):
        """Load agent's memory/state"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        
        # Initialize new agent state
        return {
            'days_active': 0,
            'total_jobs_found': 0,
            'total_jobs_applied': 0,
            'interviews_scheduled': 0,
            'last_run': None,
            'search_strategy': 'broad',  # broad, focused, aggressive
            'successful_keywords': [],
            'unsuccessful_keywords': [],
            'learning_notes': []
        }
    
    def save_state(self):
        """Save agent's memory/state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def load_applications(self):
        """Load application tracker"""
        if os.path.exists(self.applications_file):
            with open(self.applications_file, 'r') as f:
                return json.load(f)
        return {'applications': []}
    
    def save_applications(self, applications):
        """Save application tracker"""
        with open(self.applications_file, 'w') as f:
            json.dump(applications, f, indent=2)
    
    def think(self, situation):
        """
        Agent thinks about the situation and decides what to do next.
        This is where the AI makes autonomous decisions.
        """
        prompt = f"""You are an autonomous AI job agent. Your goal is: {self.goal}

CURRENT SITUATION:
{situation}

USER PROFILE:
- Experience: {self.profile.get('experience_years', 0)} years
- Skills: {', '.join(self.profile.get('skills', []))}
- Role: {self.profile.get('desired_role', '')}
- Location: {self.profile.get('location', '')}

AGENT STATE (Your Memory):
- Days active: {self.state.get('days_active', 0)}
- Jobs found so far: {self.state.get('total_jobs_found', 0)}
- Applications made: {self.state.get('total_jobs_applied', 0)}
- Interviews scheduled: {self.state.get('interviews_scheduled', 0)}
- Current strategy: {self.state.get('search_strategy', 'broad')}

QUESTION: What should I do next to achieve my goal? Consider:
1. Should I search for more jobs?
2. Should I change my search strategy?
3. Should I follow up on previous applications?
4. What keywords should I focus on?

Respond in this format:
ACTION: [search_jobs|follow_up|adjust_strategy|report]
REASONING: [Why you chose this action]
PARAMETERS: [Any specific parameters for the action]
CONFIDENCE: [High/Medium/Low]"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            decision = response.content[0].text
            return self.parse_decision(decision)
            
        except Exception as e:
            print(f"⚠️  Agent thinking error: {e}")
            # Fallback decision
            return {
                'action': 'search_jobs',
                'reasoning': 'Default action due to error',
                'parameters': {},
                'confidence': 'low'
            }
    
    def parse_decision(self, decision_text):
        """Parse the agent's decision"""
        import re
        
        action_match = re.search(r'ACTION:\s*(\w+)', decision_text)
        reasoning_match = re.search(r'REASONING:\s*(.+?)(?:\n|$)', decision_text)
        
        return {
            'action': action_match.group(1) if action_match else 'search_jobs',
            'reasoning': reasoning_match.group(1) if reasoning_match else 'No reasoning provided',
            'parameters': {},
            'confidence': 'medium',
            'full_response': decision_text
        }
    
    def search_jobs(self, keywords=None):
        """Search for jobs using real scraping - AGGRESSIVE MODE"""
        print("🔍 Searching for REAL jobs on LinkedIn and Indeed...")
        print("   🎯 AGGRESSIVE MODE: Searching with multiple keyword combinations...")
        
        # Use profile keywords if none provided
        role = self.profile.get('desired_role', 'Software Engineer')
        skills = self.profile.get('skills', [])
        location = self.profile.get('location', '')
        
        jobs_found = []
        
        # Generate MANY search queries to find 100+ jobs
        search_queries = [
            # Role-based
            f"{role}",
            f"Junior {role}",
            f"Entry Level {role}",
            f"{role} 1 year experience",
            f"{role} early career",
            
            # Skill-based (use all skills)
            f"{skills[0]} Developer" if len(skills) > 0 else f"{role}",
            f"{skills[1]} Engineer" if len(skills) > 1 else f"{role}",
            f"{skills[2]} Developer" if len(skills) > 2 else f"{role}",
            f"{skills[0]} {skills[1]}" if len(skills) > 1 else f"{role}",
            
            # Combination searches
            f"{role} {skills[0]}" if len(skills) > 0 else f"{role}",
            f"{role} {skills[1]}" if len(skills) > 1 else f"{role}",
            f"{skills[0]} {role}" if len(skills) > 0 else f"{role}",
            
            # Remote/Location
            f"Remote {role}",
            f"{role} remote",
            f"{role} work from home",
            
            # Contract/Full-time
            f"{role} full time",
            f"{role} contract",
            
            # Technology-specific
            f"Backend {role}",
            f"Frontend {role}",
            f"Full Stack {role}",
        ]
        
        # Remove duplicates
        search_queries = list(set(search_queries))
        
        print(f"   📊 Will perform {len(search_queries)} different searches")
        
        # Search LinkedIn with all queries
        print(f"\n   → Searching LinkedIn ({len(search_queries)} queries)...")
        for i, query in enumerate(search_queries, 1):
            print(f"      [{i}/{len(search_queries)}] {query[:40]}...", end=' ')
            linkedin_jobs = self._scrape_linkedin_single(query, location)
            jobs_found.extend(linkedin_jobs)
            print(f"({len(linkedin_jobs)} jobs)")
            time.sleep(1)  # Rate limiting
        
        # Search Indeed with all queries
        print(f"\n   → Searching Indeed ({len(search_queries)} queries)...")
        for i, query in enumerate(search_queries, 1):
            print(f"      [{i}/{len(search_queries)}] {query[:40]}...", end=' ')
            indeed_jobs = self._scrape_indeed_single(query, location)
            jobs_found.extend(indeed_jobs)
            print(f"({len(indeed_jobs)} jobs)")
            time.sleep(1)  # Rate limiting
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        for job in jobs_found:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        print(f"\n   ✅ Found {len(unique_jobs)} unique job postings (from {len(jobs_found)} total)")
        return unique_jobs
    
    def _scrape_linkedin_single(self, keywords, location):
        """Scrape LinkedIn for a single query"""
        jobs = []
        url = f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(keywords)}&location={quote_plus(location)}&f_TPR=r604800&sortBy=DD"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, cookies=self.linkedin_cookies, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='base-card')[:50]  # Get 50 jobs per search
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h3', class_='base-search-card__title')
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        link_elem = card.find('a', class_='base-card__full-link')
                        
                        if title_elem and company_elem and link_elem:
                            jobs.append({
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'url': link_elem.get('href', ''),
                                'platform': 'LinkedIn',
                                'match_score': 0.0
                            })
                    except:
                        continue
        except:
            pass
        
        return jobs
    
    def _scrape_indeed_single(self, keywords, location):
        """Scrape Indeed for a single query"""
        jobs = []
        url = f"https://www.indeed.com/jobs?q={quote_plus(keywords)}&l={quote_plus(location)}&fromage=7&sort=date"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')[:50]  # Get 50 jobs per search
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        company_elem = card.find('span', {'data-testid': 'company-name'})
                        
                        if title_elem and company_elem:
                            link = title_elem.find('a')
                            if link:
                                job_id = link.get('data-jk', '')
                                jobs.append({
                                    'title': title_elem.text.strip(),
                                    'company': company_elem.text.strip(),
                                    'url': f"https://www.indeed.com/viewjob?jk={job_id}",
                                    'platform': 'Indeed',
                                    'match_score': 0.0
                                })
                    except:
                        continue
        except:
            pass
        
        return jobs
    
    def evaluate_job(self, job):
        """Agent evaluates if a job is worth applying to"""
        prompt = f"""You are evaluating if this job is worth applying to.

JOB:
Title: {job['title']}
Company: {job['company']}

USER PROFILE:
- Experience: {self.profile.get('experience_years', 0)} years
- Skills: {', '.join(self.profile.get('skills', []))}

GOAL: Get job interviews

Should I apply to this job?
Respond: YES or NO
Reason: [one sentence]"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            decision = response.content[0].text
            should_apply = 'YES' in decision.upper()
            
            return should_apply, decision
            
        except Exception as e:
            return False, f"Error: {e}"
    
    def take_action(self, decision):
        """Execute the decided action"""
        action = decision['action']
        
        print(f"\n💭 Agent Decision: {action}")
        print(f"   Reasoning: {decision['reasoning']}")
        print(f"   Confidence: {decision['confidence']}")
        print()
        
        if action == 'search_jobs':
            jobs = self.search_jobs()
            self.state['total_jobs_found'] += len(jobs)
            
            # Evaluate each job
            print(f"\n📋 Evaluating {len(jobs)} jobs...")
            for i, job in enumerate(jobs, 1):
                print(f"   [{i}/{len(jobs)}] {job['title'][:50]}...", end=' ')
                
                should_apply, reason = self.evaluate_job(job)
                
                if should_apply:
                    print(f"✅")
                    self.mark_for_application(job)
                else:
                    print(f"❌")
                
                # Faster rate limiting
                if i < len(jobs):
                    time.sleep(0.3)
        
        elif action == 'follow_up':
            self.follow_up_applications()
        
        elif action == 'adjust_strategy':
            self.adjust_strategy()
        
        elif action == 'report':
            self.generate_report()
    
    def mark_for_application(self, job):
        """Mark a job for application"""
        applications = self.load_applications()
        
        applications['applications'].append({
            'job': job,
            'status': 'ready_to_apply',
            'date_found': datetime.now().isoformat(),
            'applied_date': None,
            'follow_up_date': None
        })
        
        self.save_applications(applications)
        self.state['total_jobs_applied'] += 1
    
    def follow_up_applications(self):
        """Follow up on previous applications"""
        print("📧 Checking applications that need follow-up...")
        
        applications = self.load_applications()
        needs_followup = []
        
        for app in applications['applications']:
            if app['status'] == 'applied' and app.get('applied_date'):
                applied_date = datetime.fromisoformat(app['applied_date'])
                days_since = (datetime.now() - applied_date).days
                
                if days_since >= 7 and not app.get('follow_up_date'):
                    needs_followup.append(app)
        
        print(f"   {len(needs_followup)} applications need follow-up")
        
        for app in needs_followup:
            print(f"   📌 Follow up: {app['job']['title']} at {app['job']['company']}")
    
    def adjust_strategy(self):
        """Adjust search strategy based on results"""
        print("🎯 Adjusting search strategy...")
        
        success_rate = 0
        if self.state['total_jobs_applied'] > 0:
            success_rate = self.state['interviews_scheduled'] / self.state['total_jobs_applied']
        
        if success_rate < 0.1:
            self.state['search_strategy'] = 'aggressive'
            print("   Strategy: AGGRESSIVE (low success rate, casting wider net)")
        elif success_rate > 0.3:
            self.state['search_strategy'] = 'focused'
            print("   Strategy: FOCUSED (good success rate, being selective)")
        else:
            self.state['search_strategy'] = 'balanced'
            print("   Strategy: BALANCED (moderate success rate)")
    
    def generate_report(self):
        """Generate progress report"""
        print("\n" + "="*60)
        print("📊 AGENT PROGRESS REPORT")
        print("="*60)
        print(f"\n🎯 Goal: {self.goal}")
        print(f"\n📈 Statistics:")
        print(f"   Days Active: {self.state['days_active']}")
        print(f"   Jobs Found: {self.state['total_jobs_found']}")
        print(f"   Applications Made: {self.state['total_jobs_applied']}")
        print(f"   Interviews Scheduled: {self.state['interviews_scheduled']}")
        
        if self.state['total_jobs_applied'] > 0:
            success_rate = (self.state['interviews_scheduled'] / self.state['total_jobs_applied']) * 100
            print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🧠 Current Strategy: {self.state['search_strategy']}")
        
        # Show jobs ready to apply
        applications = self.load_applications()
        ready_jobs = [app for app in applications['applications'] if app['status'] == 'ready_to_apply']
        
        if ready_jobs:
            print(f"\n📋 JOBS READY TO APPLY ({len(ready_jobs)}):")
            print("="*60)
            for i, app in enumerate(ready_jobs[-10:], 1):  # Show last 10
                job = app['job']
                print(f"\n{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Platform: {job.get('platform', 'Unknown')}")
                print(f"   🔗 {job['url']}")
        
        print(f"\n💡 Agent Learning:")
        for note in self.state.get('learning_notes', [])[-3:]:
            print(f"   - {note}")
        
        print("\n" + "="*60)
    
    def run(self):
        """Main agent loop - autonomous execution"""
        print("🚀 AI Job Agent Starting Autonomous Run\n")
        
        # Update state
        self.state['days_active'] += 1
        self.state['last_run'] = datetime.now().isoformat()
        
        # ALWAYS search for jobs first (this is the primary goal)
        print("🔍 Step 1: Searching for new job opportunities...")
        jobs = self.search_jobs()
        
        if jobs:
            self.state['total_jobs_found'] += len(jobs)
            
            # Evaluate each job
            print(f"\n📋 Step 2: Evaluating {len(jobs)} jobs with AI...")
            applied_count = 0
            
            for i, job in enumerate(jobs, 1):
                print(f"   [{i}/{len(jobs)}] {job['title'][:50]}...", end=' ')
                
                should_apply, reason = self.evaluate_job(job)
                
                if should_apply:
                    print(f"✅ APPLY")
                    self.mark_for_application(job)
                    applied_count += 1
                else:
                    print(f"❌ SKIP")
                
                # Rate limiting
                if i < len(jobs):
                    time.sleep(0.3)
            
            print(f"\n   ✅ Marked {applied_count} jobs for application")
        else:
            print("   ⚠️  No jobs found today")
        
        # Step 3: Think about what else to do
        situation = f"""
        Today is day {self.state['days_active']}.
        I just searched and found {len(jobs)} jobs.
        Total stats:
        - Jobs found: {self.state['total_jobs_found']}
        - Applications made: {self.state['total_jobs_applied']}
        - Interviews: {self.state['interviews_scheduled']}
        
        Besides searching (which I just did), what else should I do?
        Options: follow_up, adjust_strategy, or just report
        """
        
        print("\n🤔 Step 3: Agent thinking about additional actions...")
        decision = self.think(situation)
        
        # Only take non-search actions
        if decision['action'] != 'search_jobs':
            self.take_action(decision)
        
        # Step 4: Learn and adapt
        self.state['learning_notes'].append(
            f"Day {self.state['days_active']}: Found {len(jobs)} jobs, {decision['action']} - {decision['reasoning'][:50]}"
        )
        
        # Step 5: Save state
        self.save_state()
        
        # Step 6: Report
        self.generate_report()
        
        print("\n✅ Agent run complete. Will run again tomorrow.")

if __name__ == "__main__":
    agent = AIJobAgent()
    agent.run()
