# HHT-002：共轭零点计数，以及任意移位的低阶检查盲区

## 本轮状态和来源定位

本文件接续 HHT-001，是公开合成数学样例的证明草稿与精确回归测试。
不写入 canonical Problem / Attempt / Result / Solution，不是 RH 证明。

**先纠正新颖性预期：有限谱惯性公式属于经典 Hermite 理论的直接应用，不是本项目发现的新定理。**
本轮的增量是明确移位与重数、实现精确惯性计算，并把这个工具用于构造
“全部低阶、任意移位检查通过，但仍有任意多个负方向”的反例族。
后一构造给出自包含推导，但没有完成全面文献查重，不宣称首创。

已核对的原始论文（2026-09-08，读取 HTML，不复制论文全文）：

- M. B. Nathanson, *The Hermite-Sylvester criterion for real-rooted polynomials*,
  arXiv:1911.01745v1 (2019), Lemmas 1–2 / Theorem 1：实插值与非实根的负二次型。
  https://arxiv.org/html/1911.01745v1
- T. Ayyildiz Akoglu and A. Szanto, *Certified Hermite Matrices from Approximate Roots*,
  arXiv:2110.10313v1 (2021), Definitions 2.1–2.3, Theorem 2.7 / Remark 2.8：
  加权 Hermite 矩阵、实根符号计数、精确签名计算。这里取权多项式 g(x)=x^(k+1)。
  https://arxiv.org/html/2110.10313v1
- C. Berg and R. Szwarc, *A determinant characterization of moment sequences with finitely many mass-points*,
  arXiv:1405.7267v1 (2014), Introduction / Remark 1.2：行列式符号与半正定不能混用。
  本文件的具体反例不同，不把该论文列作本构造的首创性结论。
  https://arxiv.org/html/1405.7267v1

## 1. 冻结定义

令 Lambda 是有限个**互异、非零**复数 lambda 的集合，且对共轭封闭。
每个节点赋正整数重数 m_lambda，共轭节点重数相同。写

