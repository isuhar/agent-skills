---
name: yandex-direct
description: Manage Yandex Direct ad campaigns and query Wordstat via API. Use for ad statistics, campaign management, keyword analysis, search query reports, and keyword research via Wordstat.
metadata:
  clawdbot:
    emoji: "📢"
    requires:
      env: ["YANDEX_CLIENT_ID", "YANDEX_CLIENT_SECRET"]
      primaryEnv: "YANDEX_CLIENT_ID"
      bins: ["python3"]
---

# Яндекс Директ + Вордстат API

Управление рекламными кампаниями и анализ ключевых слов.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `YANDEX_CLIENT_ID` | Client ID OAuth-приложения |
| `YANDEX_CLIENT_SECRET` | Client Secret OAuth-приложения |
| `YANDEX_TOKEN_FILE` | Путь к файлу с токенами (по умолчанию `~/.yandex_tokens.json`) |

Настройка токенов — см. скилл **yandex-oauth**.

## Авторизация и базовый запрос

Авторизация через файл токенов с авто-обновлением (см. `get_yandex_token()` в скилле **yandex-oauth**).

Все запросы — HTTPS POST на `https://api.direct.yandex.com/json/v5/<service>/`.

```python
import urllib.request, urllib.parse, json, os, time

TOKEN_FILE = os.environ.get("YANDEX_TOKEN_FILE", os.path.expanduser("~/.yandex_tokens.json"))

def get_yandex_token() -> str:
    with open(TOKEN_FILE) as f:
        tokens = json.load(f)
    if time.time() < tokens.get("issued_at", 0) + tokens.get("expires_in", 0) - 3600:
        return tokens["access_token"]
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": os.environ["YANDEX_CLIENT_ID"],
        "client_secret": os.environ["YANDEX_CLIENT_SECRET"],
    }).encode()
    result = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth.yandex.ru/token", data=data, method="POST")
    ).read())
    tokens.update({"access_token": result["access_token"], "refresh_token": result["refresh_token"],
                    "expires_in": result.get("expires_in", 31536000), "issued_at": int(time.time())})
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    return tokens["access_token"]

TOKEN = get_yandex_token()

def direct_request(service: str, method: str, params: dict) -> dict:
    url = f"https://api.direct.yandex.com/json/v5/{service}/"
    body = json.dumps({"method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Language": "ru",
    })
    return json.loads(urllib.request.urlopen(req).read())
```

## Сервисы и методы

| Сервис | Методы | Описание |
|---|---|---|
| `campaigns` | get, add, update, delete, suspend, resume, archive, unarchive | Кампании |
| `adgroups` | get, add, update, delete | Группы объявлений |
| `ads` | get, add, update, delete, moderate, suspend, resume | Объявления |
| `keywords` | get, add, update, delete, suspend, resume | Ключевые фразы |
| `sitelinks` | get, add, delete | Наборы быстрых ссылок |
| `adimages` | get, add, delete | Изображения |
| `dictionaries` | get | Справочники (регионы, валюты) |

## Получение кампаний

```python
result = direct_request("campaigns", "get", {
    "SelectionCriteria": {},
    "FieldNames": ["Id", "Name", "Status", "State", "Type", "Statistics", "DailyBudget"],
})
```

## Reports API — статистика

Отдельный эндпоинт: `https://api.direct.yandex.com/json/v5/reports`.

```python
import time

def direct_report(report_def: dict) -> str:
    url = "https://api.direct.yandex.com/json/v5/reports"
    body = json.dumps({"params": report_def}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Language": "ru",
        "processingMode": "auto",
        "returnMoneyInMicros": "false",
        "skipReportHeader": "true",
        "skipReportSummary": "true",
    })
    while True:
        resp = urllib.request.urlopen(req)
        if resp.status == 200:
            return resp.read().decode("utf-8")
        elif resp.status in (201, 202):
            time.sleep(int(resp.headers.get("retryIn", 5)))
        else:
            raise Exception(f"Report error: {resp.status}")
```

### Типы отчётов

| ReportType | Группировка |
|---|---|
| `CAMPAIGN_PERFORMANCE_REPORT` | По кампаниям |
| `ADGROUP_PERFORMANCE_REPORT` | По группам |
| `AD_PERFORMANCE_REPORT` | По объявлениям |
| `CRITERIA_PERFORMANCE_REPORT` | По условиям показа |
| `SEARCH_QUERY_PERFORMANCE_REPORT` | По поисковым запросам |
| `CUSTOM_REPORT` | Произвольный |

### Основные поля

**Измерения:** CampaignId, CampaignName, AdGroupId, AdGroupName, AdId, AdNetworkType, Age, Gender, Device, Date, Month, Year, Query, Keyword

**Метрики:** Impressions, Clicks, Cost, Ctr, AvgCpc, AvgImpressionPosition, BounceRate, Conversions, ConversionRate, CostPerConversion

### Пример: расходы по кампаниям

```python
tsv = direct_report({
    "SelectionCriteria": {"DateFrom": "2026-03-01", "DateTo": "2026-03-31"},
    "FieldNames": ["CampaignName", "Impressions", "Clicks", "Cost", "Ctr", "AvgCpc"],
    "ReportName": "campaign_monthly",
    "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
    "DateRangeType": "CUSTOM_DATE",
    "Format": "TSV",
    "IncludeVAT": "YES",
})

# Парсинг TSV
lines = tsv.strip().split("\n")
headers = lines[0].split("\t")
rows = [dict(zip(headers, line.split("\t"))) for line in lines[1:]]
```

