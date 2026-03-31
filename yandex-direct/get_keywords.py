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

# Get keywords for ЕПК [Personal] ad groups
for gid in [5695401955, 5695402372]:
    result = direct_request("keywords", "get", {
        "SelectionCriteria": {"AdGroupIds": [gid]},
        "FieldNames": ["Id", "Keyword", "AdGroupId", "Status", "State"],
    })
    for kw in result["result"].get("Keywords", []):
        print(f"Group {kw['AdGroupId']}\t{kw['Id']}\t{kw['Keyword']}\t{kw['Status']}")

# Also check the suspended search campaigns
for gid in [5726769770, 5726769771, 5726769772]:
    result = direct_request("keywords", "get", {
        "SelectionCriteria": {"AdGroupIds": [gid]},
        "FieldNames": ["Id", "Keyword", "AdGroupId", "Status", "State"],
    })
    for kw in result["result"].get("Keywords", []):
        print(f"Group {kw['AdGroupId']}\t{kw['Id']}\t{kw['Keyword']}\t{kw['Status']}")
