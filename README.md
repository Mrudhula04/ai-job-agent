# AI Job Finder Agent

Automatically searches LinkedIn, Wellfound, and Indeed for jobs matching your profile.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

3. Edit `my_profile.json` with your details:
   - Skills
   - Experience years
   - Desired role
   - Location preferences
   - Remote preference

4. Run manually:
```bash
python3 job-finder-agent.py
```

## Schedule Daily Runs

### Option 1: Cron (macOS/Linux)
```bash
chmod +x schedule_daily.sh
crontab -e
```
Add this line to run at 8 AM daily:
```
0 8 * * * cd /full/path/to/project && /usr/bin/python3 job-finder-agent.py
```

### Option 2: launchd (macOS)
Create `~/Library/LaunchAgents/com.jobfinder.daily.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jobfinder.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/full/path/to/job-finder-agent.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>EnvironmentVariables</key>
    <dict>
        <key>ANTHROPIC_API_KEY</key>
        <string>your-api-key-here</string>
    </dict>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.jobfinder.daily.plist
```

## Output

Results are saved to `daily_jobs.json` and displayed in terminal.
