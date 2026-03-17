#!/usr/bin/env python3
"""
Simple Job Finder Agent
Generates personalized job search links and recommendations
"""

import json
import os
from datetime import datetime

class JobFinderAgent:
    def __init__(self):
        self.profile_file = "my_profile.json"
        self.jobs_file = "daily_jobs.json"
        
    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}
    
    def generate_recommendations(self, profile):
        """Generate job search recommendations based on profile"""
        role = profile.get('desired_role', 'Software Engineer')
        skills = profile.get('skills', [])
        experience = profile.get('experience_years', 0)
        location = profile.get('location', '')
        remote = profile.get('remote_preference', 'yes')
        
        recommendations = []
        
        # Java/Spring Boot focused roles
        if 'Java' in skills or 'Spring' in skills or 'Boot' in skills:
            recommendations.append({
                'title': f'Java {role}' if experience < 3 else f'Senior Java {role}',
                'focus': 'Backend Development',
                'keywords': f"Java Spring Boot {role}",
                'platforms': ['LinkedIn', 'Indeed', 'Dice']
            })
            
            recommendations.append({
                'title': 'Backend Engineer',
                'focus': 'Spring Boot / Microservices',
                'keywords': 'Backend Engineer Spring Boot Microservices',
                'platforms': ['LinkedIn', 'Wellfound', 'Indeed']
            })
        
        # Full stack if has frontend skills
        if 'React' in skills or 'Typescript' in skills:
            recommendations.append({
                'title': 'Full Stack Developer',
                'focus': 'Java + React/TypeScript',
                'keywords': f"Full Stack Java React TypeScript",
                'platforms': ['LinkedIn', 'Wellfound', 'Indeed']
            })
        
        # Cloud roles
        if 'AWS' in skills or 'Google Cloud' in skills:
            cloud = 'AWS' if 'AWS' in skills else 'Google Cloud'
            recommendations.append({
                'title': f'{cloud} Developer',
                'focus': 'Cloud Development',
                'keywords': f"Java {cloud} Developer",
                'platforms': ['LinkedIn', 'Indeed']
            })
        
        # Entry-level specific (for 1-2 years experience)
        if experience <= 2:
            recommendations.append({
                'title': 'Junior Software Engineer',
                'focus': 'Entry Level Opportunities',
                'keywords': f"Junior Software Engineer Java {skills[0] if skills else ''}",
                'platforms': ['LinkedIn', 'Indeed', 'Glassdoor']
            })
        
        # Remote-specific if preferred
        if remote == 'yes':
            recommendations.append({
                'title': f'Remote {role}',
                'focus': 'Remote Work',
                'keywords': f"Remote {role} Java Spring Boot",
                'platforms': ['Wellfound', 'Remote.co', 'We Work Remotely']
            })
        
        return recommendations
    
    def generate_search_urls(self, profile):
        """Generate direct search URLs"""
        role = profile.get('desired_role', 'Software Engineer')
        location = profile.get('location', '')
        skills = ' '.join(profile.get('skills', [])[:2])
        
        # URL encode
        role_encoded = role.replace(' ', '%20')
        location_encoded = location.replace(' ', '%20').replace(',', '%2C')
        skills_encoded = skills.replace(' ', '%20')
        
        urls = {
            'LinkedIn Jobs': f"https://www.linkedin.com/jobs/search/?keywords={role_encoded}%20{skills_encoded}&location={location_encoded}",
            'Wellfound (AngelList)': f"https://wellfound.com/jobs",
            'Indeed': f"https://www.indeed.com/jobs?q={role_encoded}%20{skills_encoded}&l={location_encoded}",
            'Google Jobs': f"https://www.google.com/search?q={role_encoded}+{skills_encoded}+jobs+{location_encoded}&ibp=htl;jobs",
            'Remote.co': f"https://remote.co/remote-jobs/developer/"
        }
        
        return urls
    
    def display_daily_report(self, profile, recommendations, urls):
        """Display formatted daily job report"""
        print("\n" + "="*70)
        print(f"📅 DAILY JOB SEARCH REPORT - {datetime.now().strftime('%B %d, %Y')}")
        print("="*70)
        
        print(f"\n👤 YOUR PROFILE:")
        print(f"   Role: {profile.get('desired_role')}")
        print(f"   Experience: {profile.get('experience_years')} years")
        print(f"   Top Skills: {', '.join(profile.get('skills', [])[:4])}")
        print(f"   Location: {profile.get('location')} ({'Remote preferred' if profile.get('remote_preference') == 'yes' else 'On-site'})")
        
        print(f"\n🎯 RECOMMENDED JOB SEARCHES:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n   {i}. {rec['title']}")
            print(f"      Focus: {rec['focus']}")
            print(f"      Search: \"{rec['keywords']}\"")
            print(f"      Platforms: {', '.join(rec['platforms'])}")
        
        print(f"\n🔗 DIRECT SEARCH LINKS:")
        for platform, url in urls.items():
            print(f"\n   {platform}:")
            print(f"   {url}")
        
        print(f"\n💡 TODAY'S ACTION ITEMS:")
        print(f"   ✓ Review 3-5 job postings from each platform")
        print(f"   ✓ Apply to at least 3 positions that match your profile")
        print(f"   ✓ Customize your resume for each application")
        print(f"   ✓ Follow up on applications from previous days")
        
        print("\n" + "="*70 + "\n")
    
    def save_report(self, profile, recommendations, urls):
        """Save daily report to JSON"""
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "profile": profile,
            "recommendations": recommendations,
            "search_urls": urls,
            "generated_at": datetime.now().isoformat()
        }
        with open(self.jobs_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def run(self):
        """Main execution"""
        print("\n🤖 AI Job Finder Agent")
        print(f"⏰ {datetime.now().strftime('%I:%M %p')}")
        
        profile = self.load_profile()
        if not profile:
            print("\n❌ Error: my_profile.json not found or empty")
            print("Please create your profile file first.\n")
            return
        
        recommendations = self.generate_recommendations(profile)
        urls = self.generate_search_urls(profile)
        
        self.display_daily_report(profile, recommendations, urls)
        self.save_report(profile, recommendations, urls)
        
        print(f"✅ Report saved to {self.jobs_file}")
        print("📧 Check this report every morning to stay on track!\n")

if __name__ == "__main__":
    agent = JobFinderAgent()
    agent.run()
