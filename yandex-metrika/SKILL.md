---
name: yandex-metrika
description: Query Yandex Metrika data via REST API. Use for site traffic, ad campaign analysis, traffic sources, bounce rates, visit duration, UTM breakdown, and ad search queries.
metadata:
  clawdbot:
    emoji: "📊"
    requires:
      env: ["YANDEX_METRIKA_TOKEN", "YANDEX_METRIKA_COUNTER_ID"]
      primaryEnv: "YANDEX_METRIKA_TOKEN"
      bins: ["python3"]
---

# Яндекс Метрика — REST API

Данные по посетителям сайта: трафик, источники, поведение, рекламные кампании.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `YANDEX_METRIKA_TOKEN` | OAuth-токен для Яндекс API |
| `YANDEX_METRIKA_COUNTER_ID` | ID счётчика |

## Авторизация и запросы

```python
import urllib.request, json, os

TOKEN = os.environ["YANDEX_METRIKA_TOKEN"]
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
