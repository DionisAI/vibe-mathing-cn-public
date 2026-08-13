#!/usr/bin/env bash
# 做什么：运行不依赖本地缓存和电子书二进制的项目统一质量门。
# 怎么运行：bash scripts/check.sh
# 需要什么：Python 3、requirements.txt；任一检查失败即非零退出。

set -euo pipefail

python3 scripts/validate_project.py
python3 scripts/smoke_math.py
python3 scripts/validate_portable_problem_library.py
python3 scripts/validate_portable_literature.py
python3 scripts/validate_research_spaces.py
python3 scripts/test_research_spaces.py
python3 governance/tools/validate_governance_package.py --project-root . --strict
python3 governance/tools/governance_health_report.py --project-root . --strict
