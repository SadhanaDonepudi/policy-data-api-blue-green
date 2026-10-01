
"""LOCAL blue/green simulation: router shifts traffic blue->green, health-checks, auto-rollback on alarm.
Starts nothing itself; expects blue :8021 (healthy) and green :8022. If green /health fails or error rate >5% during canary, router rolls back to 100% blue."""
import time, httpx
def health(base):
    try: return httpx.get(base+"/health",timeout=2,trust_env=False).status_code==200
    except Exception: return False
def err_rate(base,n=50):
    bad=0
    with httpx.Client(base_url=base,timeout=5, trust_env=False) as c:
        for i in range(n):
            try:
                if c.get(f"/policies/{(i%20)+1}").status_code>=500: bad+=1
            except Exception: bad+=1
    return bad/n
BLUE,GREEN="http://127.0.0.1:8021","http://127.0.0.1:8022"
log=[]
log.append(f"blue_healthy={health(BLUE)} green_healthy={health(GREEN)}")
weights=[(90,10),(50,50),(0,100)]
decision="promoted_green"
for b,g in weights:
    er=err_rate(GREEN)
    log.append(f"canary blue={b} green={g} green_error_rate={er:.3f}")
    print(log[-1])
    if er>0.05 or not health(GREEN):
        decision="ROLLED_BACK_TO_BLUE (alarm: green error rate/health)"; break
log.append(f"decision={decision}")
print("\n".join(log))
open("bluegreen_result.txt","w").write("\n".join(log)+"\n")
