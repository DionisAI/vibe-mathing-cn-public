# vibe-mathing-cn：可信数学研究与验证系统

> **非可信候选生成器 + 受信验证链：从问题空间构造候选，经验证后派生解空间。**

`vibe-mathing-cn` 把数学问题、文献、推导、计算、证明与形式化检查组织成可追溯的研究系统。生成器可以不完备、出错或不终止；只有满足明确验收谓词的候选结果，才能出现在解库派生视图中。

## 项目定位

本项目不是承诺对任意输入都返回答案的“通用数学问题求解器”，而是：

> **面向广泛数学问题的通用、可信、可审计研究与验证系统。**

“通用”表示系统采用统一的 Problem、Attempt、Result 和证据契约组织不同数学领域的研究，不表示搜索完备、必然终止或所有问题都可判定。系统保证的不是“总能求解”，而是：

1. 问题定义清楚后才进入研究；
2. 候选、失败和局部成果均可追溯；
3. Agent 不能把自己的候选直接宣布为答案；
4. 只有完整证明或反例通过验证后才能闭合问题；
5. 没有充分证据时，系统必须诚实输出 `open`。

## 系统输入与输出

系统的逻辑接口是：

\[
F:\mathrm{ProblemContract}\rightarrow\mathrm{ResearchBundle}
\]

而不是保证存在解的 `Problem → Solution` 函数。

### 输入：Problem Contract

输入不是一句未经约束的自然语言，而是一个版本化、可验证的数学问题契约。它至少需要确定：

```text
ProblemContract {
  problem_id       // 稳定标识
  statement        // 精确陈述及版本
  domain           // 对象、定义域和量词边界
  definitions      // 术语、符号和等价定义
  assumptions      // 假设、允许公理和前置结果
  sources          // 来源、已有文献和检索时间
  acceptance       // 什么证明或反例能够闭合问题
  constraints      // 可用工具、时间和资源边界
}
```

当前机器真相源使用 canonical `Problem` schema 保存稳定标识、陈述版本、MSC 分类、来源和状态；定义域、量词、定义与假设在进入自动研究前必须被规范化进陈述及其引用上下文。未来扩展字段时仍以 Problem Contract 为唯一输入语义，不另建第二套问题模型。

### 输出：Research Bundle

输出不是一段孤立“答案”，而是一个带证据、可恢复、可复核的研究结果包：

```text
ResearchBundle {
  problem          // 本次实际研究的 Problem 版本
  attempts[]       // 做过什么、使用什么方法、为何成功或失败
  results[]        // 证明、反例、局部结论、计算证据或失败路径
  evidence[]       // 计算记录、审查记录、证明证书和内核输出
  disposition      // solved | refuted | open
  solution_view[]  // 当前通过完整验证的证明或反例
}
```

`ResearchBundle` 是从 Problem / Attempt / Result、验证产物和 Solution View 聚合出的响应或导出视图，不是第四张可写表。顶层裁决定义为：

| Disposition | 严格含义 |
|:---|:---|
| `solved` | 存在与当前 Problem 忠实对应、证据仍有效且通过准入的 `proof + established` |
| `refuted` | 存在与当前 Problem 忠实对应、证据仍有效且通过准入的 `counterexample + refuted` |
| `open` | 尚无完整可信证明或反例；可以包含支持性证据、局部结果、失败路径和下一步建议 |

若同一 Problem、同一语义范围同时出现通过准入的证明和反例，系统必须把它视为契约、形式化或验证链冲突并 fail-closed，不能任选一个答案。`open` 不是失败：它表示系统准确保存了“目前真正知道什么”和“还缺什么”。

## 形式模型

设：

- \(P\)：规范化问题空间；
- \(C\)：候选结果空间；
- \(E\)：证据记录空间；
- \(D=\{\mathrm{accept},\mathrm{reject},\mathrm{undetermined}\}\)：验证判定集合。

候选生成器是多值映射：

\[
A:P\rightarrow 2^C
\]

