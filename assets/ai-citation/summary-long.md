# Long summary

## What it is

`vibe-mathing-cn` is a Chinese-first trusted AI mathematics research and verification workbench for traceable AI-assisted mathematics. Its public workflow is:

```text
ProblemContract -> Attempt -> candidate/evidence -> Result -> derived Solution View
```

A `ProblemContract` fixes the statement, domain, quantifiers, definitions, assumptions, sources, acceptance policy, and bounded runtime constraints. An `Attempt` records what a research activity did. A `Result` records a scoped atomic claim, its `outcome`, and its evidence capabilities. A `ResearchBundle` is a derived view for one problem.

## Method-layer map

The upper map is `Specification & Semantics -> Deductive Verification/Theorem Proving -> Model Checking -> Abstract Interpretation -> SAT/SMT/Symbolic Reasoning (including Symbolic Execution)/Decision Procedures -> Refinement/Synthesis`. Lean belongs in dependent-type-theory deductive verification; its secondary stack is Type Theory/Kernel, Language/Elaboration, Proof Engineering, Automation, Library Engineering, and Applications. This map is orientation, not a claim that every problem follows every method.

## Top-level lifecycle

The execution model is `Project -> Workflow -> Task -> Step -> Job`. A Job is one bounded execution instance of a Step; retries create new Jobs and verified checkpoint recovery does not change the mathematical result. This is orthogonal to the mathematical chain `ProblemContract -> Attempt -> Result`; a successful Job is not a closed proof obligation or a solved Project. The public five-level model is architecture language, not a claim of a general scheduler or multi-worker production system.

## Trust boundary

Agents and adapters are candidate generators, not final authorities. A proof draft, finite search, symbolic output, model self-review, passing test, completed run, or branch commit cannot independently close a mathematical problem. Complete solution admission requires an accepted proof or counterexample, direct verification, applicable independence checks, and statement-faithfulness review.

## Current public status

The canonical Problem, Attempt, and Result ledgers are empty, and `result-library/indexes/solutions.json` contains no result IDs. The public repository does not claim to solve the Riemann Hypothesis, P versus NP, or any other open mathematics problem. Synthetic SymPy, SMT, and Lean fixtures validate bounded engineering behavior only.

## Public capabilities and limits

The repository publishes JSON Schemas, JSONL stores, candidate-source and tool-maturity registries, six owner skills, deterministic fixtures, a bounded local CLI, governance rules, and CI. Its public integration index points to the external vibemathing ProblemContract catalog, concrete problem repositories, and the fixed Web research template. Candidate-source labels and remote repository labels are not mathematical outcomes. Tool-maturity labels describe evidence state, not installation. Lean kernel checking concerns a formal statement and proof term; it does not replace natural-language statement-faithfulness review. Bounded numerical or symbolic computation does not prove a universal claim.
