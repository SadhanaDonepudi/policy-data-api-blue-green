
import time
from collections import OrderedDict
class NoCache:
    name="none"
    def get(self,k): return None
    def set(self,k,v): pass
    def stats(self): return {"strategy":self.name,"hits":0,"misses":0}
class TTLCache:
    name="ttl"
    def __init__(self,ttl=30): self.ttl=ttl; self.d={}; self.hits=0; self.misses=0
    def get(self,k):
        e=self.d.get(k)
        if e and e[1]>time.time(): self.hits+=1; return e[0]
        self.misses+=1; return None
    def set(self,k,v): self.d[k]=(v,time.time()+self.ttl)
    def stats(self): return {"strategy":self.name,"hits":self.hits,"misses":self.misses,"size":len(self.d)}
class LRUCache:
    name="lru"
    def __init__(self,cap=512): self.cap=cap; self.d=OrderedDict(); self.hits=0; self.misses=0
    def get(self,k):
        if k in self.d: self.hits+=1; self.d.move_to_end(k); return self.d[k]
        self.misses+=1; return None
    def set(self,k,v):
        self.d[k]=v; self.d.move_to_end(k)
        while len(self.d)>self.cap: self.d.popitem(last=False)
    def stats(self): return {"strategy":self.name,"hits":self.hits,"misses":self.misses,"size":len(self.d)}
def make(name):
    return {"none":NoCache,"ttl":TTLCache,"lru":LRUCache}.get((name or "ttl").lower(),TTLCache)()
