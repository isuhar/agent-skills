---
name: yandex-direct
description: Manage Yandex Direct ad campaigns and query Wordstat via API. Use for ad statistics (clicks, impressions, cost, conversions), campaign management (get/suspend/resume), keyword analysis, search query reports, and keyword research via Wordstat (frequency, dynamics, regions). Covers Яндекс Директ API v5 and Вордстат API.
---

# Яндекс Директ + Вордстат API

Управление рекламными кампаниями и анализ ключевых слов.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `YANDEX_METRIKA_TOKEN` | base64-encoded JSON с `access_token`, `refresh_token` и др. (общий с yandex-metrika) |
| `YANDEX_CLIENT_ID` | Client ID OAuth-приложения |
| `YANDEX_CLIENT_SECRET` | Client Secret OAuth-приложения |
| `YANDEX_WORDSTAT_TOKEN` | OAuth-токен для Вордстат API (если отдельный; иначе используется тот же) |

## Авторизация

Используй `ym_auth.py` из скилла `yandex-metrika` для автоматического рефреша токена:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../yandex-metrika"))
from ym_auth import get_token
token = get_token()
```

## Часть 1: Директ API v5

### Базовый формат запросов

Все запросы — HTTPS POST на `https://api.direct.yandex.com/json/v5/<service>/`.

```python
import urllib.request, json

def direct_request(service, method, params, token):
    url = f"https://api.direct.yandex.com/json/v5/{service}/"
    body = json.dumps({"method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Language": "ru",
    })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())
```

### Сервисы и методы

| Сервис | Методы | Описание |
|---|---|---|
| `campaigns` | get, add, update, delete, suspend, resume, archive, unarchive | Управление кампаниями |
| `adgroups` | get, add, update, delete | Группы объявлений |
| `ads` | get, add, update, delete, moderate, suspend, resume | Объявления |
| `keywords` | get, add, update, delete, suspend, resume | Ключевые фразы |
| `dictionaries` | get | Справочники (регионы, валюты и др.) |

### Получение кампаний

```python
result = direct_request("campaigns", "get", {
    "SelectionCriteria": {},  # все кампании
    "FieldNames": ["Id", "Name", "Status", "State", "Type",
                   "Statistics", "DailyBudget"],
}, token)
campaigns = result["result"]["Campaigns"]
```

### Reports API — статистика

Отдельный эндпоинт: `https://api.direct.yandex.com/json/v5/reports`.

```python
def direct_report(report_def, token):
    url = "https://api.direct.yandex.com/json/v5/reports"
    body = json.dumps({"params": report_def}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
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
        elif resp.status == 201 or resp.status == 202:
            import time
            retry = int(resp.headers.get("retryIn", 5))
            time.sleep(retry)
        else:
            raise Exception(f"Report error: {resp.status}")
```

### Типы отчётов

| ReportType | Описание | Группировка |
|---|---|---|
| `ACCOUNT_PERFORMANCE_REPORT` | По аккаунту | — |
| `CAMPAIGN_PERFORMANCE_REPORT` | По кампаниям | CampaignId |
| `ADGROUP_PERFORMANCE_REPORT` | По группам | AdGroupId |
| `AD_PERFORMANCE_REPORT` | По объявлениям | AdId |
| `CRITERIA_PERFORMANCE_REPORT` | По условиям показа | AdGroupId, CriteriaId |
| `CUSTOM_REPORT` | Произвольный | — |
| `SEARCH_QUERY_PERFORMANCE_REPORT` | По поисковым запросам | AdGroupId, Query |

### Основные поля отчётов

**Измерения:** CampaignId, CampaignName, AdGroupId, AdGroupName, AdId, AdNetworkType (SEARCH/AD_NETWORK), Age, Gender, Device, Date, Month, Quarter, Year, Query, Keyword, CriteriaType, LocationOfPresenceId

**Метрики:** Impressions, Clicks, Cost, Ctr, AvgCpc, AvgImpressionPosition, AvgClickPosition, BounceRate, Conversions, ConversionRate, CostPerConversion, AvgPageviews

### Пример: расходы по кампаниям за неделю

```python
report_def = {
    "SelectionCriteria": {
        "DateFrom": "2026-02-24",
        "DateTo": "2026-03-02",
    },
    "FieldNames": ["CampaignName", "Impressions", "Clicks", "Cost", "Ctr", "AvgCpc"],
    "ReportName": "campaign_weekly",
    "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
    "DateRangeType": "CUSTOM_DATE",
    "Format": "TSV",
    "IncludeVAT": "YES",
}
tsv = direct_report(report_def, token)
```

