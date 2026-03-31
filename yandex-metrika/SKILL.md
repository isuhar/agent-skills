---
name: yandex-metrika
description: Query Yandex Metrika data via REST API. Use for site traffic, ad campaign analysis (Yandex.Direct), traffic sources, bounce rates, visit duration, UTM breakdown, and ad search queries.
---

# Яндекс Метрика — REST API

Данные по посетителям сайта: трафик, рекламные кампании (Яндекс.Директ), источники, поведение.

## Переменные окружения

- `YANDEX_METRIKA_TOKEN` — base64-encoded JSON с полями `access_token`, `refresh_token`, `expires_in`, `token_type`
- `YANDEX_METRIKA_COUNTER_ID` — ID счётчика
- `YANDEX_CLIENT_ID` — Client ID приложения Яндекс OAuth
- `YANDEX_CLIENT_SECRET` — Client Secret приложения Яндекс OAuth

## Авторизация

Используй `ym_auth.py` (в этой же папке) — парсит base64 JSON, проверяет срок действия и автоматически рефрешит токен:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../yandex-metrika"))
from ym_auth import get_token
token = get_token()
```

## Как делать запросы

REST API через `urllib` (без внешних зависимостей):

```python
import urllib.request, json, os, base64

def get_ym_token():
    raw = os.environ.get('YANDEX_METRIKA_TOKEN', '')
    try:
        data = json.loads(base64.b64decode(raw + '=='))
        return data.get('access_token', raw)
    except Exception:
        return raw

token = get_ym_token()
counter = os.environ.get('YANDEX_METRIKA_COUNTER_ID')

url = f'https://api-metrika.yandex.net/stat/v1/data?ids={counter}&date1=2026-02-01&date2=2026-02-14&metrics=ym:s:visits,ym:s:users&dimensions=ym:s:lastTrafficSource&limit=20&sort=-ym:s:visits'
req = urllib.request.Request(url, headers={'Authorization': f'OAuth {token}'})
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
```

## Типичные запросы

### Общий трафик за период
```
metrics=ym:s:visits,ym:s:users
```

### Источники трафика
```
dimensions=ym:s:lastTrafficSource
```
Возвращает: Ad traffic, Direct traffic, Search engine traffic, Social network traffic, Referral, Messenger и др.

### По UTM Source
```
dimensions=ym:s:UTMSource
```

### Рекламные кампании (CPC)
```
dimensions=ym:s:UTMCampaign
filters=ym:s:UTMMedium=='cpc'
```

### Рекламные поисковые запросы
```
dimensions=ym:s:lastDirectSearchPhrase
filters=ym:s:lastDirectSearchPhrase!~'null'
```

### SEO трафик по страницам
```
dimensions=ym:s:startURL
filters=ym:s:lastTrafficSource=='Search engine traffic'
```

### Параметры визитов (custom params)
```
dimensions=ym:s:paramsLevel1
dimensions=ym:s:paramsLevel1,ym:s:paramsLevel2
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
| `ym:s:lastDirectSearchPhrase` | Поисковый запрос из Яндекс.Директ |
| `ym:s:gender` | Пол |
| `ym:s:ageInterval` | Возрастная группа |
| `ym:s:deviceCategory` | Устройство |
| `ym:s:operatingSystem` | ОС |
| `ym:s:regionCity` | Город |
| `ym:s:paramsLevel1` | Параметры визитов (уровень 1) |
| `ym:s:paramsLevel2` | Параметры визитов (уровень 2) |

## Фильтры

```
filters=ym:s:UTMMedium=='cpc'
filters=ym:s:lastTrafficSource=='Ad traffic'
filters=ym:s:UTMSource=='yandex'
```

## Сортировка и лимит

```
sort=-ym:s:visits       # по убыванию
limit=20                # строк (макс 100000)
```
