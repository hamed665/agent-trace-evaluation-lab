# Agent Trace Evaluation Lab

![Verify](https://github.com/hamed665/agent-trace-evaluation-lab/actions/workflows/verify.yml/badge.svg)

An offline regression harness for recorded agent traces, with approval checks, tool-order assertions, citation requirements and budget gates.

**Edition:** local reference component with a runnable synthetic CLI demo.
**Maintainer:** [Hamed Minaei](https://github.com/hamed665)  
**Engineering focus:** Agent behavior verification  
**License:** MIT · Copyright © 2026 Hamed Minaei

## Use case

Use this component in an offline regression workflow to inspect approval ordering, tool restrictions, required citations and usage budgets before changing an agent integration.

**Processing flow:** Versioned cases + baseline/candidate traces → policy checks → aligned regression report and CLI exit status.

## Features

- Deterministic evaluation with per-check results and an aggregate score.
- Approval must precede the tool call and bind exact tool name and arguments.
- Approval consumption detects reuse; policy failure blocks the final pass.
- Tool allowlists/order, required answer terms, cited source IDs and usage budgets.
- Aligned baseline/candidate comparison, regression exit status and redacted answer previews.

## Review the implementation

| Resource | What to inspect |
| --- | --- |
| [Core module](evaluate.py) | Decision rules, validation and failure handling |
| [Behavioral tests](tests/) | Success paths and rejected or ambiguous cases |
| [Example output](docs/demo-output.json) | Results from the bundled synthetic scenario |
| [Engineering notes](ENGINEERING.md) | Design decisions and integration boundaries |
| [Validation record](VALIDATION.md) | Recorded verification scope |

## Quick start

Python 3.11 or newer; only the standard library is used. No package install is required.

```bash
git clone https://github.com/hamed665/agent-trace-evaluation-lab.git
cd agent-trace-evaluation-lab
python demo.py
python -m unittest discover -s tests -v
```

The demo executes the core component against synthetic inputs. Compare its output with [docs/demo-output.json](docs/demo-output.json).

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

The Dockerfile packages the same CLI demo. Consult [VALIDATION.md](VALIDATION.md) for the recorded execution scope.

## Testing

`python -m unittest discover -s tests -v` runs 13 behavioral tests.
GitHub Actions runs those tests and the demo on Python 3.11, 3.12 and 3.13.
Action dependencies are pinned to commit SHAs and the workflow token is read-only.
See [VALIDATION.md](VALIDATION.md) for local evidence and verification scope.

## Security

Traces must originate from a trusted recorder. An agent-supplied approval event is not evidence of human consent. This evaluates recorded behavior; it does not enforce runtime permissions or send messages. Redaction only covers common email and token patterns in answer previews; it is not a general PII detector. Keep traces synthetic or independently sanitize them before saving or sharing.

## Limitations

No LLM judge, live model integration, real price lookup or semantic factuality evaluation. Answer-term checks are lexical, citations check IDs rather than source truth, and reported usage is trusted evidence. Missing usage events produce a zero total; require complete usage telemetry in an integration. Multiple answers use the final answer. JSON inputs are local/trusted and file-byte limits are left to the adapter.

## Maintenance and attribution

Maintained by [Hamed Minaei](https://github.com/hamed665). See [AUTHORS.md](AUTHORS.md) for development attribution. This original reference implementation was developed with AI assistance; its source, tests and synthetic fixtures are maintained in this repository.

For a reproducible issue, include a sanitized fixture and the command used in [GitHub Issues](https://github.com/hamed665/agent-trace-evaluation-lab/issues).

## License

[MIT](LICENSE). No third-party runtime packages are required.
