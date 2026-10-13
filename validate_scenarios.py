#!/usr/bin/env python3
"""Validate the draft JSONL safety fixtures. No device inference is performed."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'tests' / 'scenarios.jsonl'
VALID = {'allow', 'deny', 'review'}
MANDATORY = {
    'scenario_id': str,
    'category': str,
    'title': str,
    'source': str,
    'user_request': str,
    'untrusted_content': str,
    'proposed_action': dict,
    'expected_decision': str,
    'expected_reason': str,
    'label_confidence': str,
    'synthetic': bool,
}

def load_and_validate(path: Path):
    problems = []
    ids = set()
    cases = []
    for lineno, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not raw.strip():
            continue
        try:
            case = json.loads(raw)
        except json.JSONDecodeError as e:
            problems.append(f'line {lineno}: invalid JSON: {e}')
            continue
        if not isinstance(case, dict):
            problems.append(f'line {lineno}: expected object')
            continue
        for key, kind in MANDATORY.items():
            if key not in case or not isinstance(case[key], kind):
                problems.append(f'line {lineno}: missing or bad {key} ({kind.__name__})')
        if any(key not in case for key in MANDATORY):
            continue
        sid = case['scenario_id']
        if sid in ids:
            problems.append(f'line {lineno}: duplicate ID {sid}')
        ids.add(sid)
        if case['expected_decision'] not in VALID:
            problems.append(f'line {lineno}: unknown decision')
        if not case['synthetic']:
            problems.append(f'line {lineno}: only synthetic seeds are allowed')
        action = case['proposed_action']
        if not isinstance(action.get('tool'), str) or not isinstance(action.get('arguments'), dict):
            problems.append(f'line {lineno}: bad proposed action')
        cases.append(case)
    return cases, problems

if __name__ == '__main__':
    if not PATH.exists():
        sys.exit('missing test file')
    cases, errors = load_and_validate(PATH)
    counts = Counter(c['expected_decision'] for c in cases)
    print(f'Loaded {len(cases)} synthetic draft cases: {dict(counts)}')
    if errors:
        for error in errors:
            print('ERROR:', error, file=sys.stderr)
        sys.exit(1)
    print('Schema check passed (not an on-device safety test).')
