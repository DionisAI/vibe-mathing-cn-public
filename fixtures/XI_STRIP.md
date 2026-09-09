# HHT-004：真实 ξ 零点映射、临界带的一侧尾界与 Lean 切片

## 状态

本轮接续 HHT-003。这里的解析推导使用真实 ζ 零点的已知临界带与计数定理，
不假定无限高度 RH；计算样例仍是明确标记的有理合成输入。

已完成：以下自包含尾界推导、精确区间程序、22 项算术回归，以及 12 条 Lean 子命题源码。
尚未完成：独立数学审查、完整解析论证的 Lean 形式化、真实根区间字节与计数证据的认证接入。
本轮执行环境没有 Lean/lake，安装路径受 GitHub DNS/下载访问限制；因此 **Lean 未编译通过**。
单独的编译工作流与依赖审计入口已经提供，不能用 Python 测试代替 Lean 运行。
不宣称首创，不写 canonical Result，不宣称解决或反驳 RH。

## 1. 冻结映射，避免重复计算零点

只枚举 **上半平面** 的全部非平凡零点 rho=beta+i*gamma，gamma>0，含重数 m_rho。
令 delta=beta-1/2，定义

$$
\lambda_\rho=-(\rho-\tfrac12)^2=(\gamma-i\delta)^2,
\qquad u_\rho=\lambda_\rho^{-1}.
$$

由 0<beta<1 得 |delta|<1/2；以下估计使用更保守的闭区间。
逐项有

$$
\Re\lambda=\gamma^2-\delta^2,\quad
\Im\lambda=-2\gamma\delta,\quad
|\lambda|=\gamma^2+\delta^2\ge\gamma^2.
$$

rho 与下半平面的 1-rho 映到同一个 lambda；不能把二者重复计入。
上半平面的 rho 与 1-conj(rho) 则映到一对共轭 lambda，重数相同。
当 gamma>0 时，lambda 为实数当且仅当 delta=0。这里没有把 beta 偷换成 1/2。

定义真实零点矩与零移位二次型

$$
\mu_n=\sum_{\gamma>0}m_\rho\lambda_\rho^{-n-1},\qquad
H_{d,0}=(\mu_{i+j})_{0\le i,j<d},\qquad
Q(p)=\sum_{\gamma>0}m_\rho u_\rho p(u_\rho)^2.
$$

所有多项式系数为实数，求和含上半平面全部零点而非只含已找到的临界线零点。
第 3 节给出绝对收敛；共轭对称因此保证这些量为实数。

与原 ξ 函数的对应：令 E(w)=xi(1/2+w)/xi(1/2)。由反射公式 E 为偶函数。
以 ξ 的整性、阶 1 与 Hadamard 分解作为显式经典解析输入，把 ±(rho-1/2)
的 genus-1 因子配对，得到 1+w²/lambda；两个指数因子相消。
残余 exp(A+B*w) 的线性项由偶性消除，常数由 E(0)=1 确定。
因 sum |lambda|^-1 有限，配对乘积局部一致收敛。
于是唯一的整函数 F 满足 F(w²)=E(w)，且

$$
F(z)=\prod_{\gamma>0}(1+z/\lambda_\rho)^{m_\rho},\qquad
F'/F=\sum_{n\ge0}(-1)^n\mu_nz^n
$$

在原点的收敛邻域成立。上述经典解析输入及此乘积分解 **不在本轮 Lean 切片内**。

### 高度截断不等于模长截断

本轮使用 gamma<=T 的前缀、gamma>T 的尾部。
前缀可以含 |lambda|>T² 的节点（最多到 T²+1/4）；尾部一定满足 |lambda|>T²。
因此不能把高度列表直接传给要求每个节点 |lambda|<=T² 的旧模长接口。
新接口始终使用 `cutoff_kind=height`，并检查每个根区间不跨越 T。

## 2. 固定可核查的计数来源

采用 Bellotti–Wong, arXiv:2412.15470v2 (2025-07-07), Theorem 1.1：
对 t>=e，计数 N(t) 包含 0<gamma<=t 的全部非平凡零点（含重数），且

$$
\left|N(t)-\frac{t}{2\pi}\log\frac{t}{2\pi e}\right|
\le 0.10076\log t+0.24460\log\log t+8.08344.
$$

