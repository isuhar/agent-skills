---
name: ga4
description: Query Google Analytics 4 (GA4) data via the Analytics Data API. Use when you need to pull website analytics like top pages, traffic sources, user counts, sessions, conversions, or any GA4 metrics/dimensions. Supports custom date ranges and filtering.
homepage: https://developers.google.com/analytics
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires":
          {
            "anyBins": ["python3", "python"],
            "anyEnv": ["GA4_SERVICE_ACCOUNT_SECRET", "GOOGLE_CLIENT_ID"],
            "env": ["GA4_PROPERTY_ID"],
          },
      },
  }
---

# GA4 - Google Analytics 4 Data API

Query GA4 properties for analytics data: page views, sessions, users, traffic sources, conversions, and more.

## Setup (one-time)

1. Enable Google Analytics Data API: https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com
2. Set `GA4_PROPERTY_ID` — your GA4 property ID (numeric, e.g., "123456789")
3. Choose **one** auth method:

### Option A: Service Account (recommended for servers/agents)
- Create a service account in GCP Console
- Add the SA email to GA4 Admin → Property Access Management (Viewer role)
- Base64-encode the JSON key: `base64 -w0 service-account.json`
- Set `GA4_SERVICE_ACCOUNT_SECRET` — base64-encoded service account JSON key
- ✅ No refresh needed, ideal for headless environments

### Option B: OAuth (for interactive use)
- Create OAuth 2.0 Client ID (Desktop app) in GCP Console
- Run `python3 scripts/ga4_auth.py url --client-id YOUR_ID` to get auth URL
- Set environment variables:
  - `GOOGLE_CLIENT_ID` — OAuth client ID
  - `GOOGLE_CLIENT_SECRET` — OAuth client secret
  - `GOOGLE_REFRESH_TOKEN` — from auth flow (`scripts/ga4_auth.py exchange ...`)

## Safety Boundaries

- This skill only connects to Google Analytics Data API endpoints.
- It does NOT write to or modify your GA4 property — read-only queries only.
- It does NOT store or transmit credentials beyond the current session.
## Common Queries

### Top Pages (by pageviews)
```bash
python3 scripts/ga4_query.py --metric screenPageViews --dimension pagePath --limit 30
```

### Top Pages with Sessions & Users
```bash
python3 scripts/ga4_query.py --metrics screenPageViews,sessions,totalUsers --dimension pagePath --limit 20
```

### Traffic Sources
```bash
python3 scripts/ga4_query.py --metric sessions --dimension sessionSource --limit 20
```

### Landing Pages
```bash
python3 scripts/ga4_query.py --metric sessions --dimension landingPage --limit 30
```

### Custom Date Range
```bash
python3 scripts/ga4_query.py --metric sessions --dimension pagePath --start 2026-01-01 --end 2026-01-15
```

### Filter by Page Path
```bash
python3 scripts/ga4_query.py --metric screenPageViews --dimension pagePath --filter "pagePath=~/blog/"
```

## Available Metrics

Common metrics: `screenPageViews`, `sessions`, `totalUsers`, `newUsers`, `activeUsers`, `bounceRate`, `averageSessionDuration`, `conversions`, `eventCount`

## Available Dimensions

Common dimensions: `pagePath`, `pageTitle`, `landingPage`, `sessionSource`, `sessionMedium`, `sessionCampaignName`, `country`, `city`, `deviceCategory`, `browser`, `date`

## Output Formats

Default: Table format
Add `--json` for JSON output
Add `--csv` for CSV output