`A` 可以返回零个或多个候选，不保证正确、完备或终止。它的输出默认不可信。

验证链对“问题—候选”对进行判定并产生证据：

\[
V:P\times C\rightarrow D\times E
\]

某个问题的解集定义为通过验证的候选子集：

\[
\operatorname{Sol}(p)=
\{c\in A(p)\mid \pi_D(V(p,c))=\mathrm{accept}\}
\]

全局解关系为：

\[
S=\{(p,c)\in P\times C\mid c\in\operatorname{Sol}(p)\}
\]

因此不能直接写 \(S=V\circ A\)：`A` 的值是候选集合，而 `V` 接受一个问题与一个具体候选，二者类型不匹配。这里发生的是“生成候选后按验证谓词筛选”，不是普通函数复合。

## 信任边界

```text
Problem ──> A（非可信生成器）──> Candidate
   │                                  │
   └────────────> V（受信验证链）<────┘
                                      │
                          accept ─────┴─────> Solution View
                          reject/undetermined ─> Attempt / Result Ledger
```

核心约束：

1. Agent 只能创建 `Attempt` 和候选 `Result`，不能直接写入解库。
2. 信任建立在验证规则、证据、独立性和验证器的可信计算基上，不建立在 Agent 自报状态上。
3. `solutions.json` 是验证通过结果的派生视图，不是第二个可写真相源。
4. 生成器与验证器可以使用同一模型家族，但不能让同一次生成上下文的自评冒充独立验证。

## 可判定性边界

“生成难、验证易”只在限定条件下成立：

- 候选搜索通常没有完备性或终止保证；在固定形式系统中，证明搜索可表现为半判定过程：找到证书即可停止，找不到时可能持续搜索。
- 对固定语法、固定公理和有限证明证书，proof kernel 的验收检查是可终止、可重复的判定过程。
- 一般自然语言数学结论的真实性不存在一个通用自动判定器；人工审查也不是可判定算法。
- 所以自动晋升门只采用有明确输入、可信计算基、终止条件和失败语义的检查器；无法机械判定的部分必须保留人工审查或 `undetermined`。

## 状态模型：结果 × 证据

项目不再把 `refuted`、`numeric`、`human`、`kernel` 混在一条状态链中。

结果轴 `outcome`：

| Outcome | 含义 |
|:---|:---|
| `undetermined` | 尚不能判定原声明成立或不成立 |
| `supported` | 有支持性证据，但不足以闭合原声明 |
| `established` | 原声明已由可接受证明闭合 |
| `refuted` | 原声明已由可接受反例或否证闭合 |
| `inconclusive` | 本次尝试结束，但没有形成支持或否证结论 |
| `withdrawn` | 声明、范围或证据已失效，不再作为当前结果 |

证据轴是能力集合，而不是 `numeric < symbolic < human < kernel` 的单一全序：

```text
numeric-check
symbolic-check
human-review
kernel-check
counterexample-check
axiom-escape-audit
statement-faithfulness
prior-art-review
```

数值检查与符号检查可能互不包含；人工审查可以检查语义和上下文，kernel 只检查形式化陈述及证明项。Lean 官方也明确区分“定理是否有有效证明”和“定理陈述是什么意思”。因此证据按已验证能力的集合包含关系形成偏序，不能用一个数字等级替代。

证据账本只追加新记录或失效记录，不覆盖历史；但“当前结论”必须由有效证据重新派生，发现错误时允许从 `established` 变为 `withdrawn` 或 `refuted`。单纯规定“状态只升不降”会固化错误结论。

## 解库准入

完整解只允许两种闭合结果：

- `proof + established`：证明原声明成立；
- `counterexample + refuted`：证明原声明不成立。

进入解库还必须同时满足：

1. 独立的直接证明/反例审查存在，或形式化证明同时具备内核检查与公理/逃逸审计；
2. 验证判定为 `accept`；
3. 验证独立性满足项目策略；
4. canonical Problem 与被验证声明之间的忠实性审计通过；
5. 当前不存在使这些证据失效的记录。

