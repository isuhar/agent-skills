---
name: yandex-metrika
description: Query Yandex Metrika data via REST API. Use for site traffic, ad campaign analysis, traffic sources, bounce rates, visit duration, UTM breakdown, ad search queries, goals/conversions, e-commerce, and time-series data.
metadata:
  clawdbot:
    emoji: "📊"
    requires:
      env: ["YANDEX_CLIENT_ID", "YANDEX_CLIENT_SECRET", "YANDEX_METRIKA_COUNTER_ID"]
      primaryEnv: "YANDEX_CLIENT_ID"
      bins: ["python3"]
---

# Яндекс Метрика — REST API

Данные по посетителям сайта: трафик, источники, поведение, конверсии, рекламные кампании, e-commerce.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `YANDEX_CLIENT_ID` | Client ID OAuth-приложения |
| `YANDEX_CLIENT_SECRET` | Client Secret OAuth-приложения |
| `YANDEX_TOKEN_FILE` | Путь к файлу с токенами (по умолчанию `~/.yandex_tokens.json`) |
| `YANDEX_METRIKA_COUNTER_ID` | ID счётчика |

**Требуется:** файл токенов `~/.yandex_tokens.json` (создаётся один раз при первоначальной настройке — см. скилл **yandex-oauth**). Если файл отсутствует, скрипт выдаст ошибку с инструкцией.

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
    """Запрос к Stat API Яндекс Метрики (таблица)."""
    url = f"https://api-metrika.yandex.net/stat/v1/data?ids={COUNTER}&{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {TOKEN}"})
    return json.loads(urllib.request.urlopen(req).read())

def ym_bytime(params: str) -> dict:
    """Запрос с разбивкой по времени (для графиков и динамики)."""
    url = f"https://api-metrika.yandex.net/stat/v1/data/bytime?ids={COUNTER}&{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {TOKEN}"})
    return json.loads(urllib.request.urlopen(req).read())

def ym_comparison(params: str) -> dict:
    """Сравнение двух сегментов."""
    url = f"https://api-metrika.yandex.net/stat/v1/data/comparison?ids={COUNTER}&{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {TOKEN}"})
    return json.loads(urllib.request.urlopen(req).read())
```

## Виды отчётов (endpoints)

| Endpoint | Описание |
|---|---|
| `/stat/v1/data` | Таблица (основной) |
| `/stat/v1/data/bytime` | По времени (графики, динамика) |
| `/stat/v1/data/comparison` | Сравнение сегментов |
| `/stat/v1/data/drilldown` | Drill-down (вложенные уровни) |

Формат: JSON (по умолчанию) или CSV (добавить `.csv` к URL).

## Типичные запросы

### Общий трафик за период

```python
data = ym_get("date1=2026-03-01&date2=2026-03-31&metrics=ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:avgVisitDurationSeconds,ym:s:pageDepth")
```

### Динамика визитов по дням (для графика)

```python
data = ym_bytime("date1=2026-03-01&date2=2026-03-31&metrics=ym:s:visits,ym:s:users&group=day")
# group: day, week, month, hour, minute (default: day)
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

### Конверсии (цели)

```python
# Количество достижений цели (нужно знать ID цели)
data = ym_get("date1=...&date2=...&metrics=ym:s:goal<GOAL_ID>reaches,ym:s:goal<GOAL_ID>conversionRate&dimensions=ym:s:lastTrafficSource")

# Все цели разом
data = ym_get("date1=...&date2=...&metrics=ym:s:goalReaches,ym:s:goalConversionRate")
```

### Поисковые фразы (SEO)

```python
data = ym_get("date1=...&date2=...&metrics=ym:s:visits&dimensions=ym:s:lastSearchPhrase&filters=ym:s:lastSearchPhrase!~'null'&sort=-ym:s:visits&limit=50")
```

### География

```python
data = ym_get("date1=...&date2=...&metrics=ym:s:visits,ym:s:users&dimensions=ym:s:regionCountry,ym:s:regionCity&sort=-ym:s:visits&limit=30")
```

### Устройства и браузеры

```python
data = ym_get("date1=...&date2=...&metrics=ym:s:visits&dimensions=ym:s:deviceCategory")
data = ym_get("date1=...&date2=...&metrics=ym:s:visits&dimensions=ym:s:browser")
```

### Топ страниц (хиты)

```python
# Используем префикс ym:pv: для метрик хитов
url = f"https://api-metrika.yandex.net/stat/v1/data?ids={COUNTER}&date1=...&date2=...&metrics=ym:pv:pageviews,ym:pv:users&dimensions=ym:pv:URLPath&sort=-ym:pv:pageviews&limit=30"
```

### Сравнение двух периодов

```python
data = ym_comparison("date1_a=2026-02-01&date2_a=2026-02-28&date1_b=2026-03-01&date2_b=2026-03-31&metrics=ym:s:visits,ym:s:users&dimensions=ym:s:lastTrafficSource")
```

### Директ-расходы

```python
data = ym_get("date1=...&date2=...&metrics=ym:s:visits,ym:s:<currency>DirectExpenses&dimensions=ym:s:UTMCampaign&direct_client_logins=LOGIN")
```

## Основные метрики (визиты, ym:s:)

