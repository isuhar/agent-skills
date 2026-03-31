---
name: ghost
description: Manage Ghost CMS blogs — create, update, publish posts, upload images, manage tags. Works with any Ghost instance via Admin API.
---

# Ghost CMS — Admin API

Универсальный скилл для работы с Ghost CMS: создание и обновление постов, загрузка изображений, управление тегами.

## Переменные окружения

Имена переменных зависят от проекта. Проверь `projects/<name>/credentials.md`.

Нужны:
- **API Key** — формат `id:secret` (Ghost Admin API key)
- **API URL** — например `https://example.com/ghost/api/admin/`

## Авторизация (JWT)

```python
import jwt, time

def ghost_token(api_key):
    """Генерация JWT токена для Ghost Admin API."""
    kid, secret = api_key.split(':')
    iat = int(time.time())
    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': kid}
    payload = {'iat': iat, 'exp': iat + 300, 'aud': '/admin/'}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
```

Установка PyJWT: `pip install PyJWT`

## Создание поста (Lexical — рекомендуемый способ)

⚠️ **Не используй `?source=html`** — Ghost оборачивает весь HTML в один HTML-блок, который неудобно редактировать в визуальном редакторе. Вместо этого конвертируй HTML в Lexical JSON и передавай поле `lexical`.

### HTML → Lexical конвертер

```python
from html.parser import HTMLParser
import json

class HTMLToLexical(HTMLParser):
    """Конвертирует простой HTML (p, h2-h4, strong, em, a, ul/ol/li) в Ghost Lexical JSON."""
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.current_children = []
        self.current_block_type = None
        self.current_tag = None
        self.format_stack = 0  # bitmask: 1=bold, 2=italic
        self.link_url = None
        self.link_children = []
        self.in_link = False
        self.in_list = False
        self.list_type = None
        self.list_items = []
        self.current_li_children = []

    def _flush_block(self):
        if self.current_children and self.current_block_type:
            block = {
                "children": self.current_children,
                "direction": "ltr", "format": "", "indent": 0,
                "type": self.current_block_type, "version": 1
            }
            if self.current_block_type == "heading":
                block["tag"] = self.current_tag or "h2"
            self.blocks.append(block)
        self.current_children = []
        self.current_block_type = None
        self.current_tag = None

    def _flush_li(self):
        if self.current_li_children:
            self.list_items.append({
                "children": self.current_li_children,
                "direction": "ltr", "format": "", "indent": 0,
                "type": "listitem", "version": 1, "value": len(self.list_items) + 1
            })
        self.current_li_children = []

    def _flush_list(self):
        self._flush_li()
        if self.list_items:
            tag = "ol" if self.list_type == "ol" else "ul"
            self.blocks.append({
                "children": self.list_items,
                "direction": "ltr", "format": "", "indent": 0,
                "type": "list", "version": 1,
                "listType": "number" if tag == "ol" else "bullet",
                "start": 1, "tag": tag
            })
        self.list_items = []
        self.in_list = False

    def _text(self, text, fmt=0):
        return {"detail": 0, "format": fmt, "mode": "normal", "style": "",
                "text": text, "type": "extended-text", "version": 1}

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "p" and not self.in_list:
            self._flush_block(); self.current_block_type = "paragraph"
        elif tag in ("h2","h3","h4"):
            self._flush_block(); self.current_block_type = "heading"; self.current_tag = tag
        elif tag in ("strong","b"): self.format_stack |= 1
        elif tag in ("em","i"): self.format_stack |= 2
        elif tag == "a":
            self.in_link = True; self.link_url = d.get("href",""); self.link_children = []
        elif tag in ("ul","ol"):
            self._flush_block(); self.in_list = True; self.list_type = tag
        elif tag == "li": self._flush_li()

    def handle_endtag(self, tag):
        if tag == "p" and not self.in_list: self._flush_block()
        elif tag in ("h2","h3","h4"): self._flush_block()
        elif tag in ("strong","b"): self.format_stack &= ~1
        elif tag in ("em","i"): self.format_stack &= ~2
        elif tag == "a":
            link = {"children": self.link_children, "direction": "ltr", "format": "",
                    "indent": 0, "type": "link", "version": 1,
                    "rel": None, "target": None, "title": None, "url": self.link_url}
            (self.current_li_children if self.in_list else self.current_children).append(link)
            self.in_link = False
        elif tag == "li": self._flush_li()
        elif tag in ("ul","ol"): self._flush_list()

    def handle_data(self, data):
        if not data.strip() and not data.startswith(" "): return
        node = self._text(data, self.format_stack)
        if self.in_link: self.link_children.append(node)
        elif self.in_list: self.current_li_children.append(node)
        elif self.current_block_type: self.current_children.append(node)

    def to_lexical(self):
        self._flush_block()
        return json.dumps({"root": {"children": self.blocks, "direction": "ltr",
                           "format": "", "indent": 0, "type": "root", "version": 1}})

def html_to_lexical(html):
    p = HTMLToLexical(); p.feed(html); return p.to_lexical()
```

