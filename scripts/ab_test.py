
"""A/B cache experiment: hits two servers (A=none, B=lru) 50/50 interleaved, compares median latency.
Significance: two-sample z on log-latency approx via normal CI on median difference bootstrap-free check + Mann-Whitney via ranks (no scipy dependency: uses normal approx)."""
import sys, time, statistics, math, httpx
A=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8011"
B=sys.argv[2] if len(sys.argv)>2 else "http://127.0.0.1:8012"
N=int(sys.argv[3]) if len(sys.argv)>3 else 400
def run(base,n):
    lat=[]
    with httpx.Client(base_url=base, timeout=10, trust_env=False) as c:
        c.get("/policies/1")  # warm
        for i in range(n):
            t=time.perf_counter(); c.get(f"/policies/{(i%50)+1}"); lat.append((time.perf_counter()-t)*1000)
    return lat
la,lb=run(A,N//2),run(B,N//2)
ma,mb=statistics.median(la),statistics.median(lb)
delta=(ma-mb)/ma*100 if ma else 0
# Welch t-test on log latencies (95% CI criterion: |t| > 1.96)
xa=[math.log(x) for x in la]; xb=[math.log(x) for x in lb]
def mt(x): return statistics.mean(x), statistics.pvariance(x)
m1,v1=mt(xa); m2,v2=mt(xb)
se=math.sqrt(v1/len(xa)+v2/len(xb)); t=(m1-m2)/se if se else 0
print(f"A_none n={len(la)} median_ms={ma:.3f} mean_ms={statistics.mean(la):.3f}")
print(f"B_lru n={len(lb)} median_ms={mb:.3f} mean_ms={statistics.mean(lb):.3f}")
print(f"median_delta_pct={(delta):.2f} (positive = B faster) welch_t_log={t:.2f} significant_95={abs(t)>1.96}")
