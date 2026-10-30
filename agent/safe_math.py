"""Sandbox-free math for public/safe mode: an AST whitelist evaluator plus fixed recipes.

Nothing here executes user code, so it is safe to expose on the public link.
"""
import ast
import math
import operator

_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {name: getattr(math, name) for name in
          ("sqrt", "sin", "cos", "tan", "log", "log10", "exp", "floor", "ceil", "factorial")}
_FUNCS.update(abs=abs, round=round, pow=pow)
_CONSTS = {"pi": math.pi, "e": math.e}
MAX_EXPONENT = 10_000


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise ValueError("Exponent too large")
        return _BIN[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        return _FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError("Unsupported expression")


def _cap(n: str, limit: int) -> int:
    value = int(float(n))
    if value > limit:
        raise ValueError(f"Number too large (max {limit:,})")
    return value


def _fib(n: int) -> list[int]:
    seq, a, b = [], 0, 1
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq


def _primes(n: int) -> list[int]:
    sieve = bytearray([1]) * max(n, 2)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(n) if sieve[i]]


RECIPES = {
    "sum_range": lambda a, b: (_cap(a, 10**12) + _cap(b, 10**12)) * (_cap(b, 10**12) - _cap(a, 10**12) + 1) // 2,
    "factorial": lambda n: math.factorial(_cap(n, 3000)),
    "fibonacci": lambda n: _fib(_cap(n, 1000)),
    "primes": lambda n: _primes(_cap(n, 1_000_000)),
    "average": lambda nums: (lambda xs: sum(xs) / len(xs))([float(x) for x in nums.replace(" ", "").split(",") if x]),
}


def evaluate(op: str, args: list[str]) -> str:
    if op == "expr":
        result = _eval(ast.parse(args[0].replace("^", "**"), mode="eval").body)
    else:
        result = RECIPES[op](*args)
    if isinstance(result, float) and result.is_integer() and abs(result) < 1e15:
        result = int(result)
    return str(result)