### Создание поста

```python
import urllib.request, json

def create_post(api_url, token, title, html, tags=None, meta_title=None, meta_description=None, feature_image=None):
    """Создать пост в Ghost (draft) с нативными Lexical-блоками."""
    lexical = html_to_lexical(html)
    post = {
        "title": title,
        "lexical": lexical,
        "status": "draft",
    }
    if tags:
        post["tags"] = [{"name": t} for t in tags]
    if meta_title:
        post["meta_title"] = meta_title
    if meta_description:
        post["meta_description"] = meta_description
    if feature_image:
        post["feature_image"] = feature_image

    url = f"{api_url}posts/"
    body = json.dumps({"posts": [post]}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Ghost {token}",
        "Content-Type": "application/json"
    })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["posts"][0]
```

Результат: каждый параграф, заголовок и список — отдельный блок в редакторе. Редактор может вставлять картинки между блоками через `+`.

## Обновление поста

```python
def update_post(api_url, token, post_id, updates):
    """Обновить пост. updates — dict с полями для обновления."""
    # Сначала получить текущий updated_at
    get_url = f"{api_url}posts/{post_id}/"
    req = urllib.request.Request(get_url, headers={"Authorization": f"Ghost {token}"})
    current = json.loads(urllib.request.urlopen(req).read())["posts"][0]

    updates["updated_at"] = current["updated_at"]
    url = f"{api_url}posts/{post_id}/?source=html"
    body = json.dumps({"posts": [updates]}).encode()
    req = urllib.request.Request(url, data=body, method="PUT", headers={
        "Authorization": f"Ghost {token}",
        "Content-Type": "application/json"
    })
    return json.loads(urllib.request.urlopen(req).read())["posts"][0]
```

## Загрузка изображений

```python
import mimetypes, os

def upload_image(api_url, token, image_path):
    """Загрузить изображение в Ghost, вернуть URL."""
    content_type = mimetypes.guess_type(image_path)[0]
    filename = os.path.basename(image_path)
    boundary = "----GhostFormBoundary"

    with open(image_path, 'rb') as f:
        image_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + image_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{api_url}images/upload/",
        data=body,
        headers={
            "Authorization": f"Ghost {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        }
    )
    result = json.loads(urllib.request.urlopen(req).read())
    return result["images"][0]["url"]
```

## Получение постов

```python
def get_posts(api_url, token, limit=15, status="all"):
    """Получить список постов."""
    url = f"{api_url}posts/?limit={limit}&filter=status:{status}"
    req = urllib.request.Request(url, headers={"Authorization": f"Ghost {token}"})
    return json.loads(urllib.request.urlopen(req).read())["posts"]
```

## Управление тегами

```python
def get_tags(api_url, token):
    """Получить все теги."""
    url = f"{api_url}tags/?limit=all"
    req = urllib.request.Request(url, headers={"Authorization": f"Ghost {token}"})
    return json.loads(urllib.request.urlopen(req).read())["tags"]
```

## Советы

- Всегда создавай посты в `status: "draft"` — публикацию подтверждает владелец
- `meta_title` — до 60 символов, `meta_description` — до 160
- Для обложек: загрузи через Images API, затем укажи URL в `feature_image`
- Ghost Lexical — внутренний формат. Не пытайся собирать Lexical JSON вручную, используй `?source=html`
