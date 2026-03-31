---
name: yandex-webmaster
description: Query Yandex Webmaster API v4. Use for indexing status, search queries, SQI history, sitemaps, diagnostics, recrawl, external/internal links, and pages in search.
metadata:
  clawdbot:
    emoji: "🔍"
    requires:
      env: ["YANDEX_WEBMASTER_TOKEN"]
      primaryEnv: "YANDEX_WEBMASTER_TOKEN"
      bins: ["python3"]
---

# Яндекс Вебмастер — API v4

Данные по индексации и поисковой видимости сайта в Яндексе.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `YANDEX_WEBMASTER_TOKEN` | OAuth-токен (скоуп: `webmaster:verify`) |

## Авторизация

Токен: OAuth access_token (заголовок `Authorization: OAuth <token>`).

Получение и обновление токенов — см. скилл **yandex-oauth**.

При ошибке 401 — обновить токен через refresh_token.

## Базовые функции

```python
import urllib.request, json, os

TOKEN = os.environ["YANDEX_WEBMASTER_TOKEN"]
BASE = "https://api.webmaster.yandex.net/v4"

def wm_get(path: str) -> dict:
    req = urllib.request.Request(f"{BASE}{path}", headers={"Authorization": f"OAuth {TOKEN}"})
    return json.loads(urllib.request.urlopen(req).read())

def wm_post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"OAuth {TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )
    return json.loads(urllib.request.urlopen(req).read())
```

## Получение user_id и host_id

```python
user_id = wm_get("/user")["user_id"]
hosts = wm_get(f"/user/{user_id}/hosts")["hosts"]

# Найти нужный хост по домену
host = next(h for h in hosts if "example.com" in h.get("ascii_host_url", ""))
host_id = host["host_id"]
prefix = f"/user/{user_id}/hosts/{host_id}"
```

`host_id` — строка вида `https:example.com:443`. Всегда определяй динамически.

## Основные эндпоинты

Все пути относительно `{prefix}` = `/user/{user_id}/hosts/{host_id}`.

### Статистика сайта (summary)

```python
summary = wm_get(f"{prefix}/summary")
```

Возвращает: ИКС, страницы в поиске, проиндексированные, исключённые, ошибки.

### ИКС — история (SQI)

```python
sqi = wm_get(f"{prefix}/sqi-history?date_from=2026-01-01&date_to=2026-03-31")
# Ответ: {"points": [{"date": "...", "sqi": 10}, ...]}
```

### Популярные поисковые запросы

```python
queries = wm_get(f"{prefix}/search-queries/popular?order_by=TOTAL_CLICKS&query_indicator=TOTAL_CLICKS&query_indicator=TOTAL_SHOWS&query_indicator=AVG_SHOW_POSITION")
```

`order_by`: `TOTAL_SHOWS`, `TOTAL_CLICKS`, `AVG_SHOW_POSITION`, `AVG_CLICK_POSITION`

### Мониторинг поисковых запросов (Query Analytics)

```python
result = wm_post(f"{prefix}/query-analytics/list", {
    "offset": 0,
    "limit": 500,
    "device_type_indicator": "ALL",
    "text_indicator": "URL",
    "query_indicator": "TOTAL_SHOWS",
    "date_from": "2026-03-01",
    "date_to": "2026-03-31",
})
```

### История индексирования

```python
indexing = wm_get(f"{prefix}/indexing/history?date_from=2026-01-01&date_to=2026-03-31")
```

### Примеры проиндексированных страниц

```python
samples = wm_get(f"{prefix}/indexing/samples?limit=100&offset=0")
```

### Страницы в поиске

```python
# История
history = wm_get(f"{prefix}/search-urls/in-search/history?date_from=2026-01-01&date_to=2026-03-31")

# Примеры
samples = wm_get(f"{prefix}/search-urls/in-search/samples?limit=100&offset=0")
```

### Диагностика сайта

```python
diagnostics = wm_get(f"{prefix}/diagnostics")
# Возвращает проблемы: FATAL, CRITICAL, WARNING, RECOMMENDATION
```

### Sitemaps

```python
sitemaps = wm_get(f"{prefix}/sitemaps")                          # все
user_sitemaps = wm_get(f"{prefix}/user-added-sitemaps")          # добавленные вручную
wm_post(f"{prefix}/user-added-sitemaps", {"url": "https://..."}) # добавить
```

### Переобход страниц (recrawl)

```python
quota = wm_get(f"{prefix}/recrawl/quota")                        # оставшаяся квота
queue = wm_get(f"{prefix}/recrawl/queue")                        # очередь
wm_post(f"{prefix}/recrawl/queue", {"url": "https://..."})       # отправить на переобход
```

### Внешние ссылки

```python
links = wm_get(f"{prefix}/links/external/samples?limit=100&offset=0")
history = wm_get(f"{prefix}/links/external/history?date_from=...&date_to=...")
```

### Битые внутренние ссылки

```python
broken = wm_get(f"{prefix}/links/internal/broken/samples?limit=100&offset=0")
```

### Мониторинг важных страниц

```python
important = wm_get(f"{prefix}/important-urls")
```
