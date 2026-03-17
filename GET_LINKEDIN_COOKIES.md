# How to Get LinkedIn Cookies for More Job Results

Using your LinkedIn account will give you access to many more job postings!

## Step-by-Step Instructions

### Option 1: Chrome Browser

1. **Open LinkedIn and Login**
   - Go to https://www.linkedin.com
   - Login with your account

2. **Open Developer Tools**
   - Press `F12` (or right-click > Inspect)
   - Click on the "Application" tab (or "Storage" in Firefox)

3. **Find Cookies**
   - In the left sidebar, expand "Cookies"
   - Click on "https://www.linkedin.com"

4. **Copy Cookie Values**
   - Find the cookie named `li_at`
   - Copy its entire value (starts with something like "AQEDATEAAAGVx...")
   - Find the cookie named `JSESSIONID`
   - Copy its entire value (starts with "ajax:")

5. **Add to .env File**
   - Open the `.env` file in your project
   - Paste the values:
   ```
   LINKEDIN_LI_AT=AQEDATEAAAGVx...your-value-here
   LINKEDIN_JSESSIONID=ajax:...your-value-here
   ```

### Option 2: Firefox Browser

1. **Open LinkedIn and Login**
   - Go to https://www.linkedin.com
   - Login with your account

2. **Open Developer Tools**
   - Press `F12`
   - Click on the "Storage" tab

3. **Find Cookies**
   - In the left sidebar, expand "Cookies"
   - Click on "https://www.linkedin.com"

4. **Copy Cookie Values**
   - Find `li_at` and copy its value
   - Find `JSESSIONID` and copy its value

5. **Add to .env File** (same as above)

## Security Notes

⚠️ **IMPORTANT:**
- These cookies give access to your LinkedIn account
- Keep the `.env` file private (it's already in .gitignore)
- Don't share these cookies with anyone
- Cookies expire after some time (usually 1 year for li_at)
- If you change your LinkedIn password, you'll need new cookies

## Benefits

With LinkedIn authentication:
- ✅ Access to 100+ jobs per search (vs 15-25 without)
- ✅ More detailed job information
- ✅ Better search results
- ✅ Fewer rate limits

## Test It

After adding cookies, run:
```bash
python3 job-scraper-smart.py
```

You should see:
```
✅ LinkedIn authentication enabled (more results!)
```

If you see this instead:
```
ℹ️  LinkedIn authentication not configured (limited results)
```

Then the cookies weren't loaded correctly. Check your .env file formatting.
