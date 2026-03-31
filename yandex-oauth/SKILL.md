---
name: yandex-oauth
description: Yandex OAuth token management — obtain, refresh, and validate tokens for Yandex APIs (Metrika, Direct, Webmaster). Use when tokens expire or need initial setup.
metadata:
  clawdbot:
    emoji: "🔑"
    requires:
      env: ["YANDEX_CLIENT_ID", "YANDEX_CLIENT_SECRET", "YANDEX_REFRESH_TOKEN"]
      primaryEnv: "YANDEX_REFRESH_TOKEN"
      bins: ["python3"]
---

# Яндекс OAuth — управление токенами

Общая авторизация для всех Яндекс API (Метрика, Директ, Вебмастер).

## Принцип работы

В env var хранится **только refresh_token** (бессрочный). access_token получается программно при каждом запуске — аналогично Google Service Account подходу.

## Переменные окружения

| Переменная | Описание |
|---|---|
| `YANDEX_CLIENT_ID` | Client ID OAuth-приложения |
| `YANDEX_CLIENT_SECRET` | Client Secret OAuth-приложения |
| `YANDEX_REFRESH_TOKEN` | Refresh token (бессрочный, хранится в env var) |

Env var не нужно обновлять — refresh_token живёт пока не отозван вручную.

## Получение access_token

```python
import urllib.request, urllib.parse, json, os

def get_yandex_token() -> str:
    """Получить access_token через refresh_token. Вызывать при старте."""
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": os.environ["YANDEX_REFRESH_TOKEN"],
        "client_id": os.environ["YANDEX_CLIENT_ID"],
        "client_secret": os.environ["YANDEX_CLIENT_SECRET"],
    }).encode()
    req = urllib.request.Request("https://oauth.yandex.ru/token", data=data, method="POST")
    result = json.loads(urllib.request.urlopen(req).read())
    return result["access_token"]

TOKEN = get_yandex_token()
```

## Первоначальная настройка (получение refresh_token)

Выполняется **один раз** при подключении Яндекс-аккаунта.

### Шаг 1: Регистрация приложения

1. Перейти на https://oauth.yandex.ru/client/new
2. Указать название, выбрать скоупы:
   - Метрика: `metrika:read`
   - Директ: настраивается при регистрации
   - Вебмастер: `webmaster:verify`
3. Redirect URI: `https://oauth.yandex.ru/verification_code`
4. Сохранить Client ID и Client Secret

### Шаг 2: Получение authorization code

Открыть в браузере:
```
https://oauth.yandex.ru/authorize?response_type=code&client_id=<CLIENT_ID>
```

Разрешить доступ → скопировать код из URL.

### Шаг 3: Обмен кода на токены

```python
import urllib.request, urllib.parse, json

data = urllib.parse.urlencode({
    "grant_type": "authorization_code",
    "code": "<КОД_ИЗ_ШАГА_2>",
    "client_id": "<CLIENT_ID>",
    "client_secret": "<CLIENT_SECRET>",
}).encode()
req = urllib.request.Request("https://oauth.yandex.ru/token", data=data, method="POST")
result = json.loads(urllib.request.urlopen(req).read())

print(f"refresh_token: {result['refresh_token']}")  # ← сохранить в YANDEX_REFRESH_TOKEN
print(f"access_token: {result['access_token']}")
print(f"expires_in: {result['expires_in']} сек")
```

Сохранить `refresh_token` в переменную окружения `YANDEX_REFRESH_TOKEN`.

## Использование в скиллах

Все Яндекс-скиллы (metrika, direct, webmaster) используют `get_yandex_token()`:

```python
TOKEN = get_yandex_token()

# Метрика (OAuth)
req = urllib.request.Request(url, headers={"Authorization": f"OAuth {TOKEN}"})

# Директ (Bearer)
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
```

## Время жизни токенов

| Токен | Время жизни |
|---|---|
| `access_token` | ~1 год (зависит от приложения), `expires_in` в ответе |
| `refresh_token` | Бессрочный (пока не отозван вручную) |

## Отзыв токена

```
POST https://oauth.yandex.ru/revoke_token
Content-Type: application/x-www-form-urlencoded

access_token=<TOKEN>&client_id=<CLIENT_ID>&client_secret=<CLIENT_SECRET>
```
