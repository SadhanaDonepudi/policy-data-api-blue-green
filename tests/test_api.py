
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),".."))
os.environ.setdefault("POLICY_DB","/tmp/test_policy.db")
from app.store import init_db
init_db(path="/tmp/test_policy.db", n_policies=100, n_claims=300)
from fastapi.testclient import TestClient
from app.main import app
c=TestClient(app)
def test_health(): assert c.get("/health").status_code==200
def test_version(): assert c.get("/version").json()["version"] in ("blue","green")
def test_stats():
    d=c.get("/meta/stats").json(); assert d["policies"]==100 and d["claims"]==300
def test_list_policies():
    d=c.get("/policies?limit=5").json(); assert len(d["items"])==5
def test_list_filter():
    d=c.get("/policies?status=active&limit=200").json(); assert all(x["status"]=="active" for x in d["items"])
def test_policy_detail(): assert c.get("/policies/1").status_code==200
def test_policy_404(): assert c.get("/policies/99999").status_code==404
def test_policy_claims(): assert c.get("/policies/1/claims").status_code==200
def test_policy_claims_404(): assert c.get("/policies/99999/claims").status_code==404
def test_list_claims(): assert len(c.get("/claims?limit=5").json()["items"])==5
def test_claim_detail(): assert c.get("/claims/1").status_code==200
def test_claim_404(): assert c.get("/claims/99999").status_code==404
def test_claims_filter():
    d=c.get("/claims?status=open&limit=200").json(); assert all(x["status"]=="open" for x in d["items"])
def test_headers():
    r=c.get("/health"); assert "x-app-version" in r.headers
