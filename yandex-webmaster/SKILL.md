---
name: yandex-webmaster
description: Query Yandex Webmaster API v4. Use for indexing status, search queries, SQI history, sitemaps, diagnostics, recrawl, external/internal links, and pages in search. Covers индексация, поисковые запросы Яндекса, ИКС, переобход страниц, диагностика сайта.
---

# Яндекс Вебмастер — API v4

Данные по индексации и поисковой видимости сайта в Яндексе.

## Переменные окружения

Авторизация — та же, что для Яндекс Метрики:

- `YANDEX_METRIKA_TOKEN` — base64-encoded JSON с `access_token`, `refresh_token`, `expires_in`, `token_type`
- `YANDEX_CLIENT_ID` — Client ID приложения Яндекс OAuth
- `YANDEX_CLIENT_SECRET` — Client Secret приложения Яндекс OAuth

Скоуп OAuth: `webmaster:verify` для полного доступа.

## Авторизация

Используй `ym_auth.py` из скилла `yandex-metrika`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../yandex-metrika"))
from ym_auth import get_token
token = get_token()
```

## Базовый URL

```
https://api.webmaster.yandex.net/v4
```

Все запросы требуют заголовок `Authorization: OAuth {token}`.

## Получение user-id

Перед любыми вызовами нужен `user_id`:

```python
import urllib.request, json

