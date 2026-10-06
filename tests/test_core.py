"""素数筛与因子分解内核的行为测试。

每条期望都写成结果本身：素数列表、个数、分解对、因数表或调用方必须看到的
异常。文件里的对照实现全部用最朴素的方式另写一遍，不调用被测函数反推。
从项目根目录执行：

    python3 -m unittest discover -s tests -v
"""

import unittest

from sieve.core import (
    SieveError,
    count_primes_between,
    divisors,
    factorize,
    is_prime,
    prime_count,
    primes_up_to,
    segmented_primes,
    sieve_flags,
    smallest_prime_factors,
)


def trial_is_prime(value):
    """独立判定：从 2 试除到平方根。"""
    if value < 2:
        return False
    factor = 2
    while factor * factor <= value:
        if value % factor == 0:
            return False
        factor += 1
    return True


def trial_primes(low, high):
    """独立列出闭区间内的素数，升序。"""
    return [value for value in range(low, high + 1) if trial_is_prime(value)]


def trial_smallest_factor(value):
    """独立求最小质因数：0 与 1 原样返回。"""
    if value < 2:
        return value
    factor = 2
    while factor * factor <= value:
        if value % factor == 0:
            return factor
        factor += 1
    return value


def trial_factorize(value):
    """独立分解：返回（质数，指数）对，质数升序。"""
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
        divisor += 1
    if rest > 1:
        factors.append((rest, 1))
    return factors


def trial_divisors(value):
    """独立列出全部正因数，升序。"""
    return [factor for factor in range(1, value + 1) if value % factor == 0]


