"""素数筛与因子分解内核（纯标准库，行为完全确定）。

模块围绕一张布尔筛表工作：筛表的下标就是数本身，flags[n] 为真表示 n 是
素数。素数列表、素数计数、最小质因子表、质因数分解、正因数列表、分段筛
与区间计数都从这张表或它的局部副本上取数。模块不读写文件、不联网、不使
用真实时钟与随机数，同一组上界与区间永远给出同样的结果。

约定：

* 0 与 1 不是素数；
* 分解结果里的质数严格升序、指数为正，各项乘积等于原数；
* 分段筛与整段筛对同一个区间给出同一串素数；
* 区间内的素数个数与逐点判定、与分段筛的长度都一致。

对外接口：

* sieve_flags            埃氏筛布尔表；
* primes_up_to           不超过上界的素数列表；
* prime_count            不超过上界的素数个数；
* is_prime               单个数判定；
* smallest_prime_factors 最小质因子表；
* factorize              质因数分解；
* divisors               全部正因数；
* segmented_primes       闭区间内的素数；
* count_primes_between   闭区间内的素数个数。
"""

from math import isqrt

__all__ = [
    "SieveError",
    "sieve_flags",
    "primes_up_to",
    "prime_count",
    "is_prime",
    "smallest_prime_factors",
    "factorize",
    "divisors",
    "segmented_primes",
    "count_primes_between",
]


class SieveError(ValueError):
    """参数越界：负上界、倒置区间、非正的待分解数。"""


def _require_int(value, label):
    """确认参数是非布尔的整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("%s 必须是整数: %r" % (label, value))
    return value


def _require_bound(value, label):
    """确认参数是非布尔整数且不为负。"""
    _require_int(value, label)
    if value < 0:
        raise SieveError("%s 不能为负: %r" % (label, value))
    return value


def sieve_flags(limit):
    """返回长度 limit 加 1 的布尔表，下标 n 上的真表示 n 是素数。"""
    _require_bound(limit, "上界")
    flags = [True] * (limit + 1)
    flags[0] = False
    if limit >= 1:
        flags[1] = False
    for prime in range(2, isqrt(limit) + 1):
        if not flags[prime]:
            continue
        for multiple in range(prime * prime, limit, prime):
            flags[multiple] = False
    return flags


def primes_up_to(limit):
    """不超过上界的全部素数，升序。"""
    return [value for value, flag in enumerate(sieve_flags(limit)) if flag]


def prime_count(limit):
    """不超过上界的素数个数。"""
    _require_bound(limit, "上界")
    flags = sieve_flags(limit)
    total = 0
    for value in range(2, limit):
        if flags[value]:
            total += 1
    return total


def is_prime(value):
    """判断单个数是不是素数。"""
    _require_int(value, "待判定数")
    if value < 1:
        return False
    if value % 2 == 0:
        return value == 2
    factor = 3
    while factor * factor <= value:
        if value % factor == 0:
            return False
        factor += 2
    return True


def smallest_prime_factors(limit):
    """最小质因子表：table[n] 是 n 的最小质因数，table[0] 为 0，table[1] 为 1。"""
    _require_bound(limit, "上界")
    table = list(range(limit + 1))
    for prime in range(2, isqrt(limit) + 1):
        if table[prime] != prime:
            continue
        for multiple in range(prime * prime, limit + 1, prime):
            table[multiple] = prime
    return table


def factorize(value):
    """质因数分解：返回（质数，指数）对，质数严格升序；1 返回空表。"""
    _require_int(value, "待分解数")
    if value < 1:
        raise SieveError("待分解数必须为正: %r" % (value,))
    factors = []
    rest = value
    divisor = 2
    while divisor * divisor <= rest:
        if rest % divisor == 0:
            exponent = 0
            while rest % divisor == 0:
                rest //= divisor
                exponent += 1
            factors.append((divisor, exponent))
        divisor += 1 if divisor == 2 else 2
    return factors


def divisors(value):
    """value 的全部正因数，升序；1 的因数是只有 1 的表。"""
    _require_int(value, "待求数")
    if value < 1:
        raise SieveError("待求数必须为正: %r" % (value,))
    result = [1]
    for prime, exponent in factorize(value):
        powers = [prime ** power for power in range(exponent)]
        result = [factor * power for factor in result for power in powers]
    return sorted(result)


def segmented_primes(low, high):
    """闭区间 [low, high] 内的全部素数，升序。"""
    _require_bound(low, "区间下界")
    _require_bound(high, "区间上界")
    if low > high:
        raise SieveError("区间下界不能高于上界: %r > %r" % (low, high))
    flags = [True] * (high - low + 1)
    base = primes_up_to(isqrt(low))
    for prime in base:
        start = max(prime * prime, ((low + prime - 1) // prime) * prime)
        for multiple in range(start, high + 1, prime):
            flags[multiple - low] = False
    if low < 2:
        for value in range(low, min(2, high + 1)):
            flags[value - low] = False
    return [low + index for index, flag in enumerate(flags) if flag]


def count_primes_between(low, high):
    """闭区间 [low, high] 内的素数个数。"""
    _require_bound(low, "区间下界")
    _require_bound(high, "区间上界")
    if low > high:
        raise SieveError("区间下界不能高于上界: %r > %r" % (low, high))
    below = prime_count(low) if low >= 1 else 0
    return prime_count(high) - below
