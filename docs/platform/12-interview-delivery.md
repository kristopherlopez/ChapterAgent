# Interview Delivery

## The Walkthrough (15-20 minutes)

### Act 1: "Before I show you the agent" (Layer 1 — Deployment Gate)

1. **Open with the pain point:** "Alex, you mentioned the manual effort to get AI solutions through governance. I built something that solves all three stages of that problem."

2. **Show the GitHub Actions pipeline:** Open the browser tab with the CI/CD run. "Before this agent could go live, it passed through an automated deployment gate. Eight policy checks — solution registration, evaluation harness, PII validation, guardrail testing, bias sweep, audit trail completeness, golden dataset sign-off, prompt governance. All automated. All passed. No meeting. No form."

3. **Show the deployment report:** "Here's the compliance report it generated. Every policy maps to a check. Every check has evidence. This is what a squad would see before promoting to production."

### Act 2: "Now let's use it" (Layer 2 — Production Monitoring)

4. **Demo the agent:** Ask it 2-3 questions. Point at the trace panel. "Now it's live. Every response passes through seven real-time compliance checks in under 200 milliseconds. Scope adherence. Citations. PII scan. Faithfulness. Bias. Toxicity. Audit trail. Continuous compliance — not a point-in-time check."

5. **Trigger a failure:** Ask an out-of-scope question. "Watch the trace panel. Scope adherence failed. The response was blocked. The failure was logged with the query, the classification, and the refusal. That's a compliance event — captured automatically."

6. **Show the compliance dashboard:** "Over the last [N] interactions, here's the health of this solution. Pass rate, failure breakdown, trends. An auditor can see this at any time."

7. **Switch platforms:** Ask the same question on a different platform. "Same compliance pipeline, different orchestration framework. The governance layer doesn't care which framework the squad chose. That's the reusable component model."

### Act 3: "Now imagine you're an auditor" (Layer 3 — Evidence Export)

8. **Click "Export Compliance Evidence":** Show the HTML report. "This was generated automatically. Nobody filled out a form. Every policy maps to a control. Every control maps to evidence. Every piece of evidence was generated as a byproduct of the system running."

9. **Show the policy-to-evidence mapping:** "APRA asks 'show me your controls for this AI solution.' You don't convene a meeting. You export the evidence package. It's already there."

### Close

10. "Three layers. Deployment gates before it goes live. Real-time monitoring while it runs. Evidence export on demand. All automated. All reusable — every squad gets the same framework. You told me governance is a manual bottleneck. This eliminates it. I built it in two weeks. Imagine what a team of five could do in 90 days."

---

## Backup Plan

- Pre-recorded demo video of all three layers if live demo fails
- Static deployment report + compliance evidence report (printed/PDF) if everything fails
- The knowledge base documents standalone as a written chapter blueprint
- GitHub Actions pipeline can be shown even if the live agent is down

---

## Risk & Mitigations

| Risk | Mitigation |
|---|---|
| Live demo fails | Pre-recorded backup video. Static scorecard printout. |
| API rate limits during demo | Cache responses for common demo questions. Have fallback to a single platform. |
| Cost overrun (multiple LLM providers) | Set budget caps. Use cheaper models for dev (GPT-4o-mini), full models for demo. LangChain/LangGraph/CrewAI share the same OpenAI backend — only 3 provider accounts needed (OpenAI, Azure OpenAI, Anthropic). |
| Over-engineering | Phase 1 delivers two working platforms (LangChain + LangGraph). Everything after is additive. Ship Phase 1, iterate. |
| Time pressure (unknown interview date) | Phase 1 is demo-ready in 3-4 days with two platforms. Follow the priority order — LangGraph + LangChain alone with full evaluation is a strong demo. |
| Six platforms too ambitious | Priority order defined. Two platforms with full evaluation scorecard > six platforms half-built. Each additional platform is ~1 day incremental given the shared component interface. |

---

## Success Criteria

The agent succeeds if the interview panel:
1. Interacts with it and gets useful, accurate answers about the chapter strategy
2. Understands the reusable component architecture from seeing it work
3. Sees the evaluation scorecard and recognises it as the framework described in the interview
4. Walks away thinking "he's already started building the chapter"

---

## Evaluation Strategy

### Golden Dataset Structure

```json
{
  "id": "q001",
  "category": "leadership",
  "question": "How would you build the team in the first 90 days?",
  "expected_chunks": [
    {"doc": "team-build-plan.md", "chunk_id": 3, "grade": 3},
    {"doc": "roadmap.md", "chunk_id": 1, "grade": 2},
    {"doc": "background.md", "chunk_id": 7, "grade": 1}
  ],
  "expected_answer_contains": [
    "senior data scientist",
    "ML engineer",
    "evaluation",
    "guardrails",
    "hire 3"
  ],
  "out_of_scope": false
}
```

### Question Categories

| Category | Example Questions | Count |
|---|---|---|
| Leadership & Team | "How would you build the team?" / "What's your leadership style?" | 8-10 |
| Technical Vision | "What reusable components would you build first?" / "How do you evaluate GenAI?" | 8-10 |
| Governance | "How would you handle AI governance at PetSure Australia scale?" / "What does compliance-as-code mean?" | 6-8 |
| Strategy & Roadmap | "What does success look like at 90/180/365 days?" / "How do you prioritise?" | 6-8 |
| Stakeholder | "How would you influence GMs to adopt your components?" / "How do you work with audit?" | 4-6 |
| Out-of-Scope | "What's PetSure Australia's share price?" / "Tell me about fraud detection models" | 5-8 |
| Kris's Background | "Why should we hire you?" / "Tell me about your PetSure experience" | 4-6 |

### Evaluation Metrics & Thresholds

| Metric | DeepEval Class | Target | Framework Layer | Mode |
|---|---|---|---|---|
| Contextual Precision | `ContextualPrecisionMetric` | > 0.80 | Layer 1: Retrieval | Batch |
| Contextual Recall | `ContextualRecallMetric` | > 0.75 | Layer 1: Retrieval | Batch |
| Faithfulness | `FaithfulnessMetric` | > 0.90 | Layer 2: Generation | Batch + Real-time |
| Answer Relevancy | `AnswerRelevancyMetric` | > 0.85 | Layer 2: Generation | Batch |
| Hallucination | `HallucinationMetric` | < 0.10 | Layer 2: Generation | Batch |
| Bias | `BiasMetric` | < 0.10 | Layer 4: Governance | Batch + Real-time |
| Toxicity | `ToxicityMetric` | < 0.05 | Layer 4: Governance | Batch + Real-time |
| Boundary Adherence | `BoundaryAdherenceMetric` (custom) | > 0.95 | Layer 4: Governance | Batch + Real-time |
| Citation Coverage | `CitationCoverageMetric` (custom) | 100% | Layer 4: Governance | Batch + Real-time |
| Avg Latency | n/a (custom) | < 3000ms | Layer 3: Production | Batch |

**Batch vs Real-time:** Metrics marked "Batch + Real-time" run in both modes. Batch uses gpt-4o as judge (accuracy). Real-time uses gpt-4o-mini (speed, < 500ms). Same thresholds, different judge models. This is a configurable parameter in the harness.
