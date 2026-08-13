---
name: math-formalization
description: "数学形式化与 proof-assistant 验证。用户要求 Lean 4/Mathlib、formal proof、kernel check、无 sorry 编译，或需要把自然语言定理切成可形式化定义和引理时使用。缺少 Lean 工具链时必须 fail-closed。"
---

# Math Formalization

把数学主张转成可由 proof assistant 内核检查的最小切片；当前环境缺工具时只产出计划，不伪造验证。

## When to Use This Skill

- 用户明确要求 Lean 4、Mathlib 或机器检查证明。
- 自然语言证明已经稳定，需要验证关键引理或高风险步骤。
- 需要建立 definitions/imports/lemmas/theorem 的形式化依赖结构。

## Not For / Boundaries

- 当前本机未安装 `lean`、`elan` 或 `lake`；在安装前状态只能是 `calibration/blocked`。
- 含 `sorry`、`admit`、未授权 axiom 或编译失败的文件不得标记 kernel-checked。
- 不采用归档 skill 中未经验证的 `lean_agent` Python API。
- 形式化成功证明 Lean 陈述成立，不自动证明它忠实表达原自然语言命题；必须做 faithfulness audit。

## Quick Reference

```bash
command -v lean
command -v lake
lean --version
lake env lean Path/To/File.lean
rg -n '\b(sorry|admit)\b' .
```

形式化包必须包含：原命题、Lean 陈述、定义映射、imports、证明义务、实际命令、退出码、Lean/Mathlib 版本、axiom/sorry 审计和 faithfulness 状态。

只有命令真实返回成功、无占位证明且陈述忠实审计完成，才能写 `kernel-checked`。

## Examples

### Example 1：工具缺失
- 输入：“把这个引理用 Lean 验证。”
- 动作：运行预检，发现 `lean` 缺失；输出安装前置和形式化切片。
- 验收：状态是 blocked，不创建伪编译日志。

### Example 2：含 sorry
- 输入：一个能够编译但包含 `sorry` 的 Lean 文件。
- 动作：扫描占位符并阻止通过。
- 验收：不能标记 kernel-checked，报告具体文件/位置。

### Example 3：陈述失真
- 输入：Lean 证明了比原命题更弱的结论。
- 动作：proof check 与 faithfulness audit 分开裁决。
- 验收：内核检查可 PASS，但总体状态仍因表达不忠实而 BLOCK。

## References

- `references/source-map.md`：Lean 指南来源与拒绝的未验证 API。
- `references/pressure-tests.md`：`sorry` 与陈述忠实性压力场景。

## Maintenance

- Sources：`wentor-research-plugins` 的 Lean 指南，仅吸收概念与工具路由，不吸收未验证 API。
- Last updated：2026-08-13。
- Verification：安装后必须用当前 Lean/Mathlib 官方工具运行最小无 `sorry` vertical slice。
