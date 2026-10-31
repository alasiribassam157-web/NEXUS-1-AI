"""Number theory and statistics for the math engine: gcd/lcm, prime factors, bases, primality, stats."""
import statistics
from math import gcd, lcm

import sympy as sp


def numeric(op: str, nums: list[float], question: str, ar: bool) -> str:
    ints = [int(n) for n in nums if float(n).is_integer()]
    if op in ("gcd", "lcm") and len(ints) >= 2:
        value = ints[0]
        for n in ints[1:]:
            value = gcd(value, n) if op == "gcd" else lcm(value, n)
        name = ("القاسم المشترك الأكبر" if op == "gcd" else "المضاعف المشترك الأصغر") if ar else op.upper()
        return f"{name} لـ {', '.join(map(str, ints))} = **{value}**" if ar else f"{name}({', '.join(map(str, ints))}) = **{value}**"
    if op == "primes" and ints and 1 < ints[0] < 10**12:
        parts = " × ".join(f"{p}^{k}" if k > 1 else str(p) for p, k in sp.factorint(ints[0]).items())
        return f"**{ints[0]} = {parts}**"
    if op == "isprime" and ints:
        yes = sp.isprime(ints[0])
        return (f"**{ints[0]} {'عدد أولي ✓' if yes else 'ليس عدداً أولياً'}**" if ar else f"**{ints[0]} is {'' if yes else 'not '}prime**")
    if op == "base" and ints:
        n = ints[0]
        return f"**{n}** → ثنائي `{bin(n)[2:]}` · ست عشري `{hex(n)[2:].upper()}` · ثماني `{oct(n)[2:]}`" if ar else \
            f"**{n}** → binary `{bin(n)[2:]}` · hex `{hex(n)[2:].upper()}` · octal `{oct(n)[2:]}`"
    if op == "stats" and len(nums) >= 2:
        rows = [("المتوسط", "Mean", statistics.mean(nums)), ("الوسيط", "Median", statistics.median(nums)),
                ("الانحراف المعياري", "Std dev", statistics.pstdev(nums)), ("التباين", "Variance", statistics.pvariance(nums)),
                ("الأصغر", "Min", min(nums)), ("الأكبر", "Max", max(nums))]
        return "\n".join(f"{a if ar else e}: **{v:.4g}**" for a, e, v in rows)
    raise ValueError("أرقام غير كافية" if ar else "not enough numbers")
