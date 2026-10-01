
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),".."))
from app.cache import NoCache, TTLCache, LRUCache, make
from app.resilience import CircuitBreaker, with_retries
def test_nocache(): c=NoCache(); c.set("a",1); assert c.get("a") is None
def test_ttl(): c=TTLCache(ttl=60); c.set("a",1); assert c.get("a")==1 and c.stats()["hits"]==1
def test_ttl_miss(): c=TTLCache(); assert c.get("x") is None and c.stats()["misses"]==1
def test_lru_evict():
    c=LRUCache(cap=2); c.set("a",1); c.set("b",2); c.set("c",3); assert c.get("a") is None and c.get("c")==3
def test_make(): assert make("lru").name=="lru" and make("none").name=="none" and make("bogus").name=="ttl"
def test_breaker_opens():
    b=CircuitBreaker(threshold=2, reset_s=60)
    b.failure(); b.failure(); assert b.state=="open" and not b.allow()
def test_breaker_success_resets():
    b=CircuitBreaker(); b.failure(); b.success(); assert b.failures==0 and b.state=="closed"
def test_retries_succeeds():
    n={"i":0}
    def flaky():
        n["i"]+=1
        if n["i"]<3: raise ValueError("boom")
        return 42
    assert with_retries(flaky, attempts=3, base_delay=0.001)==42
def test_retries_exhausts():
    import pytest
    def bad(): raise ValueError("x")
    with pytest.raises(ValueError): with_retries(bad, attempts=2, base_delay=0.001)
