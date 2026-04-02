---
name: google-sheets
description: Read and write Google Sheets via service account. Use when you need to create, update, format, or read spreadsheets. Supports service account authentication with base64-encoded JSON key.
homepage: https://developers.google.com/sheets/api
metadata:
  {
    "openclaw":
      {
        "emoji": "📊",
        "requires":
          {
            "anyBins": ["python3", "python"],
            "anyEnv": ["GOOGLE_SERVICE_ACCOUNT_SECRET", "GA4_SERVICE_ACCOUNT_SECRET"],
          },
      },
  }
---

# Google Sheets — Service Account

Read, write, and format Google Sheets via Python `gspread` library.

## Setup (one-time)

1. Enable Google Sheets API: https://console.cloud.google.com/apis/library/sheets.googleapis.com
2. Create a service account in GCP Console (or reuse existing one, e.g. from GA4 skill)
3. Base64-encode the JSON key: `base64 -w0 service-account.json`
4. Set environment variable: `GOOGLE_SERVICE_ACCOUNT_SECRET` (or `GA4_SERVICE_ACCOUNT_SECRET`) — base64-encoded JSON key
5. Share your spreadsheet with the service account email (Editor role)

## Safety Boundaries

- This skill connects to Google Sheets API endpoints only.
- It can read and write spreadsheet data (as granted by sharing permissions).
- It does NOT store or transmit credentials beyond the current session.

## Find Service Account Email

```python
import json, base64, os
sa_secret = os.environ.get('GOOGLE_SERVICE_ACCOUNT_SECRET') or os.environ.get('GA4_SERVICE_ACCOUNT_SECRET')
info = json.loads(base64.b64decode(sa_secret))
print(info['client_email'])
```

Share your spreadsheet with this email to grant access.

## Connect

```python
import gspread, json, base64, os
from google.oauth2 import service_account

sa_secret = os.environ.get('GOOGLE_SERVICE_ACCOUNT_SECRET') or os.environ.get('GA4_SERVICE_ACCOUNT_SECRET')
info = json.loads(base64.b64decode(sa_secret))
creds = service_account.Credentials.from_service_account_info(info, scopes=[
    'https://www.googleapis.com/auth/spreadsheets'
])
gc = gspread.authorize(creds)
```

Install: `pip install gspread google-auth`

## Open a Spreadsheet

```python
# By ID (from URL: docs.google.com/spreadsheets/d/{ID}/edit)
sh = gc.open_by_key('SPREADSHEET_ID_HERE')

# Work with sheets
ws = sh.sheet1                    # first sheet
ws = sh.worksheet('Sheet Name')  # by name
```

⚠️ **open_by_key** is the primary method. `open()` and `openall()` require Drive API scope.

## Read

```python
# All data
vals = ws.get_all_values()        # list of lists
records = ws.get_all_records()    # list of dicts (headers = first row)

# Range
vals = ws.get('A1:D10')

# Single cell
val = ws.acell('A1').value
```

## Write

```python
# Write range
ws.update(range_name='A1', values=[
    ["Header 1", "Header 2"],
    ["Value 1", "Value 2"],
])

# Single cell
ws.update_acell('A1', 'Hello')

# Clear
ws.clear()

# Append row
ws.append_row(["col1", "col2", "col3"])
```

## Formatting

Formatting via `batch_update` with requests:

### Header style (dark blue background, white text)
```python
{
    "repeatCell": {
        "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 8},
        "cell": {
            "userEnteredFormat": {
                "backgroundColor": {"red": 0.06, "green": 0.2, "blue": 0.37},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}, "fontSize": 10},
                "horizontalAlignment": "CENTER"
            }
        },
        "fields": "userEnteredFormat"
    }
}
```

### Zebra striping
```python
for row in range(1, num_rows):
    if row % 2 == 0:
        requests.append({
            "repeatCell": {
                "range": {"sheetId": 0, "startRowIndex": row, "endRowIndex": row+1, ...},
                "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.95, "green": 0.96, "blue": 0.97}}},
                "fields": "userEnteredFormat"
            }
        })
```

### Column width
```python
{
    "updateDimensionProperties": {
        "range": {"sheetId": 0, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
        "properties": {"pixelSize": 150},
        "fields": "pixelSize"
    }
}
```

### Number format
```python
{
    "repeatCell": {
        "range": {"sheetId": 0, "startRowIndex": 1, "endRowIndex": 15, "startColumnIndex": 4, "endColumnIndex": 5},
        "cell": {"userEnteredFormat": {"numberFormat": {"type": "NUMBER", "pattern": "#,##0"}}},
        "fields": "userEnteredFormat.numberFormat"
    }
}
```

### Freeze header row
```python
{
    "updateSheetProperties": {
        "properties": {"sheetId": 0, "gridProperties": {"frozenRowCount": 1}},
        "fields": "gridProperties.frozenRowCount"
    }
}
```

### Apply formatting
```python
sh.batch_update({"requests": requests})
```

## Get Spreadsheet ID

From URL: `docs.google.com/spreadsheets/d/{THIS_IS_THE_ID}/edit`

## Limits

- Without Drive API scope: cannot search by name (`open()`, `openall()`). Use `open_by_key()` only.
- Quotas: 300 requests/min per project
