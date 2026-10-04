import requests, urllib3
from urllib.parse import urlparse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36 TenderPulseAI/9.0"}
# Only these known public procurement hosts may use expired-certificate fallback.
ALLOW_INSECURE={"e.pprasindh.gov.pk","pprasindh.gov.pk"}
def get(url,timeout=18,params=None):
    try:
        return requests.get(url,headers=UA,timeout=timeout,params=params,allow_redirects=True)
    except requests.exceptions.SSLError:
        host=urlparse(url).hostname or ""
        if host in ALLOW_INSECURE:
            return requests.get(url,headers=UA,timeout=timeout,params=params,allow_redirects=True,verify=False)
        raise