class SieveTest(unittest.TestCase):
    """内核的对外行为。"""

    def test_01_sieve_flags_and_prime_list(self):
        flags = sieve_flags(30)
        self.assertEqual(len(flags), 31)
        self.assertFalse(flags[0], "0 不是素数")
        self.assertFalse(flags[1], "1 不是素数")
        self.assertTrue(flags[2])
        self.assertTrue(flags[3])
        self.assertFalse(flags[4])
        self.assertFalse(flags[25])
        self.assertTrue(flags[29])
        self.assertEqual(primes_up_to(0), [])
        self.assertEqual(primes_up_to(1), [])
        self.assertEqual(primes_up_to(2), [2])
        self.assertEqual(primes_up_to(3), [2, 3])
        self.assertEqual(primes_up_to(10), [2, 3, 5, 7])
        self.assertEqual(primes_up_to(20), [2, 3, 5, 7, 11, 13, 17, 19])
        self.assertEqual(
            primes_up_to(30),
            [2, 3, 5, 7, 11, 13, 17, 19, 23, 29],
        )
        self.assertEqual(
            primes_up_to(100),
            [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53,
             59, 61, 67, 71, 73, 79, 83, 89, 97],
        )
        for limit in (2, 3, 4, 9, 16, 49, 97, 100, 121, 144, 200):
            self.assertEqual(primes_up_to(limit), trial_primes(0, limit),
                             "不超过 %d 的素数" % (limit,))

    def test_02_single_number_primality(self):
        self.assertFalse(is_prime(0))
        self.assertFalse(is_prime(1))
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(3))
        self.assertFalse(is_prime(4))
        self.assertFalse(is_prime(9))
        self.assertTrue(is_prime(97))
        expected = {value for value in range(0, 101) if trial_is_prime(value)}
        for value in range(0, 101):
            self.assertEqual(is_prime(value), value in expected,
                             "is_prime(%d)" % (value,))
        for value in (101, 121, 169, 199, 289, 361, 400, 997, 1009, 1024,
                      1999, 2003, 7919, 8000, 8191, 99991, 100000, 104729):
            self.assertEqual(is_prime(value), trial_is_prime(value),
                             "is_prime(%d)" % (value,))

    def test_03_prime_count(self):
        counts = (
            (0, 0),
            (1, 0),
            (10, 4),
            (30, 10),
            (100, 25),
            (97, 25),
            (2, 1),
            (3, 2),
            (4, 2),
            (1000, 168),
            (1009, 169),
            (10000, 1229),
        )
        for limit, expected in counts:
            self.assertEqual(prime_count(limit), expected,
                             "不超过 %d 的素数个数" % (limit,))
        for limit in (2, 3, 10, 97, 100, 121, 199, 1000):
            self.assertEqual(prime_count(limit), len(primes_up_to(limit)),
                             "计数与列表一致: %d" % (limit,))

    def test_04_smallest_prime_factor_table(self):
        self.assertEqual(smallest_prime_factors(0), [0])
        self.assertEqual(smallest_prime_factors(1), [0, 1])
        table = smallest_prime_factors(200)
        self.assertEqual(len(table), 201)
        self.assertEqual(table[0], 0)
        self.assertEqual(table[1], 1)
        for value in range(2, 201):
            self.assertEqual(table[value], trial_smallest_factor(value),
                             "最小质因数 %d" % (value,))
        for value in (2, 3, 5, 7, 11, 13, 97, 199):
            self.assertEqual(table[value], value, "素数自身的最小质因数 %d" % (value,))
        self.assertEqual(table[12], 2)
        self.assertEqual(table[30], 2)
        self.assertEqual(table[49], 7)
        self.assertEqual(table[77], 7)
        self.assertEqual(table[100], 2)

    def test_05_factorize(self):
        self.assertEqual(factorize(1), [])
        self.assertEqual(factorize(2), [(2, 1)])
        self.assertEqual(factorize(3), [(3, 1)])
        self.assertEqual(factorize(4), [(2, 2)])
        self.assertEqual(factorize(12), [(2, 2), (3, 1)])
        self.assertEqual(factorize(36), [(2, 2), (3, 2)])
        self.assertEqual(factorize(60), [(2, 2), (3, 1), (5, 1)])
        self.assertEqual(factorize(97), [(97, 1)])
        self.assertEqual(factorize(1024), [(2, 10)])
        self.assertEqual(factorize(1009), [(1009, 1)])
        for value in (2, 3, 5, 6, 8, 9, 10, 16, 27, 49, 64, 72, 100, 128,
                      210, 243, 360, 1000, 2017, 4096, 999983):
            self.assertEqual(factorize(value), trial_factorize(value),
                             "分解 %d" % (value,))
        for value in range(1, 501):
            factors = factorize(value)
            product = 1
            for prime, exponent in factors:
                product *= prime ** exponent
            self.assertEqual(product, value, "分解乘积还原 %d" % (value,))
            self.assertEqual(factors, trial_factorize(value), "分解 %d" % (value,))

    def test_06_divisors(self):
        self.assertEqual(divisors(1), [1])
        self.assertEqual(divisors(2), [1, 2])
        self.assertEqual(divisors(12), [1, 2, 3, 4, 6, 12])
        self.assertEqual(divisors(36), [1, 2, 3, 4, 6, 9, 12, 18, 36])
        self.assertEqual(divisors(49), [1, 7, 49])
        self.assertEqual(divisors(97), [1, 97])
        self.assertEqual(divisors(128), [1, 2, 4, 8, 16, 32, 64, 128])
        for value in range(1, 201):
            got = divisors(value)
            self.assertEqual(got, trial_divisors(value), "正因数 %d" % (value,))
            for factor in got:
                self.assertEqual(value % factor, 0, "%d 的因数 %d" % (value, factor))

    def test_07_segmented_primes(self):
        self.assertEqual(segmented_primes(0, 2), [2])
        self.assertEqual(segmented_primes(0, 10), [2, 3, 5, 7])
        self.assertEqual(segmented_primes(2, 2), [2])
        self.assertEqual(segmented_primes(4, 4), [])
        self.assertEqual(segmented_primes(2, 30),
                         [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
        self.assertEqual(segmented_primes(8, 20), [11, 13, 17, 19])
        self.assertEqual(segmented_primes(100, 121), [101, 103, 107, 109, 113])
        self.assertEqual(segmented_primes(120, 130), [127])
        for low, high in ((0, 10), (1, 2), (2, 50), (50, 100), (90, 100),
                          (100, 200), (120, 130), (900, 1000), (1000, 1100),
                          (9900, 10000), (10000, 10100)):
            self.assertEqual(segmented_primes(low, high), trial_primes(low, high),
                             "区间 %d 到 %d" % (low, high))

    def test_08_count_primes_between(self):
        cases = (
            (0, 10, 4),
            (2, 2, 1),
            (4, 4, 0),
            (3, 11, 4),
            (7, 19, 5),
            (7, 20, 5),
            (10, 100, 21),
            (100, 200, 21),
            (997, 1009, 2),
            (1000, 2000, 135),
        )
        for low, high, expected in cases:
            self.assertEqual(count_primes_between(low, high), expected,
                             "区间 %d 到 %d 的素数个数" % (low, high))
        for low, high in ((0, 50), (7, 20), (13, 13), (100, 300), (900, 1100)):
            self.assertEqual(count_primes_between(low, high),
                             len(trial_primes(low, high)),
                             "区间 %d 到 %d 与独立列表一致" % (low, high))

    def test_09_cross_consistency(self):
        for limit in (2, 3, 10, 97, 100, 121, 199, 1000):
            self.assertEqual(prime_count(limit), len(primes_up_to(limit)),
                             "列表长度与计数一致: %d" % (limit,))
        for low, high in ((0, 50), (7, 20), (100, 200), (900, 1100)):
            self.assertEqual(count_primes_between(low, high),
                             len(segmented_primes(low, high)),
                             "区间计数与分段筛一致: %d 到 %d" % (low, high))
            self.assertEqual(segmented_primes(low, high), trial_primes(low, high),
                             "分段筛与独立列表一致: %d 到 %d" % (low, high))
        for value in range(0, 200):
            self.assertEqual(is_prime(value), trial_is_prime(value),
                             "逐点判定 %d" % (value,))
        for value in range(1, 121):
            factors = factorize(value)
            product = 1
            for prime, exponent in factors:
                product *= prime ** exponent
            self.assertEqual(product, value, "分解乘积还原 %d" % (value,))
            self.assertEqual(divisors(value), trial_divisors(value),
                             "因数与分解一致 %d" % (value,))

    def test_10_invalid_arguments_and_boundaries(self):
        self.assertEqual(sieve_flags(0), [False])
        self.assertEqual(primes_up_to(0), [])
        self.assertEqual(prime_count(0), 0)
        self.assertEqual(smallest_prime_factors(0), [0])
        self.assertEqual(smallest_prime_factors(1), [0, 1])
        self.assertEqual(factorize(1), [])
        self.assertEqual(divisors(1), [1])
        self.assertEqual(segmented_primes(0, 0), [])
        self.assertEqual(segmented_primes(2, 2), [2])
        for bad in (-1, -100):
            with self.assertRaises(SieveError):
                sieve_flags(bad)
            with self.assertRaises(SieveError):
                primes_up_to(bad)
            with self.assertRaises(SieveError):
                prime_count(bad)
            with self.assertRaises(SieveError):
                smallest_prime_factors(bad)
            with self.assertRaises(SieveError):
                segmented_primes(bad, 10)
            with self.assertRaises(SieveError):
                count_primes_between(bad, 10)
        with self.assertRaises(SieveError):
            segmented_primes(0, -1)
        with self.assertRaises(SieveError):
            segmented_primes(20, 10)
        with self.assertRaises(SieveError):
            count_primes_between(20, 10)
        with self.assertRaises(SieveError):
            factorize(0)
        with self.assertRaises(SieveError):
            factorize(-7)
        with self.assertRaises(SieveError):
            divisors(0)
        with self.assertRaises(SieveError):
            divisors(-7)
        for bad in (True, False, 1.5, "10", None, [], object()):
            with self.assertRaises(TypeError):
                sieve_flags(bad)
            with self.assertRaises(TypeError):
                is_prime(bad)
            with self.assertRaises(TypeError):
                factorize(bad)
            with self.assertRaises(TypeError):
                divisors(bad)


if __name__ == "__main__":
    unittest.main()
