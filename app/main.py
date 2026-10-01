
import os, time, random
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from app import store
from app.cache import make
VERSION=os.environ.get("APP_VERSION","blue")
STRATEGY=os.environ.get("CACHE_STRATEGY","ttl")
CHAOS_LATENCY=float(os.environ.get("CHAOS_LATENCY_MS","0"))
CHAOS_FAIL=float(os.environ.get("CHAOS_FAIL_RATE","0"))
cache=make(STRATEGY)
app=FastAPI(title="Policy Data API (local simulation)", version="1.0.0")
@app.middleware("http")
async def chaos(request: Request, call_next):
    if CHAOS_LATENCY>0: time.sleep(CHAOS_LATENCY/1000.0)
    if CHAOS_FAIL>0 and random.random()<CHAOS_FAIL:
        return JSONResponse(status_code=503, content={"detail":"injected dependency failure (local chaos simulation)"})
    r=await call_next(request); r.headers["X-App-Version"]=VERSION; r.headers["X-Cache-Strategy"]=STRATEGY
    return r
@app.get("/health")
def health(): return {"status":"ok","version":VERSION,"cache":STRATEGY}
@app.get("/version")
def version(): return {"version":VERSION,"cache_strategy":STRATEGY}
@app.get("/meta/stats")
def stats():
    return {"policies":store.q1("SELECT COUNT(*) c FROM policies")["c"],"claims":store.q1("SELECT COUNT(*) c FROM claims")["c"],"cache":cache.stats(),"version":VERSION,"store":"SQLite stand-in for PostgreSQL (local simulation)"}
@app.get("/policies")
def policies(limit:int=Query(20,ge=1,le=200), offset:int=Query(0,ge=0), status:str|None=None, type:str|None=None):
    key=f"pol:{limit}:{offset}:{status}:{type}"
    hit=cache.get(key)
    if hit is not None: return hit
    sql="SELECT * FROM policies WHERE 1=1"; a=[]
    if status: sql+=" AND status=?"; a.append(status)
    if type: sql+=" AND type=?"; a.append(type)
    sql+=" ORDER BY id LIMIT ? OFFSET ?"; a+=[limit,offset]
    out={"items":store.q(sql,a),"limit":limit,"offset":offset}
    cache.set(key,out); return out
@app.get("/policies/{pid}")
def policy(pid:int):
    key=f"pol:{pid}"; hit=cache.get(key)
    if hit is not None: return hit
    r=store.q1("SELECT * FROM policies WHERE id=?",(pid,))
    if not r: raise HTTPException(404,"policy not found")
    cache.set(key,r); return r
@app.get("/policies/{pid}/claims")
def policy_claims(pid:int):
    if not store.q1("SELECT id FROM policies WHERE id=?",(pid,)): raise HTTPException(404,"policy not found")
    return {"policy_id":pid,"items":store.q("SELECT * FROM claims WHERE policy_id=? ORDER BY id",(pid,))}
@app.get("/claims")
def claims(limit:int=Query(20,ge=1,le=200), offset:int=Query(0,ge=0), status:str|None=None):
    sql="SELECT * FROM claims WHERE 1=1"; a=[]
    if status: sql+=" AND status=?"; a.append(status)
    sql+=" ORDER BY id LIMIT ? OFFSET ?"; a+=[limit,offset]
    return {"items":store.q(sql,a),"limit":limit,"offset":offset}
@app.get("/claims/{cid}")
def claim(cid:int):
    r=store.q1("SELECT * FROM claims WHERE id=?",(cid,))
    if not r: raise HTTPException(404,"claim not found")
    return r
