# 📁 File Guide - What Each File Does

## 🎯 MAIN FILES (Use These)

### **job-scraper-smart.py** ⭐ PRIMARY FILE
- **What it does**: The main AI job scraper with Claude Sonnet 4 analysis
- **Features**:
  - Searches LinkedIn & Indeed for jobs (last 7 days)
  - Analyzes each job with Claude AI
  - Filters by experience level (rejects 5+ year jobs when you have 1 year)
  - Filters by salary requirements
  - Shows only jobs matching your profile
- **Run it**: `python3 job-scraper-smart.py`
- **Status**: ✅ ACTIVE - Use this one!

### **my_profile.json** ⭐ YOUR PROFILE
- **What it does**: Your job search preferences
- **Contains**:
  - Your skills (Java, TypeScript, Spring Boot, etc.)
  - Experience years (1 year)
  - Desired role (Software Engineer)
  - Location preference (Anywhere in USA)
  - Salary minimums (annual & hourly)
- **Edit this**: Update your skills, experience, salary requirements
- **Status**: ✅ ACTIVE - Edit as needed!

### **daily_jobs.json** 📊 RESULTS
- **What it does**: Stores today's job search results
- **Contains**:
  - Matched jobs (good fit for you)
  - Rejected jobs (too senior, low pay, etc.)
  - Reasons for each decision
- **Auto-generated**: Created every time you run the scraper
- **Status**: ✅ ACTIVE - Check this for results!

### **.env** 🔐 SECRETS
- **What it does**: Stores API keys and credentials
- **Contains**:
  - Anthropic API key (for Claude AI)
  - LinkedIn cookies (optional - for more results)
- **Security**: Never share this file!
- **Status**: ✅ ACTIVE - Keep private!

### **schedule_daily.sh** ⏰ AUTOMATION
- **What it does**: Runs the scraper automatically
- **Use with**: cron (to run at 8 AM daily)
- **Command**: `./schedule_daily.sh`
- **Status**: ✅ ACTIVE - For daily automation

---

## 📚 DOCUMENTATION FILES

### **START_HERE.txt**
- Quick start guide
- 4 simple steps to get running

### **SETUP_GUIDE.md**
- Detailed setup instructions
- Cron scheduling guide
- Troubleshooting tips

### **GET_LINKEDIN_COOKIES.md**
- How to get LinkedIn cookies
- Step-by-step with screenshots description
- Enables 100+ jobs per search (vs 15-25 without)

### **FILE_GUIDE.md** (this file)
- Explains what each file does

### **README.md**
- Original project overview

---

## 🗑️ OLD/ALTERNATIVE FILES (Don't Use)

### **job-scraper.py**
- **Status**: ❌ DEPRECATED
- **Why**: Basic version without Claude AI analysis
- **Use instead**: job-scraper-smart.py

### **job-finder-simple.py**
- **Status**: ❌ DEPRECATED
- **Why**: Just generates search links, doesn't scrape
- **Use instead**: job-scraper-smart.py

### **job-finder-enhanced.py**
- **Status**: ❌ DEPRECATED
- **Why**: Early version with API issues
- **Use instead**: job-scraper-smart.py

### **job-finder-kiro.py**
- **Status**: ❌ DEPRECATED
- **Why**: Manual search version
- **Use instead**: job-scraper-smart.py

### **job-finder-agent.py**
- **Status**: ❌ DEPRECATED
- **Why**: First prototype
- **Use instead**: job-scraper-smart.py

---

## 📦 SYSTEM FILES

### **venv/** (folder)
- Python virtual environment
- Contains all installed packages
- Don't edit manually

### **requirements.txt**
- List of Python packages needed
- Used by: `pip install -r requirements.txt`

### **setup.sh**
- Initial setup script
- Already run during installation

### **.gitignore** (if exists)
- Tells git which files to ignore
- Protects .env from being shared

---

## 📊 QUICK REFERENCE

**To run the job scraper:**
```bash
python3 job-scraper-smart.py
```

**To edit your profile:**
```bash
nano my_profile.json
```

**To view results:**
```bash
cat daily_jobs.json
```

**To schedule daily runs:**
```bash
crontab -e
# Add: 0 8 * * * cd /Users/mrudu/MRUDHU-AI-INITIATIVES && ./schedule_daily.sh >> job_finder.log 2>&1
```

---

## 🎯 WORKFLOW

1. **Edit** `my_profile.json` with your details
2. **Run** `python3 job-scraper-smart.py`
3. **Check** `daily_jobs.json` for results
4. **Apply** to matched jobs
5. **Repeat** daily or schedule with cron

---

## 🔧 OPTIONAL: LinkedIn Authentication

For 5-10x more job results:
1. Read `GET_LINKEDIN_COOKIES.md`
2. Get your LinkedIn cookies
3. Add to `.env` file
4. Run scraper again

---

## ❓ Need Help?

- **Setup issues**: Read `SETUP_GUIDE.md`
- **Quick start**: Read `START_HERE.txt`
- **LinkedIn auth**: Read `GET_LINKEDIN_COOKIES.md`
- **File questions**: You're reading it! 😊
