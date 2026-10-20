# Engineering walkthrough

**Hamed Minaei · Agent behavior verification**

## Problem and implemented scope

Recorded tool-policy checks, exact approval binding, source assertions and baseline regression gates.

## Demonstration evidence

The baseline fails because consent evidence is absent. The candidate passes with a preceding approval bound to the same tool and exact arguments.

Run `python demo.py` and compare with `docs/demo-output.json`.
Run `python -m unittest discover -s tests -v` to inspect failure-path behavior.
The verification workflow runs those commands on Python 3.11, 3.12 and 3.13.

## Review guide

1. Read the core implementation and the Architecture section of README.
2. Inspect tests for both permitted behavior and failure/ambiguity cases.
3. Review PR #1 for the initial implementation and its verification results.
4. Read Security and Limitations before extending or integrating the component.

## Portfolio description

"Agent behavior verification: Recorded tool-policy checks, exact approval binding, source assertions and baseline regression gates. Includes a reproducible synthetic demonstration,
behavioral tests and CI verification."

This describes the implemented component, not an operating production service.
Development assistance and ownership are recorded in AUTHORS.md.