来源：https://arxiv.org/html/2412.15470v2 （本轮已读取定理正文）。
该版本还指出旧 HSW 常数 9.3675 应改为 9.4925；这里不继承旧常数。
我们不依赖“这是否是最新最优估计”。

只取易于审查的保守推论：

$$
\boxed{N(t)\le t\log t\quad(t\ge50).}
$$

推导：pi>3，log t>=1，log log t<=log t，两个对数系数之和小于 1，
常数项小于 9。因此主项<=t*log(t)/6，误差<=log(t)+9<=10log(t)<=t*log(t)/5。
故 N(t)<(11/30)t*log(t)<=t*log(t)。全域计数定理是来源明确的解析输入，
不是因为程序接收了某个系数就已被程序验证。

## 3. 高度尾和与绝对收敛

对任意 q>1、T>=50，由非负项换序，

$$
\sum_{\gamma>T}m_\rho\gamma^{-q}
=q\int_T^\infty [N(t)-N(T)]t^{-q-1}\,dt
\le Z_q(T),
$$

$$
\boxed{Z_q(T)=qT^{1-q}\left(\frac{\log T}{q-1}+\frac1{(q-1)^2}\right).}
$$

把 |lambda|>=gamma² 代入得到各阶矩绝对收敛。
对于冻结 p(x)=sum c_j*x^j 与非负整数 k，通用双侧绝对尾界为

$$
|Q_{\mathrm{tail},k}(p)|
\le\sum_{i,j}|c_i c_j|Z_{2(k+i+j+1)}(T).
$$

这条双侧界既可支持严格负证书，也可支持固定尺寸的正定误差分析。

## 4. 本轮主要推导：只控制可能的负贡献

**本节严格限定 k=0。不能直接推广到任意移位 k。**
对每个尾节点写 u=x+i*y，p(u)=P+i*Q。由 gamma>T>=50 得 x>0。
有准确恒等式

$$
x\,\Re\{u p(u)^2\}+(x^2+y^2)Q^2=(xP-yQ)^2.
$$

因此

$$
\Re\{u p(u)^2\}\ge-\frac{|u|^2}{x}(\Im p(u))^2.
$$

这是下界；它绝不是 |u*p(u)^2| 的上界。p 为常数时右侧为零，但原项通常严格正。

现在利用真实临界带：

$$
x=\frac{\gamma^2-\delta^2}{(\gamma^2+\delta^2)^2},\quad
y=\frac{2\gamma\delta}{(\gamma^2+\delta^2)^2},\quad
\frac{|u|^2}{x}=\frac1{\gamma^2-\delta^2}.
$$

由 |delta|<=1/2 和 |u|<=gamma^-2，

$$
\frac{|u|^2}{x}y^2
\le\frac{\gamma^{-8}}{1-1/(4T^2)}.
$$

有限差幂恒等式 u^j-conj(u)^j=(u-conj(u))*sum u^r*conj(u)^(j-1-r)
给出

$$
|\Im p(u)|\le |y|\sum_{j\ge1}j|c_j||u|^{j-1}.
$$

对每个节点应用这两个不等式，再对上半平面全部尾节点求和。令
C_T=(1-1/(4T²))^-1，则

$$
\boxed{Q_{\mathrm{tail},0}(p)
\ge-C_T\sum_{i,j\ge1}ij|c_i c_j|Z_{2i+2j+4}(T).}
$$

没有额外的因子 2：计数 N 已枚举每个上半平面零点，共轭对的两个成员分别计数。
各阶和绝对收敛，故求实部、共轭配对、有限多项式换序都有效。

### 矩阵形式

令 p 的非恒定系数向量为 v_+=(c_1,...,c_(d-1))。
对有限导数和用 Cauchy–Schwarz，得到

$$
\boxed{H_{d,0}^{\mathrm{tail}}\succeq
-E_d(T)\operatorname{diag}(0,1,\ldots,1),\quad
E_d(T)=C_T\sum_{j=1}^{d-1}j^2Z_{4j+4}(T).}
$$

这是 Loewner 下界，不是算子范数上界。
当 d=2，只需扣除斜率方向的 C_T*Z_8(T)=O(log(T)/T^7)。
它不意味着整块绝对尾项也有这个数量级。
大移位时 u^(k+1) 的实部可能改变符号，所以没有声称所有 k 都享有同一结论。