### Пример: поисковые запросы

```python
report_def = {
    "SelectionCriteria": {
        "DateFrom": "2026-02-24",
        "DateTo": "2026-03-02",
    },
    "FieldNames": ["Query", "CampaignName", "Impressions", "Clicks", "Cost"],
    "ReportName": "search_queries",
    "ReportType": "SEARCH_QUERY_PERFORMANCE_REPORT",
    "DateRangeType": "CUSTOM_DATE",
    "Format": "TSV",
    "IncludeVAT": "YES",
}
```

### DateRangeType

| Значение | Описание |
|---|---|
| `CUSTOM_DATE` | Произвольный (DateFrom/DateTo обязательны) |
| `TODAY` | Сегодня |
| `YESTERDAY` | Вчера |
| `LAST_3_DAYS` | Последние 3 дня |
| `LAST_7_DAYS` | Последние 7 дней |
| `LAST_14_DAYS` | Последние 14 дней |
| `LAST_30_DAYS` | Последние 30 дней |
| `THIS_MONTH` | Текущий месяц |
| `LAST_MONTH` | Прошлый месяц |
| `ALL_TIME` | Всё время |

### Фильтрация (SelectionCriteria.Filter)

```json
{"Field": "CampaignName", "Operator": "EQUALS", "Values": ["mk_notion_semant"]}
{"Field": "Clicks", "Operator": "GREATER_THAN", "Values": ["0"]}
{"Field": "AdNetworkType", "Operator": "EQUALS", "Values": ["SEARCH"]}
```

Операторы: EQUALS, NOT_EQUALS, IN, NOT_IN, LESS_THAN, GREATER_THAN, STARTS_WITH_IGNORE_CASE

### Парсинг TSV-ответа

```python
lines = tsv.strip().split("\n")
headers = lines[0].split("\t")
rows = [dict(zip(headers, line.split("\t"))) for line in lines[1:]]
```

## Часть 2: Вордстат API

Базовый URL: `https://api.wordstat.yandex.net`

Авторизация: `Authorization: Bearer <token>` (нужен отдельный доступ к API Вордстата — заявка через поддержку Директа).

Квота: 10 запросов/сек, 1000 запросов/сутки.

### topRequests — частотность фраз

```python
def wordstat_top(phrase, token, regions=None, devices=None, num=50):
    url = "https://api.wordstat.yandex.net/v1/topRequests"
    body = {"phrase": phrase, "numPhrases": num}
    if regions: body["regions"] = regions
    if devices: body["devices"] = devices
    req = urllib.request.Request(url,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())
```

Ответ: `totalCount`, `topRequests` [{phrase, count}...], `associations` [{phrase, count}...]

Батч: передать `phrases` (массив до 128) вместо `phrase`.

### dynamics — динамика запросов

```python
def wordstat_dynamics(phrase, token, period="weekly", from_date="2025-01-06", to_date=None):
    body = {"phrase": phrase, "period": period, "fromDate": from_date}
    if to_date: body["toDate"] = to_date
    req = urllib.request.Request("https://api.wordstat.yandex.net/v1/dynamics",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        })
    return json.loads(urllib.request.urlopen(req).read())
```

period: `daily` (60 дней), `weekly`, `monthly` (с 2018-01-01). fromDate для monthly = 1-е число, weekly = понедельник.

### regions — география запросов

```python
def wordstat_regions(phrase, token, region_type="all"):
    body = {"phrase": phrase, "regionType": region_type}
    req = urllib.request.Request("https://api.wordstat.yandex.net/v1/regions",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        })
    return json.loads(urllib.request.urlopen(req).read())
```

regionType: `cities`, `regions`, `all`. Ответ: [{regionId, count, share, affinityIndex}...]

### getRegionsTree — справочник регионов

```
POST https://api.wordstat.yandex.net/v1/getRegionsTree
```
Без параметров. Не расходует квоту.

### userInfo — квота

```
POST https://api.wordstat.yandex.net/v1/userInfo
```
Ответ: login, limitPerSecond, dailyLimit, dailyLimitRemaining.

## Создание кампании — пошаговый процесс

### Шаг 1: Создать кампанию

```python
result = direct_request("campaigns", "add", {"Campaigns": [{
    "Name": "Название кампании [search]",
    "StartDate": "2026-03-07",
    "NegativeKeywords": {"Items": ["минус", "слова"]},
    "TextCampaign": {
        "BiddingStrategy": {
            "Search": {
                "BiddingStrategyType": "WB_MAXIMUM_CLICKS",
                "WbMaximumClicks": {"WeeklySpendLimit": 5000000000}  # 5000₽/нед (микроединицы: руб × 1_000_000)
            },
            "Network": {"BiddingStrategyType": "NETWORK_DEFAULT"}
        },
        "Settings": [
            {"Option": "ADD_METRICA_TAG", "Value": "YES"},
            {"Option": "ENABLE_SITE_MONITORING", "Value": "YES"}
        ]
    }
}]}, token)
campaign_id = result["result"]["AddResults"][0]["Id"]
```

