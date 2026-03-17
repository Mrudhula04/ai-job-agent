#!/usr/bin/env python3
"""
Find real career URLs for tech companies using web search
"""
import json
import time
import requests
from bs4 import BeautifulSoup

def find_career_url(company_name):
    """Search for company's career page URL"""
    try:
        # Google search for company careers page
        search_query = f"{company_name} careers jobs site"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find first result link
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                
                # Look for career-related URLs
                if any(kw in href.lower() for kw in ['career', 'job', 'workday', 'greenhouse', 'lever', 'ashby']):
                    # Extract actual URL from Google redirect
                    if '/url?q=' in href:
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        return actual_url
                    elif href.startswith('http'):
                        return href
        
        # Fallback: try common patterns
        common_patterns = [
            f"https://careers.{company_name.lower().replace(' ', '')}.com",
            f"https://www.{company_name.lower().replace(' ', '')}.com/careers",
            f"https://jobs.{company_name.lower().replace(' ', '')}.com",
            f"https://{company_name.lower().replace(' ', '')}.com/jobs",
        ]
        
        for url in common_patterns:
            try:
                test_response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
                if test_response.status_code == 200:
                    return url
            except:
                continue
        
        return None
        
    except Exception as e:
        print(f"   Error finding URL for {company_name}: {e}")
        return None

# Load current companies
with open('companies_list.json', 'r') as f:
    companies = json.load(f)

print(f"🔍 Finding real career URLs for {len(companies)} companies...")
print("This will take a while (rate limiting to avoid blocks)\n")

# Only process companies with generic URLs (not already verified)
companies_to_check = []
for company in companies:
    # Check if URL looks generic
    if company['url'].startswith('https://www.techcorp'):
        companies_to_check.append(company)
    elif company['name'].lower().replace(' ', '') not in company['url'].lower():
        companies_to_check.append(company)

print(f"Found {len(companies_to_check)} companies with potentially incorrect URLs")
print(f"Keeping {len(companies) - len(companies_to_check)} companies with verified URLs\n")

# Update URLs
updated = 0
failed = []

for i, company in enumerate(companies_to_check, 1):
    print(f"[{i}/{len(companies_to_check)}] {company['name']}...", end=' ', flush=True)
    
    new_url = find_career_url(company['name'])
    
    if new_url:
        # Find and update in original list
        for c in companies:
            if c['name'] == company['name']:
                c['url'] = new_url
                updated += 1
                print(f"✅ {new_url}")
                break
    else:
        print("❌ Not found")
        failed.append(company['name'])
    
    # Rate limiting
    time.sleep(2)

# Remove companies we couldn't find URLs for
companies = [c for c in companies if c['name'] not in failed]

# Save updated list
with open('companies_list.json', 'w') as f:
    json.dump(companies, f, indent=2)

print(f"\n✅ Updated {updated} career URLs")
print(f"❌ Removed {len(failed)} companies (couldn't find career pages)")
print(f"📊 Final list: {len(companies)} companies")
print(f"💾 Saved to companies_list.json")
