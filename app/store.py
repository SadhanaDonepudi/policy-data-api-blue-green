
import sqlite3, random, os
from pathlib import Path
DB=os.environ.get("POLICY_DB", str(Path(__file__).resolve().parent.parent/"data"/"policy.db"))
STATUSES=["active","lapsed","pending","cancelled"]
TYPES=["auto","home","life","health","commercial"]
def init_db(path=None, n_policies=2000, n_claims=5000, seed=42):
    p=path or DB; Path(p).parent.mkdir(parents=True, exist_ok=True)
    con=sqlite3.connect(p); con.row_factory=sqlite3.Row
    con.executescript("""
    DROP TABLE IF EXISTS policies; DROP TABLE IF EXISTS claims;
    CREATE TABLE policies(id INTEGER PRIMARY KEY, policy_number TEXT UNIQUE, holder TEXT, type TEXT, status TEXT, premium REAL, state TEXT);
    CREATE TABLE claims(id INTEGER PRIMARY KEY, claim_number TEXT UNIQUE, policy_id INTEGER, status TEXT, amount REAL, filed TEXT);
    CREATE INDEX idx_claims_policy ON claims(policy_id);
    """)
    rng=random.Random(seed)
    states=["IL","TX","CA","NY","FL","WA","OH"]
    pols=[(i+1,f"POL-{100000+i}",f"Holder {i+1}",rng.choice(TYPES),rng.choice(STATUSES),round(rng.uniform(200,5000),2),rng.choice(states)) for i in range(n_policies)]
    con.executemany("INSERT INTO policies VALUES (?,?,?,?,?,?,?)",pols)
    claims=[(j+1,f"CLM-{200000+j}",rng.randint(1,n_policies),rng.choice(["open","closed","denied","processing"]),round(rng.uniform(100,50000),2),f"2025-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}") for j in range(n_claims)]
    con.executemany("INSERT INTO claims VALUES (?,?,?,?,?,?)",claims)
    con.commit(); n1=con.execute("SELECT COUNT(*) c FROM policies").fetchone()["c"]; n2=con.execute("SELECT COUNT(*) c FROM claims").fetchone()["c"]; con.close()
    return {"policies":n1,"claims":n2}
def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def q(sql,args=()):
    c=conn(); r=[dict(x) for x in c.execute(sql,args).fetchall()]; c.close(); return r
def q1(sql,args=()):
    r=q(sql,args); return r[0] if r else None
