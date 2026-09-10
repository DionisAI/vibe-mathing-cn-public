#!/usr/bin/env python3
"""Compile the pinned coefficient dependency and the actual deflation statements."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'fixtures'/'lean-proof'


def main():
    """Tool absence, compiler errors, escapes or missing dependency audits block acceptance."""
    if shutil.which('lake') is None:
        print('BLOCKED: Lean/lake absent; no kernel verification.',file=sys.stderr);return 2
    from check_hht_lean import audit_output,limit_child,MAX_OUTPUT
    if (WORK/'lean-toolchain').read_text().strip()!='leanprover/lean4:v4.33.0':
        raise ValueError('toolchain drift')
    env={k:v for k,v in os.environ.items() if k in {'PATH','HOME','LANG','LC_ALL','TMPDIR','LEAN_PATH','ELAN_HOME'}}
    version=subprocess.run(['lake','env','lean','--version'],cwd=WORK,env=env,
        capture_output=True,text=True,timeout=30,check=True)
    if not re.search(r'Lean \(version 4\.33\.0(?:,|\s|\))',version.stdout):raise ValueError('actual toolchain drift')
    print(version.stdout.strip())
    target=WORK/'.lake'/'build'/'lib'/'lean';target.mkdir(parents=True,exist_ok=True)
    for stem,namespace,count in [('HHTCoefficientCone','HHTCoefficientCone',17),('HHTDeflation','HHTDeflation',14)]:
        src=WORK/(stem+'.lean');text=src.read_text()
        if re.search(r'\b(sorry|admit|unsafe|native_decide|axiom|run_elab|run_cmd)\b|#eval|Lean\.ofReduceBool',text):
            raise ValueError('prohibited proof escape')
        names=[namespace+'.'+n for n in re.findall(r'^theorem\s+(\w+)',text,re.M)]
        if len(names)!=count or len(set(names))!=count:raise ValueError('theorem manifest drift')
        out=target/(stem+'.olean')
        with tempfile.TemporaryFile() as output:
            result=subprocess.run(['lake','env','lean','-j1','-DwarningAsError=true','-o',str(out),src.name],
                cwd=WORK,env=env,stdout=output,stderr=subprocess.STDOUT,timeout=180,
                check=False,preexec_fn=limit_child)
            output.seek(0);raw=output.read(MAX_OUTPUT+1)
        if len(raw)>MAX_OUTPUT:raise ValueError('output budget exceeded')
        log=raw.decode();print(log,end='')
        if result.returncode:raise ValueError('Lean compilation failed: '+stem)
        audit_output(log,names)
        print(stem+' SHA256 '+hashlib.sha256(src.read_bytes()).hexdigest())
    print('DEFLATION_LEAN_PASS: 14 audited theorems plus 17 dependency audits; root/sign barrier and actual Schur criterion; xi inputs external.')
    return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,ImportError,subprocess.SubprocessError) as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr);raise SystemExit(1) from exc
