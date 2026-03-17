#!/usr/bin/env python3
"""
Add OPT-friendly startups and universities to companies list
"""
import json

# Load current companies
with open('companies_list.json', 'r') as f:
    companies = json.load(f)

# OPT-friendly startups (E-Verify, known to hire OPT)
opt_startups = [
    # Y Combinator Startups (OPT-friendly)
    {'name': 'Brex', 'url': 'https://www.brex.com/careers', 'type': 'Startup'},
    {'name': 'Rippling', 'url': 'https://www.rippling.com/careers', 'type': 'Startup'},
    {'name': 'Ramp', 'url': 'https://ramp.com/careers', 'type': 'Startup'},
    {'name': 'Retool', 'url': 'https://retool.com/careers', 'type': 'Startup'},
    {'name': 'Scale AI', 'url': 'https://scale.com/careers', 'type': 'Startup'},
    {'name': 'Anduril', 'url': 'https://www.anduril.com/careers/', 'type': 'Startup'},
    {'name': 'Anthropic', 'url': 'https://www.anthropic.com/careers', 'type': 'Startup'},
    {'name': 'OpenAI', 'url': 'https://openai.com/careers/', 'type': 'Startup'},
    {'name': 'Hugging Face', 'url': 'https://huggingface.co/jobs', 'type': 'Startup'},
    {'name': 'Weights & Biases', 'url': 'https://wandb.ai/careers', 'type': 'Startup'},
    
    # E-Verify Startups
    {'name': 'Plaid', 'url': 'https://plaid.com/careers/', 'type': 'Startup'},
    {'name': 'Chime', 'url': 'https://www.chime.com/careers/', 'type': 'Startup'},
    {'name': 'Gusto', 'url': 'https://gusto.com/about/careers', 'type': 'Startup'},
    {'name': 'Carta', 'url': 'https://carta.com/careers/', 'type': 'Startup'},
    {'name': 'Airtable', 'url': 'https://www.airtable.com/careers', 'type': 'Startup'},
    {'name': 'Notion', 'url': 'https://www.notion.so/careers', 'type': 'Startup'},
    {'name': 'Figma', 'url': 'https://www.figma.com/careers/', 'type': 'Startup'},
    {'name': 'Canva', 'url': 'https://www.canva.com/careers/jobs/', 'type': 'Startup'},
    {'name': 'Discord', 'url': 'https://discord.com/careers', 'type': 'Startup'},
    {'name': 'Asana', 'url': 'https://asana.com/jobs', 'type': 'Startup'},
    
    # Consulting (OPT-friendly)
    {'name': 'Accenture', 'url': 'https://www.accenture.com/us-en/careers/jobsearch', 'type': 'Consulting'},
    {'name': 'Deloitte', 'url': 'https://www2.deloitte.com/us/en/careers/search-jobs.html', 'type': 'Consulting'},
    {'name': 'PwC', 'url': 'https://www.pwc.com/us/en/careers/campus/programs-events.html', 'type': 'Consulting'},
    {'name': 'EY', 'url': 'https://www.ey.com/en_us/careers', 'type': 'Consulting'},
    {'name': 'KPMG', 'url': 'https://www.kpmg.us/careers.html', 'type': 'Consulting'},
    {'name': 'Cognizant', 'url': 'https://careers.cognizant.com/us/en', 'type': 'Consulting'},
    {'name': 'Infosys', 'url': 'https://www.infosys.com/careers/', 'type': 'Consulting'},
    {'name': 'TCS', 'url': 'https://www.tcs.com/careers', 'type': 'Consulting'},
    {'name': 'Wipro', 'url': 'https://careers.wipro.com/', 'type': 'Consulting'},
    {'name': 'HCL Technologies', 'url': 'https://www.hcltech.com/careers', 'type': 'Consulting'},
]

# Universities (hire OPT for research/IT positions)
universities = [
    # Top Research Universities
    {'name': 'MIT', 'url': 'https://careers.mit.edu/jobs', 'type': 'University'},
    {'name': 'Stanford University', 'url': 'https://careersearch.stanford.edu/', 'type': 'University'},
    {'name': 'Harvard University', 'url': 'https://hr.harvard.edu/jobs', 'type': 'University'},
    {'name': 'UC Berkeley', 'url': 'https://jobs.berkeley.edu/', 'type': 'University'},
    {'name': 'Carnegie Mellon', 'url': 'https://www.cmu.edu/jobs/', 'type': 'University'},
    {'name': 'Georgia Tech', 'url': 'https://careers.gatech.edu/', 'type': 'University'},
    {'name': 'University of Michigan', 'url': 'https://careers.umich.edu/', 'type': 'University'},
    {'name': 'UT Austin', 'url': 'https://utdirect.utexas.edu/apps/hr/jobs/', 'type': 'University'},
    {'name': 'UIUC', 'url': 'https://jobs.illinois.edu/', 'type': 'University'},
    {'name': 'University of Washington', 'url': 'https://uwhires.admin.washington.edu/', 'type': 'University'},
    {'name': 'UCLA', 'url': 'https://careers.ucla.edu/', 'type': 'University'},
    {'name': 'USC', 'url': 'https://careers.usc.edu/', 'type': 'University'},
    {'name': 'Columbia University', 'url': 'https://opportunities.columbia.edu/', 'type': 'University'},
    {'name': 'NYU', 'url': 'https://www.nyu.edu/employees/resources-and-services/careers-at-nyu.html', 'type': 'University'},
    {'name': 'Princeton University', 'url': 'https://jobs.princeton.edu/', 'type': 'University'},
    {'name': 'Yale University', 'url': 'https://your.yale.edu/work-yale/find-job', 'type': 'University'},
    {'name': 'Cornell University', 'url': 'https://hr.cornell.edu/jobs', 'type': 'University'},
    {'name': 'Duke University', 'url': 'https://hr.duke.edu/careers/', 'type': 'University'},
    {'name': 'Northwestern University', 'url': 'https://www.northwestern.edu/hr/careers/', 'type': 'University'},
    {'name': 'Johns Hopkins', 'url': 'https://jobs.jhu.edu/', 'type': 'University'},
]

# Add to companies list (avoid duplicates)
existing_names = {c['name'] for c in companies}

for startup in opt_startups:
    if startup['name'] not in existing_names:
        companies.append(startup)
        print(f"Added startup: {startup['name']}")

for university in universities:
    if university['name'] not in existing_names:
        companies.append(university)
        print(f"Added university: {university['name']}")

# Save updated list
with open('companies_list.json', 'w') as f:
    json.dump(companies, f, indent=2)

print(f"\n✅ Total companies: {len(companies)}")
print(f"   - Startups: {len([c for c in companies if c['type'] == 'Startup'])}")
print(f"   - Consulting: {len([c for c in companies if c['type'] == 'Consulting'])}")
print(f"   - Universities: {len([c for c in companies if c['type'] == 'University'])}")
print(f"   - Tech Companies: {len([c for c in companies if c['type'] not in ['Startup', 'Consulting', 'University']])}")
