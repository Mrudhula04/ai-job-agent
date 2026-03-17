#!/usr/bin/env python3
"""
AI Job Finder Agent
Searches LinkedIn, Wellfound, Indeed for jobs matching your profile
"""

import json
import os
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class JobFinderAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.profile_file = "my_profile.json"
        self.jobs_file = "daily_jobs.json"
        
    def load_profile(self):
        """Load user profile from JSON file"""
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}
    
    def search_jobs(self, profile):
        """Use Claude with web search to find relevant jobs"""
        profile_summary = f"""
Skills: {', '.join(profile.get('skills', []))}
Experience: {profile.get('experience_years', 0)} years
Role: {profile.get('desired_role', '')}
Location: {profile.get('location', '')}
Remote: {profile.get('remote_preference', 'yes')}
"""
        
        prompt = f"""You are a job search assistant. Find 5-10 relevant job postings for this profile:

{profile_summary}

Search these platforms:
1. LinkedIn Jobs (linkedin.com/jobs)
2. Wellfound (wellfound.com/jobs)
3. Indeed (indeed.com)

For each job, provide:
- Job Title
- Company
- Location
- Job URL
- Why it matches (brief)

Format as JSON array with these fields: title, company, location, url, match_reason
"""
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def save_daily_jobs(self, jobs_data):
        """Save today's job recommendations"""
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "jobs": jobs_data
        }
        with open(self.jobs_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def run(self):
        """Main execution"""
        print("🤖 AI Job Finder Agent Starting...")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        profile = self.load_profile()
        if not profile:
            print("❌ No profile found. Please create my_profile.json first.")
            return
        
        print("🔍 Searching for jobs across platforms...")
        jobs_result = self.search_jobs(profile)
        
        print("\n" + "="*60)
        print("📋 TODAY'S JOB RECOMMENDATIONS")
        print("="*60 + "\n")
        print(jobs_result)
        
        self.save_daily_jobs(jobs_result)
        print(f"\n✅ Results saved to {self.jobs_file}")

if __name__ == "__main__":
    agent = JobFinderAgent()
    agent.run()
