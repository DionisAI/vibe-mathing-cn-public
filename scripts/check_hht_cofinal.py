#!/usr/bin/env python3
"""Compile the locked four-phase and cofinal statements and audit every dependency."""
from __future__ import annotations
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from check_hht_lean import audit_output,limit_child,MAX_OUTPUT

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'fixtures'/'lean-proof'
SOURCE=WORK/'HHTCofinal.lean'


def main():
    """Fail closed on tool absence, drift, proof escapes, compiler errors or missing audits."""
    if shutil.which('lake') is None:
        print('BLOCKED: Lean/lake absent; no kernel verification.',file=sys.stderr)
        return 2
    s=SOURCE.read_text(encoding='utf-8')
    if re.search(r'\b(sorry|admit|unsafe|native_decide|axiom|run_elab|run_cmd)\b|#eval|Lean\.ofReduceBool',s):
        raise ValueError('prohibited proof escape')
    names=['HHTCofinal.'+n for n in re.findall(r'^theorem\s+(\w+)',s,re.M)]
    if len(names)!=13 or len(set(names))!=13:raise ValueError('unexpected theorem manifest')
    if (WORK/'lean-toolchain').read_text().strip()!='leanprover/lean4:v4.33.0':
        raise ValueError('toolchain drift')
    env={k:v for k,v in os.environ.items() if k in {'PATH','HOME','LANG','LC_ALL','TMPDIR','LEAN_PATH','ELAN_HOME'}}
    v=subprocess.run(['lake','env','lean','--version'],cwd=WORK,env=env,
                     capture_output=True,text=True,timeout=30,check=True)
    if not re.search(r'Lean \(version 4\.33\.0(?:,|\s|\))',v.stdout):raise ValueError('actual toolchain drift')
    print(v.stdout.strip())
    with tempfile.TemporaryFile() as output:
        result=subprocess.run(['lake','env','lean','-j1','-DwarningAsError=true',SOURCE.name],
             cwd=WORK,env=env,stdout=output,stderr=subprocess.STDOUT,timeout=240,
             check=False,preexec_fn=limit_child)
        output.seek(0);raw=output.read(MAX_OUTPUT+1)
    if len(raw)>MAX_OUTPUT:raise ValueError('output budget exceeded')
    text=raw.decode('utf-8');print(text,end='')
    if result.returncode:raise ValueError('Lean compilation failed')
    audit_output(text,names)
    print('COFINAL_LEAN_PASS: 13 audited theorems; actual infinite-tail detection and cofinal contradiction; spectral interpolation and xi external.')
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr);raise SystemExit(1) from exc
