# AI Job Finder Agent - Setup Guide

## Quick Start

1. **Edit your profile** (IMPORTANT - Do this first!):
```bash
nano my_profile.json
```
Update with your actual:
- Skills
- Experience years
- Desired role
- Location
- Remote preference
- Salary expectations

2. **Run the agent manually**:
```bash
source venv/bin/activate
python3 job-finder-simple.py
```

You'll see a daily report with:
- Personalized job search recommendations
- Direct links to LinkedIn, Wellfound, Indeed
- Action items for the day

## Schedule Daily Runs (8 AM Every Morning)

### Option 1: Using Cron (Recommended)

1. Make the script executable:
```bash
chmod +x schedule_daily.sh
```

2. Get the full path to your project:
```bash
pwd
```

3. Edit crontab:
```bash
crontab -e
```

4. Add this line (replace `/full/path/to/project` with your actual path):
```
0 8 * * * cd /full/path/to/project && ./schedule_daily.sh >> job_finder.log 2>&1
```

5. Save and exit (press `Esc`, then type `:wq` and press Enter)

6. Verify it's scheduled:
```bash
crontab -l
```

### Option 2: Using launchd (macOS Alternative)

1. Create a plist file:
```bash
nano ~/Library/LaunchAgents/com.jobfinder.daily.plist
```

2. Paste this content (update the path):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jobfinder.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/full/path/to/project/schedule_daily.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/full/path/to/project/job_finder.log</string>
    <key>StandardErrorPath</key>
    <string>/full/path/to/project/job_finder_error.log</string>
</dict>
</plist>
```

3. Load the agent:
```bash
launchctl load ~/Library/LaunchAgents/com.jobfinder.daily.plist
```

4. Test it immediately:
```bash
launchctl start com.jobfinder.daily
```

## Daily Workflow

Every morning at 8 AM, the agent will:
1. Generate a personalized job search report
2. Save it to `daily_jobs.json`
3. Create search links for LinkedIn, Wellfound, Indeed

You should:
1. Check the report (or run manually: `python3 job-finder-simple.py`)
2. Click the search links
3. Apply to 3-5 jobs that match your profile
4. Track your applications

## Files Explained

- `my_profile.json` - Your job search profile (EDIT THIS!)
- `job-finder-simple.py` - Main agent script
- `daily_jobs.json` - Today's job recommendations
- `schedule_daily.sh` - Automation script
- `job_finder.log` - Execution logs

## Troubleshooting

**Cron job not running?**
- Check logs: `cat job_finder.log`
- Verify cron: `crontab -l`
- Test manually: `./schedule_daily.sh`

**No output?**
- Make sure you edited `my_profile.json`
- Check file permissions: `ls -la`
- Run with: `python3 job-finder-simple.py` to see errors

**Want to change the time?**
- Edit crontab: `crontab -e`
- Change `0 8` to your preferred hour (24-hour format)
- Example: `0 9` for 9 AM, `0 7` for 7 AM

## Tips for Success

1. **Update your profile regularly** as you learn new skills
2. **Customize your resume** for each application
3. **Track applications** in a spreadsheet
4. **Follow up** after 1 week if no response
5. **Network** on LinkedIn while job searching
6. **Apply early** - be one of the first applicants

Good luck with your job search! 🚀
