# HHT-SHIFTS：真实 ξ 的固定维数、全部非负移位认证

## 0. 命题、执行状态与不混用的信任层

本研究接在相对尾界分支 `research/xi-relative-tail` 的固定提交
`f6e4ed456a0d9159a1af7d1c014f8207ed65da8b` 之后，不覆盖其他研究分支。
已由下述混合证据链认证的精确结论是

$$
H_{d,k}\succ0\qquad(1\le d\le10,\ k\in\mathbb Z_{\ge0}),
$$

其中矩来自**实际 ξ 函数**，定义见第 1 节。这是固定维数、无限多个移位的结论；
不是所有维数的结论，也不宣称 RH。一般引理不主张文献首创。

本文件把自包含解析证明、严格数值认证和 Lean 条件性定理分开。
数值算法依赖固定 `python-flint==0.8.0` 的 ζ、Γ、Taylor 与计数算法；
Lean 的八条定理覆盖第 3 节的几何预算和无限和传播，但不重证整个特殊函数后端、
ξ 的 Hadamard 对应、具体 Lagrange 插值外包或引用的零点计数定理。
执行状态与最终代码提交绑定，记录在本 PR 的实际作业回执中。
已核实代码提交 `2e142a6e9bcfc5b318d082ce7a8737edbdf10813` 的实际运行：

