"""Export only explicitly approved public reference rows from the authoritative Sheet."""
import json, os, pathlib, tempfile, math
from sheets import workbook, records

def export(book, target):
    logs=records(book,"SYSTEM_LOGS")
    successful={x["run_id"]:x["started_at"] for x in logs if x.get("stage")=="PUBLISH" and x.get("status")=="SUCCESS"}
    cats={x["category_id"]:x["category_kr"] for x in records(book,"CATEGORIES")}
    approved={x["product_id"] for x in records(book,"PUBLIC_APPROVALS") if x.get("approved","").upper()=="TRUE"}
    items=[]
    run=max(successful,key=successful.get) if successful else None
    for x in records(book,"DAILY_REFERENCES"):
        if not run or x.get("run_id")!=run or x.get("product_id") not in approved:
            continue
        if x.get("sku_verified","").upper()!="TRUE":
            continue
        try:
            values={k:float(x[k]) for k in ("price_cny","design_score","overall_score")}
            if not all(math.isfinite(v) for v in values.values()) or values["price_cny"]<=0 or not all(0<=values[k]<=100 for k in ("design_score","overall_score")):
                continue
        except (ValueError,KeyError,TypeError):
            continue
        from engine import https
        if not https(x.get("image_url")) or not https(x.get("product_url")):
            continue
        items.append(dict(values,product_id=x["product_id"],title_kr=x.get("title_kr",""),title_cn=x.get("title_cn",""),category_kr=cats.get(x.get("category_id"),""),image_url=x["image_url"],product_url=x["product_url"]))
    payload={"status":"published" if items else "not_published","reference_date":successful[run][:10] if items else None,"items":items}
    target=pathlib.Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=target.parent,delete=False) as f:
        json.dump(payload,f,ensure_ascii=False);tmp=f.name
    os.replace(tmp,target)

if __name__=="__main__":
    export(workbook(),"site/data/references.json")
