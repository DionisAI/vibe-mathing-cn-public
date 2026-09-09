#!/usr/bin/env python3
"""Run the pinned Lean compiler and inspect every printed theorem dependency.

Missing tools, errors, missing audit records, unapproved dependencies, timeouts
and output overflow fail closed. This runner is NOT a canonical Result verifier.
"""
from __future__ import annotations
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'fixtures' / 'lean-proof'
SOURCE = WORK / 'HHTCertificates.lean'
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
MAX_OUTPUT = 1_048_576


def audit_output(text: str, names: list[str]) -> None:
    """Require one axiom report per named theorem and reject unexpected dependencies."""
    for name in names:
        pattern = (r"'?" + re.escape(name) + r"'?\s+(?:depends on axioms:\s*\[([^\]]*)\]"
                   r"|does not depend on any axioms)")
        records = list(re.finditer(pattern, text))
        if len(records) != 1:
            raise ValueError(f'missing or duplicate theorem audit: {name}')
        raw = records[0].group(1)
        dependencies = set(re.findall(r'[A-Za-z_][A-Za-z0-9_.]*', raw or ''))
        if not dependencies <= ALLOWED:
            raise ValueError(f'unapproved theorem dependencies: {name}: {dependencies - ALLOWED}')


def limit_child() -> None:
    """Bound output, CPU and memory for the Linux compiler child."""
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT, MAX_OUTPUT))
    resource.setrlimit(resource.RLIMIT_CPU, (180, 180))
    resource.setrlimit(resource.RLIMIT_AS, (8 * 1024**3, 8 * 1024**3))


def main() -> int:
    """Compile this exact source with the fixture's pinned Lean/Mathlib project."""
    if shutil.which('lake') is None:
        print('BLOCKED: lake/Lean is not installed; no kernel verification occurred.', file=sys.stderr)
        return 2
    source = SOURCE.read_text(encoding='utf-8')
    if re.search(r'\b(sorry|admit|unsafe|native_decide|axiom|run_elab|run_cmd)\b|#eval|Lean\.ofReduceBool', source):
        raise ValueError('prohibited proof escape or side-effect command in certificate source')
    names = ['HHT004.' + n for n in re.findall(r'^theorem\s+(\w+)', source, re.M)]
    if not names or len(names) != len(set(names)):
        raise ValueError('empty or duplicated theorem list')
    if (WORK/'lean-toolchain').read_text().strip() != 'leanprover/lean4:v4.33.0':
        raise ValueError('toolchain drift')
    environment = {k:v for k,v in os.environ.items() if k in
                   {'PATH','HOME','LANG','LC_ALL','TMPDIR','LEAN_PATH','ELAN_HOME'}}
    version = subprocess.run(['lake','env','lean','--version'], cwd=WORK, env=environment,
                             capture_output=True, text=True, timeout=30, check=True)
    if not re.search(r'Lean \(version 4\.33\.0(?:,|\s|\))',version.stdout):
        raise ValueError('unexpected actual Lean version: '+version.stdout[:200])
    print(version.stdout.strip())
    with tempfile.TemporaryFile() as output:
        completed = subprocess.run(['lake','env','lean','-j1','-DwarningAsError=true', SOURCE.name],
            cwd=WORK, env=environment, stdout=output, stderr=subprocess.STDOUT,
            timeout=240, check=False, preexec_fn=limit_child)
        output.seek(0)
        data=output.read(MAX_OUTPUT+1)
    if len(data)>MAX_OUTPUT:
        raise ValueError('compiler output exceeded budget')
    text=data.decode('utf-8',errors='strict')
    print(text,end='')
    if completed.returncode != 0:
        raise ValueError(f'Lean compile failed: exit {completed.returncode}')
    audit_output(text,names)
    print(f'LEAN_SLICES_PASS: {len(names)} theorem audits; not the full analytic theorem or RH.')
    return 0


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr)
        raise SystemExit(1) from exc
