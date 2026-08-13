# Debug Record

## Bug

- 标题：伪造证据摘要可错误晋升解库
- 症状：不存在的 artifact、调用者自填的 SHA-256 与 `independent=true` 可让伪 Result 进入 Solution View。
- 首次发现位置 / 时间：`scripts/validate_research_spaces.py::accepted_independent_capabilities`，2026-08-13。

## Environment

- 仓库 / 模块：`vibe-mathing-cn` / research-space validator
- 运行环境：WSL Ubuntu，Python 3.12，单机文件系统
- 依赖 / 版本：Python stdlib、jsonschema；与网络和模型无关
- 配置差异：无；默认仓库状态可稳定复现

## Reproduction

1. 构造 generator 为 `candidate-generator` 的 Attempt。
2. 构造 proof Result，附两个指向不存在文件的 accept 证据，并自填 `independent=true` 与 64 位伪摘要。
3. 调用 `qualifies_as_solution`；修复前错误返回 `True`。

## Observations

- O1: 现有实现只检查摘要字段是字符串，从不读取 locator。
- O2: 独立性完全相信调用者布尔值，只比较 verifier 字符串不等于 generator。
- O3: 没有受信 artifact 根、verifier registry、现场 hash 或 symlink/path traversal 校验。

## Hypotheses

### H1: 证据摘要被当成证据本身（ROOT HYPOTHESIS）
- Supports: `accepted_independent_capabilities` 不进行任何 I/O 或 registry 查询。
- Conflicts: 无。
- Test: 用不存在 locator 和伪摘要运行固定回归测试，预期修复前错误晋升。

### H2: Result schema 足以阻止伪造
- Supports: schema 约束摘要格式和字段完整性。
- Conflicts: schema 无法证明文件存在、摘要匹配或签发者可信。
- Test: 伪记录能通过字段形状要求但仍被旧业务逻辑接受。

### H3: verifier 名称不同即可证明独立
- Supports: 旧实现只做字符串不等比较。
- Conflicts: 调用者可以任意填写两个名称。
- Test: 任意 `forged-verifier` 在旧实现中被接受。

## Experiments

### E1
- Hypothesis: H1。
- Change: 只新增固定回归测试，不改产品代码。
- Expected: 测试因伪 Result 错误晋升而 RED。
- Result: 标准化 RED 1/1 失败；GREEN 1/1 通过；移除修复后的 counterfactual 1/1 以相同指纹失败。
- Verdict: confirmed
- Revert: 测试不修改业务状态，无需回滚。

## Root Cause

- 信任边界落在 Result 的调用者自报字段，而不是由受信 verifier registry 和真实 artifact 派生；结构校验错误承担了真实性校验职责。

## Fix

- 在 TP-01 引入唯一可信证据解析入口：限制根目录、拒绝 symlink/逃逸、重算 SHA-256、校验 registry capability，并从 generator/verifier trust domain 派生独立性。

## Regression Evidence

- 回归证据契约：Required
- 契约文件：REGRESSION_EVIDENCE.json
- 测试：`scripts/test_trusted_evidence.py`
- 结果：`REGRESSION_EVIDENCE.json` 已绑定标准化 RED / GREEN / counterfactual 三阶段记录。
- 备注：原始 `regression-red.json` 保留首次发现证据；标准化记录用于 owner validator。更广的路径、摘要、symlink、自验证攻击矩阵由独立契约测试补充。

## Failed Nodes

- Result evidence admission
- Solution View derivation
-

## First Invalid Node

- `accepted_independent_capabilities`
-

## Upstream Lineage

- caller-supplied Result evidence fields
-

## Downstream Blast Radius

- `qualifies_as_solution` → `derive_solution_ids` → `solutions.json`
-

## Lowest Common Refinement Ancestor

- trusted evidence resolver
-

## Repair Boundary

- evidence path/digest/issuer/capability/independence validation；不改数学 outcome 规则。
-

## Frozen Nodes

- Problem、Attempt、Result 三对象模型
- outcome × evidence 二维语义
- append-only invalidation 规则
-

## Invalidated Nodes

- caller-supplied `independent` 的信任语义
- 未经现场校验的 `sha256` 与 `locator`
-

## Reverification Required

- research-space schema/cross-reference tests
- trusted evidence attack matrix
- Solution View rebuild
-
