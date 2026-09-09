#!/usr/bin/env python3
"""Compile HHT006 and reuse the existing dependency allowlist without alteration."""
from __future__ import annotations
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from check_hht_lean import audit_output, limit_child, MAX_OUTPUT

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'fixtures'/'lean-proof'
SOURCE=WORK/'HHTRelative.lean'


def main() -> int:
    """Missing tools, compiler errors, or missing audits cannot produce success."""
    if shutil.which('lake') is None:
        print('BLOCKED: lake/Lean not installed; no kernel verification.',file=sys.stderr)
        return 2
    source=SOURCE.read_text(encoding='utf-8')
    if re.search(r'\b(sorry|admit|unsafe|native_decide|axiom|run_elab|run_cmd)\b|#eval|Lean\.ofReduceBool',source):
        raise ValueError('prohibited proof escape or side-effect command')
    names=['HHT006.'+n for n in re.findall(r'^theorem\s+(\w+)',source,re.M)]
    if not names or len(names)!=len(set(names)): raise ValueError('empty or duplicate theorem set')
    if (WORK/'lean-toolchain').read_text().strip()!='leanprover/lean4:v4.33.0':
        raise ValueError('toolchain drift')
    env={k:v for k,v in os.environ.items() if k in
         {'PATH','HOME','LANG','LC_ALL','TMPDIR','ELAN_HOME'}}
    version=subprocess.run(['lake','env','lean','--version'],cwd=WORK,env=env,
                           capture_output=True,text=True,timeout=30,check=True)
    if not re.search(r'Lean \(version 4\.33\.0(?:,|\s|\))',version.stdout):
        raise ValueError('unexpected actual Lean version')
    print(version.stdout.strip())
    with tempfile.TemporaryFile() as output:
        compiled=subprocess.run(['lake','env','lean','-j1','-DwarningAsError=true',SOURCE.name],
            cwd=WORK,env=env,stdout=output,stderr=subprocess.STDOUT,timeout=240,
            check=False,preexec_fn=limit_child)
        output.seek(0);data=output.read(MAX_OUTPUT+1)
    if len(data)>MAX_OUTPUT: raise ValueError('output exceeded budget')
    text=data.decode('utf-8',errors='strict');print(text,end='')
    if compiled.returncode: raise ValueError(f'Lean compilation failed: {compiled.returncode}')
    audit_output(text,names)
    print(f'HHT006_LEAN_PASS: {len(names)} audited dimension-parametric theorems; '
          'the xi all-dimension budget is not asserted.')
    return 0


if __name__=='__main__':
    try: raise SystemExit(main())
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr)
        raise SystemExit(1) from exc
