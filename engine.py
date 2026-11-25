import math
from collections import Counter
from urllib.parse import urlparse

FIELDS = ["design", "price", "innovation", "marketing", "market_response"]

def https(value):
    return isinstance(value, str) and urlparse(value).scheme == "https" and bool(urlparse(value).hostname)

def rank(items, cfg, previous=()):
    weights = {k: float(cfg[k]) for k in FIELDS}
    if any(not math.isfinite(v) or v < 0 for v in weights.values()) or not math.isclose(sum(weights.values()), 1):
        raise ValueError("Invalid scoring weights")
    candidates = []
    for item in items:
        try:
            if item.get("sku_verified") is not True or not https(item.get("image_url")) or not https(item.get("product_url")):
                continue
            if item.get("accessory_only") or not item.get("product_id") or not item.get("category_id"):
                continue
            price = float(item["price_cny"])
            if not math.isfinite(price) or price <= 0:
                continue
            scores = {k: float(item["scores"][k]) for k in FIELDS}
            if any(not math.isfinite(v) or not 0 <= v <= 100 for v in scores.values()):
                continue
            overall = round(sum(scores[k]*weights[k] for k in FIELDS), 2)
            if overall < float(cfg["min_total"]) or scores["design"] < float(cfg["min_design"]) or scores["price"] < float(cfg["min_price"]):
                continue
            grade = next((g.upper() for g in ("s","a","b","c") if overall >= float(cfg["grade_"+g])), "D")
            candidates.append(dict(item, scores=scores, overall_score=overall, grade=grade))
        except (KeyError, TypeError, ValueError):
            continue
    seen = set(previous)
    counts = Counter()
    result = []
    for x in sorted(candidates, key=lambda x: (-x["overall_score"], x["product_id"])):
        cluster = x.get("cluster_id") or x["product_id"]
        cat = x["category_id"]
        if cluster in seen or counts[cat] >= int(cfg["category_limit"]):
            continue
        if len(result) >= int(cfg["daily_limit"]):
            break
        seen.add(cluster)
        counts[cat] += 1
        result.append(dict(x, rank=len(result)+1))
    return result
