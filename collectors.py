import os, json
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

def collect_feeds():
    # Normalized, licensed feeds only. Map provider-specific schemas separately.
    for feed in json.loads(os.getenv("FEEDS_JSON", "[]")):
        if not feed.get("authorized"):
            continue
        url = feed["url"]
        if urlparse(url).scheme != "https":
            raise ValueError("HTTPS required")
        token = os.getenv(feed.get("token_env", "UNUSED_TOKEN"))
        headers = {"Authorization": "Bearer "+token} if token else {}
        with httpx.Client(timeout=30, follow_redirects=False) as client:
            r = client.get(url, headers=headers)
            r.raise_for_status()
            payload = r.json()
        if not isinstance(payload, list):
            raise ValueError("Expected normalized list")
        for x in payload:
            yield dict(x, source=feed["name"])

def collect_pages():
    # Explicitly authorized URLs, robots compliant, no login or bypass.
    for page in json.loads(os.getenv("AUTHORIZED_PAGES_JSON", "[]")):
        if not page.get("authorized"):
            continue
        url = page["url"]
        if urlparse(url).scheme != "https":
            continue
        agent = "ProductDiscoveryBot"
        with httpx.Client(timeout=20, follow_redirects=False, headers={"User-Agent":agent}) as client:
            robots = client.get(urljoin(url, "/robots.txt"))
            if robots.status_code != 200:
                continue
            parser = RobotFileParser()
            parser.parse(robots.text.splitlines())
            if not parser.can_fetch(agent, url):
                continue
            response = client.get(url)
            response.raise_for_status()
        for node in BeautifulSoup(response.text, "html.parser").select('script[type="application/ld+json"]'):
            try:
                obj = json.loads(node.string or "")
            except ValueError:
                continue
            for p in (obj if isinstance(obj,list) else [obj]):
                if isinstance(p,dict) and p.get("@type") == "Product":
                    yield {"product_id": str(p.get("sku") or url), "title_cn":p.get("name",""), "category_id":page["category_id"], "product_url":url, "image_url":p.get("image"), "source":"NATIVE", "sku_verified":False, "scores":{}}
