#!/usr/bin/env python3
"""Compile finite-jet lemmas with the existing pinned Lean project.

Reuses, without modifying, the prior compiler resource limit and axiom policy.
This runner is not a mathematical Result admission tool.
"""
from __future__ import annotations
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT/'fixtures'/'lean-proof'
SOURCE = WORK/'HHTFiniteJet.lean'
MAX_OUTPUT = 1_048_576


def main() -> int:
    """Only an actual successful compiler run and complete audits can pass."""
    if shutil.which('lake') is None:
        print('BLOCKED: lake/Lean is not installed; no kernel verification occurred.',file=sys.stderr)
        return 2
    from check_hht_lean import audit_output, limit_child
    source=SOURCE.read_text(encoding='utf-8')
    if re.search(r'\b(sorry|admit|unsafe|native_decide|axiom|run_elab|run_cmd)\b|#eval|Lean\.ofReduceBool',source):
        raise ValueError('prohibited proof escape or side-effect command')
    names=['HHTFiniteJet.'+n for n in re.findall(r'^theorem\s+(\w+)',source,re.M)]
    if len(names)!=6 or len(set(names))!=6:
        raise ValueError('unexpected theorem roster')
    if (WORK/'lean-toolchain').read_text().strip()!='leanprover/lean4:v4.33.0':
        raise ValueError('toolchain drift')
    env={k:v for k,v in os.environ.items() if k in
         {'PATH','HOME','LANG','LC_ALL','TMPDIR','LEAN_PATH','ELAN_HOME'}}
    version=subprocess.run(['lake','env','lean','--version'],cwd=WORK,env=env,
        capture_output=True,text=True,timeout=30,check=True)
    if not re.search(r'Lean \(version 4\.33\.0(?:,|\s|\))',version.stdout):
        raise ValueError('unexpected compiler version')
    print(version.stdout.strip())
    with tempfile.TemporaryFile() as output:
        result=subprocess.run(['lake','env','lean','-j1','-DwarningAsError=true',SOURCE.name],
            cwd=WORK,env=env,stdout=output,stderr=subprocess.STDOUT,timeout=240,
            check=False,preexec_fn=limit_child)
        output.seek(0)
        data=output.read(MAX_OUTPUT+1)
    if len(data)>MAX_OUTPUT:
        raise ValueError('compiler output budget exceeded')
    text=data.decode('utf-8',errors='strict')
    print(text,end='')
    if result.returncode:
        raise ValueError(f'Lean compile failed: {result.returncode}')
    audit_output(text,names)
    print('FINITE_JET_LEAN_PASS: 6 algebraic lemmas; no full root-count/product formalization or RH.')
    return 0


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr)
        raise SystemExit(1) from exc