| Метрика | Описание |
|---|---|
| `ym:s:visits` | Визиты |
| `ym:s:users` | Уникальные посетители |
| `ym:s:bounceRate` | Отказы (%) |
| `ym:s:avgVisitDurationSeconds` | Средняя длительность визита (сек) |
| `ym:s:pageDepth` | Глубина просмотра |
| `ym:s:goalReaches` | Достижения целей (все) |
| `ym:s:goalConversionRate` | Конверсия (все цели, %) |
| `ym:s:goal<ID>reaches` | Достижения конкретной цели |
| `ym:s:goal<ID>conversionRate` | Конверсия конкретной цели (%) |
| `ym:s:newUsers` | Новые посетители |
| `ym:s:newUsersShare` | Доля новых посетителей (%) |
| `ym:s:percentNewVisitors` | % новых визитов |

## Метрики хитов (ym:pv:)

| Метрика | Описание |
|---|---|
| `ym:pv:pageviews` | Просмотры страниц |
| `ym:pv:users` | Уникальные посетители |

⚠️ Нельзя смешивать `ym:s:` и `ym:pv:` метрики/dimensions в одном запросе (кроме фильтров).

## Основные dimensions (визиты)

| Dimension | Описание |
|---|---|
| `ym:s:lastTrafficSource` | Тип источника (Ad, Direct, Search, Social...) |
| `ym:s:UTMSource` | UTM source |
| `ym:s:UTMMedium` | UTM medium (cpc, organic...) |
| `ym:s:UTMCampaign` | UTM campaign |
| `ym:s:UTMContent` | UTM content |
| `ym:s:UTMTerm` | UTM term |
| `ym:s:lastDirectSearchPhrase` | Поисковый запрос из Директа |
| `ym:s:lastSearchPhrase` | Поисковый запрос (SEO) |
| `ym:s:lastSearchEngineRoot` | Поисковая система |
| `ym:s:lastReferalSource` | Реферальный источник |
| `ym:s:lastSocialNetwork` | Социальная сеть |
| `ym:s:gender` | Пол |
| `ym:s:ageInterval` | Возрастная группа |
| `ym:s:deviceCategory` | Устройство (desktop, mobile, tablet) |
| `ym:s:operatingSystem` | ОС |
| `ym:s:browser` | Браузер |
| `ym:s:regionCountry` | Страна |
| `ym:s:regionCity` | Город |
| `ym:s:startURL` | Страница входа |
| `ym:s:exitPage` | Страница выхода |
| `ym:s:paramsLevel1` | Параметры визитов (уровень 1) |
| `ym:s:paramsLevel2` | Параметры визитов (уровень 2) |
| `ym:s:date` | Дата |
| `ym:s:datePeriodday` | День |
| `ym:s:datePeriodweek` | Неделя |
| `ym:s:datePeriodmonth` | Месяц |
| `ym:s:goal` | Цель |

## Dimensions хитов (ym:pv:)

| Dimension | Описание |
|---|---|
| `ym:pv:URLPath` | Путь страницы |
| `ym:pv:title` | Заголовок страницы |
| `ym:pv:URLDomain` | Домен |

## Фильтры

```
filters=ym:s:UTMMedium=='cpc'
filters=ym:s:lastTrafficSource=='Ad traffic'
filters=ym:s:UTMSource=='yandex'
filters=ym:s:startURL=@'/blog/'
```

Операторы: `==` (равно), `!=` (не равно), `=~` (содержит подстроку), `!~` (не содержит), `=@` (содержит), `=*` (regex), `>`, `<`.

Логические: `AND`, `OR` (AND приоритетнее).

Можно миксовать префиксы в фильтрах: `filters=ym:s:trafficSourceName=='...' AND ym:pv:URL=@'help'`.

## Параметры запроса

| Параметр | Описание | По умолчанию |
|---|---|---|
| `date1` | Начало периода (YYYY-MM-DD, today, yesterday, NdaysAgo) | 6daysAgo |
| `date2` | Конец периода | today |
| `metrics` | Метрики через запятую (макс 20) | — |
| `dimensions` | Группировки через запятую (макс 10) | — |
| `filters` | Фильтры сегментации | — |
| `sort` | Сортировка (минус = DESC) | — |
| `limit` | Кол-во строк (макс 100000) | 100 |
| `offset` | Начиная с (от 1) | 1 |
| `accuracy` | Семплирование (1 = точно, low/medium/high) | — |
| `group` | Группировка по времени (bytime): day, week, month, hour, minute | day |
| `include_undefined` | Включить строки с неопределёнными значениями | false |
| `lang` | Язык ответа (ru, en, ...) | — |
| `timezone` | Часовой пояс (±hh:mm) | по счётчику |
| `preset` | Шаблон отчёта (sources_summary, tech_browsers...) | — |

## Шаблоны отчётов (preset)

Вместо ручного указания metrics/dimensions:

```python
data = ym_get("date1=...&date2=...&preset=sources_summary")
```

Доступные: `sources_summary`, `sources_search_engines`, `sources_social_networks`, `sources_direct_clicks`, `tech_browsers`, `tech_os`, `tech_devices`, `geo_country`, и другие.

## Структура ответа

```json
{
  "query": { "date1": "...", "date2": "...", "metrics": [...], "dimensions": [...] },
  "data": [
    {
      "dimensions": [{"name": "...", "id": "..."}],
      "metrics": [1234.0, 56.7]
    }
  ],
  "total_rows": 100,
  "totals": [5000.0, 3000.0],
  "min": [1.0, 0.0],
  "max": [500.0, 100.0],
  "sampled": false,
  "sample_share": 1.0
}
```

## Лимиты API

- Метрик в запросе: до 20
- Группировок: до 10
- Строк в ответе: до 100 000
- Фильтров: до 20, длина строки до 10 000 символов
- Запросов: рекомендуется не более 5 в секунду
