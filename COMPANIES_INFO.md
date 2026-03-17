# 527 US Tech Companies

The AI job agent now searches **527 US tech company career portals** directly!

## Breakdown by Category

- **FAANG**: 6 companies (Google, Amazon, Microsoft, Apple, Meta, Netflix)
- **Enterprise**: 35 companies (Salesforce, Oracle, Adobe, IBM, SAP, etc.)
- **Unicorns**: 30 companies (Stripe, Airbnb, Uber, SpaceX, Tesla, Palantir, etc.)
- **Fintech**: 17 companies (Affirm, Brex, Carta, Plaid, Chime, Square, PayPal, etc.)
- **Cloud**: 13 companies (Databricks, Snowflake, MongoDB, Cloudflare, etc.)
- **DevTools**: 21 companies (GitHub, GitLab, Atlassian, Docker, Postman, etc.)
- **Ecommerce**: 14 companies (Shopify, Etsy, Wayfair, eBay, Chewy, etc.)
- **Social**: 22 companies (Twitter, Snap, Pinterest, Reddit, LinkedIn, TikTok, etc.)
- **Gaming**: 14 companies (Roblox, Unity, Epic Games, Riot Games, EA, etc.)
- **PropTech**: 11 companies (Zillow, Redfin, Opendoor, Compass, etc.)
- **Travel**: 7 companies (Expedia, Booking.com, TripAdvisor, Airbnb, etc.)
- **FoodTech**: 7 companies (GrubHub, Gopuff, Toast, OpenTable, Yelp, etc.)
- **EdTech**: 11 companies (Coursera, Udemy, Duolingo, Chegg, Codecademy, etc.)
- **Healthtech**: 19 companies (23andMe, Zocdoc, Teladoc, Peloton, Fitbit, etc.)
- **Additional Startups**: 300 emerging tech companies

## How It Works

1. Agent loads all 527 companies from `companies_list.json`
2. Searches each company's career portal directly
3. Finds software engineering jobs matching your profile
4. Uses Claude AI to filter by experience level
5. Shows you the best matches with direct application links

## Run the Agent

```bash
python3 job-agent-final.py
```

The agent will search ALL 527 companies and show you jobs to apply!

## Customize the List

Want to add more companies? Edit `build_companies_list.py` and run:

```bash
python3 build_companies_list.py
```

This regenerates `companies_list.json` with your additions.
