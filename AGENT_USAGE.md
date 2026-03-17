# 🤖 AI Job Agent - Usage Guide

## What You Have Now

Your AI agent is working! It:
- ✅ Searches LinkedIn & Indeed for REAL jobs
- ✅ Uses Claude AI to evaluate each job
- ✅ Filters out senior roles (5+ years experience)
- ✅ Shows you job links to apply
- ✅ Tracks applications and learns

## Current Stats

```
Days Active: 10
Jobs Found: 60
Applications Made: 9
Jobs Ready to Apply: 9 with links!
```

## How to Use

### Run the Agent:
```bash
python3 ai-job-agent.py
```

### Check Jobs to Apply:
The agent shows job links at the end:
```
📋 JOBS READY TO APPLY (9):
5. Software Engineer at Encamp
   🔗 https://www.linkedin.com/jobs/view/...
```

Click those links and apply!

### Check Application Tracker:
```bash
cat applications_tracker.json
```

## Getting 100+ Jobs

Currently finding ~13 jobs per run. To get 100+:

### Option 1: Add LinkedIn Cookies (Recommended)
1. Read `GET_LINKEDIN_COOKIES.md`
2. Add cookies to `.env` file
3. Get 5-10x more results

### Option 2: Use Full Scraper
```bash
python3 job-scraper-smart.py
```
This gets 100+ jobs but doesn't have the agent's autonomy.

### Option 3: Run Agent Multiple Times
```bash
# Morning
python3 ai-job-agent.py

# Afternoon  
python3 ai-job-agent.py

# Evening
python3 ai-job-agent.py
```

## Agent Behavior

The agent makes autonomous decisions:
- **Day 1-3**: Searches aggressively
- **Day 4-7**: Adjusts strategy if no interviews
- **Day 7+**: Follows up on applications
- **Always**: Searches for new jobs first

## Files Created

- `agent_state.json` - Agent's memory
- `applications_tracker.json` - Jobs to apply to
- `my_profile.json` - Your profile

## Tips

1. **Apply to the jobs!** The agent finds them, you apply
2. **Update interview count** in `agent_state.json` when you get one
3. **Run daily** for fresh jobs
4. **Check the links** - they're real LinkedIn/Indeed URLs

## Next Steps

Want to enhance the agent?
- Auto-apply to jobs (needs LinkedIn API)
- Email notifications
- Better tracking
- More platforms (Glassdoor, etc.)

Let me know!
