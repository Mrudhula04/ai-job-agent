#!/usr/bin/env python3
"""
Autonomous AI Job Agent
Goal: Find optimal job opportunities by searching US tech company career portals directly

This agent:
- Searches 50+ top US tech company career websites
- Gets accurate, direct job information (no middleman)
- Uses Claude AI for intelligent filtering
- Makes autonomous decisions
- Learns and adapts
- Runs daily automatically
"""

import json
import os
import sys
import time
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

class JobAgent:
    """
    Autonomous AI Agent - Searches US Company Career Portals
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.profile_file = "my_profile.json"
        self.state_file = "agent_state.json"
        self.jobs_file = "daily_jobs.json"
        
        # Agent's goal
        self.goal = "Find optimal jobs by searching US tech company career portals directly for accurate information"
        
        # Load state and profile
        self.state = self.load_state()
        self.profile = self.load_profile()
        
        # Load companies from JSON file (527+ companies)
        self.companies = self.load_companies_list()
        
        # Initialize Selenium driver (lazy loading)
        self.driver = None
        
        print("🤖 AI Job Agent Initialized")
        print(f"📋 Goal: {self.goal}")
        print(f"🏢 Monitoring {len(self.companies)} US tech company career portals")
        print(f"🧠 Day {self.state.get('days_active', 0)} of operation\n")
    
    def get_selenium_driver(self):
        """Get or create Selenium driver with overload protection"""
        # Restart driver every 30 companies to prevent memory leaks and stale sessions
        self.selenium_request_count = getattr(self, 'selenium_request_count', 0) + 1
        
        if self.driver and self.selenium_request_count % 30 == 0:
            print("\n   🔄 Recycling Selenium driver (memory protection)...", flush=True)
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        
        if self.driver is None:
            try:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-infobars')
                chrome_options.add_argument('--disable-notifications')
                chrome_options.add_argument('--disable-popup-blocking')
                chrome_options.add_argument('--disable-translate')
                chrome_options.add_argument('--disable-background-timer-throttling')
                chrome_options.add_argument('--disable-renderer-backgrounding')
                chrome_options.add_argument('--disable-backgrounding-occluded-windows')
                chrome_options.add_argument('--memory-pressure-off')
                chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.driver.set_page_load_timeout(20)
                self.driver.set_script_timeout(15)
            except Exception as e:
                print(f"\n   ⚠️ Selenium driver failed: {e}", flush=True)
                self.driver = None
                raise
        
        return self.driver
    
    def close_selenium(self):
        """Close Selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def load_companies_list(self):
        """Load companies from JSON file"""
        companies_file = 'companies_list.json'
        if os.path.exists(companies_file):
            with open(companies_file, 'r') as f:
                return json.load(f)
        
        # Fallback to minimal list if file doesn't exist
        return [
            {'name': 'Google', 'url': 'https://careers.google.com/jobs/results/', 'type': 'FAANG'},
            {'name': 'Amazon', 'url': 'https://www.amazon.jobs/en/search', 'type': 'FAANG'},
            {'name': 'Microsoft', 'url': 'https://careers.microsoft.com/us/en/search-results', 'type': 'FAANG'},
            {'name': 'Apple', 'url': 'https://jobs.apple.com/en-us/search', 'type': 'FAANG'},
            {'name': 'Meta', 'url': 'https://www.metacareers.com/jobs', 'type': 'FAANG'},
            {'name': 'Netflix', 'url': 'https://jobs.netflix.com/search', 'type': 'FAANG'},
        ]
    
    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}
    
    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        
        return {
            'days_active': 0,
            'total_jobs_found': 0,
            'jobs_shown_to_user': 0,
            'companies_checked': 0,
            'last_run': None,
            'learning_log': []
        }
    
    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def think(self):
        """Agent decides strategy - always searches ALL companies"""
        # User wants agent to go wild on ALL tech companies
        reasoning = f"Searching ALL {len(self.companies)} US tech company career portals for maximum job coverage"
        return 'All', reasoning
    
    def is_non_usa_title(self, title):
        """Quick check if job title/text contains non-USA location indicators"""
        text = title.lower()
        non_usa_in_title = [
            'london', 'united kingdom', ', uk', '(uk)', 'england', 'scotland',
            'berlin', 'munich', 'hamburg', 'frankfurt', ', germany',
            'paris', 'lyon', ', france',
            'amsterdam', 'rotterdam', ', netherlands',
            'dublin', 'cork', ', ireland',
            'zurich', 'geneva', ', switzerland',
            'stockholm', 'gothenburg', ', sweden',
            'copenhagen', ', denmark', 'oslo', ', norway', 'helsinki', ', finland',
            'madrid', 'barcelona', ', spain',
            'milan', 'rome', ', italy',
            'prague', ', czech', 'warsaw', 'krakow', ', poland',
            'budapest', ', hungary', 'bucharest', ', romania', 'vienna', ', austria',
            'brussels', ', belgium', 'lisbon', ', portugal', 'athens', ', greece',
            'toronto', 'vancouver', 'montreal', 'ottawa', 'calgary', ', canada',
            'bangalore', 'bengaluru', 'mumbai', 'hyderabad', 'pune', 'noida',
            'gurgaon', 'gurugram', 'chennai', 'kolkata', 'delhi', ', india',
            'tokyo', 'osaka', ', japan',
            'singapore', ', singapore',
            'hong kong',
            'shanghai', 'beijing', 'shenzhen', 'hangzhou', ', china',
            'seoul', ', korea', 'taipei', ', taiwan',
            'sydney', 'melbourne', 'brisbane', ', australia',
            'auckland', ', new zealand',
            'tel aviv', 'haifa', ', israel',
            'dubai', 'abu dhabi', ', uae',
            'mexico city', ', mexico', 'sao paulo', ', brazil',
            'buenos aires', ', argentina', 'bogota', ', colombia',
            'remote spain', 'remote - spain', 'remote: spain',
            'remote uk', 'remote - uk', 'remote: uk',
            'remote europe', 'remote - europe', 'remote: europe',
            'remote india', 'remote - india', 'remote: india',
            'remote canada', 'remote - canada', 'remote: canada',
            'remote japan', 'remote - japan', 'remote: japan',
            'remote - emea', 'remote emea', 'remote: emea',
            'remote - apac', 'remote apac', 'remote: apac',
            'remote - latam', 'remote latam', 'remote: latam',
            'remote: germany', 'remote: ireland', 'remote: australia',
            'remote: singapore', 'remote: china', 'remote: korea',
            'remote: brazil', 'remote: mexico', 'remote: netherlands',
            'remote: france', 'remote: sweden', 'remote: denmark',
            'remote: norway', 'remote: finland', 'remote: switzerland',
            'remote: austria', 'remote: poland', 'remote: czech',
            'remote: israel', 'remote: argentina', 'remote: colombia',
            'ontario, canada', 'ontario,canada',
            'emea', 'apac', 'latam',
        ]
        for loc in non_usa_in_title:
            if loc in text:
                # Make sure it's not a false positive
                # User wants USA ONLY — reject if ANY non-USA location appears in title
                return True
        return False

    def search_company(self, company):
        """Search a single company's career portal"""
        jobs = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(company['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Special handling for Amazon (uses JSON API)
                if 'amazon.jobs' in company['url']:
                    return self.search_amazon()
                
                # Special handling for Google
                if 'google.com' in company['url'] and 'careers' in company['url']:
                    return self.search_google(soup, company)
                
                # Special handling for Microsoft
                if 'microsoft.com' in company['url'] and 'careers' in company['url']:
                    return self.search_microsoft(company)
                
                # Special handling for Meta
                if 'metacareers.com' in company['url']:
                    return self.search_meta(company)
                
                # Special handling for Netflix
                if 'netflix' in company['url'].lower() and 'jobs' in company['url'].lower():
                    return self.search_netflix(company)
                
                # Special handling for Salesforce
                if 'salesforce.com' in company['url'] and 'careers' in company['url']:
                    return self.search_salesforce(company)
                
                # Special handling for Oracle
                if 'oracle.com' in company['url'] and 'careers' in company['url']:
                    return self.search_oracle(company)
                
                # Special handling for Adobe
                if 'adobe.com' in company['url'] and 'careers' in company['url']:
                    return self.search_adobe(company)
                
                # Special handling for IBM
                if 'ibm.com' in company['url'] and 'careers' in company['url']:
                    return self.search_ibm(company)
                
                # Special handling for SAP
                if 'jobs.sap.com' in company['url']:
                    return self.search_sap(company)
                
                # Special handling for Stripe
                if 'stripe.com' in company['url'] and 'jobs' in company['url']:
                    return self.search_stripe(company)
                
                # Special handling for ServiceNow
                if 'servicenow.com' in company['url'] and 'careers' in company['url']:
                    return self.search_servicenow(company)
                
                # Special handling for HP (Eightfold AI JS site)
                if 'apply.hp.com' in company['url']:
                    return self.search_hp(company)
                
                # Special handling for HPE (JS-heavy career site)
                if 'careers.hpe.com' in company['url']:
                    return self.search_hpe(company)
                
                # Special handling for Dell (Phenom People JS site)
                if 'jobs.dell.com' in company['url']:
                    return self.search_dell(company)
                
                # Special handling for Intuit (Phenom People JS site)
                if 'jobs.intuit.com' in company['url']:
                    return self.search_intuit(company)
                
                # Special handling for Capital One (Phenom People JS site)
                if 'capitalonecareers.com' in company['url']:
                    return self.search_capitalone(company)
                
                # Special handling for Oracle HCM Cloud sites (JPMorgan, etc.)
                if 'oraclecloud.com' in company['url']:
                    return self.search_oracle_hcm(company)
                
                # Special handling for Goldman Sachs (custom React app)
                if 'higher.gs.com' in company['url']:
                    return self.search_goldman(company)
                
                # Special handling for Walmart (JS-heavy career site)
                if 'careers.walmart.com' in company['url']:
                    return self.search_walmart(company)
                
                # Special handling for xAI (React site)
                if 'x.ai' in company['url']:
                    return self.search_xai(company)
                
                # Special handling for Spotify (React site)
                if 'lifeatspotify.com' in company['url']:
                    return self.search_spotify(company)
                
                # Special handling for AT&T (Phenom People JS site)
                if 'att.jobs' in company['url']:
                    return self.search_att(company)
                
                # Special handling for Verizon (JS-heavy career site)
                if 'mycareer.verizon.com' in company['url']:
                    return self.search_verizon(company)
                
                # Special handling for T-Mobile (JS-heavy career site)
                if 'careers.t-mobile.com' in company['url']:
                    return self.search_tmobile(company)
                
                # Special handling for Zoom (JS-heavy career site)
                if 'careers.zoom.us' in company['url']:
                    return self.search_zoom(company)
                
                # Special handling for Qualcomm (Eightfold AI JS site)
                if 'careers.qualcomm.com' in company['url']:
                    return self.search_qualcomm(company)
                
                # Special handling for Palantir (JS-heavy site)
                if 'palantir.com' in company['url']:
                    return self.search_palantir(company)
                
                # Special handling for Jane Street (JS-heavy site)
                if 'janestreet.com' in company['url']:
                    return self.search_janestreet(company)
                
                # Special handling for Palo Alto Networks (Phenom People JS site)
                if 'jobs.paloaltonetworks.com' in company['url']:
                    return self.search_paloalto(company)
                
                # Special handling for Eightfold AI career sites (Johns Hopkins, PayPal, etc.)
                if 'hiring.jhu.edu' in company['url'] or 'eightfold.ai' in company['url']:
                    return self.search_eightfold(company)
                
                # Generic Workday handler (Broadcom, CrowdStrike, Salesforce WD, Autodesk, NVIDIA, Ohio State, etc.)
                # University Workday sites use the same Workday handler — it works the same way
                if 'myworkdayjobs.com' in company['url']:
                    return self.search_workday(company)
                
                # Generic Phenom People handler (UVA, and other /us/en/ style career sites)
                if any(pattern in company['url'] for pattern in ['/us/en/c/', '/us/en/job/', '/us/en/search-results', '/en/job/', '/en/search-jobs/']):
                    return self.search_phenom(company)
                
                # Generic handler for Taleo, PeopleAdmin, iCIMS, and other JS-heavy career sites
                if company.get('type') == 'University' or any(platform in company['url'] for platform in [
                    'taleo.net', 'peopleadmin.com', 'icims.com', 'pageuppeople.com', 'csod.com',
                    'careers-home/jobs',  # iCIMS platform (AMD, etc.)
                    'careers.purdue.edu', 'careers.gatech.edu', 'careers.mit.edu', 'careersearch.stanford.edu',
                    'hr.harvard.edu', 'hr.cornell.edu', 'jobs.berkeley.edu', 'explore.jobs.ufl.edu'
                ]):
                    return self.search_university(company)
                
                # Find all links
                links = soup.find_all('a', href=True)
                
                for link in links:
                    text = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # Skip if text is too short (likely not a job title)
                    if len(text) < 15:
                        continue
                    
                    # Check if it looks like a software engineering job
                    text_lower = text.lower()
                    if any(kw in text_lower for kw in ['software', 'engineer', 'developer', 'java', 'typescript', 'backend', 'frontend', 'full stack', 'fullstack', 'data analyst', 'cloud', 'devops', 'qa', 'it specialist', 'systems admin', 'database', 'web developer', 'application', 'network', 'security analyst', 'research computing', 'hpc', 'machine learning']):
                        # Skip if clearly senior/managerial/faculty
                        if any(word in text_lower for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'director', 'manager', 'vp', 'head of', 'professor', 'faculty', 'dean']):
                            continue
                        
                        # Skip internships
                        if 'intern ' in text_lower or 'internship' in text_lower:
                            continue
                        
                        # Quick title-based non-USA filter
                        if self.is_non_usa_title(text):
                            continue
                        
                        # Make full URL
                        if not href.startswith('http'):
                            if href.startswith('/'):
                                base_url = '/'.join(company['url'].split('/')[:3])
                                href = base_url + href
                            else:
                                continue
                        
                        href_lower = href.lower()
                        
                        # STRICT: Must be an actual job posting URL, not a category page
                        # Reject category/department pages
                        if any(category in href_lower for category in ['/engineering', '/technology', '/departments/', '/teams/', '/locations/', '/all-jobs', '/search']):
                            # Only accept if it has a job ID or specific job indicator
                            if not any(indicator in href_lower for indicator in ['job', 'position', 'req', 'opening', 'jid', 'gh_jid', 'lever', 'greenhouse', 'workday', 'ashby', 'apply']):
                                continue
                        
                        # Must contain job-specific indicators (job ID, posting, etc.)
                        has_job_indicator = any(indicator in href_lower for indicator in [
                            '/job/', '/jobs/', '/position/', '/positions/', '/opening/', '/openings/',
                            '/career/', '/careers/', '/apply/', '/vacancy/', '/vacancies/',
                            'jid=', 'job_id=', 'req=', 'requisition', 'gh_jid', 'lever.co', 
                            'greenhouse.io', 'workday', 'myworkdayjobs', 'ashbyhq', 'jobvite',
                            '/details/', '/view/', '/listing/'
                        ])
                        
                        if not has_job_indicator:
                            continue
                        
                        # Skip non-job URLs (documentation, products, etc.)
                        if any(skip in href_lower for skip in ['/docs/', '/documentation/', '/products/', '/solutions/', '/about/', '/blog/', '/news/', '/press/']):
                            continue
                        
                        # Check if job is in USA by fetching the job page
                        if self.is_usa_job(href):
                            jobs.append({
                                'title': text,
                                'company': company['name'],
                                'company_type': company['type'],
                                'url': href,
                                'source': 'Company Career Portal'
                            })
                        
                        # Limit per company
                        if len(jobs) >= 5:
                            break
        
        except Exception as e:
            pass
        
        return jobs
    
    def search_google(self, soup, company):
        """Special handler for Google careers"""
        jobs = []
        try:
            # Find all links that look like job postings
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                
                # Google job links look like: jobs/results/123456789-job-title
                if 'jobs/results/' in href and '-' in href:
                    # Extract job title from URL
                    parts = href.split('/')
                    if len(parts) >= 3:
                        job_slug = parts[-1].split('?')[0]  # Remove query params
                        
                        # Skip if it's a senior role
                        if any(word in job_slug.lower() for word in ['senior', 'sr-', 'lead-', 'staff-', 'principal-']):
                            continue
                        
                        # Convert slug to title
                        title_parts = job_slug.split('-')[1:]  # Skip job ID
                        title = ' '.join(title_parts).title()
                        
                        # Build full URL
                        if href.startswith('http'):
                            full_url = href
                        elif href.startswith('./'):
                            full_url = 'https://www.google.com/about/careers/applications/' + href[2:]
                        else:
                            full_url = 'https://www.google.com/about/careers/applications/' + href
                        
                        jobs.append({
                            'title': title,
                            'company': 'Google',
                            'company_type': 'FAANG',
                            'url': full_url,
                            'source': 'Company Career Portal'
                        })
                        
                        if len(jobs) >= 5:
                            break
        except Exception as e:
            pass
        
        return jobs
    
    def search_microsoft(self, company):
        """Special handler for Microsoft careers (JavaScript-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])
            
            # Wait for jobs to load
            time.sleep(5)
            
            # Find job cards
            job_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/job/"]')
            
            for element in job_elements[:5]:  # Limit to 5
                try:
                    title = element.text.strip()
                    url = element.get_attribute('href')
                    
                    if len(title) < 15:
                        continue
                    
                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title.lower() for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue
                    
                    jobs.append({
                        'title': title,
                        'company': 'Microsoft',
                        'company_type': 'FAANG',
                        'url': url,
                        'source': 'Company Career Portal'
                    })
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Microsoft: {e}")
        
        return jobs
    
    def search_ibm(self, company):
        """Special handler for IBM careers (JavaScript-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])
            
            # Wait for jobs to load
            time.sleep(12)
            
            # Find job links
            job_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="JobDetail"]')
            
            for link in job_links[:5]:  # Limit to 5
                try:
                    text = link.text.strip()
                    url = link.get_attribute('href')
                    
                    # Extract title from multi-line text
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    
                    # Find the actual job title (usually has keywords)
                    title = None
                    for line in lines:
                        if len(line) > 15 and any(kw in line.lower() for kw in ['engineer', 'developer', 'analyst', 'architect']):
                            title = line
                            break
                    
                    if not title:
                        continue
                    
                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title.lower() for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue
                    
                    jobs.append({
                        'title': title,
                        'company': 'IBM',
                        'company_type': 'Enterprise',
                        'url': url,
                        'source': 'Company Career Portal'
                    })
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for IBM: {e}")
        
        return jobs
    
    def search_adobe(self, company):
        """Special handler for Adobe careers (JavaScript-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])
            
            # Wait for jobs to load
            time.sleep(10)
            
            # Find job links
            job_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/job/R"]')
            
            for link in job_links[:5]:  # Limit to 5
                try:
                    text = link.text.strip()
                    url = link.get_attribute('href')
                    
                    if len(text) < 15:
                        continue
                    
                    # Skip "Apply Now" links
                    if text.lower() == 'apply now':
                        continue
                    
                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in text.lower() for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue
                    
                    jobs.append({
                        'title': text,
                        'company': 'Adobe',
                        'company_type': 'Enterprise',
                        'url': url,
                        'source': 'Company Career Portal'
                    })
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Adobe: {e}")
        
        return jobs
    
    def search_oracle(self, company):
        """Special handler for Oracle careers (JavaScript-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])
            
            # Wait for jobs to load
            time.sleep(12)
            
            # Find job cards
            job_cards = driver.find_elements(By.CSS_SELECTOR, 'div.job-grid-item')
            
            for card in job_cards[:5]:  # Limit to 5
                try:
                    # Get title
                    title_elem = card.find_element(By.CSS_SELECTOR, 'h3, .job-title, [class*="title"]')
                    title = title_elem.text.strip()
                    
                    if len(title) < 15:
                        continue
                    
                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title.lower() for word in ['senior', 'sr.', 'snr', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue
                    
                    # Get link
                    link_elem = card.find_element(By.CSS_SELECTOR, 'a')
                    url = link_elem.get_attribute('href')
                    
                    jobs.append({
                        'title': title,
                        'company': 'Oracle',
                        'company_type': 'Enterprise',
                        'url': url,
                        'source': 'Company Career Portal'
                    })
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Oracle: {e}")
        
        return jobs
    
    def search_salesforce(self, company):
        """Special handler for Salesforce careers (JavaScript-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])
            
            # Wait for jobs to load
            time.sleep(10)
            
            # Find job links
            job_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/jobs/jr"]')
            
            for link in job_links[:5]:  # Limit to 5
                try:
                    text = link.text.strip()
                    url = link.get_attribute('href')
                    
                    if len(text) < 15:
                        continue
                    
                    # Must be relevant role
                    if not any(kw in text.lower() for kw in ['engineer', 'developer', 'software', 'analyst', 'qa', 'cloud']):
                        continue
                    
                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in text.lower() for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue
                    
                    jobs.append({
                        'title': text,
                        'company': 'Salesforce',
                        'company_type': 'Enterprise',
                        'url': url,
                        'source': 'Company Career Portal'
                    })
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Salesforce: {e}")
        
        return jobs
    
    def search_netflix(self, company):
        """Special handler for Netflix careers (JavaScript-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])
            
            # Wait for jobs to load
            time.sleep(10)
            
            # Find job cards
            job_cards = driver.find_elements(By.CSS_SELECTOR, 'div.position-card, div[class*="position"]')
            
            for card in job_cards[:5]:  # Limit to 5
                try:
                    text = card.text.strip()
                    
                    if len(text) < 20:
                        continue
                    
                    # Extract title (first line)
                    lines = text.split('\n')
                    title = lines[0].strip()
                    
                    if len(title) < 15:
                        continue
                    
                    # Must be software/engineering related
                    if not any(kw in title.lower() for kw in ['engineer', 'developer', 'software']):
                        continue
                    
                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title.lower() for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue
                    
                    # Try to find the link within the card
                    try:
                        link = card.find_element(By.CSS_SELECTOR, 'a')
                        url = link.get_attribute('href')
                    except:
                        # If no link, try to click the card itself
                        url = company['url']  # Fallback
                    
                    jobs.append({
                        'title': title,
                        'company': 'Netflix',
                        'company_type': 'FAANG',
                        'url': url if url else company['url'],
                        'source': 'Company Career Portal'
                    })
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Netflix: {e}")
        
        return jobs
    
    def search_meta(self, company):
        """Special handler for Meta careers (JavaScript-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])
            
            # Wait longer for jobs to load (Meta is slow)
            time.sleep(12)
            
            # Find all clickable elements that might be jobs
            clickable = driver.find_elements(By.CSS_SELECTOR, 'a, button, div[role="button"]')
            
            for element in clickable:
                try:
                    text = element.text.strip()
                    url = element.get_attribute('href')
                    
                    # Must have URL with job_details
                    if not url or 'job_details' not in url:
                        continue
                    
                    # Must have reasonable length text with job keywords
                    if len(text) < 20:
                        continue
                    
                    if not any(kw in text.lower() for kw in ['engineer', 'developer', 'software']):
                        continue
                    
                    # Extract just the title (first line)
                    title = text.split('\n')[0].strip()
                    
                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title.lower() for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue
                    
                    jobs.append({
                        'title': title,
                        'company': 'Meta',
                        'company_type': 'FAANG',
                        'url': url,
                        'source': 'Company Career Portal'
                    })
                    
                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Meta: {e}")
        
        return jobs
    
    def search_amazon(self):
        """Special handler for Amazon jobs (uses API)"""
        jobs = []
        try:
            # Amazon's job search API — fetch more results to filter from
            api_url = "https://www.amazon.jobs/en/search.json?offset=0&result_limit=50&sort=recent&category[]=software-development&base_query=software+engineer"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'jobs' in data:
                    for job in data['jobs']:
                        title = job.get('title', '')
                        job_id = job.get('id_icims', '')
                        location = job.get('location', '')
                        
                        # USA only — location starts with "US,"
                        if not location.startswith('US,'):
                            continue
                        
                        title_lower = title.lower()
                        
                        # Skip senior/mid-level roles and internships
                        if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                            continue
                        
                        # Check experience in basic_qualifications
                        quals = job.get('basic_qualifications', '').lower()
                        import re
                        exp_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', quals)
                        if exp_matches and max(int(y) for y in exp_matches) >= 3:
                            continue
                        
                        if job_id:
                            jobs.append({
                                'title': title,
                                'company': 'Amazon',
                                'company_type': 'FAANG',
                                'location': job.get('normalized_location', 'USA'),
                                'url': f'https://www.amazon.jobs/en/jobs/{job_id}',
                                'source': 'Company Career Portal'
                            })
                        
                        if len(jobs) >= 5:
                            break
        except Exception as e:
            pass
        
        return jobs

    def search_sap(self, company):
        """Special handler for SAP careers (JavaScript-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            # Use the filtered URL for software development in US
            url = "https://jobs.sap.com/search/?createNewAlert=false&q=software+engineer&locationsearch=United+States&optionsFacetsDD_department=Software-Design+and+Development&optionsFacetsDD_country=US"
            driver.get(url)

            time.sleep(10)

            # Find job links
            job_links = driver.find_elements(By.CSS_SELECTOR, 'a.jobTitle-link, a[href*="/job/"]')

            for link in job_links[:5]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if len(text) < 10:
                        continue

                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in text.lower() for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://jobs.sap.com' + href

                    jobs.append({
                        'title': text,
                        'company': 'SAP',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for SAP: {e}")

        return jobs

    def search_stripe(self, company):
        """Special handler for Stripe careers (JavaScript-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            url = "https://stripe.com/jobs/search?office_locations=North+America--San+Francisco+Bridge+HQ&office_locations=North+America--Seattle&office_locations=North+America--New+York&office_locations=North+America--Chicago"
            driver.get(url)

            time.sleep(10)

            # Find job links
            job_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/jobs/listing/"]')

            for link in job_links[:5]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if len(text) < 10:
                        continue

                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in text.lower() for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://stripe.com' + href

                    jobs.append({
                        'title': text,
                        'company': 'Stripe',
                        'company_type': 'Unicorn',
                        'url': href,
                        'source': 'Company Career Portal'
                    })
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Stripe: {e}")

        return jobs

    def search_servicenow(self, company):
        """Special handler for ServiceNow careers (JavaScript-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            url = "https://careers.servicenow.com/jobs/?search=software+engineer&country=United+States"
            driver.get(url)

            time.sleep(10)

            # Find job links
            job_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/jobs/"]')

            for link in job_links[:5]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if len(text) < 15:
                        continue

                    # Must be relevant
                    if not any(kw in text.lower() for kw in ['engineer', 'developer', 'software', 'analyst', 'qa', 'cloud']):
                        continue

                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in text.lower() for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://careers.servicenow.com' + href

                    jobs.append({
                        'title': text,
                        'company': 'ServiceNow',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for ServiceNow: {e}")

        return jobs

    def search_workday(self, company):
        """Generic handler for Workday-based career sites (JS-heavy, need Selenium)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            # Workday sites are slow to render
            time.sleep(12)

            # Try multiple Workday CSS selectors (varies by implementation)
            selectors = [
                'a[data-automation-id="jobTitle"]',           # Common Workday pattern
                'a[data-automation-id="job-title"]',
                'a.css-19uc56f',                              # Workday styled links
                'li.css-1q2dra3 a',                           # Job list items
                'a[href*="/job/"]',                           # Generic job links
                'a[href*="/details/"]',
                'div[data-automation-id="jobResults"] a',
                'section[data-automation-id="jobResults"] a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            # If no specific selectors worked, try broader approach
            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 15 and ('/job/' in href or '/details/' in href):
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:15]:  # Check more, filter down
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    if len(text) < 10:
                        continue

                    # Extract just the title (first line if multi-line)
                    lines = text.split('\n')
                    title = lines[0].strip()
                    # Remaining lines often contain location info
                    extra_text = ' '.join(lines[1:]).lower().strip()

                    if len(title) < 10:
                        continue

                    # Check location from the listing card text
                    # If location text exists and has non-USA indicators, skip
                    non_usa_words = ['uk', 'united kingdom', 'england', 'japan', 'india', 'canada',
                                     'germany', 'france', 'ireland', 'australia', 'singapore',
                                     'china', 'korea', 'brazil', 'mexico', 'netherlands',
                                     'london', 'tokyo', 'bangalore', 'bengaluru', 'toronto',
                                     'dublin', 'sydney', 'berlin', 'paris', 'amsterdam',
                                     'mumbai', 'hyderabad', 'pune', 'shanghai', 'beijing',
                                     'hong kong', 'seoul', 'taipei', 'vancouver', 'montreal',
                                     'munich', 'zurich', 'stockholm', 'copenhagen', 'oslo',
                                     'prague', 'warsaw', 'budapest', 'tel aviv', 'dubai']
                    if extra_text and any(loc in extra_text for loc in non_usa_words):
                        continue  # USA ONLY — any non-USA location = reject

                    # Must look like a tech role
                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'fullstack',
                        'sre', 'platform', 'infrastructure', 'security engineer'
                    ]):
                        continue

                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'vp', 'head of', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    # Extract location from extra text
                    location = extra_text.strip() if extra_text else 'USA'

                    jobs.append({
                        'title': title,
                        'company': company['name'],
                        'company_type': company.get('type', 'Enterprise'),
                        'location': location,
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for {company['name']} (Workday): {e}")

        return jobs

    
    def search_university(self, company):
        """Special handler for university career sites (Taleo, PeopleAdmin, iCIMS, etc.)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])
            time.sleep(8)

            # University job title keywords
            uni_tech_keywords = [
                'software', 'engineer', 'developer', 'programmer', 'analyst',
                'data', 'cloud', 'devops', 'web developer', 'application',
                'it specialist', 'systems administrator', 'database',
                'information technology', 'full stack', 'backend', 'frontend',
                'qa', 'quality assurance', 'network', 'security analyst',
                'research computing', 'hpc', 'machine learning', 'ai ',
                'python', 'java', 'computing', 'technical'
            ]

            # Job link selectors
            selectors = [
                'a[href*="/job/"]', 'a[href*="/jobs/"]',
                'a[href*="/position/"]', 'a[href*="/posting/"]',
                'a[href*="/postings/"]', 'a[href*="/requisition"]',
                'a[href*="jobdetail"]', 'a[href*="JobDetail"]',
                'a[href*="requisitions/"]', 'a[href*="/details/"]',
                'a[href*="/go/"]',  # Purdue-style filtered pages
                'a.job-title', 'a.jobTitle-link',
                'td.colTitle a', 'div.job-title a',
                'tr.data-row a', 'div.job-listing a',
            ]

            # FIRST: Check if job links already exist on the page (pre-filtered URLs like Purdue)
            job_links = []
            for selector in selectors:
                found = driver.find_elements(By.CSS_SELECTOR, selector)
                if found:
                    job_links.extend(found)

            # Broader fallback check
            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    href_lower = href.lower()
                    if len(text) > 10 and any(ind in href_lower for ind in ['/job', '/position', '/posting', '/requisition', 'jobdetail', '/details']):
                        job_links.append(link)

            # ONLY if no job links found, try searching
            if not job_links:
                search_selectors = [
                    'input[type="search"]',
                    'input[type="text"]',
                    'input[name="q"]',
                    'input[name="query"]',
                    'input[name="keyword"]',
                    'input[name="keywords"]',
                    'input[name="search"]',
                    'input[id*="search"]',
                    'input[id*="keyword"]',
                    'input[placeholder*="Search"]',
                    'input[placeholder*="search"]',
                    'input[placeholder*="keyword"]',
                    'input[aria-label*="Search"]',
                    'input[aria-label*="search"]',
                ]

                search_filled = False
                for selector in search_selectors:
                    try:
                        search_box = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_box.is_displayed():
                            search_box.clear()
                            search_box.send_keys('software engineer')
                            search_box.send_keys('\n')
                            search_filled = True
                            time.sleep(8)
                            break
                    except:
                        continue

                # If no search box, try clicking a search/browse button
                if not search_filled:
                    try:
                        buttons = driver.find_elements(By.CSS_SELECTOR, 'a[href*="search"], a[href*="jobs"], button')
                        for btn in buttons:
                            text = btn.text.strip().lower()
                            if text in ['search jobs', 'search', 'browse jobs', 'view all jobs', 'job search', 'find jobs']:
                                btn.click()
                                time.sleep(5)
                                for selector in search_selectors:
                                    try:
                                        search_box = driver.find_element(By.CSS_SELECTOR, selector)
                                        if search_box.is_displayed():
                                            search_box.clear()
                                            search_box.send_keys('software engineer')
                                            search_box.send_keys('\n')
                                            time.sleep(8)
                                            break
                                    except:
                                        continue
                                break
                    except:
                        pass

                # Re-check for job links after searching
                for selector in selectors:
                    found = driver.find_elements(By.CSS_SELECTOR, selector)
                    if found:
                        job_links.extend(found)

                if not job_links:
                    all_links = driver.find_elements(By.TAG_NAME, 'a')
                    for link in all_links:
                        href = link.get_attribute('href') or ''
                        text = link.text.strip()
                        href_lower = href.lower()
                        if len(text) > 10 and any(ind in href_lower for ind in ['/job', '/position', '/posting', '/requisition', 'jobdetail', '/details']):
                            job_links.append(link)

            # Process found job links
            seen_urls = set()
            for link in job_links[:20]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 8:
                        continue

                    title_lower = title.lower()

                    if not any(kw in title_lower for kw in uni_tech_keywords):
                        continue

                    # Skip senior/mid-level roles and internships
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        base_url = '/'.join(company['url'].split('/')[:3])
                        href = base_url + href

                    jobs.append({
                        'title': title,
                        'company': company['name'],
                        'company_type': 'University',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for {company['name']}: {e}")

        return jobs

    def search_phenom(self, company):
        """Generic handler for Phenom People career sites (UVA, etc.)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])
            time.sleep(12)

            # Phenom People uses /job/ or /en/job/ style links
            selectors = [
                'a[href*="/us/en/job/"]',
                'a[href*="/en/job/"]',
                'a[href*="/job/"]',
                'a[href*="/jobs/"]',
                'a.job-title-link',
                'a.job-title',
                'div.job-card a',
                'li.jobs-list-item a',
                'a[phx-track-id]',
            ]

            job_links = []
            for selector in selectors:
                found = driver.find_elements(By.CSS_SELECTOR, selector)
                if found:
                    job_links = found
                    break

            # Fallback: find all links with /job/ in href
            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if '/job/' in href and link.text.strip():
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:15]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    lines = text.split('\n')
                    title = lines[0].strip()
                    extra_text = ' '.join(lines[1:]).lower().strip()

                    if len(title) < 10:
                        continue

                    # Check location from listing card text
                    non_usa_words = ['uk', 'united kingdom', 'england', 'japan', 'india', 'canada',
                                     'germany', 'france', 'ireland', 'australia', 'singapore',
                                     'china', 'korea', 'brazil', 'mexico', 'netherlands',
                                     'london', 'tokyo', 'bangalore', 'bengaluru', 'toronto',
                                     'dublin', 'sydney', 'berlin', 'paris', 'amsterdam',
                                     'mumbai', 'hyderabad', 'pune', 'shanghai', 'beijing',
                                     'hong kong', 'seoul', 'taipei', 'vancouver', 'montreal',
                                     'munich', 'zurich', 'stockholm', 'copenhagen', 'oslo',
                                     'prague', 'warsaw', 'budapest', 'tel aviv', 'dubai']
                    if extra_text and any(loc in extra_text for loc in non_usa_words):
                        continue  # USA ONLY — any non-USA location = reject

                    title_lower = title.lower()

                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre',
                        'platform', 'programmer', 'application', 'it specialist',
                        'systems administrator', 'database', 'web developer',
                        'information technology', 'computing', 'technical'
                    ]):
                        continue

                    # Skip senior/mid-level roles and internships
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        base_url = '/'.join(company['url'].split('/')[:3])
                        href = base_url + href

                    jobs.append({
                        'title': title,
                        'company': company['name'],
                        'company_type': company.get('type', 'Enterprise'),
                        'location': extra_text.strip() if extra_text else 'USA',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for {company['name']} (Phenom): {e}")

        return jobs

    def search_dell(self, company):
        """Special handler for Dell careers (Phenom People JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            # Dell uses Phenom People - job cards with specific structure
            selectors = [
                'a[href*="/en/job/"]',
                'a[href*="/job/"]',
                'a.job-title-link',
                'div.job-card a',
                'li.jobs-list-item a',
                'a[phx-track-id]',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            # Fallback: find all links with /job/ in href
            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if '/job/' in href and link.text.strip():
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()

                    if len(title) < 10:
                        continue

                    title_lower = title.lower()

                    # Must be a tech role
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://jobs.dell.com' + href

                    jobs.append({
                        'title': title,
                        'company': 'Dell',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Dell: {e}")

        return jobs

    def search_intuit(self, company):
        """Special handler for Intuit careers (Phenom People JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/job/"]',
                'a.job-title-link',
                'div.job-card a',
                'li.jobs-list-item a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if '/job/' in href and link.text.strip():
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://jobs.intuit.com' + href

                    jobs.append({
                        'title': title,
                        'company': 'Intuit',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Intuit: {e}")

        return jobs

    def search_capitalone(self, company):
        """Special handler for Capital One careers (Phenom People JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/job/"]',
                'a.job-title-link',
                'div.job-card a',
                'li.jobs-list-item a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if '/job/' in href and link.text.strip():
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://www.capitalonecareers.com' + href

                    jobs.append({
                        'title': title,
                        'company': 'Capital One',
                        'company_type': 'Fintech',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Capital One: {e}")

        return jobs

    def search_oracle_hcm(self, company):
        """Special handler for Oracle HCM Cloud career sites (JPMorgan, etc.)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(15)  # Oracle HCM is slow

            selectors = [
                'a[href*="/jobs/"]',
                'a[href*="/job/"]',
                'a[href*="requisitionId"]',
                'a.job-list-item',
                'div.job-card a',
                'span.job-title',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 10 and ('job' in href.lower() or 'requisition' in href.lower()):
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    jobs.append({
                        'title': title,
                        'company': company['name'],
                        'company_type': company.get('type', 'Fintech'),
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for {company['name']} (Oracle HCM): {e}")

        return jobs

    def search_goldman(self, company):
        """Special handler for Goldman Sachs careers (custom React app)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            # GS uses card-based layout
            selectors = [
                'a[href*="/roles/"]',
                'a[href*="/jobs/"]',
                'a[href*="/job/"]',
                'div[class*="card"] a',
                'div[class*="result"] a',
                'div[class*="listing"] a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 10 and ('gs.com' in href or 'goldmansachs' in href) and any(x in href.lower() for x in ['/role', '/job', '/position']):
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'vp', 'vice president', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    jobs.append({
                        'title': title,
                        'company': 'Goldman Sachs',
                        'company_type': 'Fintech',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Goldman Sachs: {e}")

        return jobs

    def search_walmart(self, company):
        """Special handler for Walmart careers (JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/us/en/job/"]',
                'a[href*="/job/"]',
                'a[href*="/jobs/"]',
                'div.job-card a',
                'div[class*="result"] a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 10 and '/job/' in href.lower():
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    # Skip senior/mid-level roles and internships (0-2 years only)
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://careers.walmart.com' + href

                    jobs.append({
                        'title': title,
                        'company': 'Walmart',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Walmart: {e}")

        return jobs

    def search_xai(self, company):
        """Special handler for xAI careers (React site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(10)

            # Find job links
            all_links = driver.find_elements(By.TAG_NAME, 'a')

            seen_urls = set()
            for link in all_links:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href') or ''

                    if not href or href in seen_urls or len(text) < 10:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    title_lower = title.lower()

                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform', 'infrastructure'
                    ]):
                        continue

                    # Skip senior/mid-level roles and internships
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    jobs.append({
                        'title': title,
                        'company': 'xAI',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for xAI: {e}")

        return jobs

    def search_spotify(self, company):
        """Special handler for Spotify careers (React site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/jobs/"]',
                'a[href*="/job/"]',
                'div[class*="job"] a',
                'li[class*="job"] a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 10 and '/jobs/' in href.lower():
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform', 'machine learning'
                    ]):
                        continue

                    # Skip senior/mid-level roles and internships
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    jobs.append({
                        'title': title,
                        'company': 'Spotify',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Spotify: {e}")

        return jobs

    def search_att(self, company):
        """Special handler for AT&T careers (Phenom People JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/job/"]',
                'a.job-title-link',
                'div.job-card a',
                'li.jobs-list-item a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if '/job/' in href and link.text.strip():
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    # Skip senior/mid-level roles and internships
                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://www.att.jobs' + href

                    jobs.append({
                        'title': title,
                        'company': 'AT&T',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for AT&T: {e}")

        return jobs

    def search_verizon(self, company):
        """Special handler for Verizon careers (JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/jobs/"]',
                'a[href*="/job/"]',
                'a[href*="job-id"]',
                'div.job-card a',
                'div[class*="result"] a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 10 and ('/job' in href.lower()):
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://mycareer.verizon.com' + href

                    jobs.append({
                        'title': title,
                        'company': 'Verizon',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Verizon: {e}")

        return jobs

    def search_tmobile(self, company):
        """Special handler for T-Mobile careers (JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/jobs/"]',
                'a[href*="/job/"]',
                'div.job-card a',
                'div[class*="result"] a',
                'li[class*="job"] a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 10 and '/job' in href.lower():
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://careers.t-mobile.com' + href

                    jobs.append({
                        'title': title,
                        'company': 'T-Mobile',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for T-Mobile: {e}")

        return jobs

    def search_zoom(self, company):
        """Special handler for Zoom careers (JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/jobs/"]',
                'a[href*="/job/"]',
                'div.job-card a',
                'div[class*="result"] a',
                'li[class*="job"] a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 10 and '/job' in href.lower():
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://careers.zoom.us' + href

                    jobs.append({
                        'title': title,
                        'company': 'Zoom',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Zoom: {e}")

        return jobs

    def search_qualcomm(self, company):
        """Special handler for Qualcomm careers (Eightfold AI JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/job/"]',
                'a[href*="/careers/"]',
                'div.position-card a',
                'div[class*="job"] a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 10 and ('/job/' in href or '/careers/' in href) and 'qualcomm' in href:
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    jobs.append({
                        'title': title,
                        'company': 'Qualcomm',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Qualcomm: {e}")

        return jobs

    def search_palantir(self, company):
        """Special handler for Palantir careers (JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(10)

            # Palantir lists roles with links
            all_links = driver.find_elements(By.TAG_NAME, 'a')

            seen_urls = set()
            for link in all_links:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href') or ''

                    if not href or href in seen_urls or len(text) < 10:
                        continue

                    # Must be a job posting link
                    if '/careers/' not in href and '/jobs/' not in href and '/role/' not in href:
                        continue
                    # Skip the main careers page itself
                    if href.rstrip('/') == 'https://www.palantir.com/careers' or 'open-positions' in href:
                        continue

                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    title_lower = title.lower()

                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform', 'infrastructure'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    jobs.append({
                        'title': title,
                        'company': 'Palantir',
                        'company_type': 'Startup',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Palantir: {e}")

        return jobs

    def search_janestreet(self, company):
        """Special handler for Jane Street careers (JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(10)

            all_links = driver.find_elements(By.TAG_NAME, 'a')

            seen_urls = set()
            for link in all_links:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href') or ''

                    if not href or href in seen_urls or len(text) < 10:
                        continue
                    if 'open-roles' in href and '?' not in href.split('open-roles')[-1]:
                        continue
                    if '/position/' not in href and '/role/' not in href and '/open-roles/' not in href:
                        continue

                    seen_urls.add(href)
                    title = text.split('\n')[0].strip()
                    title_lower = title.lower()

                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform', 'infrastructure', 'linux', 'network'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    jobs.append({
                        'title': title,
                        'company': 'Jane Street',
                        'company_type': 'Fintech',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Jane Street: {e}")

        return jobs

    def search_paloalto(self, company):
        """Special handler for Palo Alto Networks careers (Phenom People JS site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/job/"]',
                'a.job-title-link',
                'div.job-card a',
                'li.jobs-list-item a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if '/job/' in href and link.text.strip():
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform', 'security'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://jobs.paloaltonetworks.com' + href

                    jobs.append({
                        'title': title,
                        'company': 'Palo Alto Networks',
                        'company_type': 'Security',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for Palo Alto Networks: {e}")

        return jobs

    def search_eightfold(self, company):
        """Special handler for Eightfold AI career sites (Johns Hopkins, etc.)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            selectors = [
                'a[href*="/job/"]',
                'a[href*="/careers/"]',
                'div.position-card a',
                'div[class*="job"] a',
                'a[data-test-id="job-link"]',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 10 and ('/job/' in href or '/careers/' in href):
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform',
                        'it specialist', 'systems administrator', 'database', 'programmer',
                        'information technology', 'web developer', 'application', 'technical'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    jobs.append({
                        'title': title,
                        'company': company['name'],
                        'company_type': company.get('type', 'University'),
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for {company['name']} (Eightfold): {e}")

        return jobs

















    def search_hp(self, company):
        """Special handler for HP careers (Eightfold AI JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(10)

            # Eightfold AI platform - similar to Microsoft careers
            selectors = [
                'a[href*="/job/"]',
                'a[href*="/careers/"]',
                'div.position-card a',
                'div[class*="job"] a',
                'a[data-test-id="job-link"]',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            # Fallback: broader search
            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 15 and ('/job/' in href or '/careers/' in href) and 'apply.hp.com' in href:
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()

                    if len(title) < 10:
                        continue

                    title_lower = title.lower()

                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    jobs.append({
                        'title': title,
                        'company': 'HP',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for HP: {e}")

        return jobs

    def search_hpe(self, company):
        """Special handler for HPE careers (JS-heavy site)"""
        jobs = []
        try:
            driver = self.get_selenium_driver()
            driver.get(company['url'])

            time.sleep(12)

            # HPE uses Phenom People style
            selectors = [
                'a[href*="/us/en/job/"]',
                'a[href*="/job/"]',
                'a.job-title',
                'a[data-ph-at-id="job-link"]',
                'div.job-card a',
            ]

            job_links = []
            for selector in selectors:
                job_links = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_links:
                    break

            if not job_links:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if len(text) > 15 and '/job/' in href:
                        job_links.append(link)

            seen_urls = set()
            for link in job_links[:10]:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')

                    if not href or href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title = text.split('\n')[0].strip()
                    if len(title) < 10:
                        continue

                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in [
                        'engineer', 'developer', 'software', 'analyst', 'qa', 'cloud',
                        'devops', 'data', 'backend', 'frontend', 'full stack', 'sre', 'platform'
                    ]):
                        continue

                    if any(word in title_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'staff', 'principal', 'director', 'manager', 'intern ', 'internship', ' iii', ' iv', ' v', 'mid-level', 'mid level']):
                        continue

                    if not href.startswith('http'):
                        href = 'https://careers.hpe.com' + href

                    jobs.append({
                        'title': title,
                        'company': 'HPE',
                        'company_type': 'Enterprise',
                        'url': href,
                        'source': 'Company Career Portal'
                    })

                    if len(jobs) >= 5:
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Error with Selenium for HPE: {e}")

        return jobs





    
    def is_usa_job(self, job_url):
        """Check if job is located in USA and requires 0-2 years experience only"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(job_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                result = self.check_usa_and_experience(response.text)
                if result is not None:
                    return result
            
            # If requests didn't give a clear answer, try Selenium
            try:
                driver = self.get_selenium_driver()
                driver.get(job_url)
                time.sleep(5)
                page_text = driver.page_source
                result = self.check_usa_and_experience(page_text)
                if result is not None:
                    return result
            except:
                pass
        
        except Exception as e:
            pass
        
        # If we can't determine, reject to be safe
        return False
    
    def check_usa_and_experience(self, page_content):
        """Check page content for USA location and 0-2 years experience. Returns True/False/None"""
        import re
        content = page_content.lower()
        
        # If page is too short (JS shell), return None to signal "can't determine"
        if len(content) < 1500:
            return None
        
        # Reject if job page explicitly requires 3+ years experience
        exp_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)',
            r'(?:experience|exp)\s*(?:of\s+)?(\d+)\+?\s*(?:years?|yrs?)',
            r'minimum\s+(\d+)\s*(?:years?|yrs?)',
            r'at\s+least\s+(\d+)\s*(?:years?|yrs?)',
        ]
        for pattern in exp_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                years = int(match)
                if years >= 4:
                    return False
        
        # STRICT non-USA locations — reject immediately if found
        non_usa_locations = [
            # Europe
            'london', 'manchester', 'edinburgh', 'cambridge, uk', 'bristol, uk', 'oxford, uk',
            'berlin', 'munich', 'hamburg', 'frankfurt', 'paris', 'lyon', 'amsterdam', 'rotterdam',
            'dublin', 'cork', 'zurich', 'geneva', 'stockholm', 'gothenburg', 'copenhagen',
            'oslo', 'helsinki', 'lisbon', 'madrid', 'barcelona', 'milan', 'rome',
            'prague', 'warsaw', 'krakow', 'budapest', 'bucharest', 'vienna',
            'brussels', 'luxembourg', 'athens',
            # UK / EU markers
            'united kingdom', ', uk', ', england', ', scotland', ', wales',
            ', germany', ', france', ', netherlands', ', ireland', ', spain', ', italy',
            ', sweden', ', norway', ', denmark', ', finland', ', switzerland', ', austria',
            ', poland', ', czech', ', hungary', ', romania', ', belgium', ', portugal',
            # Canada
            'toronto', 'vancouver', 'montreal', 'ottawa', 'calgary', 'waterloo, on',
            ', canada', 'british columbia', 'ontario, ca',
            # Asia
            'bangalore', 'bengaluru', 'mumbai', 'hyderabad', 'pune', 'noida', 'gurgaon',
            'gurugram', 'chennai', 'kolkata', 'delhi', ', india',
            'tokyo', 'osaka', ', japan',
            'singapore', ', singapore',
            'hong kong',
            'shanghai', 'beijing', 'shenzhen', 'hangzhou', ', china',
            'seoul', ', korea', 'taipei', ', taiwan',
            'kuala lumpur', ', malaysia', 'jakarta', ', indonesia',
            'bangkok', ', thailand', 'ho chi minh', ', vietnam',
            # Australia / NZ
            'sydney', 'melbourne', 'brisbane', 'perth', ', australia',
            'auckland', ', new zealand',
            # Middle East
            'tel aviv', 'haifa', ', israel', 'dubai', 'abu dhabi', ', uae',
            # Latin America
            'mexico city', ', mexico', 'sao paulo', ', brazil', 'buenos aires', ', argentina',
            'bogota', ', colombia', 'santiago', ', chile', 'lima', ', peru',
            # Region markers
            'location: europe', 'location: asia', 'location: emea', 'location: apac',
            'location: india', 'location: canada', 'location: uk', 'location: germany',
            'location: ireland', 'location: australia', 'location: japan',
            'location: singapore', 'location: china', 'location: korea',
            'remote - europe', 'remote - uk', 'remote - eu', 'remote - asia',
            'remote - india', 'remote - canada', 'remote - japan', 'remote - apac',
            'remote - emea', 'remote - latam',
            'emea region', 'apac region', 'latam region',
        ]
        
        # Check for non-USA locations
        has_non_usa = False
        for location in non_usa_locations:
            if location in content:
                has_non_usa = True
                break
        
        # Check for USA indicators
        usa_indicators = [
            'united states', ', usa', 'u.s.a', ', us ',
            # States
            'california', 'new york', 'texas', 'washington', 'massachusetts',
            'illinois', 'florida', 'colorado', 'georgia', 'virginia',
            'north carolina', 'south carolina', 'oregon', 'arizona',
            'minnesota', 'michigan', 'ohio', 'pennsylvania', 'new jersey',
            'maryland', 'connecticut', 'utah', 'nevada', 'tennessee',
            'indiana', 'missouri', 'wisconsin', 'iowa', 'kansas',
            'alabama', 'kentucky', 'louisiana', 'nebraska', 'oklahoma',
            'arkansas', 'mississippi', 'idaho', 'montana', 'new hampshire',
            'rhode island', 'delaware', 'vermont', 'wyoming', 'maine',
            'hawaii', 'alaska', 'new mexico', 'west virginia', 'south dakota',
            'north dakota',
            # Major US cities
            'san francisco', 'seattle', 'austin', 'boston', 'chicago', 'atlanta',
            'los angeles', 'san jose', 'san diego', 'denver', 'portland, or',
            'dallas', 'houston', 'phoenix', 'philadelphia', 'pittsburgh',
            'raleigh', 'charlotte', 'nashville', 'salt lake city', 'detroit',
            'minneapolis', 'miami', 'tampa', 'orlando', 'indianapolis',
            'san antonio', 'columbus, oh', 'jacksonville', 'memphis',
            'baltimore', 'milwaukee', 'albuquerque', 'tucson', 'fresno',
            'sacramento', 'kansas city', 'mesa', 'omaha', 'tulsa',
            'arlington', 'new orleans', 'cleveland', 'bakersfield',
            'aurora', 'anaheim', 'honolulu', 'santa ana', 'riverside',
            'lexington', 'stockton', 'henderson', 'st. paul', 'st. louis',
            'cincinnati', 'irvine', 'fremont', 'richmond, va', 'boise',
            'spokane', 'des moines', 'morrisville', 'sunnyvale', 'mountain view',
            'palo alto', 'menlo park', 'cupertino', 'redmond', 'bellevue',
            'kirkland', 'cambridge, ma', 'somerville', 'hoboken', 'jersey city',
            'brooklyn', 'manhattan',
            # Remote US
            'remote - us', 'remote - usa', 'remote - united states', 'remote us',
            'remote, us', 'remote, usa', 'us remote', 'usa remote',
            'location: united states', 'location: usa', 'location: us',
            'united states of america',
        ]
        
        has_usa = False
        for indicator in usa_indicators:
            if indicator in content:
                has_usa = True
                break
        
        # Decision logic
        if has_usa and not has_non_usa:
            return True
        if has_non_usa and not has_usa:
            return False
        if has_usa and has_non_usa:
            # Page has both — this is normal for big companies (global office list in footer).
            # The job itself is likely USA since we already filtered non-USA from the TITLE
            # in is_non_usa_title(). If USA indicator is present, accept it.
            return True
        
        # No location info found at all — reject to be safe
        return False
    
    def evaluate_job(self, job):
        """Use Claude to evaluate job match"""
        prompt = f"""Quick job evaluation for OPT candidate:

JOB: {job['title']} at {job['company']} ({job.get('company_type', 'Unknown')})

CANDIDATE:
- Education: {self.profile.get('education', "Master's in Computer Information Science")}
- Experience: {self.profile.get('experience_years', 0)} year(s) of professional experience
- Max experience required: {self.profile.get('max_experience_required', 3)} years
- Skills: {', '.join(self.profile.get('skills', []))}
- Desired Roles: {', '.join(self.profile.get('desired_roles', ['Software Engineer']))}
- Visa: OPT/STEM OPT (needs H-1B sponsorship eventually)
- Job types: Full-time or contract ONLY (NO internships, but externships are OK)
- Location: USA only
- Focus: University/college technical staff roles + OPT-friendly companies

ACCEPT roles like: Software Engineer, Data Analyst, IT Specialist, Cloud Engineer, QA Engineer, Research Software Engineer, Systems Administrator, DBA, Web Developer, Application Developer, DevOps, AI/ML Engineer, Backend Developer, Full Stack Developer, Network Engineer, Information Security Analyst, HPC Engineer, Research Computing

STRICT RULES — REJECT if ANY of these are true:
1. Job requires 4+ years of experience (0-3 years is OK)
2. Title contains "Senior", "Sr.", "Lead", "Staff", "Principal", "III", "IV", "V", "Mid-Level"
3. Job is an internship (but externships are OK)
4. Job is not in the United States
5. Job requires US citizenship or security clearance
6. Job is a faculty, professor, or teaching position
7. Job is managerial (Director, VP, Head of, Manager)

MATCH: YES or NO
REASON: [one sentence]
OPT_FRIENDLY: [YES/NO/UNKNOWN]"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            is_match = 'MATCH: YES' in result.upper() or 'MATCH:YES' in result.upper()
            
            return is_match, result
            
        except Exception as e:
            # Fallback
            title_lower = job['title'].lower()
            if any(word in title_lower for word in ['senior', 'sr.', 'lead', 'staff', 'principal', 'director', 'manager', 'vp', 'professor', 'faculty']):
                return False, "Senior/managerial/faculty role"
            
            if ('intern ' in title_lower or 'internship' in title_lower) and 'extern' not in title_lower:
                return False, "Internship role"
            
            desired_roles = ['software', 'data analyst', 'qa', 'quality', 'cloud', 'devops',
                           'it specialist', 'systems admin', 'database', 'web developer',
                           'application', 'backend', 'frontend', 'full stack', 'network',
                           'security analyst', 'research computing', 'hpc', 'ai ', 'ml ']
            if any(role in title_lower for role in desired_roles):
                return True, "Potential match for OPT candidate"
            
            return False, "Role doesn't match profile"
    
    def check_h1b_sponsorship(self, company_name):
        """Check if company has H-1B sponsorship history"""
        # Known H-1B sponsors (FAANG and major tech companies)
        known_sponsors = {
            # FAANG
            'Google': 'Yes - Major H-1B sponsor',
            'Amazon': 'Yes - Major H-1B sponsor',
            'Microsoft': 'Yes - Major H-1B sponsor',
            'Apple': 'Yes - Major H-1B sponsor',
            'Meta': 'Yes - Major H-1B sponsor',
            'Netflix': 'Yes - H-1B sponsor',
            
            # Enterprise
            'Salesforce': 'Yes - Major H-1B sponsor',
            'Oracle': 'Yes - Major H-1B sponsor',
            'IBM': 'Yes - Major H-1B sponsor',
            'Intel': 'Yes - Major H-1B sponsor',
            'Cisco': 'Yes - Major H-1B sponsor',
            'Adobe': 'Yes - H-1B sponsor',
            'SAP': 'Yes - H-1B sponsor',
            'VMware': 'Yes - H-1B sponsor',
            'Dell': 'Yes - H-1B sponsor',
            'HP': 'Yes - H-1B sponsor',
            'Qualcomm': 'Yes - H-1B sponsor',
            'NVIDIA': 'Yes - H-1B sponsor',
            'AMD': 'Yes - H-1B sponsor',
            
            # Unicorns
            'Uber': 'Yes - H-1B sponsor',
            'Lyft': 'Yes - H-1B sponsor',
            'Airbnb': 'Yes - H-1B sponsor',
            'Stripe': 'Yes - H-1B sponsor',
            'Coinbase': 'Yes - H-1B sponsor',
            'Databricks': 'Yes - H-1B sponsor',
            'Snowflake': 'Yes - H-1B sponsor',
            
            # Consulting (Major OPT/H-1B sponsors)
            'Accenture': 'Yes - Major H-1B sponsor (OPT-friendly)',
            'Deloitte': 'Yes - Major H-1B sponsor (OPT-friendly)',
            'PwC': 'Yes - H-1B sponsor (OPT-friendly)',
            'EY': 'Yes - H-1B sponsor (OPT-friendly)',
            'KPMG': 'Yes - H-1B sponsor (OPT-friendly)',
            'Cognizant': 'Yes - Major H-1B sponsor (OPT-friendly)',
            'Infosys': 'Yes - Major H-1B sponsor (OPT-friendly)',
            'TCS': 'Yes - Major H-1B sponsor (OPT-friendly)',
            'Wipro': 'Yes - Major H-1B sponsor (OPT-friendly)',
            'HCL Technologies': 'Yes - Major H-1B sponsor (OPT-friendly)',
            
            # Startups (E-Verify, OPT-friendly)
            'Brex': 'Yes - E-Verify (OPT-friendly)',
            'Rippling': 'Yes - E-Verify (OPT-friendly)',
            'Ramp': 'Yes - E-Verify (OPT-friendly)',
            'Plaid': 'Yes - E-Verify (OPT-friendly)',
            'Chime': 'Yes - E-Verify (OPT-friendly)',
            'Gusto': 'Yes - E-Verify (OPT-friendly)',
            'Carta': 'Yes - E-Verify (OPT-friendly)',
            'Airtable': 'Yes - E-Verify (OPT-friendly)',
            'Notion': 'Yes - E-Verify (OPT-friendly)',
            'Figma': 'Yes - E-Verify (OPT-friendly)',
            'Canva': 'Yes - E-Verify (OPT-friendly)',
            'Discord': 'Yes - E-Verify (OPT-friendly)',
            'Asana': 'Yes - E-Verify (OPT-friendly)',
            'Scale AI': 'Yes - E-Verify (OPT-friendly)',
            'Anthropic': 'Yes - E-Verify (OPT-friendly)',
            'OpenAI': 'Yes - E-Verify (OPT-friendly)',
            
            # Universities (OPT-friendly, can sponsor H-1B)
            'MIT': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Stanford University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Harvard University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'UC Berkeley': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Carnegie Mellon': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Georgia Tech': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Michigan': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'UT Austin': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'UIUC': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Washington': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'UCLA': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'USC': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Columbia University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'NYU': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Princeton University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Yale University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Cornell University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Duke University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Northwestern University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Johns Hopkins': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Purdue University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Ohio State University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Penn State': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Virginia': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Maryland': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Arizona State University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Florida': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Rice University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Caltech': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Colorado Boulder': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Pennsylvania': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Brown University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Dartmouth College': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Wisconsin-Madison': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Minnesota': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Indiana University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Pittsburgh': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Rutgers University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of North Carolina': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'NC State University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Virginia Tech': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Boston University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Northeastern University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Emory University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Vanderbilt University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Washington University in St. Louis': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Texas A&M University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Texas at Dallas': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Illinois Chicago': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of California San Diego': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'UC Davis': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'UC Irvine': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'UC Santa Barbara': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Michigan State University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Georgia': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Florida State University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Miami': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'George Mason University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'George Washington University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Georgetown University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Stony Brook University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University at Buffalo': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Syracuse University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Massachusetts Amherst': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'University of Connecticut': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'Clemson University': 'Yes - University (OPT-friendly, H-1B cap-exempt)',
            'MIT Lincoln Laboratory': 'Yes - National Lab (OPT-friendly, H-1B cap-exempt)',
            'Johns Hopkins APL': 'Yes - National Lab (OPT-friendly, H-1B cap-exempt)',
            'Argonne National Laboratory': 'Yes - National Lab (OPT-friendly, H-1B cap-exempt)',
            'Oak Ridge National Laboratory': 'Yes - National Lab (OPT-friendly, H-1B cap-exempt)',
            'Sandia National Laboratories': 'Yes - National Lab (OPT-friendly, H-1B cap-exempt)',
            'Lawrence Berkeley National Lab': 'Yes - National Lab (OPT-friendly, H-1B cap-exempt)',
            'Brookhaven National Laboratory': 'Yes - National Lab (OPT-friendly, H-1B cap-exempt)',
            'Pacific Northwest National Lab': 'Yes - National Lab (OPT-friendly, H-1B cap-exempt)',
            
            # More Startups (E-Verify, OPT-friendly)
            'Wiz': 'Yes - E-Verify (OPT-friendly)',
            'Verkada': 'Yes - E-Verify (OPT-friendly)',
            'Applied Intuition': 'Yes - E-Verify (OPT-friendly)',
            'Shield AI': 'Yes - E-Verify (OPT-friendly)',
            'Anduril': 'Yes - E-Verify (OPT-friendly)',
            'Cerebras Systems': 'Yes - E-Verify (OPT-friendly)',
            'Perplexity AI': 'Yes - E-Verify (OPT-friendly)',
            'Replit': 'Yes - E-Verify (OPT-friendly)',
            'Retool': 'Yes - E-Verify (OPT-friendly)',
            'Verily': 'Yes - H-1B sponsor (Alphabet subsidiary)',
            'Miro': 'Yes - E-Verify (OPT-friendly)',
            'Webflow': 'Yes - E-Verify (OPT-friendly)',
            'Drata': 'Yes - E-Verify (OPT-friendly)',
            'Vanta': 'Yes - E-Verify (OPT-friendly)',
            'Abnormal Security': 'Yes - E-Verify (OPT-friendly)',
            'Roblox': 'Yes - H-1B sponsor',
            'Epic Games': 'Yes - H-1B sponsor',
            'Unity': 'Yes - H-1B sponsor',
            'Riot Games': 'Yes - H-1B sponsor',
            'Twitch': 'Yes - H-1B sponsor (Amazon subsidiary)',
            
            # Fintech / Finance (Major H-1B sponsors)
            'Visa': 'Yes - Major H-1B sponsor',
            'Mastercard': 'Yes - Major H-1B sponsor',
            'Capital One': 'Yes - Major H-1B sponsor (OPT-friendly)',
            'JPMorgan Chase': 'Yes - Major H-1B sponsor',
            'Goldman Sachs': 'Yes - Major H-1B sponsor',
            'Morgan Stanley': 'Yes - Major H-1B sponsor',
            'Bloomberg': 'Yes - Major H-1B sponsor',
            'Citadel': 'Yes - H-1B sponsor',
            'Two Sigma': 'Yes - H-1B sponsor',
            'Jane Street': 'Yes - H-1B sponsor',
            'Klarna': 'Yes - H-1B sponsor',
            
            # Enterprise / Telecom
            'Qualcomm': 'Yes - Major H-1B sponsor',
            'NVIDIA': 'Yes - Major H-1B sponsor',
            'AMD': 'Yes - H-1B sponsor',
            'Intel': 'Yes - Major H-1B sponsor',
            'Cisco': 'Yes - Major H-1B sponsor',
            'T-Mobile': 'Yes - H-1B sponsor',
            'Verizon': 'Yes - H-1B sponsor',
            'AT&T': 'Yes - H-1B sponsor',
            'Walmart': 'Yes - Major H-1B sponsor',
            'Target': 'Yes - H-1B sponsor',
            'Shopify': 'Yes - H-1B sponsor',
            'Pinterest': 'Yes - H-1B sponsor',
            'Snap': 'Yes - H-1B sponsor',
            'Reddit': 'Yes - H-1B sponsor',
            'LinkedIn': 'Yes - H-1B sponsor (Microsoft subsidiary)',
            'Spotify': 'Yes - H-1B sponsor',
            'ServiceNow': 'Yes - H-1B sponsor',
            'Broadcom': 'Yes - Major H-1B sponsor',
            'Workday': 'Yes - H-1B sponsor',
            'Palo Alto Networks': 'Yes - H-1B sponsor',
            'CrowdStrike': 'Yes - H-1B sponsor',
            'Cloudflare': 'Yes - H-1B sponsor',
            'Datadog': 'Yes - H-1B sponsor',
            'MongoDB': 'Yes - H-1B sponsor',
            'Confluent': 'Yes - H-1B sponsor',
            'HubSpot': 'Yes - H-1B sponsor',
            'Twilio': 'Yes - H-1B sponsor',
            'DoorDash': 'Yes - H-1B sponsor',
            'Instacart': 'Yes - H-1B sponsor',
            'Robinhood': 'Yes - H-1B sponsor',
            'Affirm': 'Yes - H-1B sponsor',
            'SoFi': 'Yes - H-1B sponsor',
            'Square': 'Yes - H-1B sponsor',
            'PayPal': 'Yes - Major H-1B sponsor',
            'Toast': 'Yes - H-1B sponsor',
            'Grammarly': 'Yes - H-1B sponsor',
            'Duolingo': 'Yes - H-1B sponsor',
        }
        
        return known_sponsors.get(company_name, 'Unknown - Check myvisajobs.com')
    
    def generate_html_report(self, results, matched_jobs):
        """Generate beautiful HTML report with clickable links"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Search Results - {results['date']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .date {{
            color: #666;
            font-size: 1.1em;
            margin-bottom: 20px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .jobs-section {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        .section-title {{
            color: #333;
            font-size: 1.8em;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }}
        
        .job-card {{
            background: #f8f9fa;
            border-left: 5px solid #667eea;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }}
        
        .job-card:hover {{
            transform: translateX(10px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .job-title {{
            color: #333;
            font-size: 1.4em;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        
        .job-company {{
            color: #667eea;
            font-size: 1.1em;
            font-weight: 500;
            margin-bottom: 8px;
        }}
        
        .job-type {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            margin-bottom: 15px;
        }}
        
        .job-source {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        
        .job-evaluation {{
            background: #e8f5e9;
            border-left: 3px solid #4caf50;
            padding: 10px 15px;
            margin: 15px 0;
            border-radius: 5px;
            font-size: 0.95em;
            color: #2e7d32;
        }}
        
        .apply-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
            margin-top: 10px;
        }}
        
        .apply-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .no-jobs {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }}
        
        .no-jobs-icon {{
            font-size: 4em;
            margin-bottom: 20px;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
            opacity: 0.9;
        }}
        
        @media (max-width: 768px) {{
            h1 {{
                font-size: 1.8em;
            }}
            
            .stats {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Your Daily Job Matches</h1>
            <div class="date">📅 {results['date']}</div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{results['companies_checked']}</div>
                    <div class="stat-label">Companies Searched</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{results['jobs_found']}</div>
                    <div class="stat-label">Jobs Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{results['jobs_matched']}</div>
                    <div class="stat-label">Perfect Matches</div>
                </div>
            </div>
        </div>
        
        <div class="jobs-section">
            <h2 class="section-title">✅ Jobs to Apply Today</h2>
"""
        
        if matched_jobs:
            for i, job in enumerate(matched_jobs, 1):
                h1b_status = self.check_h1b_sponsorship(job['company'])
                h1b_color = '#4caf50' if 'Yes' in h1b_status else '#ff9800'
                
                html += f"""
            <div class="job-card">
                <div class="job-title">{i}. {job['title']}</div>
                <div class="job-company">🏢 {job['company']}</div>
                <span class="job-type">{job['company_type']}</span>
                <div class="job-source">📍 {job.get('location', 'USA')} | {job['source']}</div>
                <div class="job-evaluation">
                    💡 AI Evaluation: {job.get('evaluation', 'Good match for your profile')}
                </div>
                <div style="background: {h1b_color}20; border-left: 3px solid {h1b_color}; padding: 10px 15px; margin: 15px 0; border-radius: 5px;">
                    🛂 H-1B Sponsorship: <strong>{h1b_status}</strong>
                </div>
                <a href="{job['url']}" target="_blank" class="apply-button">
                    🚀 Apply Now
                </a>
            </div>
"""
        else:
            html += """
            <div class="no-jobs">
                <div class="no-jobs-icon">😔</div>
                <h3>No matches found today</h3>
                <p>All jobs required more experience than your profile. The agent will search again tomorrow!</p>
            </div>
"""
        
        html += f"""
        </div>
        
        <div class="footer">
            <p>🤖 Generated by AI Job Agent</p>
            <p>Powered by Claude AI • Searching {len(self.companies)} US Tech Companies</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Save HTML file
        html_file = 'job_results.html'
        with open(html_file, 'w') as f:
            f.write(html)
        
        print(f"\n✅ HTML report saved to {html_file}")
        print(f"   Open it in your browser to see clickable job links!")
    
    def run_daily(self):
        """Main daily execution"""
        print("🚀 Starting Daily Job Hunt\n")
        
        # Update state
        self.state['days_active'] += 1
        self.state['last_run'] = datetime.now().isoformat()
        
        # Step 1: Think about strategy
        print("🤔 Agent deciding which companies to prioritize...")
        priority, reasoning = self.think()
        print(f"   Priority: {priority}")
        print(f"   Reasoning: {reasoning[:100]}...\n")
        
        # Step 2: Filter companies by priority
        if priority == 'All':
            companies_to_check = self.companies
        else:
            companies_to_check = [c for c in self.companies if c['type'] == priority]
        
        print(f"🏢 Searching {len(companies_to_check)} company career portals...")
        print("   (This may take a few minutes)\n")
        
        all_jobs = []
        
        for i, company in enumerate(companies_to_check, 1):
            print(f"   [{i}/{len(companies_to_check)}] {company['name']}...", end=' ', flush=True)
            
            try:
                jobs = self.search_company(company)
                
                # Filter: only keep USA jobs
                # Universities are all in the USA — skip location check for them
                verified_jobs = []
                for job in jobs:
                    if self.is_non_usa_title(job.get('title', '')):
                        continue
                    title_lower = job.get('title', '').lower()
                    if 'intern ' in title_lower or 'internship' in title_lower:
                        continue
                    if any(w in title_lower for w in ['professor', 'faculty', 'teaching', 'lecturer', 'dean', 'provost', 'clearance', 'ts/sci', 'top secret']):
                        continue
                    if company.get('type') == 'University' or self.is_usa_job(job['url']):
                        verified_jobs.append(job)
                
                all_jobs.extend(verified_jobs)
                print(f"({len(verified_jobs)} jobs)")
            except Exception as e:
                print(f"(error: {str(e)[:40]})")
                # Reset Selenium if it crashed
                try:
                    if self.driver:
                        self.driver.quit()
                        self.driver = None
                except:
                    self.driver = None
            
            self.state['companies_checked'] += 1
            time.sleep(2)
        
        self.state['total_jobs_found'] += len(all_jobs)
        
        print(f"\n   ✅ Found {len(all_jobs)} total jobs\n")
        
        if not all_jobs:
            print("⚠️  No jobs found today. Companies may have updated their websites.")
            print("💡 The agent will try again tomorrow.\n")
            self.save_state()
            return
        
        # Step 3: Evaluate with Claude AI
        print(f"🧠 Evaluating {len(all_jobs)} jobs with Claude AI...\n")
        
        matched_jobs = []
        
        for i, job in enumerate(all_jobs, 1):
            print(f"   [{i}/{len(all_jobs)}] {job['title'][:50]}...", end=' ')
            
            is_match, reason = self.evaluate_job(job)
            job['evaluation'] = reason
            
            if is_match:
                print("✅")
                matched_jobs.append(job)
            else:
                print("❌")
            
            time.sleep(0.5)
        
        # Step 4: Show results
        print("\n" + "="*70)
        print("📊 TODAY'S JOB RECOMMENDATIONS")
        print("="*70)
        print(f"\nDate: {datetime.now().strftime('%B %d, %Y')}")
        print(f"Companies Checked: {len(companies_to_check)}")
        print(f"Jobs Found: {len(all_jobs)}")
        print(f"Jobs Matched: {len(matched_jobs)}")
        
        if matched_jobs:
            print(f"\n✅ JOBS TO APPLY TODAY ({len(matched_jobs)}):")
            print("="*70 + "\n")
            
            for i, job in enumerate(matched_jobs, 1):
                print(f"{i}. {job['title']}")
                print(f"   Company: {job['company']} ({job['company_type']})")
                print(f"   Source: Direct Career Portal")
                print(f"   🔗 {job['url']}")
                print()
            
            self.state['jobs_shown_to_user'] += len(matched_jobs)
        else:
            print("\n⚠️  No matches today. All jobs required too much experience.")
        
        # Step 5: Save results
        results = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'priority': priority,
            'companies_checked': len(companies_to_check),
            'jobs_found': len(all_jobs),
            'jobs_matched': len(matched_jobs),
            'matched_jobs': matched_jobs
        }
        
        with open(self.jobs_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Step 5.5: Generate HTML report
        self.generate_html_report(results, matched_jobs)
        
        # Step 6: Learning
        self.state['learning_log'].append({
            'day': self.state['days_active'],
            'priority': priority,
            'companies': len(companies_to_check),
            'jobs_found': len(all_jobs),
            'jobs_matched': len(matched_jobs)
        })
        
        self.state['learning_log'] = self.state['learning_log'][-30:]
        
        # Step 7: Stats
        print("\n" + "="*70)
        print("🤖 AGENT STATISTICS")
        print("="*70)
        print(f"\nDays Active: {self.state['days_active']}")
        print(f"Total Companies Checked: {self.state['companies_checked']}")
        print(f"Total Jobs Found: {self.state['total_jobs_found']}")
        print(f"Jobs Shown to You: {self.state['jobs_shown_to_user']}")
        
        if self.state['learning_log']:
            print(f"\nRecent Performance:")
            for log in self.state['learning_log'][-3:]:
                print(f"   Day {log['day']}: {log['jobs_matched']} matches from {log['jobs_found']} jobs")
        
        print("\n" + "="*70)
        
        self.save_state()
        
        # Close Selenium if it was used
        self.close_selenium()
        
        print(f"\n✅ Results saved to {self.jobs_file}")
        print("✅ Agent state saved")
        print(f"✅ HTML report: job_results.html")
        print("\n💡 Open job_results.html in your browser to see clickable job links!")
        print("🔄 Run again tomorrow for fresh jobs\n")

if __name__ == "__main__":
    # Check for flags
    test_mode = '--test' in sys.argv
    university_mode = '--university' in sys.argv
    
    agent = JobAgent()
    
    if university_mode:
        uni_companies = [c for c in agent.companies if c['type'] == 'University']
        print(f"🎓 UNIVERSITY MODE: Searching {len(uni_companies)} universities & research labs\n")
        agent.companies = uni_companies
        agent.run_daily()
    elif test_mode:
        print("🧪 TEST MODE: Searching only 50 companies for fast iteration\n")
        original_companies = agent.companies
        agent.companies = agent.companies[:50]
        agent.run_daily()
        agent.companies = original_companies
    else:
        agent.run_daily()
