import sys, os, json
sys.path.insert(0, "/root/.openclaw/workspace/skills/yandex-metrika")
from ym_auth import get_token
import urllib.request

token = get_token()

def direct_request(service, method, params):
    url = f"https://api.direct.yandex.com/json/v5/{service}/"
    body = json.dumps({"method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept-Language": "ru",
    })
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# Task 4: mk1 → add to ЕПК [Personal], group "Аналог OneNote" (5695402372)
# Text editor, notepad, knowledge base keywords
mk1_keywords = [
    "текстовый редактор онлайн",
    "текстовый редактор онлайн бесплатно",
    "текстовый редактор онлайн на русском",
    "записная книжка онлайн",
    "записная книжка онлайн бесплатно",
    "лучшие онлайн записные книжки",
    "база знаний бесплатно",
    "база знаний онлайн бесплатно",
    "создание базы знаний",
]
mk1_negatives = ["пдф", "pdf", "фото", "изменение", "смотреть", "фильм", "тайна"]

# Task 5: Planer semant → add to "Трекер задач [search]" (707847922), group 5726769772
planer_keywords = [
    "канбан доска",
    "канбан доска бесплатно",
    "канбан доска онлайн",
    "канбан доска приложение",
    "доска задач канбан",
    "чек лист онлайн",
    "чек лист онлайн бесплатно",
    "создать чек лист онлайн",
    "создать чек лист онлайн бесплатно",
    "трекер привычек",
    "трекер привычек бесплатно",
    "трекер полезных привычек",
    "планировщик задач онлайн",
    "планировщик задач онлайн бесплатно",
]
planer_negatives = ["битрикс", "шаблон", "эксель", "excel", "гугл"]

# Task 7: Notion semant → add to ЕПК [Personal], group "Аналог Google Keep" (5695401955)
notion_keywords = [
    "notion замена",
    "замена notion в россии",
    "notion альтернатива",
    "альтернатива notion в россии",
    "notion на русском",
    "приложение notion на русском",
    "notion на русском бесплатно",
    "скачать notion на русском",
]

# Add keywords function
def add_keywords(ad_group_id, keywords, label):
    kw_items = [{"Keyword": kw, "AdGroupId": ad_group_id} for kw in keywords]
    result = direct_request("keywords", "add", {"Keywords": kw_items})
    print(f"\n=== {label} (group {ad_group_id}) ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

# Add negative keywords to ad group
def add_negative_keywords(campaign_id, negatives, label):
    # Use campaign negative keywords
    # First get current negative keywords
    result = direct_request("campaigns", "get", {
        "SelectionCriteria": {"Ids": [campaign_id]},
        "FieldNames": ["Id", "Name", "NegativeKeywords"],
    })
    campaign = result["result"]["Campaigns"][0]
    current_negatives = campaign.get("NegativeKeywords", {}).get("Items", [])
    print(f"\n=== {label} - Current negatives for campaign {campaign['Name']}: {current_negatives}")
    
    # Add new negatives
    new_negatives = list(set(current_negatives + negatives))
    result = direct_request("campaigns", "update", {
        "Campaigns": [{
            "Id": campaign_id,
            "NegativeKeywords": {"Items": new_negatives},
        }]
    })
    print(f"Updated negatives: {json.dumps(result, ensure_ascii=False)}")

# Execute
print("=== ADDING KEYWORDS ===")

# Task 4: mk1 → group "Аналог OneNote" in ЕПК [Personal]
add_keywords(5695402372, mk1_keywords, "mk1 (Аналог OneNote)")

# Task 5: Planer → group "Трекер задач" in Трекер задач [search]
add_keywords(5726769772, planer_keywords, "Planer semant (Трекер задач)")

# Task 7: Notion → group "Аналог Google Keep" in ЕПК [Personal]  
add_keywords(5695401955, notion_keywords, "Notion semant (Аналог Google Keep)")

print("\n=== ADDING NEGATIVE KEYWORDS ===")

# Task 4 negatives → campaign ЕПК [Personal] (but only relevant to mk1 group - use group level if possible)
# Actually add negatives at campaign level for now
add_negative_keywords(705986177, mk1_negatives, "mk1 negatives → ЕПК [Personal]")

# Task 5 negatives → campaign Трекер задач [search]
add_negative_keywords(707847922, planer_negatives, "Planer negatives → Трекер задач [search]")

print("\nDone!")
