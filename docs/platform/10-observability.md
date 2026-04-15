# Component #3: Observability Layer

Every interaction is fully traced -- proving the step-level observability the Governance Portal would require.

## What Gets Logged

- Full request/response chain
- Which platform was used
- Retrieval: query -> chunks retrieved -> relevance scores -> chunks selected
- Generation: prompt constructed -> LLM call -> raw response -> guardrail checks -> final output
- Token usage and cost per query
- Latency breakdown: retrieval time, LLM time, guardrail time, total
- Component attribution: which reusable components were invoked and what they did

## Trace Panel (UI)

- Visible in the UI alongside the chat response
- Collapsible detail: summary view ("Used: RAG, Guardrails, Citations") and detailed view (full trace)
- Cross-platform comparison: ask the same question on all six platforms, compare traces side by side

## Integration

- LangFuse or OpenTelemetry for structured tracing
- Exportable audit trail -- shows what "can we defend this to a regulator?" looks like in practice

## What it demonstrates

- Step-level observability as described in the guardrail framework
- Audit trail completeness -- a governance requirement
- Cost tracking and platform comparison -- practical operational insight
