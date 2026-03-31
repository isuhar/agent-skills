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

# Get all campaigns
result = direct_request("campaigns", "get", {
    "SelectionCriteria": {},
    "FieldNames": ["Id", "Name", "Status", "State"],
})
for c in result["result"]["Campaigns"]:
    print(f"{c['Id']}\t{c['Name']}\t{c['Status']}\t{c['State']}")