## 5. 一个可复核但仍有根数据前提的二阶比较

假定已有独立证据证明：一个临界线零点的高度属于 (14,15)，另一个属于 (21,22)，
并且其余 gamma<=50 的零点也全在临界线上。
**这些根数据前提未由本轮程序认证。**

两个倒数节点 u,v 的矩阵 A 的 Schur 补为 uv(u-v)²/(u+v)。由上述区间可得

$$
\mathrm{Schur}(A)\ge\frac{64}{10838953125}.
$$

使用 log(50)<4（也可由本轮有理 log 包络确认），

$$
E_2(50)<\frac{29}{4784677734375},\quad
\frac{64}{10838953125}-\frac{29}{4784677734375}
=\frac{4035853}{684208916015625}>0.
$$

所有其他已确认的临界线前缀节点提供半正定贡献；第 4 节覆盖未知的完整尾部。
所以这些根数据前提成立时，完整 H_(2,0) 严格正定。这个比较只涉及固定二阶、零移位，
不能推广为全部 Hankel 矩阵正定，更不能宣称 RH。
Lean 切片核查的是上述有理恒等式与条件不等式，而不是零点存在性。

## 6. 根区间接入的真实状态

LMFDB 的来源、完备性与可靠性说明已核对：其零点表有明确的高度覆盖、
误差以及基于严格 Turing 方法的完整性证明。本轮查询具体数值列表时返回浏览器检查页，
所以 **没有下载并认证实际根表字节，也没有用记忆中的小数代替证书**。

- https://www.lmfdb.org/zeros/zeta/Source
- https://www.lmfdb.org/zeros/zeta/Completeness
- https://www.lmfdb.org/zeros/zeta/Reliability

`RootBox` 只存放候选矩形；`prefix_structure()` 只检验上下界、上半平面、
镜像重数、重复/相交矩形和高度截断。返回的 `actual_zeros_verified` 与
`completeness_verified` 固定为 false。正确的 JSON 形状不是正确的根证书。
`conditional_prefix_interval()` 对矩形做精确有理外包，但明确以根区间真值为前提。

## 7. 有理 log 包络与测试

对 1<=y<=2，z=(y-1)/(y+1) 属于 [0,1/3]。取 n 项，有

$$
2\sum_{j=0}^{n-1}\frac{z^{2j+1}}{2j+1}
\le\log y\le
2\sum_{j=0}^{n-1}\frac{z^{2j+1}}{2j+1}
+\frac{2z^{2n+1}}{(2n+1)(1-z^2)}.
$$

尾界来自正项级数及分母 2j+1>=2n+1。对一般 T>=1 做精确二进制约化，
加上相应倍数的 log(2) 包络。程序不使用浮点 log 来生成上界。

```bash
(ulimit -v 524288; ulimit -t 20; ulimit -f 256; timeout 30s python3 scripts/test_xi_strip.py)
(ulimit -v 524288; ulimit -t 20; timeout 30s python3 scripts/test_hht_lean_runner.py)
python3 scripts/check_hht_lean.py
```

本轮前两组分别执行通过 22 项与 6 项。第二组仅测试 Lean 输出审计解析器，
**不运行 Lean**；第三条在本机实际返回 BLOCKED（缺少 Lean/lake）。
算术测试含 75 个映射恒等式点、54 个配方恒等式点、48 个多项式负界点、
36 个非退化根矩形样本、条件余量、反向误用与错误输入拒绝。
有限回归不替代第 1–5 节的全称证明。

## 8. 下一义务

1. 在固定工具链上真正编译 HHTCertificates.lean；消除编译问题并检查全部依赖报告。
2. 取得并锁定实际根表、严格误差和完整性证据；不能只填写 `verified=true`。
3. 把多项式虚部估计、可求和性与全域计数输入接入 Lean；当前 12 个切片没有覆盖这些步骤。
4. 研究维数增长时前缀最小特征值/Schur 余量是否能压住 E_d(T)。这才关系到全维数结论；
   固定二阶正定不是 RH 证明。

其他引用：NIST DLMF §§25.4, 25.10（ξ 定义、反射与临界带对称）：
https://dlmf.nist.gov/25.4 ，https://dlmf.nist.gov/25.10 。
所有来源为显式数学输入，不因被引用就成为本仓内核证据。
