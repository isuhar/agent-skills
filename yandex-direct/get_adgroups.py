import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../yandex-metrika"))
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

# Get ad groups for all campaigns
for cid in [705986177, 706470948, 706513694, 706586043, 707847920, 707847921, 707847922, 707854825]:
    try:
        result = direct_request("adgroups", "get", {
            "SelectionCriteria": {"CampaignIds": [cid]},
            "FieldNames": ["Id", "Name", "CampaignId", "Status"],
        })
        for g in result["result"].get("AdGroups", []):
            print(f"Campaign {cid}\tGroup {g['Id']}\t{g['Name']}\t{g['Status']}")
    except Exception as e:
        print(f"Campaign {cid}\tError: {e}")
