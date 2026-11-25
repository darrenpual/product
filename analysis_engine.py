"""Evidence-based scoring. Missing evidence stays missing, never invented."""
import math
from statistics import median

def price_score(price, peers):
    if not math.isfinite(price) or price <= 0:
        return None
    valid = [p for p in peers if math.isfinite(p) and p > 0]
    if len(valid) < 5:
        return None
    percentile = (sum(p < price for p in valid) + .5*sum(p == price for p in valid))/len(valid)
    return {"score":round(100*(1-percentile),2),"median":median(valid),"peer_count":len(valid),"percentile":percentile}

def analyze(items, design_evaluator):
    result=[]
    for item in items:
        x=dict(item)
        if x.get("sku_verified") is not True:
            result.append(x)
            continue
        # Comparisons require an explicitly assigned functional peer group.
        group=x.get("peer_group")
        peers={}
        for p in items:
            if group and p.get("peer_group")==group and p.get("sku_verified") is True and p.get("product_id") != x.get("product_id"):
                try:
                    value=float(p["price_cny"])
                    if math.isfinite(value) and value > 0:
                        peers.setdefault(p.get("cluster_id") or p["product_id"],value)
                except (ValueError,TypeError,KeyError):
                    pass
        try:
            price=price_score(float(x["price_cny"]),list(peers.values()))
        except (KeyError,ValueError,TypeError):
            price=None
        if price:
            x["price_analysis"]=price
        if design_evaluator and x.get("image_url"):
            x["design_analysis"]=design_evaluator(x)
        scores=dict(x.get("scores") or {})
        if price:
            scores["price"]=price["score"]
        if x.get("design_analysis"):
            scores["design"]=x["design_analysis"]["design_score"]
        x["scores"]=scores
        result.append(x)
    return result
