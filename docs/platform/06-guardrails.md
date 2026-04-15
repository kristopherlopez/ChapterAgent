# Component #2: Guardrail Framework

The agent enforces guardrails that mirror what the Governance Portal would build for all teams.

## Boundary Adherence

- Agent only answers questions about the team strategy, Kris's background, or the reusable component architecture
- Out-of-scope queries get a clear refusal: "That's outside my scope. I can answer questions about the team strategy, team build, or reusable components."
- Demonstrates scope containment -- a key agentic guardrail

## Input/Output Filtering

- Input validation: prompt injection detection, topic classification
- Output validation: no hallucinated claims beyond the source documents, no PII leakage
- Demonstrates content safety guardrails

## Action Boundaries (for agentic implementations)

- Explicit tool whitelist: retrieval tool, citation tool, evaluation tool -- nothing else
- Read-only -- agent cannot modify anything
- Demonstrates the action boundary pattern from the guardrail framework

## Human-in-the-Loop Gate (demo)

- For questions the agent is uncertain about (low retrieval confidence), it flags: "I'm not confident in this answer. Here's what I found, but you should verify."
- Demonstrates the configurable gate pattern

## What it demonstrates

- Foundation guardrails applied in practice
- Agentic-specific guardrails (action boundaries, scope containment)
- The Governance Portal/team ownership split: the framework is reusable, the specific thresholds are configurable