有限数值证据、符号特例、局部结果、条件结果、证明草稿与失败路径可以进入成果账本，但不能进入完整解视图。准入条件不是含糊的 `evidence >= human`：human review 与 kernel check 的保证不同，完整形式化证明仍需要 statement faithfulness。

## `/vibe-mathing` 的职责

`/vibe-mathing` 是候选生成和研究编排入口，目标职责是：

1. 选择并固定一个 canonical Problem；
2. 检索文献、定义、已知定理与已有结果；
3. 将问题拆成可验证子问题和证明义务；
4. 调用 discovery、derivation、computation、proof 或 formalization；
5. 创建可追溯 `Attempt` 和候选 `Result`；
6. 将候选提交验证链，不自行改变解库视图。

仓库已提供单机可恢复 CLI；开放式研究仍由 `vibe-mathing-router` 和五个数学 owner skills 分阶段产生候选，CLI 负责确定性 adapter 的受控写入、恢复、取消与验证。

## 与 Lean / AlphaProof 的关系

本项目采用与形式化数学系统相同的基本分工：高能力、非可信的搜索过程生成候选，较小的可信验证基础检查证明证书。Lean 的内核负责检查证明项；AlphaProof 也采用“生成候选并在 Lean 中证明或否证”的路径。

这只是信任结构上的同类设计，不表示当前项目具备 AlphaProof 的训练系统、搜索能力或验证成熟度。自然语言问题到形式化陈述的映射仍是独立的语义忠实性风险。

