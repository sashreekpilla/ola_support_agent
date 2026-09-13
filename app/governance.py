from __future__ import annotations
import re
from app.config import MAX_INPUT_CHARS

_CACHE={}


def mask_pii(text:str)->str:
    return re.sub(r"(?<!\d)\d{10}(?!\d)", lambda m: "******"+m.group(0)[-2:], text)


def detect_injection(text:str)->bool:
    patterns=[r"ignore\s+(all\s+)?previous\s+instructions", r"reveal\s+(private|secret|customer)\s+data", r"system\s+prompt"]
    return any(re.search(p,text,re.I) for p in patterns)


def enforce_budget(text:str, token_budget:int):
    # Simple deterministic proxy: one token ~= four characters for the request budget demonstration.
    estimated=max(1, len(text)//4)
    if estimated>token_budget:
        raise ValueError(f"request exceeds token budget: {estimated}>{token_budget}")


def cache_get(query): return _CACHE.get(" ".join(query.lower().split()))
def cache_put(query,value): _CACHE[" ".join(query.lower().split())]=value
