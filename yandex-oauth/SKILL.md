---
name: yandex-oauth
description: Yandex OAuth token management — obtain, refresh, and persist tokens for Yandex APIs (Metrika, Direct, Webmaster). Use when tokens expire or need initial setup.
metadata:
  clawdbot:
    emoji: "🔑"
    requires:
      env: ["YANDEX_CLIENT_ID", "YANDEX_CLIENT_SECRET"]
      primaryEnv: "YANDEX_CLIENT_ID"
      bins: ["python3"]
---

# Яндекс OAuth — управление токенами

Общая авторизация для всех Яндекс API (Метрика, Директ, Вебмастер).

## Важно: refresh_token не бессрочный

В отличие от Google, Яндекс OAuth **возвращает новый refresh_token** при каждом обновлении. Время жизни refresh_token совпадает с access_token. Если не сохранить новый refresh_token — авторизация сломается.

Поэтому токены хранятся в **файле** (не в env var).

## Переменные окружения

| Переменная | Описание |
|---|---|
| `YANDEX_CLIENT_ID` | Client ID OAuth-приложения |
| `YANDEX_CLIENT_SECRET` | Client Secret OAuth-приложения |
| `YANDEX_TOKEN_FILE` | Путь к файлу с токенами (по умолчанию `~/.yandex_tokens.json`) |

## Формат файла токенов

```json
{
  "access_token": "AQAAAACy1C6Z...",
  "refresh_token": "1:GN686Q:uf1KBsi...",
  "expires_in": 31536000,
  "issued_at": 1711843200
}
```

## Модуль авторизации

Все Яндекс-скиллы используют эту функцию:

```python
import urllib.request, urllib.parse, json, os, time

TOKEN_FILE = os.environ.get("YANDEX_TOKEN_FILE", os.path.expanduser("~/.yandex_tokens.json"))

def get_yandex_token() -> str:
    """Получить access_token, обновив при необходимости. Сохраняет новый refresh_token в файл."""

    # 1. Прочитать текущие токены из файла
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            f"Token file not found: {TOKEN_FILE}\n"
            "Run initial setup first (see yandex-oauth skill)."
        )
    with open(TOKEN_FILE) as f:
        tokens = json.load(f)

    # 2. Проверить не истёк ли access_token (с запасом 1 час)
    issued_at = tokens.get("issued_at", 0)
    expires_in = tokens.get("expires_in", 0)
    if time.time() < issued_at + expires_in - 3600:
        return tokens["access_token"]

    # 3. Обновить через refresh_token
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": os.environ["YANDEX_CLIENT_ID"],
        "client_secret": os.environ["YANDEX_CLIENT_SECRET"],
    }).encode()
    req = urllib.request.Request("https://oauth.yandex.ru/token", data=data, method="POST")
    result = json.loads(urllib.request.urlopen(req).read())

    # 4. Сохранить новые токены в файл
    tokens["access_token"] = result["access_token"]
    tokens["refresh_token"] = result["refresh_token"]
    tokens["expires_in"] = result.get("expires_in", 31536000)
    tokens["issued_at"] = int(time.time())
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    return tokens["access_token"]
```

## Первоначальная настройка

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

### Шаг 3: Обмен кода на токены и сохранение

```python
import urllib.request, urllib.parse, json, time

CLIENT_ID = "<CLIENT_ID>"
CLIENT_SECRET = "<CLIENT_SECRET>"
CODE = "<КОД_ИЗ_ШАГА_2>"

data = urllib.parse.urlencode({
    "grant_type": "authorization_code",
    "code": CODE,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}).encode()
req = urllib.request.Request("https://oauth.yandex.ru/token", data=data, method="POST")
result = json.loads(urllib.request.urlopen(req).read())

# Сохранить в файл
tokens = {
    "access_token": result["access_token"],
    "refresh_token": result["refresh_token"],
    "expires_in": result.get("expires_in", 31536000),
    "issued_at": int(time.time()),
}
with open(os.path.expanduser("~/.yandex_tokens.json"), "w") as f:
    json.dump(tokens, f, indent=2)

print("Токены сохранены в ~/.yandex_tokens.json")
```

## Необходимые скоупы

| API | Скоуп |
|---|---|
| Метрика | `metrika:read` (чтение), `metrika:write` (запись) |
| Директ | Доступ настраивается при регистрации приложения |
| Вебмастер | `webmaster:verify` |

## Рекомендации

- Яндекс рекомендует обновлять долгоживущие токены **раз в 3 месяца**
- При обновлении access_token может не измениться, если срок ещё длительный
- `~/.yandex_tokens.json` не должен попадать в git — добавить в `.gitignore`
