# pairwise-sieve

只依赖 Python 标准库的素数筛与因子分解内核：上界与区间都由调用方给出，
不使用真实时钟、线程、网络或随机数，同一组参数永远给出同样的结果。

- `sieve/core.py` — 内核：埃氏筛布尔表、素数列表与计数、单个数判定、
  最小质因子表、质因数分解、正因数列表，以及分段筛与区间素数计数。
- `tests/test_core.py` — 验收用例。

## 运行测试

在项目根目录执行：

```
python3 -m unittest discover -s tests -v
```

Windows 上如果没有 `python3`，可用：

```
python -m unittest discover -s tests -v
```
