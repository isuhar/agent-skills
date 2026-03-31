---
name: yandex-oauth
description: Yandex OAuth token management — obtain, refresh, and validate tokens for Yandex APIs (Metrika, Direct, Webmaster). Use when tokens expire or need initial setup.
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

## Переменные окружения

| Переменная | Описание |
|---|---|
| `YANDEX_CLIENT_ID` | Client ID OAuth-приложения |
| `YANDEX_CLIENT_SECRET` | Client Secret OAuth-приложения |
| `YANDEX_OAUTH_TOKEN` | Текущий access_token (опционально, если уже получен) |
| `YANDEX_REFRESH_TOKEN` | Refresh token для обновления access_token |

## Как это работает

1. **Первичное получение** — пользователь открывает URL в браузере, разрешает доступ, получает код
2. **Обмен кода на токен** — POST-запрос с кодом → access_token + refresh_token
3. **Использование** — access_token в заголовке `Authorization: OAuth <token>`
4. **Обновление** — когда access_token истёк, POST с refresh_token → новый access_token

## Шаг 1: Получение кода авторизации

Пользователь открывает в браузере:

```
https://oauth.yandex.ru/authorize?response_type=code&client_id=<YANDEX_CLIENT_ID>
```

После разрешения Яндекс редиректит на callback URL с параметром `code=<код>`.

Для ручного получения (redirect_uri = `https://oauth.yandex.ru/verification_code`):
```
https://oauth.yandex.ru/authorize?response_type=token&client_id=<YANDEX_CLIENT_ID>
```
Токен будет показан прямо на странице.

## Шаг 2: Обмен кода на токен

```python
import urllib.request, urllib.parse, json, os

def exchange_code(code: str) -> dict:
    """Обменять authorization code на access_token + refresh_token."""
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "client_id": os.environ["YANDEX_CLIENT_ID"],
        "client_secret": os.environ["YANDEX_CLIENT_SECRET"],
    }).encode()
    req = urllib.request.Request("https://oauth.yandex.ru/token", data=data, method="POST")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())
    # Ответ: {"access_token": "...", "refresh_token": "...", "expires_in": 31536000, "token_type": "bearer"}
```

## Шаг 3: Обновление токена

```python
def refresh_token(refresh_token: str) -> dict:
    """Обновить access_token через refresh_token."""
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": os.environ["YANDEX_CLIENT_ID"],
        "client_secret": os.environ["YANDEX_CLIENT_SECRET"],
    }).encode()
    req = urllib.request.Request("https://oauth.yandex.ru/token", data=data, method="POST")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())
    # Ответ: {"access_token": "новый_токен", "refresh_token": "новый_refresh", "expires_in": ...}
```

## Обёртка с авто-обновлением

```python
import urllib.request, urllib.parse, json, os

class YandexAuth:
    def __init__(self):
        self.access_token = os.environ.get("YANDEX_OAUTH_TOKEN", "")
        self.refresh_tok = os.environ.get("YANDEX_REFRESH_TOKEN", "")
        self.client_id = os.environ.get("YANDEX_CLIENT_ID", "")
        self.client_secret = os.environ.get("YANDEX_CLIENT_SECRET", "")

    def get_token(self) -> str:
        """Вернуть access_token, обновив если нужно."""
        return self.access_token

    def do_refresh(self) -> str:
        """Обновить токен через refresh_token."""
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_tok,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }).encode()
        req = urllib.request.Request("https://oauth.yandex.ru/token", data=data, method="POST")
        result = json.loads(urllib.request.urlopen(req).read())
        self.access_token = result["access_token"]
        self.refresh_tok = result.get("refresh_token", self.refresh_tok)
        return self.access_token

    def request(self, url: str, data=None, method="GET", headers=None) -> dict:
        """HTTP-запрос с авто-обновлением токена при 401."""
        hdrs = {"Authorization": f"OAuth {self.access_token}"}
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            resp = urllib.request.urlopen(req)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 401 and self.refresh_tok:
                self.do_refresh()
                hdrs["Authorization"] = f"OAuth {self.access_token}"
                req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
                resp = urllib.request.urlopen(req)
                return json.loads(resp.read())
            raise
```

## Использование в других скиллах

```python
auth = YandexAuth()

# Метрика
data = auth.request(f"https://api-metrika.yandex.net/stat/v1/data?ids={counter}&metrics=ym:s:visits")

# Вебмастер
data = auth.request("https://api.webmaster.yandex.net/v4/user")

# Директ (использует Bearer вместо OAuth)
# Для Директа заменить заголовок на Authorization: Bearer
```

## Время жизни токенов

- **access_token**: обычно 1 год (зависит от приложения), `expires_in` в ответе
- **refresh_token**: бессрочный (пока не отозван)
- При refresh оба токена обновляются — **сохраняйте новый refresh_token**

## Необходимые скоупы

| API | Скоуп |
|---|---|
| Метрика | `metrika:read` (чтение), `metrika:write` (запись) |
| Директ | Доступ настраивается при регистрации приложения |
| Вебмастер | `webmaster:verify` |

## Регистрация приложения

1. Перейти на https://oauth.yandex.ru/client/new
2. Указать название, выбрать нужные скоупы
3. Redirect URI: `https://oauth.yandex.ru/verification_code` (для ручного получения)
4. Сохранить Client ID и Client Secret