### DateRangeType

`CUSTOM_DATE`, `TODAY`, `YESTERDAY`, `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `THIS_MONTH`, `LAST_MONTH`, `ALL_TIME`

### Фильтрация

```json
{"Field": "CampaignName", "Operator": "EQUALS", "Values": ["campaign_name"]}
{"Field": "Clicks", "Operator": "GREATER_THAN", "Values": ["0"]}
{"Field": "AdNetworkType", "Operator": "EQUALS", "Values": ["SEARCH"]}
```

Операторы: `EQUALS`, `NOT_EQUALS`, `IN`, `NOT_IN`, `LESS_THAN`, `GREATER_THAN`, `STARTS_WITH_IGNORE_CASE`

## Создание кампании — пошагово

### 1. Кампания

```python
result = direct_request("campaigns", "add", {"Campaigns": [{
    "Name": "Campaign Name",
    "StartDate": "2026-04-01",
    "NegativeKeywords": {"Items": ["minus", "words"]},
    "TextCampaign": {
        "BiddingStrategy": {
            "Search": {
                "BiddingStrategyType": "WB_MAXIMUM_CLICKS",
                "WbMaximumClicks": {"WeeklySpendLimit": 5000000000}  # руб × 1_000_000
            },
            "Network": {"BiddingStrategyType": "NETWORK_DEFAULT"}
        },
    }
}]})
campaign_id = result["result"]["AddResults"][0]["Id"]
```

### 2. Группа объявлений

```python
result = direct_request("adgroups", "add", {"AdGroups": [{
    "Name": "Ad Group Name",
    "CampaignId": campaign_id,
    "RegionIds": [225],  # 225 = Россия
}]})
adgroup_id = result["result"]["AddResults"][0]["Id"]
```

### 3. Ключевые фразы

```python
direct_request("keywords", "add", {"Keywords": [
    {"Keyword": "keyword phrase", "AdGroupId": adgroup_id},
]})
```

### 4. Объявления

```python
# Title: до 56 символов, Title2: до 30, Text: до 81
direct_request("ads", "add", {"Ads": [{
    "AdGroupId": adgroup_id,
    "TextAd": {
        "Title": "Headline up to 56 chars",
        "Title2": "Subheading up to 30",
        "Text": "Ad text up to 81 characters with CTA.",
        "Href": "https://example.com/?utm_source=yandex&utm_medium=cpc"
    }
}]})
```

### 5. Модерация и запуск

```python
direct_request("ads", "moderate", {"SelectionCriteria": {"Ids": [ad_id]}})
direct_request("campaigns", "resume", {"SelectionCriteria": {"Ids": [campaign_id]}})
```

## ⚠️ Частые ошибки

| Ошибка | Решение |
|---|---|
| `DailyBudget` с автостратегиями | Нельзя — используй `WeeklySpendLimit` |
| Sitelinks inline в TextAd | Создавай через сервис `sitelinks`, привязывай через `update` |
| Символ `·` в Title2 | Запрещён — используй `-` или `,` |
| WebP-картинки | Не поддерживаются — конвертируй в PNG |
| Мастер-кампании через API | Недоступны — только TEXT_CAMPAIGN |

---

## Вордстат API

Базовый URL: `https://api.wordstat.yandex.net`

Квота: 10 запросов/сек, 1000 запросов/сутки.

### topRequests — частотность фраз

```python
WORDSTAT_TOKEN = TOKEN  # тот же токен, если приложение имеет доступ к Вордстат API

def wordstat_top(phrase: str, regions=None, num=50) -> dict:
    body = {"phrase": phrase, "numPhrases": num}
    if regions:
        body["regions"] = regions
    req = urllib.request.Request(
        "https://api.wordstat.yandex.net/v1/topRequests",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {WORDSTAT_TOKEN}", "Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())
```

Ответ: `totalCount`, `topRequests` [{phrase, count}], `associations` [{phrase, count}].

Батч: `phrases` (массив до 128) вместо `phrase`.

### dynamics — динамика запросов

```python
def wordstat_dynamics(phrase: str, period="weekly", from_date="2025-01-06") -> dict:
    body = {"phrase": phrase, "period": period, "fromDate": from_date}
    req = urllib.request.Request(
        "https://api.wordstat.yandex.net/v1/dynamics",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {WORDSTAT_TOKEN}", "Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())
```

`period`: `daily` (60 дней), `weekly`, `monthly` (с 2018-01-01).

### regions — география запросов

```python
def wordstat_regions(phrase: str, region_type="all") -> dict:
    body = {"phrase": phrase, "regionType": region_type}
    req = urllib.request.Request(
        "https://api.wordstat.yandex.net/v1/regions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {WORDSTAT_TOKEN}", "Content-Type": "application/json"},
    )
    return json.loads(urllib.request.urlopen(req).read())
```

`regionType`: `cities`, `regions`, `all`.

### userInfo — проверка квоты

```
POST https://api.wordstat.yandex.net/v1/userInfo
```
