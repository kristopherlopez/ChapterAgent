# Build Phases

## Phase 1: Shared Core + Two Platforms (3-4 days)

- Write all 8 knowledge base documents
- Chunk, embed, store in ChromaDB
- Build custom compliance gates (scope classifier, PII scanner via Presidio, citation checker)
- Build observability layer (step tracing, token counting, component attribution via LangFuse)
- Implement first two platform adapters:
  - **LangChain** (most common — proves the shared component interface works)
  - **LangGraph** (most architecturally interesting — graph-based agentic retrieval, compliance subgraph)
- Wire up DeepEval real-time checks (FaithfulnessMetric, BiasMetric, ToxicityMetric with gpt-4o-mini as judge)
- Layer 2 compliance pipeline: custom gates + DeepEval checks running on every response
- Basic Streamlit UI with chat + compliance trace panel
- Manual testing with sample questions

## Phase 2: Evaluation Harness + Deployment Gate (2-3 days)

- Write golden dataset (40-50 question-answer pairs across all categories)
- Format as DeepEval `EvaluationDataset` with `LLMTestCase` entries
- Configure DeepEval batch metrics: Faithfulness, AnswerRelevancy, ContextualPrecision, ContextualRecall, Hallucination, Bias, Toxicity
- Add custom metrics: CitationCoverageMetric, BoundaryAdherenceMetric
- Set chapter-defined thresholds per risk tier
- Run `deepeval evaluate` against golden dataset, tune retrieval (chunking, top-k, reranking)
- Add DeepEval scorecard display to UI (per-metric scores, pass/fail per threshold)
- **Build Layer 1 deployment gate:** GitHub Actions pipeline with 8 compliance checks
- Write compliance check modules (`compliance.checks.*`) — registration, evaluation, PII, guardrails, bias, audit trail, golden dataset sign-off, prompt governance
- Run the pipeline, generate first deployment compliance report
- Compare LangChain vs LangGraph scores — first two entries in the comparative scorecard

## Phase 3: Evidence Export + Remaining Platforms (4-5 days)

- **Build Layer 3 evidence export:** compliance report generator (JSON + HTML)
- Build policy-to-evidence mapping template
- Build compliance health dashboard in UI
- "Export Compliance Evidence" button generating full evidence package
- Implement OpenAI Agents SDK adapter
- Implement Claude Agent SDK adapter (with harness-native retrieval)
- Implement CrewAI adapter
- Implement Semantic Kernel adapter
- Cross-platform comparison mode in UI
- Run evaluation across all six platforms
- Generate comparative scorecard

## Phase 4: Polish & Deploy (2-3 days)

- Deploy to hosted environment (shareable URL)
- UI polish: cross-platform comparison view, evaluation dashboard, compliance dashboard
- Run full deployment gate pipeline against hosted environment
- "How was this built?" meta-explanation feature
- Prepare three-act walkthrough narrative for the interview
- Record backup demo video of all three compliance layers
- Generate final evidence package for the demo

## Total: ~2.5 weeks

## Priority Order (if time-constrained)

If the interview comes before everything is built, the priority order is:

**Must have (the demo doesn't work without these):**
1. **Layer 2: Real-time compliance pipeline** — the trace panel showing pass/fail on every response. This is the visual centrepiece.
2. **LangGraph adapter** — the most impressive orchestration. Compliance as a subgraph.
3. **LangChain adapter** — the baseline. Proves shared components work.
4. **Layer 1: Deployment gate** — the GitHub Actions pipeline. Can be shown as a separate browser tab even if the live agent has issues.

**Should have (significantly strengthens the story):**
5. **Layer 3: Evidence export** — the "Export Compliance Evidence" button. Transforms the demo from "guardrails" into "full compliance-as-code."
6. **OpenAI Agents SDK adapter** — listed in JD. Provider SDK comparison.
7. **Claude Agent SDK adapter** — multi-provider story. Harness-native retrieval.

**Nice to have (polish):**
8. **CrewAI adapter** — multi-agent preview.
9. **Semantic Kernel adapter** — enterprise/Azure story.
10. **Compliance health dashboard** — production monitoring view.

Two platforms with all three compliance layers is more impressive than six platforms with only Layer 2.