参考：[Lean Proof Validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/)、[Google DeepMind AlphaProof](https://deepmind.google/blog/ai-solves-imo-problems-at-silver-medal-level/)。

## 最简框架

项目当前采用三个核心空间：

```text
vibe-mathing-cn/
├── problem-library/   # 问题空间：研究什么
├── research/          # 研究空间：做过什么、得到什么证据
└── result-library/    # 成果空间：验证后真正知道了什么
    └── indexes/solutions.json # 解库视图：完整证明或反例
```

对应三个核心对象：

| 对象 | 回答的问题 | 最小内容 |
|:---|:---|:---|
| `Problem` | 研究什么？ | 精确陈述、版本、来源、分类、开放状态 |
| `Attempt` | 做过什么？ | 目标、方法、输入、过程、工具、产物、失败条件 |
| `Result` | 真正知道了什么？ | 原子主张、证据、适用范围、验证和结论等级 |

工程上就是 `problems / attempts / results` 三张逻辑表及跨表完整性约束；当前实现使用可审阅、可迁移的 JSONL 真相源，不提前引入数据库。Result 与 Attempt 必须引用同一个 Problem，独立证据的 verifier 不能等于 Attempt 的 generator。

一个问题可以对应多次尝试、多个局部成果和多个不同证明。`indexes/solutions.json` 应从通过验证的 `Result` 派生，不应成为可以绕过验证直接写入的第二套真相源。

> **当前仓库已经建立空的 canonical Problem、Attempt、Result 真相源和机器晋升门；它们证明结构与边界已经存在，不代表已经产生数学成果。**

## 当前能力

| 能力 | 状态 | 真实后端或边界 |
|:---|:---|:---|
| 问题来源库 | 可用 | Wikipedia MediaWiki API + UnsolvedMath 公开目录快照 |
| 数学电子书库 | 可用 | Work → Edition → File 目录 + MSC2020 分类 + 文件摘要 |
| 文献与定义检索 | 可用 | Codex Web/SearXNG；arXiv、Semantic Scholar、Crossref、OpenAlex 可降级 |
| 公式推导 | 可用 | 结构化推导契约；不冒充证明 |
| 符号计算 | 可用 | Python 3.12 + SymPy 1.14 |
| 数值检查 | 可用 | NumPy、SciPy、mpmath |
| 自然语言证明 | 可用 | 证明义务、依赖图与反例审计契约 |
| LaTeX 构建 | 可用 | latexmk、pdfLaTeX、XeLaTeX、LuaLaTeX、BibTeX、Biber |
| `/vibe-mathing` 单机入口 | 可用 | `run/resume/verify/status/cancel` + checkpoint + 有界状态机 |
| 研究空间与成果空间 | 可用 | Problem/Attempt/Result schema + `flock/WAL/os.replace` 唯一 writer |
| 解库视图 | 可用 | 真实 artifact/receipt/registry 校验后派生；当前业务记录为空 |
| Lean 形式化验证 | 固定 fixture | Lean/Mathlib v4.33.0；kernel + escape/axiom + faithfulness 三证据 |

## Active Skills

当前项目级 skills 位于 `.codex/skills/`：

| Skill | 当前职责 | 停止条件 |
|:---|:---|:---|
| `vibe-mathing-router` | 判断当前研究瓶颈，只选择一个 owner | 已明确唯一下一步 |
| `math-discovery` | 定义问题、检索文献、建立来源账本 | 问题和证据边界已经清楚 |
| `math-derivation` | 固定对象、假设与记号，建立推导链 | 推导一致或暴露出明确缺口 |
| `math-computation` | 符号/数值检查和有限反例搜索 | 产生可重跑证据或达到停止条件 |
| `math-proof` | 拆分证明义务、攻击反例、形成证明草稿 | 义务闭合或明确阻塞点 |
| `math-formalization` | Lean 预检、形式化切片和内核验证 | 真正编译通过或 fail-closed |

当前路由关系：

```text
vibe-mathing-router
├── math-discovery
├── math-derivation
├── math-computation
├── math-proof
└── math-formalization
```

每次只选择当前最需要的一个主 skill，避免把检索、计算、证明和形式化同时启动后互相掩盖缺口。

## 快速开始

### 查询问题库

```bash
python3 scripts/query_problem_library.py --text "Riemann" --limit 10
python3 scripts/query_problem_library.py --source unsolvedmath --category "Number Theory" --limit 20
```

`problem-library/` 当前保存的是可追溯的**来源记录**。同名记录不自动等于同一个数学问题，也不代表问题陈述已经足够完整。

公开仓库不会分发 UnsolvedMath 未明确授权的派生目录内容或原始网页；首次克隆后需要运行抓取器在本地重建来源库。canonical Problem、schema 和抓取代码可以版本化。

明确刷新公开来源快照：

```bash
python3 scripts/fetch_problem_library.py --refresh
```

默认重建会复用本地原始缓存；只有 `--refresh` 会重新访问来源网站。

### 使用电子书库

`literature/` 使用 Work → Edition → File 三层模型。电子书二进制存放在被 Git 忽略的 `literature/files/`，可版本化目录只保存书目、分类、关系和文件摘要。

当前馆藏与分类见 [`literature/README.md`](literature/README.md)。

### 运行项目检查

CI 与本地共用同一个可移植入口：

```bash
make check
```

确定性反例问题的单机闭环入口：

```bash
python3 scripts/vibe_mathing_cli.py register-problem \
  --file fixtures/sympy-counterexample/problem.json
python3 scripts/vibe_mathing_cli.py run \
  --problem-id problem:sympy-counterexample-fixture
python3 scripts/vibe_mathing_cli.py status --run-id run:<stable-id>
python3 scripts/vibe_mathing_cli.py resume --run-id run:<stable-id>
python3 scripts/vibe_mathing_cli.py verify --run-id run:<stable-id>
python3 scripts/vibe_mathing_cli.py cancel --run-id run:<stable-id>
```

CLI 只接受已注册 adapter 和 canonical Problem，不提供任意命令执行。真实开放问题仍先由 owner skills 生成候选；未经注册 verifier 的证据不会晋升。

它不依赖被 Git 忽略的上游缓存、原始网页或电子书二进制。拥有完整本地材料时运行加强门禁：

```bash
make check-full
```

首次或需要重新拉取固定版本的上游供应链缓存时：

```bash
python3 scripts/sync_supply_chain.py
```

## 项目结构

```text
vibe-mathing-cn/
├── README.md                  # 项目思想、能力、入口与路线图
├── AGENTS.md                  # Agent 操作规则与数学真实性边界
├── CHANGELOG.md               # 项目变更记录
├── problem-library/           # 公开问题目录的快照、统一记录与索引
├── literature/                # 数学电子书书目、分类和本地文件
├── research/                  # 一次次研究运行及其机器契约
├── result-library/            # 候选/验证成果与派生解库索引
├── governance/                # 项目操作模型、标准、ADR、Gate 与任务证据
├── .github/workflows/         # GitHub Actions 可移植质量门
├── .codex/skills/             # 当前项目 active skills
├── scripts/                   # 供应链、结构、问题库、文献库和数学验证脚本
├── fixtures/                  # 固定 Lean/Mathlib 等无业务数据验证样例
└── vendor/
    ├── sources.lock.json      # 上游来源、固定 commit、许可和导入映射
    ├── snapshots/             # 本机或无远端来源的精简审计快照
    └── upstream/              # 可重建上游 Git 缓存，不参与 active skill 发现
```

详细的数据与维护边界：

- [`problem-library/README.md`](problem-library/README.md)：来源范围、许可、重建和查询方法；
- [`literature/README.md`](literature/README.md)：电子书分类和 Work/Edition/File 模型；
- [`research/README.md`](research/README.md)：Attempt 契约与研究过程边界；
- [`result-library/README.md`](result-library/README.md)：Result 晋升与解库派生规则；
- [`governance/README.md`](governance/README.md)：项目治理和上下文入口；
- [`scripts/README.md`](scripts/README.md)：项目脚本职责；
- [`vendor/README.md`](vendor/README.md)：研究 skill 供应链与审计边界。

## 项目原则

1. **先定义问题，再寻找答案**：陈述、量词、定义域和版本不清时，不进入求解。
2. **先尝试证伪，再尝试证明**：反例能够更快淘汰错误命题和隐藏假设。
3. **过程必须可追溯**：来源、输入、工具版本、命令、输出与失败条件都要留下记录。
4. **证据不得越权**：有限计算不是一般证明，自然语言证明不是内核验证。
5. **生成与验证分离**：产生候选结果的 Agent 不能只靠自我评价完成晋升。
6. **失败也是研究资产**：保留可复用的失败原因，但不能把失败包装成成果。
7. **成熟能力优先**：优先使用数学数据库、计算库、文献标准和 proof assistant，自研只负责连接、编排和项目特有规则。

## 下一阶段

基础生产闭环完成后，下一阶段不再扩建第二套 runtime，而是校准研究质量：

1. 用一个公开、非开放的自然语言定理校准 Problem Contract → Lean statement 的人工忠实性审查；
2. 为外部领域专家或平台 reviewer 接入不可由实现者自签的 attestation；
3. 在真实开放问题上只运行有限证据路径，验证系统持续保持 `supported/undetermined` 而不误关问题；
4. 当 JSONL 写入达到可测瓶颈时，再依据 benchmark 迁移 SQLite/PostgreSQL。

验收标准很简单：

> **如果开放问题的有限实验结果会被系统误写成完整解，框架就是失败的。**

## 当前边界

- 本项目不是自动解决世界上全部未解数学问题的承诺。
- 问题库的“完整”只表示抓取批次覆盖来源目录，不表示覆盖全部数学问题。
- UnsolvedMath 未发现公开许可声明；这里只保存公开目录事实字段和短摘要，不镜像详情正文。
- 只有固定 fixture 和真实成功 receipt 能声明 `kernel_check`；自然语言到 Lean 的语义仍需独立 faithfulness 审查。
- 当前解库索引为空；只有 `Result` 满足证明/反例、直接证据、独立验证与陈述忠实性条件后才允许进入。
- 100% 就绪度仅指本仓库定义的单机、单 Agent、可恢复、可审计生产闭环；不包含分布式高可用、外部 reviewer 实际签发或保证解决任意开放问题。

---

> **问题库是起点，解库是终点，Agent 是探索者，验证是守门员。**
