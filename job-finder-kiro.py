#!/usr/bin/env python3
"""
AI Job Finder Agent - Kiro Version
Uses manual web search approach for job discovery
"""

import json
import os
from datetime import datetime

class JobFinderAgent:
    def __init__(self):
        self.profile_file = "my_profile.json"
        self.jobs_file = "daily_jobs.json"
        
    def load_profile(self):
        """Load user profile from JSON file"""
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}
    
    def generate_search_queries(self, profile):
        """Generate search queries for each platform"""
        role = profile.get('desired_role', 'Software Engineer')
        location = profile.get('location', '')
        remote = profile.get('remote_preference', 'yes')
        skills = ' '.join(profile.get('skills', [])[:3])  # Top 3 skills
        
        queries = {
            'linkedin': f"site:linkedin.com/jobs {role} {skills} {location if not remote else 'remote'}",
            'wellfound': f"site:wellfound.com {role} {skills} {location if not remote else 'remote'}",
            'indeed': f"site:indeed.com {role} {skills} {location if not remote else 'remote'}"
        }
        
        return queries
    
    def display_instructions(self, profile, queries):
        """Display manual search instructions"""
        print("="*60)
        print("📋 JOB SEARCH INSTRUCTIONS")
        print("="*60)
        print(f"\n👤 Your Profile:")
        print(f"   Role: {profile.get('desired_role', 'N/A')}")
        print(f"   Skills: {', '.join(profile.get('skills', []))}")
        print(f"   Location: {profile.get('location', 'N/A')}")
        print(f"   Remote: {profile.get('remote_preference', 'N/A')}")
        
        print(f"\n🔍 Search Queries to Use:\n")
        for platform, query in queries.items():
            print(f"{platform.upper()}:")
            print(f"   {query}\n")
        
        print("💡 Manual Steps:")
        print("   1. Copy each search query above")
        print("   2. Paste into Google or directly on the job sites")
        print("   3. Review and bookmark interesting positions")
        print("   4. Apply to 3-5 jobs that match your profile\n")
        
        print("🔗 Direct Links:")
        print(f"   LinkedIn: https://www.linkedin.com/jobs/search/?keywords={profile.get('desired_role', '').replace(' ', '%20')}")
        print(f"   Wellfound: https://wellfound.com/jobs")
        print(f"   Indeed: https://www.indeed.com/jobs?q={profile.get('desired_role', '').replace(' ', '+')}")
        print("\n" + "="*60)
    
    def run(self):
        """Main execution"""
        print("🤖 AI Job Finder Agent Starting...")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        profile = self.load_profile()
        if not profile:
            print("❌ No profile found. Please edit my_profile.json first.")
            return
        
        queries = self.generate_search_queries(profile)
        self.display_instructions(profile, queries)
        
        # Save queries for reference
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "profile": profile,
            "search_queries": queries
        }
        with open(self.jobs_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Search queries saved to {self.jobs_file}")

if __name__ == "__main__":
    agent = JobFinderAgent()
    agent.run()
