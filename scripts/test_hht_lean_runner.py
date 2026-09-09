#!/usr/bin/env python3
"""Synthetic parser tests only; PASS here is explicitly not Lean kernel execution."""
from pathlib import Path
import re
import unittest
import check_hht_lean as M


class LeanAuditTests(unittest.TestCase):
    def test_allowed_axioms(self):
        """A normal Lean dependency report can be parsed."""
        M.audit_output("'HHT004.x' depends on axioms: [propext, Classical.choice, Quot.sound]",['HHT004.x'])

    def test_empty_axioms(self):
        """Both documented no-dependency forms are accepted."""
        M.audit_output("'HHT004.x' does not depend on any axioms",['HHT004.x'])
        M.audit_output("'HHT004.x' depends on axioms: []",['HHT004.x'])

    def test_proof_escapes_rejected(self):
        """Neither an unfinished proof nor a code-generation oracle may pass."""
        for name in ('sorryAx','Lean.ofReduceBool','MyFakeAxiom'):
            with self.assertRaises(ValueError):
                M.audit_output(f"'HHT004.x' depends on axioms: [{name}]",['HHT004.x'])

    def test_missing_and_duplicate_rejected(self):
        """A compiler success without a unique theorem audit is insufficient."""
        line="'HHT004.x' depends on axioms: [propext]\n"
        for output in ('',line*2,line.replace('HHT004.x','HHT004.xy')):
            with self.assertRaises(ValueError): M.audit_output(output,['HHT004.x'])

    def test_wrapped_output(self):
        """Long dependency lists can wrap without weakening the allowlist."""
        M.audit_output("'HHT004.x' depends on axioms:\n [propext,\nQuot.sound]",['HHT004.x'])

    def test_every_source_theorem_has_print(self):
        """The source's complete theorem list is visible; this is not type checking."""
        source=M.SOURCE.read_text()
        names=re.findall(r'^theorem\s+(\w+)',source,re.M)
        printed=re.findall(r'^#print axioms HHT004\.(\w+)',source,re.M)
        self.assertEqual(names,printed)
        self.assertEqual(len(names),12)


if __name__=='__main__': unittest.main(verbosity=2)
