#!/usr/bin/env python3
"""Static origin-policy regression tests; not full scanner/runtime integration."""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name("validate_public_boundary.py")


def origin_policy() -> set[str]:
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    assignments = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "PUBLIC_ORIGINS"
                for target in node.targets)
    ]
    if len(assignments) != 1:
        raise ValueError("PUBLIC_ORIGINS must have one auditable literal assignment")
    policy = ast.literal_eval(assignments[0].value)
    if not isinstance(policy, set) or not all(isinstance(url, str) for url in policy):
        raise ValueError("PUBLIC_ORIGINS must be a literal set of URL strings")
    return policy


class PublicOriginPolicyTests(unittest.TestCase):
    def test_upstream_forms_remain_allowed(self) -> None:
        for url in (
            "https://github.com/vibemathing/vibe-mathing-cn-public",
            "https://github.com/vibemathing/vibe-mathing-cn-public.git",
            "git@github.com:vibemathing/vibe-mathing-cn-public.git",
        ):
            with self.subTest(url=url):
                self.assertIn(url, origin_policy())

    def test_this_fork_forms_are_allowed(self) -> None:
        for url in (
            "https://github.com/DionisAI/vibe-mathing-cn-public",
            "https://github.com/DionisAI/vibe-mathing-cn-public.git",
            "git@github.com:DionisAI/vibe-mathing-cn-public.git",
        ):
            with self.subTest(url=url):
                self.assertIn(url, origin_policy())

    def test_only_two_reviewed_identities(self) -> None:
        self.assertEqual(len(origin_policy()), 6)

    def test_unreviewed_owners_stay_blocked(self) -> None:
        for owner in ("example", "DionisAI-other", "vibemathing-other"):
            for suffix in ("", ".git"):
                self.assertNotIn(
                    f"https://github.com/{owner}/vibe-mathing-cn-public{suffix}",
                    origin_policy(),
                )

    def test_host_and_userinfo_spoofing_stays_blocked(self) -> None:
        for url in (
            "https://github.com.github.com.example.org/DionisAI/vibe-mathing-cn-public",
            "https://github.com@evil.example/DionisAI/vibe-mathing-cn-public",
            "https://evil.example/DionisAI/vibe-mathing-cn-public",
            "http://github.com/DionisAI/vibe-mathing-cn-public",
        ):
            self.assertNotIn(url, origin_policy())

    def test_suffix_query_and_path_variants_stay_blocked(self) -> None:
        url = "https://github.com/DionisAI/vibe-mathing-cn-public"
        for suffix in ("-other", "/../other", "?owner=other", "#fragment", "/", ".git/extra"):
            self.assertNotIn(url + suffix, origin_policy())

    def test_validator_still_uses_exact_membership(self) -> None:
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        validate = next(node for node in tree.body
                        if isinstance(node, ast.FunctionDef) and node.name == "validate")
        expected = ast.parse("origin.stdout.decode().strip() not in PUBLIC_ORIGINS", mode="eval").body
        self.assertTrue(any(
            ast.dump(node) == ast.dump(expected)
            for node in ast.walk(validate)
        ), "Do not replace the exact allowlist check with suffix/substring matching")


if __name__ == "__main__":
    unittest.main(verbosity=2)
