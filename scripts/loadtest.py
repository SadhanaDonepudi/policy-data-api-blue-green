
"""Local load test: measures latency percentiles + success rate against a running server."""
import sys, time, statistics, httpx
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8001"
N=int(sys.argv[2]) if len(sys.argv)>2 else 300
def pct(v,p): return sorted(v)[min(len(v)-1,int(p/100*len(v)))] if v else 0
lat=[]; ok=0
with httpx.Client(base_url=BASE, timeout=10, trust_env=False) as c:
    for i in range(N):
        t=time.perf_counter()
        try:
            r=c.get(f"/policies/{(i%50)+1}")
            if r.status_code==200: ok+=1
        except Exception: pass
        lat.append((time.perf_counter()-t)*1000)
print(f"requests={N} success={ok} success_rate={ok/N:.4f} median_ms={statistics.median(lat):.2f} p95_ms={pct(lat,95):.2f} mean_ms={statistics.mean(lat):.2f}")
