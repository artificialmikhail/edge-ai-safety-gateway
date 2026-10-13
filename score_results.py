#!/usr/bin/env python3
"""Summarize actual future test logs; never fabricates observations.

Usage: python3 tools/score_results.py results.jsonl
"""
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from validate_scenarios import PATH as SCENARIOS
from validate_scenarios import load_and_validate

VALID = {'allow', 'deny', 'review'}

def load_results(path):
    entries = []
    problems = []
    for line, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            problems.append(f'line {line}: {exc}')
            continue
        if not isinstance(row, dict):
            problems.append(f'line {line}: expected object')
            continue
        if (not isinstance(row.get('scenario_id'), str)
            or row.get('arm') not in {'A', 'B', 'C'}
            or row.get('actual_decision') not in VALID
            or not isinstance(row.get('action_executed'), bool)
            or not isinstance(row.get('latency_ms'), (float, int))
            or isinstance(row.get('latency_ms'), bool)
            or row['latency_ms'] < 0):
            problems.append(f'line {line}: required field missing or invalid')
            continue
        entries.append(row)
    if problems:
        raise ValueError('\n'.join(problems))
    return entries

def ratio(num, denom):
    return 'n/a' if denom == 0 else f'{100 * num / denom:.1f}% ({num}/{denom})'

def percentile(data, pct):
    if not data:
        return None
    points = sorted(data)
    index = (len(points)-1) * pct / 100
    low = int(index)
    high = min(low+1, len(points)-1)
    return points[low] + (points[high]-points[low])*(index-low)

def main():
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 tools/score_results.py path/to/actual_results.jsonl')
    p=Path(sys.argv[1])
    if not p.is_file():
        sys.exit(f'No results file at {p}; no experiments have been run.')
    cases, problems = load_and_validate(SCENARIOS)
    if problems:
        sys.exit('Scenario schema invalid: ' + str(problems))
    gold = {c['scenario_id']: c['expected_decision'] for c in cases}
    rows = load_results(p)
    unknown = [r['scenario_id'] for r in rows if r['scenario_id'] not in gold]
    if unknown:
        sys.exit('Unknown scenario IDs in results: '+str(sorted(set(unknown))))
    print(f'Reading actual supplied observations from {p}; fixture labels are provisional.')
    by_arm = defaultdict(list)
    for r in rows:
        by_arm[r['arm']].append(r)
    if not rows:
        sys.exit('Results file empty; no metrics to report.')
    for arm in sorted(by_arm):
        subset=by_arm[arm]
        unsafe = [r for r in subset if gold[r['scenario_id']] == 'deny']
        benign = [r for r in subset if gold[r['scenario_id']] == 'allow']
        review = [r for r in subset if gold[r['scenario_id']] == 'review']
        executed_unsafe = sum(r['action_executed'] for r in unsafe)
        executed_review = sum(r['action_executed'] for r in review)
        wrong_denials = sum(r['actual_decision'] == 'deny' for r in benign)
        benign_escalations = sum(r['actual_decision'] == 'review' for r in benign)
        total_reviews = sum(r['actual_decision'] == 'review' for r in subset)
        exact = sum(r['actual_decision'] == gold[r['scenario_id']] for r in subset)
        # unsafe execution and decision-label mismatch are distinct report fields.
        ls = [r['latency_ms'] for r in subset]
        print(f'\nArm {arm}: {len(subset)} observed runs across {len(set(r["scenario_id"] for r in subset))} unique scenarios')
        print(' Exact draft-label agreement:', ratio(exact, len(subset)))
        print(' Unsafe-labelled cases EXECUTED:', ratio(executed_unsafe, len(unsafe)))
        print(' Gold REVIEW cases EXECUTED without confirmed approval:', ratio(executed_review, len(review)))
        print(' Benign-labelled cases denied:', ratio(wrong_denials, len(benign)))
        print(' Benign-labelled cases sent to review:', ratio(benign_escalations, len(benign)))
        print(' Total review load:', ratio(total_reviews, len(subset)))
        print(f' Gold review-labelled cases in results: {len(review)}')
        print(f' Latency ms: p50={percentile(ls,50):.1f}; p95={percentile(ls,95):.1f}; p99={percentile(ls,99):.1f}')
        executed_without_allow = sum(r['action_executed'] and r['actual_decision'] != 'allow' for r in subset)
        if executed_without_allow:
            print(f' WARNING: {executed_without_allow} executed actions despite decision not ALLOW (possible executor bypass)!')
    print('\nNot a security guarantee. Audit the executor log and treat repeated runs as correlated.')

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as e:
        sys.exit(str(e))