def get_user_id(token):
    req = urllib.request.Request(
        "https://api.webmaster.yandex.net/v4/user",
        headers={"Authorization": f"OAuth {token}"}
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["user_id"]
```

## Получение host-id

```python
def get_hosts(token, user_id):
    req = urllib.request.Request(
        f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts",
        headers={"Authorization": f"OAuth {token}"}
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["hosts"]
```

`host_id` — строка вида `https:example.com:443`. Определяй динамически через список хостов.

## Шаблон запроса

```python
BASE = "https://api.webmaster.yandex.net/v4"

def wm_get(token, path):
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Authorization": f"OAuth {token}"}
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def wm_post(token, path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers={
            "Authorization": f"OAuth {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())
```

## Основные эндпоинты

Все пути начинаются с `/user/{user_id}/hosts/{host_id}`.

### Статистика сайта (summary)
```
GET .../summary
```
Возвращает: ИКС, кол-во страниц в поиске, проиндексированных, исключённых, ошибки.

### ИКС — история (SQI)
```
GET .../sqi-history?date_from=2026-01-01&date_to=2026-03-01
```
Возвращает массив `{date, sqi}`.

### Популярные поисковые запросы
```
GET .../search-queries/popular?order_by=TOTAL_SHOWS&query_indicator=TOTAL_SHOWS&query_indicator=TOTAL_CLICKS&query_indicator=AVG_SHOW_POSITION&query_indicator=AVG_CLICK_POSITION
```
Параметры:
- `order_by` — сортировка: `TOTAL_SHOWS`, `TOTAL_CLICKS`, `AVG_SHOW_POSITION`, `AVG_CLICK_POSITION`

### Мониторинг поисковых запросов (Query Analytics)
```
POST .../query-analytics/list
```
Body:
```json
{
  "offset": 0,
  "limit": 500,
  "device_type_indicator": "ALL",
  "text_indicator": "URL",
  "region_ids": [],
  "filters": {},
  "sort_by_date": "2026-03-01",
  "query_indicator": "TOTAL_SHOWS",
  "date_from": "2026-02-01",
  "date_to": "2026-03-01"
}
```
Ответ содержит `text_indicator_to_statistics` с данными по каждому запросу/URL: показы, клики, CTR, позиция.

### История индексирования
```
GET .../indexing/history?date_from=2026-01-01&date_to=2026-03-01
```
Массив `{date, http_2xx_urls_count, ...}` — сколько страниц проиндексировано.

### Примеры проиндексированных страниц
```
GET .../indexing/samples?limit=100&offset=0
```

### Страницы в поиске — история
```
GET .../search-urls/in-search/history?date_from=2026-01-01&date_to=2026-03-01
```
Массив `{date, total_urls_count}`.

### Примеры страниц в поиске
```
GET .../search-urls/in-search/samples?limit=100&offset=0
```

### Появление/исключение страниц из поиска — история
```
GET .../search-urls/events/history?date_from=2026-01-01&date_to=2026-03-01
```

### Диагностика сайта
```
GET .../diagnostics
```
Возвращает список проблем (`FATAL`, `CRITICAL`, `WARNING`, `RECOMMENDATION`).

### Sitemaps
```
GET .../sitemaps                         # все sitemap
GET .../user-added-sitemaps              # добавленные пользователем
POST .../user-added-sitemaps             # добавить sitemap {"url": "https://..."}
DELETE .../user-added-sitemaps/{id}      # удалить
```

### Переобход страниц (recrawl)
```
GET .../recrawl/quota                    # оставшаяся квота
GET .../recrawl/queue                    # очередь задач
POST .../recrawl/queue                   # отправить на переобход {"url": "https://..."}
GET .../recrawl/queue/{task-id}          # статус задачи
```

### Внешние ссылки
```
GET .../links/external/samples?limit=100&offset=0
GET .../links/external/history?date_from=...&date_to=...
```

### Битые внутренние ссылки
```
GET .../links/internal/broken/samples?limit=100&offset=0
GET .../links/internal/broken/history?date_from=...&date_to=...
```

### Мониторинг важных страниц
```
GET .../important-urls
GET .../important-urls/history?url=https://example.com/...
```

## Полный пример: получить summary + ИКС + топ запросы

```python
#!/usr/bin/env python3
import sys, os, json, urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../yandex-metrika"))
from ym_auth import get_token

token = get_token()
BASE = "https://api.webmaster.yandex.net/v4"

def wm_get(path):
    req = urllib.request.Request(f"{BASE}{path}", headers={"Authorization": f"OAuth {token}"})
    return json.loads(urllib.request.urlopen(req).read())

def wm_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers={"Authorization": f"OAuth {token}", "Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req).read())

# 1. Get user_id
user_id = wm_get("/user")["user_id"]

# 2. Get host_id for your site
hosts = wm_get(f"/user/{user_id}/hosts")["hosts"]
host = hosts[0]  # or filter by domain: next(h for h in hosts if "example.com" in h.get("ascii_host_url", ""))
host_id = host["host_id"]
prefix = f"/user/{user_id}/hosts/{host_id}"

# 3. Summary
summary = wm_get(f"{prefix}/summary")
print("=== Summary ===")
print(json.dumps(summary, indent=2, ensure_ascii=False))

# 4. SQI history (last 90 days)
from datetime import date, timedelta
today = date.today()
sqi = wm_get(f"{prefix}/sqi-history?date_from={(today - timedelta(days=90)).isoformat()}&date_to={today.isoformat()}")
print("\n=== SQI History ===")
for point in sqi.get("points", []):
    print(f"  {point['date']}: {point['sqi']}")

# 5. Popular search queries
queries = wm_get(f"{prefix}/search-queries/popular?order_by=TOTAL_CLICKS&query_indicator=TOTAL_CLICKS&query_indicator=TOTAL_SHOWS&query_indicator=AVG_SHOW_POSITION")
print("\n=== Top Search Queries ===")
for q in queries.get("queries", [])[:20]:
    print(f"  {q['query_text']}: clicks={q.get('indicators',{}).get('TOTAL_CLICKS','-')}, shows={q.get('indicators',{}).get('TOTAL_SHOWS','-')}, pos={q.get('indicators',{}).get('AVG_SHOW_POSITION','-')}")
```

## Связанные скиллы

- **yandex-metrika** — трафик сайта, рекламные кампании Яндекс.Директ
- **yandex-direct** — управление рекламными кампаниями
- **ga4** — продуктовые метрики (MAU, DAU, events)
- **google-search-console** — SEO в Google
