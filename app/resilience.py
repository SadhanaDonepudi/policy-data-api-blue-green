
import time
class CircuitBreaker:
    def __init__(self,threshold=5,reset_s=5): self.threshold=threshold; self.reset_s=reset_s; self.failures=0; self.opened_at=None
    @property
    def state(self):
        if self.opened_at is None: return "closed"
        return "half_open" if time.time()-self.opened_at>=self.reset_s else "open"
    def allow(self): return self.state!="open"
    def success(self): self.failures=0; self.opened_at=None
    def failure(self):
        self.failures+=1
        if self.failures>=self.threshold: self.opened_at=time.time()
def with_retries(fn, attempts=3, base_delay=0.05):
    last=None
    for i in range(attempts):
        try: return fn()
        except Exception as e:
            last=e
            if i<attempts-1: time.sleep(base_delay*(2**i))
    raise last
