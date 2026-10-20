# Agent Trace Evaluation Lab

### A Hamed Minaei engineering project

![Verify](https://github.com/hamed665/agent-trace-evaluation-lab/actions/workflows/verify.yml/badge.svg)

An offline regression harness for recorded agent traces, with approval checks, tool-order assertions, citation requirements and budget gates.

**Status:** tested reference implementation with a reproducible synthetic CLI demo.
**Project owner & maintainer:** [Hamed Minaei](https://github.com/hamed665)  
**Engineering focus:** Agent behavior verification  
**License:** MIT · Copyright © 2026 Hamed Minaei

## Features

- Deterministic evaluation with per-check results and an aggregate score.
- Approval must precede the tool call and bind exact tool name and arguments.
- Approval consumption detects reuse; policy failure blocks the final pass.
- Tool allowlists/order, required answer terms, cited source IDs and usage budgets.
- Aligned baseline/candidate comparison, regression exit status and redacted answer previews.

## Quick start

Python 3.11 or newer; only the standard library is used. No package install is required.

```bash
git clone https://github.com/hamed665/agent-trace-evaluation-lab.git
cd agent-trace-evaluation-lab
python demo.py
python -m unittest discover -s tests -v
```

The demo performs real computation against synthetic data. Its captured output is in
[docs/demo-output.json](docs/demo-output.json). It uses no customer records or production systems.

Evaluate your own schema-compatible local fixture with `python demo.py --input sample.json`.

## Architecture

A case declares expected behavior; a trace records trusted approval, tool, answer and usage events. `evaluate` walks events in order, consumes matching approvals and computes five checks. All five must pass; the score is diagnostic and never overrides a failed gate. `compare` aligns case IDs and reports pass-to-fail regressions. The CLI exits 1 on regression, making a versioned fixture suitable for CI.

Core implementation: [evaluate.py](evaluate.py).
The core is separate from the demonstration runner and can be imported directly:

```python
from demo import run

report = run("sample.json")
assert not report["baseline"]["approved-email"]["passed"]
assert report["candidate"]["approved-email"]["passed"]
assert report["comparison"]["improvements"] == ["approved-email"]
assert not report["comparison"]["regressions"]
```

## Installation and configuration

No model, API key or network access is required. `sample.json` maps case IDs to case, baseline and candidate. Supported event types are tool, approval, answer and usage. Approval-required tools must include action_id and exact JSON arguments on both approval and execution events. Set per-case budget in USD; usage costs must be finite and nonnegative. Input traces are capped at 10,000 events per evaluation.

An optional Dockerfile runs the same demo under a non-root UID:

```bash
docker build -t agent-trace-evaluation-lab .
docker run --rm --read-only --network none --tmpfs /tmp:rw,noexec,nosuid,size=32m agent-trace-evaluation-lab
```

The Docker definition is provided for reproducibility. Container execution is not claimed as verified unless recorded in VALIDATION.md.

## Testing

`python -m unittest discover -s tests -v` runs 13 behavioral tests.
GitHub Actions runs those tests and the demo on Python 3.11, 3.12 and 3.13.
Action dependencies are pinned to commit SHAs and the workflow token is read-only.
See [VALIDATION.md](VALIDATION.md) for local evidence and verification scope.

## Security

Traces must originate from a trusted recorder. An agent-supplied approval event is not evidence of human consent. This evaluates recorded behavior; it does not enforce runtime permissions or send messages. Redaction only covers common email and token patterns in answer previews; it is not a general PII detector. Keep traces synthetic or independently sanitize them before saving or sharing.

## Limitations

No LLM judge, live model integration, real price lookup or semantic factuality evaluation. Answer-term checks are lexical, citations check IDs rather than source truth, and reported usage is trusted evidence. Missing usage events produce a zero total; require complete usage telemetry in an integration. Multiple answers use the final answer. JSON inputs are local/trusted and file-byte limits are left to the adapter.

## Maintainer

[Hamed Minaei](https://github.com/hamed665) owns and maintains this portfolio repository.
For implementation details, review the source, behavioral tests and merged pull requests.
See [AUTHORS.md](AUTHORS.md) for development attribution and [ENGINEERING.md](ENGINEERING.md)
for a concise technical walkthrough.

## Attribution and ownership

This repository is an original implementation created for Hamed Minaei's portfolio with
AI-assisted development and local verification. No upstream application's source code or
Git history was imported. Python's standard library supplies the underlying runtime,
SQLite bindings, cryptography primitives, JSON, dates and decimal arithmetic as used here.
The implementation, tests, synthetic fixtures and documentation are maintained in this repository.

License: [MIT](LICENSE). No third-party runtime packages are required.
