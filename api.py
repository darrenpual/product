import os, secrets
from fastapi import FastAPI, Header, HTTPException
from sheets import workbook, records

app=FastAPI(title="Product Discovery", version="0.1.0")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/api/v1/references/latest")
def latest(authorization: str = Header(default="")):
    token=os.environ.get("DELIVERY_API_TOKEN")
    if not token or not secrets.compare_digest(authorization, "Bearer "+token):
        raise HTTPException(401,"Unauthorized")
    book=workbook()
    logs=records(book,"SYSTEM_LOGS")
    successful={x["run_id"]:x["started_at"] for x in logs if x.get("stage")=="PUBLISH" and x.get("status")=="SUCCESS"}
    if not successful:
        return {"status":"not_published","items":[]}
    run_id=max(successful,key=successful.get)
    items=[x for x in records(book,"DAILY_REFERENCES") if x.get("run_id")==run_id]
    return {"status":"published","reference_date":successful[run_id][:10],"items":items}
