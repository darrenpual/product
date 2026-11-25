import json, uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from collectors import collect_feeds, collect_pages
from engine import rank
from sheets import workbook, records, config, append

def run():
    book = workbook()
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    date = now.date().isoformat()
    run_id = str(uuid.uuid4())
    cfg = config(book)
    try:
        logs = records(book,"SYSTEM_LOGS")
        if any(x.get("stage")=="PUBLISH" and x.get("status")=="SUCCESS" and x.get("started_at","").startswith(date) for x in logs):
            return
        items = list(collect_feeds()) + list(collect_pages())
        if not items:
            raise RuntimeError("No authorized feed/page data; configure sources")
        refs = records(book,"DAILY_REFERENCES")
        previous = [x.get("cluster_id") or x.get("product_id") for x in refs]
        selected = rank(items,cfg,previous)
        # Only reviewed/verified inputs can be published. No fabricated scores.
        rows = []
        for x in selected:
            s = x["scores"]
            rows.append([date,x["rank"],x["product_id"],x.get("cluster_id") or x["product_id"],x.get("title_kr",""),x.get("title_cn",""),x["category_id"],x["image_url"],x["product_url"],x["price_cny"],True,s["design"],s["price"],s["innovation"],s["marketing"],s["market_response"],x["overall_score"],x["grade"],json.dumps(x.get("labels",[]),ensure_ascii=False),x.get("summary",""),x.get("source",""),x.get("first_seen_at",""),x.get("listed_at",""),cfg["version"],"SKU_VERIFIED",run_id])
        append(book,"DAILY_REFERENCES",rows)
        append(book,"SYSTEM_LOGS",[[run_id,"PUBLISH","PIPELINE",now.isoformat(),datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),"SUCCESS",len(rows),""]])
    except Exception as exc:
        append(book,"SYSTEM_LOGS",[[run_id,"PUBLISH","PIPELINE",now.isoformat(),datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),"FAILED",0,type(exc).__name__]])
        raise

if __name__ == "__main__":
    run()