### Шаг 2: Создать группу объявлений

```python
result = direct_request("adgroups", "add", {"AdGroups": [{
    "Name": "Название группы",
    "CampaignId": campaign_id,
    "RegionIds": [225],  # 225 = Россия
    "TrackingParams": "utm_source=yandex&utm_medium=cpc&utm_campaign=название"
}]}, token)
adgroup_id = result["result"]["AddResults"][0]["Id"]
```

### Шаг 3: Добавить ключевые фразы

```python
direct_request("keywords", "add", {"Keywords": [
    {"Keyword": "ключевая фраза", "AdGroupId": adgroup_id},
    # ... до 1000 фраз за запрос
]}, token)
```

### Шаг 4: Создать объявления

```python
# Лимиты: Title до 56 символов, Title2 до 30, Text до 81
result = direct_request("ads", "add", {"Ads": [{
    "AdGroupId": adgroup_id,
    "TextAd": {
        "Title": "Заголовок до 56 символов",
        "Title2": "Подзаголовок до 30",
        "Text": "Текст объявления до 81 символа. Преимущество + CTA.",
        "Href": "https://example.com/?utm_source=yandex&utm_medium=cpc&utm_campaign=name"
    }
}]}, token)
ad_id = result["result"]["AddResults"][0]["Id"]
```

### Шаг 5: Быстрые ссылки (SitelinksSets)

```python
# Создать набор ссылок
result = direct_request("sitelinks", "add", {"SitelinksSets": [{
    "Sitelinks": [
        {"Title": "До 30 символов", "Href": "https://...", "Description": "До 60 символов"},
        {"Title": "Ссылка 2", "Href": "https://...", "Description": "Описание"},
        {"Title": "Ссылка 3", "Href": "https://...", "Description": "Описание"},
        {"Title": "Ссылка 4", "Href": "https://...", "Description": "Описание"}
    ]
}]}, token)
sitelink_set_id = result["result"]["AddResults"][0]["Id"]

# Привязать к объявлению
direct_request("ads", "update", {"Ads": [{
    "Id": ad_id,
    "TextAd": {"SitelinkSetId": sitelink_set_id}
}]}, token)
```

### Шаг 6: Загрузить изображения

```python
import base64

# Форматы: PNG, JPEG, GIF (НЕ WebP!)
# Размеры: стандарт мин 450x450, широкоформат 1080x607
with open("image.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

result = direct_request("adimages", "add", {"AdImages": [{
    "ImageData": image_data,
    "Name": "image_name"
}]}, token)
image_hash = result["result"]["AddResults"][0]["AdImageHash"]

# Привязать к объявлению
direct_request("ads", "update", {"Ads": [{
    "Id": ad_id,
    "TextAd": {"AdImageHash": image_hash}
}]}, token)
```

### Шаг 7: Модерация и включение

```python
# Отправить на модерацию
direct_request("ads", "moderate", {"SelectionCriteria": {"Ids": [ad_id]}}, token)

# После прохождения модерации — включить кампанию
direct_request("campaigns", "resume", {"SelectionCriteria": {"Ids": [campaign_id]}}, token)
```

## ⚠️ Частые ошибки

| Ошибка | Решение |
|---|---|
| `DailyBudget` с автостратегиями | Нельзя — используй `WeeklySpendLimit` |
| Sitelinks inline в TextAd | Нельзя — создавай через сервис `sitelinks`, привязывай через `update` |
| Символ `·` в Title2 | Запрещён — используй `-` или `,` |
| WebP-картинки | Не поддерживаются — конвертируй в PNG |
| Картинки 1536x1024 | Слишком большие — ресайзь wide до 1080x607 |
| Мастер-кампании (МК) через API | Недоступны — только TEXT_CAMPAIGN |

## Правила работы

1. **Перед созданием/изменением кампаний** — тексты и настройки на согласование заказчику
2. **Не публиковать** без одобрения
3. **Если не найдена кампания** — НЕ трогать похожие, уточнить

## Связанные скиллы

- **yandex-metrika** — трафик сайта, поведение посетителей (Метрика видит Директ как источник)
- **ga4** — продуктовые метрики (MAU, DAU, events)
