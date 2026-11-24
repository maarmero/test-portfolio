"""Keeps TEST_PLAN.md and the automated tests in step.

- Every test named in the plan's "Automated?" column must exist.
- Every test must carry a priority tag (p1, p2 or p3) equal to the highest
  priority (P1 is highest) of the plan rows that name it.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def priorities_in_plan():
    """{test name: highest priority number among the rows that name it}"""
    found = {}
    for line in (ROOT / "TEST_PLAN.md").read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if re.fullmatch(r"TC-\d+", cells[0]) and len(cells) >= 6:
            for name in re.findall(r"`(test_\w+)`", cells[5]):
                found.setdefault(name, []).append(int(cells[2][1]))
    return {name: min(p) for name, p in found.items()}


def priority_tags_in_code():
    """{test name: set of priority numbers from @pytest.mark.pN}"""
    found = {}
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        if path.name == Path(__file__).name:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                found[node.name] = {
                    int(d.attr[1])
                    for d in node.decorator_list
                    if isinstance(d, ast.Attribute) and re.fullmatch(r"p[123]", d.attr)
                }
    return found


def test_every_test_in_the_plan_exists():
    missing = set(priorities_in_plan()) - set(priority_tags_in_code())
    assert not missing, f"named in TEST_PLAN.md but not found in tests/: {sorted(missing)}"


def test_every_test_has_the_priority_from_the_plan():
    plan, code = priorities_in_plan(), priority_tags_in_code()
    wrong = {
        name: f"plan P{plan.get(name)}, tag {sorted(tags) or 'none'}"
        for name, tags in code.items()
        if tags != {plan.get(name)}
    }
    assert not wrong, f"priority tag does not match TEST_PLAN.md: {wrong}"
