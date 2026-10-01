
"""Client with retries + circuit breaker used by the chaos harness."""
import sys, time, httpx
sys.path.insert(0,".")
from app.resilience import CircuitBreaker
def fetch_all(base, n=200):
    br= CircuitBreaker(); ok=0; lat=[]; attempts=0
    with httpx.Client(base_url=base, timeout=10, trust_env=False) as c:
        for i in range(n):
            if not br.allow(): time.sleep(0.05); continue
            t=time.perf_counter(); done=False
            for a in range(3):
                attempts+=1
                try:
                    r=c.get(f"/policies/{(i%50)+1}")
                    if r.status_code==200: done=True; br.success(); break
                    if r.status_code>=500: br.failure()
                except Exception: br.failure()
                time.sleep(0.02*(2**a))
            if done: ok+=1
            lat.append((time.perf_counter()-t)*1000)
    return ok, lat, attempts, br.state
