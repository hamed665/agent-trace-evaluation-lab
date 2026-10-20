"""Offline deterministic agent-trace policy evaluation, not an LLM judge."""
import json
import math
import re


def redact(text):
    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '[EMAIL]', text)
    return re.sub(r'\b(?:sk-|token_)[A-Za-z0-9_-]{8,}', '[SECRET]', text)


def evaluate(case, trace):
    """Read-only recorded evidence; approvals are explicit trusted trace events."""
    budget = case.get('budget', 1.0)
    if not isinstance(budget, (int, float)) or isinstance(budget, bool) or not math.isfinite(budget) or budget < 0:
        raise ValueError('Invalid budget')
    if not isinstance(trace, list) or len(trace) > 10000:
        raise ValueError('Invalid or oversized trace')
    approved, used, citations, violations = {}, [], set(), []
    answer, cost = '', 0.0
    for event in trace:
        if not isinstance(event, dict):
            raise ValueError('Event must be an object')
        kind = event.get('type')
        if kind == 'approval':
            action_id = event.get('action_id')
            if not isinstance(action_id, str) or not action_id:
                raise ValueError('Approval requires action_id')
            if not isinstance(event.get('name'), str) or not isinstance(event.get('arguments'), dict):
                raise ValueError('Approval requires tool name and exact arguments')
            approved[action_id] = (event['name'], json.dumps(event['arguments'], sort_keys=True, allow_nan=False))
        elif kind == 'tool':
            name, action_id = event.get('name'), event.get('action_id')
            if not isinstance(name, str):
                raise ValueError('Tool requires name')
            used.append(name)
            if name not in case.get('allowed_tools', []):
                violations.append('tool_not_allowed')
            if name in case.get('approval_required', []):
                actual = (name, json.dumps(event.get('arguments', {}), sort_keys=True, allow_nan=False))
                if not action_id or approved.get(action_id) != actual:
                    violations.append('approval_missing')
                else:
                    del approved[action_id]
        elif kind == 'answer':
            if not isinstance(event.get('text'), str):
                raise ValueError('Answer requires text')
            answer = event['text']
            sources = event.get('sources', [])
            if not isinstance(sources, list) or any(not isinstance(s, str) for s in sources):
                raise ValueError('Invalid citations')
            citations = set(sources)
        elif kind == 'usage':
            value = event.get('cost_usd')
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
                raise ValueError('Invalid cost')
            cost += value
        else:
            raise ValueError('Unknown event type')
    expected = iter(case.get('required_tool_order', []))
    next_tool = next(expected, None)
    for tool in used:
        if tool == next_tool:
            next_tool = next(expected, None)
    checks = {
        'tool_order': next_tool is None,
        'answer_terms': bool(answer) and all(t.casefold() in answer.casefold() for t in case.get('answer_terms', [])),
        'citations': set(case.get('required_sources', [])).issubset(citations),
        'budget': cost <= budget,
        'policy': not violations,
    }
    return {'passed': all(checks.values()), 'score': sum(checks.values()) / len(checks),
            'checks': checks, 'violations': sorted(set(violations)),
            'cost_usd': round(cost, 8), 'answer_preview': redact(answer)[:240]}


def compare(baseline, candidate):
    """Compare aligned named cases; missing or extra cases fail comparison."""
    if set(baseline) != set(candidate) or not baseline:
        raise ValueError('Runs must contain the same nonempty case set')
    return {'regressions': sorted(k for k in baseline if baseline[k]['passed'] and not candidate[k]['passed']),
            'improvements': sorted(k for k in baseline if not baseline[k]['passed'] and candidate[k]['passed']),
            'pass_rate': sum(v['passed'] for v in candidate.values()) / len(candidate)}
