---
name: yandex-metrika
description: Query Yandex Metrika data via REST API. Use for site traffic, ad campaign analysis, traffic sources, bounce rates, visit duration, UTM breakdown, and ad search queries.
metadata:
  clawdbot:
    emoji: "📊"
    requires:
      env: ["YANDEX_CLIENT_ID", "YANDEX_CLIENT_SECRET", "YANDEX_METRIKA_COUNTER_ID"]
      primaryEnv: "YANDEX_CLIENT_ID"
      bins: ["python3"]
---

# Яндекс Метрика — REST API

Данные по посетителям сайта: трафик, источники, поведение, рекламные кампании.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `YANDEX_CLIENT_ID` | Client ID OAuth-приложения |
| `YANDEX_CLIENT_SECRET` | Client Secret OAuth-приложения |
| `YANDEX_TOKEN_FILE` | Путь к файлу с токенами (по умолчанию `~/.yandex_tokens.json`) |
| `YANDEX_METRIKA_COUNTER_ID` | ID счётчика |

Настройка токенов — см. скилл **yandex-oauth**.

## Авторизация и запросы

Авторизация через файл токенов с авто-обновлением (см. `get_yandex_token()` в скилле **yandex-oauth**).

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
COUNTER = os.environ["YANDEX_METRIKA_COUNTER_ID"]

def ym_get(params: str) -> dict:
    """Запрос к Stat API Яндекс Метрики."""
    url = f"https://api-metrika.yandex.net/stat/v1/data?ids={COUNTER}&{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {TOKEN}"})
    return json.loads(urllib.request.urlopen(req).read())
```

## Типичные запросы

### Общий трафик за период

```python
data = ym_get("date1=2026-03-01&date2=2026-03-31&metrics=ym:s:visits,ym:s:users")
```

### Источники трафика

```python
data = ym_get("date1=2026-03-01&date2=2026-03-31&metrics=ym:s:visits,ym:s:users&dimensions=ym:s:lastTrafficSource&sort=-ym:s:visits&limit=20")
```

### По UTM Source / Medium / Campaign

```python
# UTM source
data = ym_get("date1=...&date2=...&metrics=ym:s:visits&dimensions=ym:s:UTMSource")

# Рекламные кампании (CPC)
data = ym_get("date1=...&date2=...&metrics=ym:s:visits,ym:s:users&dimensions=ym:s:UTMCampaign&filters=ym:s:UTMMedium=='cpc'")
```

### Поисковые запросы из Яндекс.Директ

```python
data = ym_get("date1=...&date2=...&metrics=ym:s:visits&dimensions=ym:s:lastDirectSearchPhrase&filters=ym:s:lastDirectSearchPhrase!~'null'&sort=-ym:s:visits&limit=50")
```

### SEO трафик по страницам

```python
data = ym_get("date1=...&date2=...&metrics=ym:s:visits,ym:s:users&dimensions=ym:s:startURL&filters=ym:s:lastTrafficSource=='Search engine traffic'&sort=-ym:s:visits&limit=30")
```

## Основные метрики

| Метрика | Описание |
|---|---|
| `ym:s:visits` | Визиты |
| `ym:s:users` | Уникальные посетители |
| `ym:s:bounceRate` | Отказы (%) |
| `ym:s:avgVisitDurationSeconds` | Средняя длительность визита (сек) |
| `ym:s:pageDepth` | Глубина просмотра |

## Основные dimensions

| Dimension | Описание |
|---|---|
| `ym:s:lastTrafficSource` | Тип источника (Ad, Direct, Search, Social...) |
| `ym:s:UTMSource` | UTM source |
| `ym:s:UTMMedium` | UTM medium (cpc, organic...) |
| `ym:s:UTMCampaign` | UTM campaign |
| `ym:s:lastDirectSearchPhrase` | Поисковый запрос из Директа |
| `ym:s:gender` | Пол |
| `ym:s:ageInterval` | Возрастная группа |
| `ym:s:deviceCategory` | Устройство |
| `ym:s:operatingSystem` | ОС |
| `ym:s:regionCity` | Город |
| `ym:s:startURL` | Страница входа |
| `ym:s:paramsLevel1` | Параметры визитов (уровень 1) |

## Фильтры

```
filters=ym:s:UTMMedium=='cpc'
filters=ym:s:lastTrafficSource=='Ad traffic'
filters=ym:s:UTMSource=='yandex'
```

Операторы: `==`, `!=`, `=~` (содержит), `!~` (не содержит), `=*` (regex), `>`, `<`.

## Сортировка и лимит

```
sort=-ym:s:visits       # по убыванию (минус = DESC)
limit=20                # строк (макс 100000)
offset=1                # с какой строки (начинается с 1)
```
