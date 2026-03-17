# OPT/STEM OPT Job Search Guide

## Your Updated Profile

✅ **Roles**: Software Engineer, Data Analyst, QA Engineer, Cloud Engineer
✅ **Experience**: 0-2 years (entry-level friendly)
✅ **Skills**: Java, Spring Boot, AWS, SQL, Python, React
✅ **Location**: Open to relocation anywhere in USA
✅ **Visa**: OPT/STEM OPT (needs sponsorship)
✅ **Job Type**: Full-time or Contract

## How to Run the Agent

```bash
# Test mode (50 companies, faster)
python3 job-agent-final.py --test

# Full mode (150 companies)
python3 job-agent-final.py
```

## What the Agent Does

1. ✅ Searches 150 US tech companies
2. ✅ Filters for 0-2 years experience
3. ✅ Matches your roles (Software Engineer, Data Analyst, QA, Cloud)
4. ✅ Checks H-1B sponsorship history
5. ✅ Generates HTML report with:
   - Company name
   - Job title
   - Location
   - Apply link
   - H-1B sponsorship status

## H-1B Sponsorship Database

The agent checks if companies have H-1B sponsorship history:

### ✅ Major H-1B Sponsors (Best for OPT)
- **FAANG**: Google, Amazon, Microsoft, Apple, Meta, Netflix
- **Enterprise**: Salesforce, Oracle, IBM, Intel, Cisco, Adobe, SAP
- **Hardware**: NVIDIA, AMD, Qualcomm, Dell, HP
- **Unicorns**: Uber, Lyft, Airbnb, Stripe, Coinbase, Databricks, Snowflake

### How to Verify
For companies marked "Unknown", check:
- **myvisajobs.com** - H-1B sponsor database
- **h1bdata.info** - H-1B salary data
- **Company careers page** - Look for "E-Verify" or "Visa sponsorship"

## OPT-Friendly Companies

### Best Bets (Known OPT Sponsors):
1. **FAANG** - All sponsor OPT and H-1B
2. **Large Tech** - Salesforce, Oracle, Adobe, SAP, IBM
3. **Consulting** - Accenture, Deloitte, Cognizant, Infosys, TCS
4. **E-Verify Companies** - Required for STEM OPT extension

### Red Flags (Avoid):
- ❌ Small startups (<50 employees)
- ❌ "US Citizen only" in job description
- ❌ "No visa sponsorship" mentioned
- ❌ Companies with no H-1B history

## View Results

After running the agent:
```bash
open job_results.html
```

The HTML report shows:
- 📋 Job title and company
- 📍 Location
- 🛂 H-1B sponsorship status (Green = Yes, Orange = Unknown)
- 🚀 Direct apply link
- 💡 AI evaluation

## Tips for OPT Job Search

1. **Apply Early** - OPT has 90-day unemployment limit
2. **Target E-Verify** - Required for STEM OPT extension
3. **Network** - LinkedIn, company referrals help
4. **Highlight Skills** - Java, Spring Boot, AWS are in-demand
5. **Be Flexible** - Consider contract roles (easier to get)

## Additional Resources

- **myvisajobs.com** - H-1B sponsor database
- **h1bdata.info** - Salary information
- **e-verify.gov** - Check if company is E-Verify
- **LinkedIn** - Connect with recruiters at target companies

## Schedule Daily Runs

```bash
crontab -e
```

Add:
```
0 8 * * * cd ~/MRUDHU-AI-INITIATIVES && python3 job-agent-final.py >> agent.log 2>&1
```

This runs the agent every morning at 8 AM and emails you the results!

## Questions?

The agent is configured for OPT candidates. It will:
- ✅ Filter for entry-level roles (0-2 years)
- ✅ Show H-1B sponsorship history
- ✅ Match your skills (Java, Spring Boot, AWS, Python, React)
- ✅ Include multiple roles (Software Engineer, Data Analyst, QA, Cloud)

Good luck with your job search! 🚀