- [真实 ξ 数值与完整移位预算](https://github.com/DionisAI/vibe-mathing-cn-public/actions/runs/34366306327/job/102515803449)：completed / success。
- [八条 Lean 定理编译及逐条公理审计](https://github.com/DionisAI/vibe-mathing-cn-public/actions/runs/34366306327/job/102515804047)：completed / success。
- [同一代码的完整 CI](https://github.com/DionisAI/vibe-mathing-cn-public/actions/runs/34366306512)：completed / success。
- 本地和远端 16 项有理回归均通过；它们不替代上述数值/Lean 执行。

本说明与索引/测试入口的后续提交不改变已验证的数值算法、Lean 源码或原公理白名单；
后续提交自己的复跑状态由 PR #11 回执另外记录。该 PR 未合并，main 不变。
首次工作流的 YAML pip 命令被解析阻断后，改成块标量重新执行；没有忽略失败检查。

### 实际有限阈值与无限覆盖

| 维数 d | 有理预算首次通过 B_K<1 的充分阈值 K |
|---|---:|
| 1 | 1 |
| 2 | 1 |
| 3 | 2 |
| 4 | 2 |
| 5 | 3 |
| 6 | 4 |
| 7 | 5 |
| 8 | 6 |
| 9 | 6 |
| 10 | 7 |

两个精度的阈值完全相同。具体使用十阶的 K=7：k=0,...,6 的七个完整矩阵均经
严格区间 LDL 认证；k>=7 由同一个精确几何预算的单调性覆盖，无需逐一计算。
前七个十阶矩阵各有十个严格正主元，并在 1024/1536 位各从头重算。
较低维数由左上主块继承，所以结论覆盖每个 1<=d<=10、每个整数 k>=0。
总计数 N(256)=111，(50,256] 有 101 个新单根区间；完整计数分割共使用 808 次查询。
这些是本次输出的实际结果，不是从渐近估计或记忆中的根表推测。

## 1. 固定 ξ、谱坐标和矩，不预设 RH

令

$$
E(w)=\frac{\xi(1/2+w)}{\xi(1/2)},\qquad F(w^2)=E(w).
$$

ξ 的经典实对称性和函数方程保证 E 是实偶整函数，唯一确定 F。沿用 HHT004 的
Hadamard 配对论证，枚举上半平面全部非平凡零点，含重数。对
\(\rho=\beta+i\gamma\)、\(\delta=\beta-1/2\)，写

$$
\lambda_\rho=-(\rho-1/2)^2=(\gamma-i\delta)^2,\qquad
u_\rho=\lambda_\rho^{-1}.
$$

为避免与插值下标冲突，本文件用 ν 表示任意谱节点，用 u_j 表示选择的正实节点。
没有把 β 全部设为 1/2。上半平面反射 \(\rho\mapsto1-\overline\rho\)
对应 ν 的共轭，重数相同；下半平面不再重复计入。

$$
\frac{F'(z)}{F(z)}=\sum_{n\ge0}(-1)^n\mu_nz^n,
\quad\mu_n=\sum_{\gamma>0}m_\rho\nu_\rho^{n+1},
\quad H_{d,k}=(\mu_{k+i+j})_{0\le i,j<d}.
$$

对实系数多项式 \(p(X)=\sum_{j=0}^{d-1}v_jX^j\)，有

$$
Q_k(p)=\sum_{\gamma>0}m_\rho\nu_\rho^{k+1}p(\nu_\rho)^2
=v^TH_{d,k}v.
$$

这里是普通平方，不是模平方。各和绝对收敛，共轭对称使总和为实数。
任意固定多项式在有界谱上有界，而全部逆谱的一次模和有限，足以保证这些换序。
完整解析输入在 `XI_STRIP.md` 第 1–3 节中说明；它们没有因为本轮 Lean 成功而
自动变成端到端内核验证。

## 2. 有限认证前缀与未知完整尾部

首先用全临界带计数加实连续 ξ 的严格变号认证高度 50 内的十个单根，
复用并实际重跑 `zero_cover(256)`。十根用 128 次严格有理二分得到区间。

对于每个半开高度区间 `(a,b]`，计算全临界带计数差 `N(b)-N(a)`，
而不是只数临界线找根器找到的根。程序自适应分割 `(50,256]`，
保留全部非空区间并核对总数。只有当每个保留区间的**总重数恰为 1**时才继续。

理由：区间对上半平面反射封闭。非临界线根必须与一个不同的反射根同时出现在
同一高度区间，总重数至少 2。因此完整单根区间必位于临界线上，并且根是单根。
这个推理不需要假设上面全部高度都满足 RH；它只认证一个有限高度前缀。

选择前 d 个严格正实逆谱节点 \(u_j\)，其余高度不超过 256 的已认证正实节点
为全部 k 提供非负贡献。对未知的整个高度大于 256 的尾部，临界带给出

$$
|\nu|=\frac1{\gamma^2+\delta^2}<\frac1{256^2}=:r.
$$

Bellotti–Wong, arXiv:2412.15470v2, Theorem 1.1 给出全域计数上界。
沿用已写出的保守推论 \(N(t)\le t\log t\)（t≥50），非负换序给出

$$
\sum_{\gamma>256}m_\rho|\nu_\rho|
\le\sum_{\gamma>256}m_\rho\gamma^{-2}
=2\int_{256}^\infty [N(t)-N(256)]t^{-3}\,dt
\le\frac{2(\log256+1)}{256}<\frac7{128}=:S.
$$

\(\log256<6\) 可独立由 \(e^3>\sum_{n=0}^{4}3^n/n!=131/8>16\) 推出。
程序冻结 r=1/65536、S=7/128，不用浮点对数生成上界。
该 S 覆盖**所有未知尾节点与其重数**，不预设尾节点是实数。

计数来源原文：
https://arxiv.org/html/2412.15470v2 （Theorem 1.1；版本日期 2025-07-07）。
并不依赖这个界是当前最优界。

## 3. 一般定理：谱隙把无限移位归约为有限验证

### 3.1 假设与插值

固定 d≥1 个互异正实节点 \(u_1,\ldots,u_d\)。其他前缀节点均为正实、重数为正；
整个尾部对共轭封闭，\(|\nu|\le r<\min_j u_j\)、\(\sum m_\nu|\nu|\le S<\infty\)。
固定实多项式 p，次数小于 d。定义

$$
\ell_j(z)=\prod_{l\ne j}\frac{z-u_l}{u_j-u_l},\qquad
A_k(p)=\sum_{j=1}^{d}u_j^{k+1}p(u_j)^2.
$$

Lagrange 插值恒等式 \(p(z)=\sum_jp(u_j)\ell_j(z)\) 对每个复数 z 成立。
若 p 非零，d 个互异根不能全部成为 p 的根，所以 A_k(p)>0。
额外正实节点的贡献记为 R_k(p)≥0。

对每个 j 选严格分离的正有理区间 \([a_j,b_j]\ni u_j\)，满足 r<a_j。
记区间距离

$$
\Delta_{jl}=\max\{a_j-b_l,a_l-b_j\}>0,
\qquad M_j=\prod_{l\ne j}\frac{r+b_l}{\Delta_{jl}}.
$$

则全部 |z|≤r 上有 \(|\ell_j(z)|\le M_j\)。所有区间重叠、接触或谱隙失败均拒绝认证。

### 3.2 相对绝对尾界

复数的加权 Cauchy–Schwarz 不等式给出

$$
|p(z)|^2
\le A_k(p)\sum_{j=1}^{d}\frac{|\ell_j(z)|^2}{u_j^{k+1}}.
$$

因此，包括所有未知节点的尾和满足

$$
\begin{aligned}
|Q_{\mathrm{tail},k}(p)|
&\le\sum_{\mathrm{tail}}m_\nu|\nu|^{k+1}|p(\nu)|^2\\
&\le A_k(p)S r^k\sum_{j=1}^{d}\frac{M_j^2}{u_j^{k+1}}\\
&\le A_k(p)\sum_{j=1}^{d}c_j\alpha_j^k,
\end{aligned}
$$

其中所有预算常数均可取精确有理数：

$$
c_j=\frac{SM_j^2}{a_j}\ge0,\qquad
\alpha_j=\frac r{a_j}\in(0,1),\qquad
B_k=\sum_{j=1}^{d}c_j\alpha_j^k.
$$

与零移位的一侧负界不同，这里直接控制整个尾部绝对值，故不需要
\(\Re(\nu^{k+1})>0\)，不存在把零移位配方错误推广到大移位的问题。

### 3.3 对所有足够大 k 的结论

由于 B_k 非增且趋于零，存在有限 K 使 B_K<1。于是对全部 k≥K，

$$
\boxed{Q_k(p)=A_k(p)+R_k(p)+Q_{\mathrm{tail},k}(p)
\ge(1-B_K)A_k(p)>0\quad(p\ne0).}
$$

这给出整个 H_(d,k) 的正定性，不是只检查一个方向或一个行列式。
若另外认证有限多个 H_(d,0),...,H_(d,K-1) 正定，就得到**全部 k≥0**。
K 是这个保守预算的充分阈值，不声称是最小实际正定阈值。

程序逐个用 Fraction 比较严格不等式 B_K<1，而不是用浮点 logarithm 猜 K。
预算达到上限返回不能判断；B_K=1 也不通过。算法的搜索上限不进入一般存在性论证。

## 4. 实际 ξ 的有限异常验证

程序对前 d 个根（d=1,...,10）分别生成有理预算。对最终 d=10 取得 K 后，
直接计算 k=0,...,K-1 的十阶矩阵。所有更低维矩阵是左上主块，因此也正定。

使用完成 ζ 公式

$$
\xi(s)=\tfrac12s(s-1)\pi^{-s/2}\Gamma(s/2)\zeta(s)
$$

在 s=1/2+w 的严格 Taylor 级数，取偶次项形成 F，再求 F'/F。
有限多项式系数由真实解析函数的运算产生，不是把若干零点的有限乘积当成 F。
所以无限零点对于所用矩的贡献没有被舍弃。

需要到下标 K+2d-3 的矩，总共 K+2d-2 个；代码先检查截断精度足够，
再逐项检查实系数和偶性的一致性。实性/偶性的数学保证来自经典 ξ 对称性，
不是因为一个小球碰巧包含零。

为改善尺度，以 \(200^{n+1}\mu_n\) 构造第 k 个矩阵。这恰为

$$
200^{k+1}\operatorname{diag}(1,200,\ldots,200^{d-1})\,
H_{d,k}\,\operatorname{diag}(1,200,\ldots,200^{d-1}),
$$

是正标量乘正对角合同变换，不改变正定性。区间 LDL 每一步只在整个主元区间严格正时继续；
所有对称条目来源于同一个矩对象，不能把重叠但含义不同的区间当成相同条目。
主元不是原矩阵的特征值。

1024、1536 位各从头重算；输出精确有理根区间、预算常数、全部使用的矩与主元外包，
并检查两次矩区间相交、阈值相同。这是同一后端的精度交叉检查，不声称独立后端或独立数学审查。
本轮不依赖临界线的动态网页根表。

## 5. Lean 的实际陈述范围

`fixtures/lean-proof/HHTShifts.lean` 中的八条定理：

| 名称（HHTShifts 命名空间） | 范围 |
|---|---|
| budget_nonneg | 非负系数和比例产生非负预算 |
| budget_step_le | 每增加一次移位预算不增 |
| budget_add_le | 从 K 到 K+n 的全称预算控制 |
| budget_below_one_after | 严格阈值传递到每一个 k≥K |
| complex_pairing_bound | 实部、虚部两次 Cauchy 合并的模平方控制 |
| infinite_envelope_lower | 明确可求和前提下的真正无限和比较 |
| one_shift_positive | 预算小于一时完整方向严格正 |
| all_shifts_positive | 有限异常验证加收缩预算推出全部移位与全部非零方向 |

最后一条量化任意有限维 d，但并不声称具体 ξ 对每个 d 都满足其参数。
前缀正定、插值包络、可求和性、预算和低移位结论均是明写假设，未被放进全局公理。
本文件没有声称 Lagrange 多项式的构造与外包、真实 ξ 的系数或零点计数已经端到端形式化。

检查入口实际调用锁定 Lean 4.33.0，固定 Mathlib 提交
`db584cd6d46c92f209a44c0f1c829460d327499d`，开启 warningAsError。
每条定理必须有恰好一条依赖回执，只允许 `propext / Classical.choice / Quot.sound`。
实际日志的八条报告全部只含上述三项，最终输出：

```text
SHIFT_LEAN_PASS: 8 audited theorems; interpolation and xi backend inputs are explicit, not fully formalized.
```
缺工具、编译错误、输出溢出或不允许的依赖均阻断。

## 6. 复算入口与工程边界

```bash
# 标准库逻辑与有理回归，不代替 FLINT 或 Lean 的实际运行。
(ulimit -v 524288; ulimit -t 20; ulimit -f 256; timeout 30s python3 scripts/test_xi_shifts.py)
# 在固定 python-flint==0.8.0 环境中重算根、有限异常及整个无限移位预算。
(ulimit -v 2097152; ulimit -t 180; ulimit -f 2048; timeout 240s python3 scripts/certify_xi_shifts.py)
# 准备仓库已有锁定 Mathlib 缓存后实际编译和审计。
timeout 300s python3 scripts/check_hht_shifts.py
```

新脚本不联网查询私人数据，不写 canonical Result，不更改已有可信准入规则。
工作流只读、限时，无凭据持久化、定时或付费模型调用。完整上游 CI 与新增数学验证作业
分别记录，不能用一个作业成功代替另一个。

## 7. 来源和下一处真正的缺口

- Bellotti–Wong, arXiv:2412.15470v2, Theorem 1.1：全临界带计数的明确解析输入。
  https://arxiv.org/html/2412.15470v2
- NIST DLMF §3.3(i)：Lagrange 插值恒等式与互异节点要求。
  https://dlmf.nist.gov/3.3
- FLINT acb_dirichlet 官方文档：ζ、ξ、Taylor jet 与全零点计数算法。
  https://flintlib.org/doc/acb_dirichlet.html
- python-flint 官方 arb 文档：zeta_nzeros 的全临界带计数接口。
  https://python-flint.readthedocs.io/en/latest/arb.html

以上公开原始来源在 2026-09-09 核对；固定软件执行版本为 0.8.0，而非自动采用文档当前版本。
没有声称完成全面新颖性检索或外部独立审查。

本轮区分两个全称量词：固定 d 时，k 的无限方向可由严格谱隙闭合；
但 d 增大时插值常数和锚点数量都会变化，不能用同一个 K 或同一有限前缀覆盖所有 d。
所有移位的固定阶正性仍不能排除更高维负见证。真正的全维数不等式仍未证明，
也没有通过假设任意高处的完整临界线覆盖把 RH 偷放进前提。
