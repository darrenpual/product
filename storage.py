import json
from sheets import append,records

def save_products(book,items,now):
    tab=book.worksheet("PRODUCTS")
    rows=tab.get_all_values()
    existing={r[0]:(i+1,r) for i,r in enumerate(rows) if i and r}
    updates=[]
    fresh=[]
    for x in {x["product_id"]:x for x in items if x.get("product_id")}.values():
        key=x["product_id"]
        old=existing.get(key)
        first=(old[1][13] if old and len(old[1])>13 else "") or x.get("first_seen_at") or now
        row=[key,x.get("platform",""),x.get("platform_item_id",""),x.get("cluster_id") or key,x.get("title_cn",""),x.get("title_kr",""),x.get("category_id",""),x.get("store_id",""),x.get("product_url",""),x.get("image_url","") if isinstance(x.get("image_url"),str) else "",x.get("price_cny",""),x.get("sku_id",""),x.get("sku_verified") is True,first,now,x.get("listed_at") or "",x.get("source",""),"VERIFIED" if x.get("sku_verified") is True else "PENDING"]
        x["first_seen_at"]=first
        if old:
            updates.append({"range":f"A{old[0]}:R{old[0]}","values":[row]})
        else:
            fresh.append(row)
    if updates:
        tab.batch_update(updates,value_input_option="RAW")
    append(book,"PRODUCTS",fresh)
    append(book,"PRICE_HISTORY",[[x["product_id"],x.get("sku_id",""),now,x["price_cny"],x.get("source","")] for x in items if x.get("product_id") and x.get("sku_verified") is True and x.get("price_cny") is not None])

def save_analysis(book,items,now):
    design=[];price=[]
    for x in items:
        d=x.get("design_analysis")
        if d:
            design.append([x["product_id"],now,d["model_version"],*[d[k] for k in ("form_quality","originality","premium","cmf","function","brand_potential","ad_visual")],d["design_score"],json.dumps(d.get("labels",[]),ensure_ascii=False),d.get("evidence",""),""])
        p=x.get("price_analysis")
        if p:
            price.append([x["product_id"],now,x.get("sku_id",""),x["price_cny"],True,p["median"],p["peer_count"],p["percentile"],p["score"],"Verified comparable group"])
    append(book,"DESIGN_ANALYSIS",design)
    append(book,"PRICE_ANALYSIS",price)
