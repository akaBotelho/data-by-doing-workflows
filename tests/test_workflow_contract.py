from __future__ import annotations

import re
import unittest
from pathlib import Path

WORKFLOW = (
    Path(__file__).parents[1] / ".github" / "workflows" / "stage-1.yml"
).read_text(encoding="utf-8")
APPROVED_TESTS_SHA = "7d864e0b3965e90f70d221732c9f4d2a589ab65e"
THIRD_PARTY_ACTION = re.compile(
    r"^\s*uses:\s+[^./\s]+/[^@\s]+@([^\s#]+)",
    re.MULTILINE,
)


class WorkflowContractTest(unittest.TestCase):
    def test_controlled_tests_are_pinned(self) -> None:
        self.assertIn(f"ref: {APPROVED_TESTS_SHA}", WORKFLOW)
        self.assertIn("repository: akaBotelho/data-by-doing-workflows", WORKFLOW)

    def test_third_party_actions_are_pinned_by_full_sha(self) -> None:
        pins = THIRD_PARTY_ACTION.findall(WORKFLOW)

        self.assertTrue(pins)
        self.assertTrue(all(re.fullmatch(r"[0-9a-f]{40}", pin) for pin in pins))

    def test_permissions_and_credentials_stay_minimal(self) -> None:
        self.assertIn("permissions:\n  contents: read", WORKFLOW)
        self.assertEqual(WORKFLOW.count("persist-credentials: false"), 2)
        self.assertNotIn("secrets:", WORKFLOW)
        self.assertNotIn("${{ secrets.", WORKFLOW)

    def test_stage_name_is_stable(self) -> None:
        self.assertRegex(
            WORKFLOW,
            r"(?m)^  stage-1:\n    name: Stage 1 verification$",
        )


if __name__ == "__main__":
    unittest.main()
