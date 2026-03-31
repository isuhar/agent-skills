---
name: yandex-wordstat
description: >
  Query Yandex Wordstat API for keyword research — frequency, dynamics, regional distribution.
  Use for SEO keyword planning, demand analysis, seasonality trends, and competitive research.
---

# Яндекс Вордстат API

Анализ поисковых запросов: частотность, динамика, география.

## Авторизация

Используй OAuth-токен Яндекса (тот же что для Директа/Метрики).

```
Authorization: Bearer <token>
```

Получение токена — см. скилл `yandex-oauth`.

Если задана переменная `YANDEX_TOKEN_FILE` — читай `access_token` из JSON-файла. Если токен истёк — обнови через refresh (см. `yandex-oauth`).

## Базовый URL

```
https://api.wordstat.yandex.net/v1/
```

Все запросы — POST, Content-Type: application/json.

## Квоты

- 10 запросов/сек
- 1000 запросов/сутки
- Проверить остаток: `POST /v1/userInfo`

## Общий шаблон запроса

```python
import urllib.request, json, os

def wordstat_request(endpoint, body, token=None):
    """Запрос к Wordstat API."""
    if not token:
        token_file = os.environ.get("YANDEX_TOKEN_FILE")
        if token_file:
            with open(token_file) as f:
                token = json.load(f)["access_token"]
    
    url = f"https://api.wordstat.yandex.net/v1/{endpoint}"
    req = urllib.request.Request(url,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())
```

## Методы

### topRequests — частотность фраз

Основной метод. Показывает частотность фразы и связанные запросы.

```python
def wordstat_top(phrase, token=None, regions=None, devices=None, num=50):
    """Получить частотность фразы и связанные запросы.
    
    Args:
        phrase: ключевая фраза (или phrases — массив до 128)
        regions: список ID регионов (225=Россия, 213=Москва, 2=Питер)
        devices: фильтр устройств
        num: кол-во результатов (до 500)
    """
    body = {"phrase": phrase, "numPhrases": num}
    if regions: body["regions"] = regions
    if devices: body["devices"] = devices
    return wordstat_request("topRequests", body, token)
```

**Ответ:**
```json
{
  "totalCount": 12345,
  "topRequests": [{"phrase": "заметки онлайн", "count": 5000}, ...],
  "associations": [{"phrase": "приложение для заметок", "count": 3000}, ...]
}
```

- `totalCount` — общая частотность фразы
- `topRequests` — вложенные запросы (уточнения)
- `associations` — ассоциированные запросы (похожие)

**Батч-запрос:** передать `phrases` (массив до 128 фраз) вместо `phrase`.

### dynamics — динамика запросов

Показывает как менялась частотность во времени.

```python
def wordstat_dynamics(phrase, token=None, period="weekly", from_date="2025-01-06", to_date=None):
    """Динамика частотности фразы.
    
    Args:
        period: "daily" (макс 60 дней), "weekly", "monthly" (с 2018-01-01)
        from_date: начало периода (для monthly — 1-е число, для weekly — понедельник)
    """
    body = {"phrase": phrase, "period": period, "fromDate": from_date}
    if to_date: body["toDate"] = to_date
    return wordstat_request("dynamics", body, token)
```

**Ответ:**
```json
{
  "periods": [
    {"date": "2026-03-01", "count": 4500},
    {"date": "2026-03-08", "count": 5200},
    ...
  ]
}
```

### regions — география запросов

Распределение запросов по регионам.

```python
def wordstat_regions(phrase, token=None, region_type="all"):
    """География запросов.
    
    Args:
        region_type: "cities", "regions", "all"
    """
    body = {"phrase": phrase, "regionType": region_type}
    return wordstat_request("regions", body, token)
```

**Ответ:**
```json
[
  {"regionId": 213, "count": 15000, "share": 0.25, "affinityIndex": 1.8},
  ...
]
```

- `share` — доля от общего числа запросов
- `affinityIndex` — индекс аффинитивности (>1 = запрос популярнее среднего в регионе)

### getRegionsTree — справочник регионов

```python
regions_tree = wordstat_request("getRegionsTree", {})
```

Не расходует квоту. Возвращает дерево регионов с ID.

### userInfo — проверка квоты

```python
info = wordstat_request("userInfo", {})
# {"login": "...", "limitPerSecond": 10, "dailyLimit": 1000, "dailyLimitRemaining": 950}
```

## Популярные ID регионов

| ID | Регион |
|---|---|
| 225 | Россия |
| 213 | Москва |
| 2 | Санкт-Петербург |
| 1 | Москва и область |
| 10174 | Екатеринбург |
| 43 | Казань |
| 54 | Новосибирск |

## Операторы запросов

| Оператор | Пример | Значение |
|---|---|---|
| без оператора | `заметки онлайн` | Все формы слов, любой порядок |
| `"..."` | `"заметки онлайн"` | Точная фраза (любые формы слов) |
| `!` | `!заметки !онлайн` | Точная форма слова |
| `+` | `+для заметок` | Учитывать предлог/союз |
| `-` | `заметки -бесплатно` | Минус-слово |

## Советы

- Начинай с широких фраз → смотри `associations` для расширения семантики
- Используй `regions` для оценки спроса в целевых регионах
- `dynamics` с `period=monthly` — для оценки сезонности
- Батч-режим (`phrases`) экономит квоту — до 128 фраз за запрос
- `affinityIndex` > 1.5 в регионе = точка роста для геотаргетинга
