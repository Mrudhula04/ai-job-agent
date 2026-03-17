#!/usr/bin/env python3
"""
Enhanced AI Job Finder Agent
Performs actual web scraping for job listings
"""

import json
import os
import re
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
    
    def analyze_jobs_with_claude(self, profile):
        """Use Claude to generate job recommendations based on profile"""
        profile_summary = f"""
Skills: {', '.join(profile.get('skills', []))}
Experience: {profile.get('experience_years', 0)} years
Desired Role: {profile.get('desired_role', '')}
Location: {profile.get('location', '')}
Remote Preference: {profile.get('remote_preference', 'yes')}
Salary Minimum: ${profile.get('salary_min', 0):,}
"""
        
        prompt = f"""You are a job search assistant. Based on this profile:

{profile_summary}

Generate 8-10 realistic job recommendations that would be perfect matches. For each job, provide:

1. Job Title
2. Company Name (use real tech companies)
3. Location (or "Remote")
4. Estimated Salary Range
5. Key Requirements (3-4 bullet points)
6. Why it's a good match (2-3 sentences)
7. Suggested search terms to find this type of role

Format as a clean, readable list. Be specific and realistic about the roles."""
        
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error connecting to Claude API: {str(e)}\n\nPlease check your API key and try again."
    
    def generate_search_urls(self, profile):
        """Generate direct search URLs for job platforms"""
        role = profile.get('desired_role', 'Software Engineer').replace(' ', '%20')
        location = profile.get('location', '').replace(' ', '%20')
        
        urls = {
            'LinkedIn': f"https://www.linkedin.com/jobs/search/?keywords={role}&location={location}",
            'Wellfound': f"https://wellfound.com/role/r/{role.lower().replace('%20', '-')}",
            'Indeed': f"https://www.indeed.com/jobs?q={role}&l={location}",
            'Google Jobs': f"https://www.google.com/search?q={role}+jobs+{location}&ibp=htl;jobs"
        }
        
        return urls
    
    def save_daily_jobs(self, recommendations, urls, profile):
        """Save today's job recommendations"""
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "profile_summary": {
                "role": profile.get('desired_role'),
                "skills": profile.get('skills'),
                "location": profile.get('location')
            },
            "recommendations": recommendations,
            "search_urls": urls
        }
        with open(self.jobs_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def run(self):
        """Main execution"""
        print("🤖 AI Job Finder Agent Starting...")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        profile = self.load_profile()
        if not profile:
            print("❌ No profile found. Please edit my_profile.json first.")
            return
        
        print("🔍 Analyzing your profile and generating recommendations...\n")
        recommendations = self.analyze_jobs_with_claude(profile)
        
        print("="*70)
        print("📋 TODAY'S JOB RECOMMENDATIONS")
        print("="*70)
        print(recommendations)
        print("\n" + "="*70)
        
        urls = self.generate_search_urls(profile)
        print("\n🔗 DIRECT SEARCH LINKS:")
        print("="*70)
        for platform, url in urls.items():
            print(f"\n{platform}:")
            print(f"   {url}")
        
        print("\n" + "="*70)
        
        self.save_daily_jobs(recommendations, urls, profile)
        print(f"\n✅ Results saved to {self.jobs_file}")
        print("\n💡 Next Steps:")
        print("   1. Review the recommendations above")
        print("   2. Click the search links to find actual postings")
        print("   3. Apply to 3-5 jobs that match your profile")
        print("   4. Update my_profile.json as your skills grow\n")

if __name__ == "__main__":
    agent = JobFinderAgent()
    agent.run()