$$
G(z)=\prod_{\lambda\in\Lambda}(1+z/\lambda)^{m_\lambda},\qquad
\frac{G'(z)}{G(z)}=\sum_{n\ge0}(-1)^n\mu_nz^n,
\qquad \mu_n=\sum_{\lambda\in\Lambda}m_\lambda\lambda^{-n-1}.
$$

展开范围为 |z|<min|lambda|。G 的零点为 -lambda。
设 N=|Lambda|=r+2q，r 是互异实节点数，q 是互异非实共轭对数；
**N 不是计入重数后的多项式次数**。定义

$$
H_{d,k}=(\mu_{k+i+j})_{0\le i,j<d},\qquad d\ge1,\ k\ge0.
$$

所有 d,k 均为整数。惯性记为 In(A)=(正特征值个数,负特征值个数,零特征值个数)。
本节及下一节不要求 Re(lambda)>0；只有涉及热迹积分时才增加正实部假设。

## 2. 结论 A：满秩及更大尺寸的惯性（经典理论应用）

对任意 k>=0、d>=N，令

$$
p_k=\#\{\lambda\in\Lambda\cap\mathbb R:\lambda^{-k-1}>0\},\qquad
n_k=\#\{\lambda\in\Lambda\cap\mathbb R:\lambda^{-k-1}<0\}.
$$

则

$$
\boxed{\operatorname{In}(H_{d,k})=(p_k+q,n_k+q,d-N).}
$$

若所有实 lambda>0，则

$$
\boxed{\operatorname{In}(H_{d,k})=(r+q,q,d-N).}
$$

实负节点在 k 为偶数时贡献负方向，在 k 为奇数时贡献正方向。
每个非实共轭对始终贡献一个正方向和一个负方向；正重数只改变尺度，不增加秩。
该等式**不能**用于 d<N。

### 证明

令 u=1/lambda，p(x)=sum_{j=0}^{d-1}v_j x^j，v 为实向量。有限交换求和给出

$$
v^TH_{d,k}v=\sum_\lambda m_\lambda u^{k+1}p(u)^2.
$$

在实节点处，这是符号为 sign(u^(k+1)) 的一个实平方项。
对一对非实共轭节点，写 w=m_lambda u^(k+1)，p(u)=X+iY，配对贡献为

$$
2\operatorname{Re}(w(X+iY)^2)
=2\begin{pmatrix}X&Y\end{pmatrix}
\begin{pmatrix}\operatorname{Re}w&-\operatorname{Im}w\\
-\operatorname{Im}w&-\operatorname{Re}w\end{pmatrix}
\begin{pmatrix}X\\Y\end{pmatrix}.
$$

该实对称块的特征值为 +2|w|、-2|w|，都非零。
当 d=N 时，把 p 的系数映射为所有实节点值和非实节点值的实部/虚部，
得到一个 N 维实线性映射。若它的像为零，p 在 N 个互异节点取零，
而 deg(p)<N，所以 p=0。因此此映射可逆，原矩阵与上述块对角矩阵实合同。
惯性由各块相加即得。

当 d>N 时，前 N 个单项式已经使同一求值映射满射，核维数 d-N；
选取核与补空间的基，得到相同的非零块加 d-N 个零方向。证毕。

**直接后果：** 若实节点全正，则 sign(det H_{N,k})=(-1)^q。
因此非实共轭对数为正偶数时，满秩行列式为正，矩阵却仍不定。
这不否定 Sylvester 判据；它说明不能只检查一个满秩行列式。

## 3. 可直接核查的两个负方向反例

取 Lambda={1,3+i,3-i,4+i,4-i}，重数全为 1。则

$$
G(z)=(1+z)(1+3z/5+z^2/10)(1+8z/17+z^2/17),
$$

$$
\Theta(t)=e^{-t}+2(e^{-3t}+e^{-4t})\cos t>0\quad(t>0).
$$

严格正性证明：0<t<=1 时 cos t>0；t>=1 时
Theta(t)>=e^(-t)[1-2e^(-2t)-2e^(-3t)]>e^(-t)/4，使用 e>2。

尽管如此，对所有 k>=0，

$$
\operatorname{In}(H_{5,k})=(3,2,0),\qquad
\det H_{5,k}=\frac1{118587876497000\cdot170^k}>0.
$$

行列式常数可用精确有理消元核对，移位因子来自所有倒数节点之积 1/170。
甚至不必计算特征值：取整数向量

$$
v=(44,-411,1235,-1123,255)^T,
\qquad \boxed{v^TH_{5,0}v=-375/16<0.}
$$

相应多项式为 p(x)=(x-1)(17x^2-8x+1)(15x-44)。
它在 1、1/(4+i)、1/(4-i) 上取零，在 1/(3-i) 上取 25i/4，
在共轭点取 -25i/4，因此二次型精确等于
2 Re[(3+i)/10 * (25i/4)^2]=-375/16。

## 4. 结论 B：固定阶数、所有移位仍可能看不到非实零点

**量词不可交换：** 对每一组给定的正整数 L、q，存在一个具有 q 对非实零点的
实多项式 G，使得以下三件事同时成立：

$$
\Theta(t)>0\quad(\forall t>0),
$$

$$
H_{d,k}\succ0\quad(1\le d\le L,\ \forall k\ge0),
$$

$$
\operatorname{In}(H_{L+2q,k})=(L+q,q,0)\quad(\forall k\ge0).
$$

不是对一个固定 G 声称所有维数都正定；G 随 L、q 改变。
此结论比“有限个移位检查不够”更强：这里全部非负整数移位都通过。

### 显式构造与充分条件

取实节点 a_i=i (1<=i<=L)，以及复节点 B+j+i、B+j-i (0<=j<q)，重数全 1，
其中 B 是稍后选定的大正整数。实节点对应的 L 阶基准矩阵为

$$
A=(\sum_{s=1}^L s^{-1-i-j})_{0\le i,j<L}\succ0.
$$

其正定性来自互异正倒数节点的可逆 Vandermonde 分解。设

$$
\ell=\frac{\det A}{(\operatorname{tr}A)^{L-1}}>0,\qquad
\epsilon_B=\frac{2q}{B}\sum_{j=0}^{L-1}B^{-2j}.
$$

取 B 满足

$$
\boxed{B\ge\max(L,2q+2),\qquad \epsilon_B<\ell.}
$$

这是可计算的有理充分条件，不主张是最小 B。由于 epsilon_B->0，这样的整数 B 必定存在。
L=1 时分母指数为零，公式仍有效。

### 对所有移位的统一正定下界

A 的每个特征值至多 tr(A)，所以 lambda_min(A)>=ell。
任意实系数多项式 p，deg(p)<d<=L，实节点部分的二次型满足

$$
Q_{\rm real,k}(p)=\sum_{s=1}^L s^{-k-1}p(1/s)^2
\ge L^{-k}\ell\|v\|_2^2.
$$

这是因为 s^(-k)>=(1/L)^k；d<L 时将系数向量补零。
每个复倒数节点 u 满足 |u|<=1/B<=1/L，且 Cauchy–Schwarz 给出

$$
|p(u)|^2\le\|v\|_2^2\sum_{j=0}^{L-1}|u|^{2j}.
$$

q 对复节点的总贡献 E 因而满足

$$
|v^TE_{d,k}v|\le
2\sum_{\text{one per pair}} |u|^{k+1}|p(u)|^2
\le L^{-k}\epsilon_B\|v\|_2^2.
$$

两式结合得到真正量化所有 k 的下界

$$
\boxed{H_{d,k}\succeq L^{-k}(\ell-\epsilon_B)I_d\succ0
\quad(1\le d\le L,\ k\ge0).}
$$

### 热迹及更高维数

本构造的热迹为

$$
\Theta(t)=\sum_{s=1}^L e^{-st}+2\cos t\sum_{j=0}^{q-1}e^{-(B+j)t}.
$$

0<t<=1 时每项为正；t>=1 时
Theta(t)>=e^(-t)[1-2q e^(-(B-1)t)]>0，
因为 B>=2q+2 保证 e^(B-1)>2q。结论 A 给出高维惯性，完成构造。

此外，所有维数、所有移位的**阶乘加权**矩阵仍正定：

$$
\mathcal B_{d,k}=((k+i+j)!\mu_{k+i+j})_{i,j},\qquad
v^T\mathcal B_{d,k}v=\int_0^\infty t^kp(t)^2\Theta(t)\,dt>0.
$$

这里只有有限谱且所有 Re(lambda)>0，故积分绝对收敛，无无限换序缺口。

## 5. 一个完全有理的低阶盲区证书

取 L=2、q=2、B=128。节点为 1、2、128±i、129±i。

$$
A=\begin{pmatrix}3/2&5/4\\5/4&9/8\end{pmatrix},\quad
\ell=1/21,\quad \epsilon_B=16385/524288,
\quad \ell-\epsilon_B=180203/11010048>0.
$$

因此对**每一个** k>=0，H_{1,k}、H_{2,k} 都严格正定；
H_{6,k} 却有 4 个正方向、2 个负方向，且行列式为正。
这不是把测试 k=0..16 的结果外推；全称结论来自第 4 节的统一不等式。

## 6. 可复现检查与未完成项

```bash
(ulimit -v 524288; ulimit -t 20; ulimit -f 256; \
 timeout 30s python3 scripts/test_hankel_inertia.py)
```

20 项测试在本轮执行通过，包含 270 个完整惯性比较、30 个实块分解比较、
10 个谱各 17 个矩系数的双路径比较、40 个带零方向的精确合同变换测试，
以及 20 个谱/移位组合的特征多项式交叉检查。
特征多项式算法还交叉检查了上述 40 个合同变换样例。

重点覆盖：正负实节点的移位奇偶性、重数和互异节点数的区别、纯虚节点、
对角元全零时的 2x2 主元、奇异矩阵、正行列式下的显式负二次型，
以及有理的任意移位正定充分条件。计算不使用浮点特征值。

实现算法与交叉检查均由本轮研究过程编写，不等于独立审查者。
软件限制为 12 个互异节点、总次数 32、矩序列阶数 64；这些计算预算不是数学定理的限制。
输入和输出矩阵均使用有界精确有理数；外层执行还有墙钟、CPU、内存及文件大小限制。
文件无网络调用、子进程、模型调用或正式账本写入。

本轮通过的是新增测试，不冒称完整 make check、Lean 构建或独立数学审查通过。
本地完整克隆因 GitHub DNS 解析失败而未完成，发布使用 GitHub 连接器。

- [x] HHT-002 精确命题与自包含推导。
- [x] 与经典 Hermite 理论的关系及新颖性边界。
- [x] 精确测试及显式反例证书。
- [ ] 独立数学审查及 Lean 形式化。
- [ ] 对任意移位构造的全面文献查重。

## 7. 对 RH 主线的具体约束与下一任务

本轮没有研究真实 xi 的无限零点谱。固定阶数即使覆盖全部移位，仍不能代替全阶正定。
要排除本构造，必须使用目标函数额外的解析/算术结构，或者提供对矩阵阶数有效的统一估计。
有限谱的 Lagrange 插值也不能不加控制地拿去消掉无限多个节点。

**HHT-003（尚未执行）：** 对一个已冻结的实系数测试多项式 p 和移位 k，
建立可复核的无限谱尾项界。若截断二次型为 -eta<0，需要真正证明

$$
\sum_{\lambda\ \text{outside cutoff}}m_\lambda
|\lambda|^{-k-1}|p(1/\lambda)|^2<\eta
$$

并核查绝对收敛，才可把该负证书转移到完整谱；截断正性不能这样反向外推。
下一轮先处理这个有界、明确的证明义务，不把本次有限谱结论改写成 RH 进展声明。
