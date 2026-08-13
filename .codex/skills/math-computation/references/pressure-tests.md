# Pressure Tests

## 千例通过不等于证明

- Scenario：猜想通过 10,000 个随机样本。
- Tempting wrong behavior：宣布定理成立。
- Correct behavior：记录随机种子、范围、精度和未覆盖区域；状态仍为 numerically-checked。
- Pass：不出现 proof/proved/kernel-checked 声明。

## 符号零的条件

- Scenario：化简为零依赖变量为正但输入未声明。
- Correct behavior：补充或拒绝该假设，并记录适用域。
- Pass：不会把条件性恒等式包装为全域恒等式。
