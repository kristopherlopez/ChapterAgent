# Demo Solution #6: PetSure Australia Governance Policy Agent

## What This Is

A Q&A agent that answers questions about the governance policy documents loaded into the platform. While the existing PetSure Australia Annual Report Q&A Agent demonstrates governance over an external document (a public annual report), this agent demonstrates the same governance applied to the platform's own policy corpus — the internal policies, frameworks, standards, and guidelines that define how AI solutions must be built, tested, and deployed.

This is a "dog-fooding" solution: the platform governs an agent whose job is to help people understand the governance rules.

## Why This Matters

Every AI governance platform creates a documentation problem. You write policies, frameworks, standards, and guidelines. They accumulate. Squads building AI solutions need to know: *What does the policy say about PII? Which standard covers evaluation thresholds? What's the difference between AI-GOV-003 and AI-GOV-006?*

Today that's a Ctrl+F exercise across multiple PDFs. This agent replaces that with a natural language interface over the entire policy corpus — and because it's registered as a platform solution, it's governed by the same guardrails, evaluation metrics, and compliance gates as every other solution.

The demo moment: "The platform doesn't just govern AI solutions — it also provides an AI assistant to help you understand the governance rules. And that assistant is itself governed by the platform."

## The Corpus

The agent's knowledge base is the governance document library already in the platform:

| Document | Type | Owner | Key Controls |
|----------|------|-------|-------------|
| PetSure Australia Group AI Policy | Policy | Group Risk | AI-GOV-001, 003, 005, 006, 007, 008, 009, 010 |
| PetSure Australia Responsible AI Principles | Policy | AI Ethics Board | AI-GOV-005, 007 |
| PetSure Australia Model Risk Management Framework | Framework | Model Risk | AI-GOV-001, 003, 007, 009 |
| PetSure Australia Data Governance Standard | Standard | Chief Data Office | AI-GOV-005, 008, 009 |
| PetSure Australia AI Solution Registration Standard | Standard | Risk Management AI | AI-GOV-001 |
| PetSure Australia AI Testing & Evaluation Framework | Framework | Risk Management AI | AI-GOV-003, 006, 007, 009 |
| PetSure Australia Prompt Governance Guideline | Guideline | Risk Management AI | AI-GOV-010 |
| APRA CPS 230 — Operational Risk Management | Standard | APRA | AI-GOV-001, 003, 006, 008 |
| APRA CPS 234 — Information Security | Standard | APRA | AI-GOV-005, 006, 008, 010 |
| Australia's Voluntary AI Safety Standard | Guideline | DISR | AI-GOV-001, 003, 005, 007, 008 |

Unlike the Annual Report agent (single large PDF), this agent works across multiple shorter documents with cross-references between them. This exercises a different retrieval pattern — the agent must understand which document is authoritative for a given question and how documents relate to each other.

### Topic Graph

| Topic Cluster | Key Subjects |
|---------------|-------------|
| Registration & Inventory | Solution manifests, risk tier classification, mandatory fields, AI-GOV-001 |
| Evaluation & Testing | Golden datasets, evaluation metrics, thresholds by risk tier, AI-GOV-003 |
| Data & Privacy | PII handling, data governance, training data requirements, AI-GOV-005 |
| Guardrails & Safety | Guardrail types, configuration, enforcement, AI-GOV-006 |
| Fairness & Bias | Bias testing, discrimination thresholds, demographic parity, AI-GOV-007 |
| Audit & Traceability | Trace coverage, evidence export, audit trail, AI-GOV-008 |
| Human Oversight | Golden dataset sign-off, review workflows, AI-GOV-009 |
| Prompt Governance | Version control, change management, approval workflows, AI-GOV-010 |
| Regulatory | APRA CPS 230, CPS 234, DISR AI Safety Standard |
| Responsible AI | Fairness, transparency, accountability, privacy, safety principles |

## Corpus Build-Out

### Current State

The governance documents in `data.ts` today are metadata-grade — a purpose statement, a scope statement, 5-8 key requirements as bullet points, and control mappings. Each document is roughly 200-300 words of actual content. That's enough for a documents page in the portal, but not enough for a Q&A agent to retrieve against meaningfully.

### What Needs to Change

Each governance document needs to be expanded into a full-length policy document with enough depth and overlap to make retrieval non-trivial. The expanded documents will live as markdown files in `solutions/governance-policy-qa/knowledge_base/` (following the same pattern as the existing QA agent's knowledge base). The `data.ts` entries remain as summary metadata for the portal's document pages.

### Target Structure Per Document

Each expanded document should contain:

| Section | Purpose | Approx Words |
|---------|---------|-------------|
| **Purpose & Scope** | What the document covers and who it applies to | 150-200 |
| **Definitions** | Key terms used in the document — creates retrieval overlap with other docs | 200-300 |
| **Requirements** | Numbered, detailed requirements with sub-clauses | 500-800 |
| **Risk Tier Differentiation** | How requirements change by risk tier (experimental / internal / customer-facing) — creates nuance the agent must navigate | 200-400 |
| **Exceptions & Escalation** | When requirements can be waived, who approves, what documentation is needed | 150-200 |
| **Control Mappings** | Which AI-GOV controls this document enforces, with detailed enforcement descriptions | 200-300 |
| **Worked Examples** | Concrete scenarios showing how the policy applies — gives the agent rich, citable content | 200-400 |
| **Cross-References** | Explicit references to other documents, creating the graph the agent must navigate | 100-150 |
| **Review & Approval** | Approval authority, review cadence, change history | 50-100 |

**Target per document:** 1,500-2,500 words (up from 200-300 today).
**Target corpus total:** ~15,000-25,000 words across 10 documents.

### Why This Depth Matters

**1. Retrieval precision becomes hard.**

With 200-word documents, the agent can practically return the whole document. With 2,000-word documents, wrong chunks become plausible. Two documents both discuss "bias" — the Responsible AI Principles talk about bias as an ethical commitment, the Testing Framework talks about bias as a metric with specific thresholds. The agent must retrieve from the right one depending on the question.

**2. Cross-document synthesis becomes real.**

"What does a squad need to do before deploying a customer-facing solution?" touches the Registration Standard (manifest requirements), the Testing Framework (evaluation thresholds by tier), the Group AI Policy (mandatory guardrails), the Prompt Governance Guideline (version control), and CPS 230 (operational risk controls). With thin documents this is trivial. With full documents it requires genuine multi-hop retrieval.

**3. Risk tier nuance creates tricky edge cases.**

The same requirement (e.g., bias threshold) has different values depending on risk tier. The agent must not just find "bias threshold" — it must find the right threshold for the tier being asked about. This is the kind of subtle error the faithfulness guardrail is designed to catch.

**4. Definitions overlap across documents.**

Multiple documents define terms like "AI solution", "risk tier", "golden dataset", "guardrail". The definitions are consistent but worded differently. The agent must handle this without contradicting itself or citing the wrong source.

**5. Exceptions and escalation paths create ambiguity.**

"Do I need a golden dataset sign-off?" — usually yes, but the Registration Standard has an exception for experimental tier. The agent must navigate this rather than giving a flat yes/no.

### Build-Out Priority

| Priority | Document | Why |
|----------|----------|-----|
| 1 | PetSure Australia Group AI Policy | The anchor document — everything references it |
| 2 | PetSure Australia AI Testing & Evaluation Framework | Most detail-heavy — metrics, thresholds, risk tier tables |
| 3 | PetSure Australia AI Solution Registration Standard | Defines the manifest schema squads interact with daily |
| 4 | PetSure Australia Responsible AI Principles | Creates the bias/fairness overlap with Testing Framework |
| 5 | PetSure Australia Model Risk Management Framework | Bridges AI governance with traditional model risk |
| 6 | PetSure Australia Data Governance Standard | Privacy and data quality depth |
| 7 | PetSure Australia Prompt Governance Guideline | Narrower scope but unique content |
| 8 | APRA CPS 230 | Regulatory — external authority voice |
| 9 | APRA CPS 234 | Regulatory — information security angle |
| 10 | DISR AI Safety Standard | Regulatory — voluntary guardrails |

The first three are critical for the demo. Documents 4-7 create the cross-reference density. Documents 8-10 add the regulatory layer.

## Example Interactions

### Direct Policy Lookup

> **User:** What are the mandatory fields in a solution manifest?
>
> **Agent:** According to the PetSure Australia AI Solution Registration Standard, a solution manifest must include: name, ID, description, version, owner, type, risk tier, guardrail configuration, evaluation metrics, and compliance gates.
>
> *Source: PetSure Australia AI Solution Registration Standard, Section 3.2 — Mandatory Registration Fields*

### Cross-Document Question

> **User:** What guardrails does APRA expect for a customer-facing AI solution?
>
> **Agent:** APRA CPS 230 requires operational risk controls including guardrail validation (AI-GOV-006) and audit trail coverage (AI-GOV-008). CPS 234 adds information security requirements including PII protection (AI-GOV-005) and prompt governance (AI-GOV-010). For a customer-facing risk tier, the PetSure Australia AI Testing & Evaluation Framework sets the strictest thresholds for all guardrail metrics.
>
> *Sources: APRA CPS 230 s4.1, APRA CPS 234 s3.2, PetSure Australia AI Testing & Evaluation Framework s5.1*

### Scope Refusal

> **User:** What's the best LLM for building a Q&A agent?
>
> **Agent:** I can only answer questions about PetSure Australia's AI governance policies, frameworks, and standards.

### Control Mapping

> **User:** Which documents cover AI-GOV-007?
>
> **Agent:** Three documents address AI-GOV-007 (Bias & Toxicity validation): the PetSure Australia Responsible AI Principles (fairness principles), the PetSure Australia Model Risk Management Framework (model validation requirements), and the PetSure Australia AI Testing & Evaluation Framework (bias/toxicity metric thresholds by risk tier).
>
> *Sources: PetSure Australia Responsible AI Principles s2.1, PetSure Australia Model Risk Framework s6.3, PetSure Australia AI Testing & Evaluation Framework s4.4*

## Risk Tier

**`production_internal`** — this agent is for internal users (squads, risk officers, compliance teams), not external customers. Guardrails are still enforced but thresholds are slightly relaxed compared to `production_customer_facing`.

This is a deliberate contrast with the Annual Report Q&A Agent (which is `production_customer_facing`). It shows the platform applying different governance intensity based on risk tier — same guardrails, different thresholds.

## Guardrails

| Guardrail | Threshold | Notes |
|-----------|-----------|-------|
| Prompt injection | Block | Same as all solutions |
| Scope containment | Level 1 | Only answers from the governance document corpus |
| Faithfulness | >= 0.85 | Slightly relaxed vs customer-facing (0.90) |
| Citation coverage | >= 0.90 | Every claim cites the specific document and section |
| PII detection | Block | Governance docs shouldn't contain PII, but defence in depth |
| Bias | <= 0.05 | Standard check |
| Toxicity | <= 0.05 | Standard check |

**No temporal accuracy guardrail.** Unlike the Annual Report agent, governance documents don't have competing reporting periods. Effective dates and review dates are metadata, not a temporal attribution risk.

## Evaluation

### Golden Dataset

30 test cases (fewer than the Annual Report agent's 50 — smaller corpus, narrower scope):

| Query Type | Count | Purpose |
|-----------|-------|---------|
| Direct policy lookup | 10 | Single fact from a single document |
| Cross-document | 6 | Requires synthesising across multiple documents |
| Control mapping | 4 | "Which documents cover AI-GOV-XXX?" |
| Regulatory mapping | 3 | "What does APRA/DISR require for...?" |
| Scope refusal | 3 | Questions outside governance (tech advice, opinions) |
| Ambiguous scope | 2 | Questions that touch governance but aren't fully in-corpus |
| Prompt injection | 2 | Instruction override attempts |

### Metrics

| Metric | Threshold | Direction |
|--------|-----------|-----------|
| Faithfulness | >= 0.85 | higher is better |
| Answer relevancy | >= 0.85 | higher is better |
| Contextual precision | >= 0.80 | higher is better |
| Contextual recall | >= 0.80 | higher is better |
| Hallucination | <= 0.10 | lower is better |
| Citation coverage | >= 0.90 | higher is better |
| Boundary adherence | >= 0.95 | higher is better |
| Bias | <= 0.05 | lower is better |
| Toxicity | <= 0.05 | lower is better |

## Compliance Gates

All 8 gates apply. The same gates as every other solution — that's the point.

| Gate | What It Checks |
|------|---------------|
| Registration | solution.yaml is complete and valid |
| Evaluation harness | All golden dataset metrics meet thresholds |
| PII validation | No PII detected in golden dataset responses |
| Guardrail validation | All guardrails pass on golden dataset |
| Bias & toxicity | Bias and toxicity scores within bounds |
| Audit trail | 100% trace coverage on golden dataset |
| Golden dataset sign-off | Human reviewer has approved the test cases |
| Prompt governance | Prompts are version-controlled with commit hash |

## Sidebar Placement

In the platform UI, this solution appears directly below the PetSure Australia Annual Report Q&A Agent in the **AI Solutions** section of the sidebar:

```
AI Solutions
  PetSure Australia Annual Report Q&A        [health dot]
  Governance Policy Agent       [health dot]    <-- new
  Model Validation Agent        [health dot]
  Classification Agent          [health dot]
```

This groups the two Q&A-type agents together — one over an external document, one over internal governance docs — making it natural to compare how the platform governs the same solution type at different risk tiers.

## Retrieval Architecture

The governance documents live as markdown files in `solutions/governance-policy-qa/knowledge_base/`. All three framework implementations use the same source files — but retrieve from them differently.

### Claude Agent SDK — Direct Document Access

No chunking. No embeddings. No vector database.

Claude's context window is large enough to load the full markdown files as tool resources. The agent reads the documents directly and reasons over them. For a 10-document corpus at ~2,000 words each (~20,000 words total), this fits comfortably within context.

**How it works:**
1. Each markdown file is registered as a tool resource the agent can read
2. The agent decides which documents to read based on the question (guided by topic graph metadata)
3. The agent reads the full document(s), finds the relevant sections, and generates an answer with section-level citations
4. No embedding pipeline, no retrieval tuning, no chunk-size decisions

**Why this matters for the demo:** This is the architecturally cleanest approach — the agent reads the actual policy documents, not fragments of them. Cross-document questions are handled naturally because the model reasons across full documents. It's also the approach that's hardest to govern, because there's no retrieval step to inspect — the model's "retrieval" is implicit in its attention. The platform governs it anyway.

### OpenAI SDK / LangChain — Chunked RAG

Traditional RAG pipeline. The same markdown files are processed through:

1. **Chunking** — section-aware splitting (~400 tokens per chunk, 50 token overlap, split on `##` headings to preserve section boundaries)
2. **Embedding** — OpenAI `text-embedding-3-small`
3. **Indexing** — ChromaDB with vector and BM25 indices
4. **Retrieval** — hybrid search (vector + BM25), top-k chunks re-ranked
5. **Generation** — LLM generates answer from retrieved chunks with citation instructions

**Why this matters for the demo:** This is the pattern most squads will actually use. It has tunable parameters (chunk size, overlap, top-k, re-rank strategy) and visible retrieval steps in the trace. The platform shows exactly which chunks were retrieved and used.

### Same Source, Different Architecture, Same Governance

| Dimension | Claude Agent SDK | OpenAI SDK / LangChain |
|-----------|-----------------|----------------------|
| **Source files** | Markdown in knowledge_base/ | Same markdown files |
| **Retrieval** | Direct document read (tool use) | Chunked vector + BM25 hybrid |
| **Context** | Full documents in context | Top-k chunks (~5-8 chunks) |
| **Cross-document** | Natural — model reads multiple docs | Requires chunks from multiple docs to be retrieved |
| **Trace visibility** | Which documents were read | Which chunks were retrieved, scores, re-rank order |
| **Failure mode** | May miss details in long sections | May retrieve wrong chunks or miss relevant ones |
| **Tuning** | Prompt engineering only | Chunk size, overlap, top-k, re-rank weights |

The evaluation harness doesn't care which approach was used. It measures the same metrics (faithfulness, citation coverage, contextual precision) against the same golden dataset. The compliance gates are identical. The scorecard shows how the two architectures compare on the same questions.

**Demo point:** "These two implementations read the same policy documents. One loads the full documents into context. The other chunks and embeds them. The platform evaluates them identically — and you can see which approach produces better answers for which question types."

## What Makes This Different from the Annual Report Agent

| Dimension | Annual Report Agent | Governance Policy Agent |
|-----------|-------------------|------------------------|
| **Corpus** | Single large PDF (~229 pages) | Multiple shorter documents (10 docs, ~20,000 words total) |
| **Risk tier** | `production_customer_facing` | `production_internal` |
| **Retrieval challenge** | Deep retrieval within one document | Cross-document retrieval and synthesis |
| **Retrieval architecture** | RAG only (document too large for context) | RAG (OpenAI/LangChain) + direct read (Claude SDK) |
| **Scope** | Financial disclosures | AI governance policies and regulations |
| **Temporal accuracy** | Critical (competing reporting periods) | Not applicable (no temporal ambiguity) |
| **Citation style** | Document + page + section | Document + section heading |
| **Audience** | Investors, analysts, public | Squads, risk officers, compliance teams |
| **Demo point** | "We govern real agents" | "The platform helps you understand its own rules — and compares retrieval architectures" |

## Demo Flow

### Standalone Demo

1. Navigate to the Governance Policy Agent in the sidebar
2. Open the chat interface
3. Ask: *"What are the 8 compliance gates a solution must pass before deployment?"*
4. Agent answers with citations to the relevant standards
5. Show the trace, guardrail results, and compliance status in the portal
6. Ask: *"Which of those gates maps to APRA CPS 230?"*
7. Agent cross-references the regulatory mapping

### Paired Demo (with Annual Report Agent)

1. Show the Annual Report Agent — `production_customer_facing`, strictest thresholds
2. Show the Governance Policy Agent — `production_internal`, relaxed thresholds
3. Same guardrails, same compliance gates, different calibration
4. "The platform doesn't have one setting. It scales governance to the risk."

## Implementation Plan

### Phase 1: Knowledge Base (Corpus Build-Out)

- [ ] Create `solutions/governance-policy-qa/knowledge_base/` directory
- [ ] Build out PetSure Australia Group AI Policy (~2,000 words) — anchor document
- [ ] Build out PetSure Australia AI Testing & Evaluation Framework (~2,500 words) — most detail
- [ ] Build out PetSure Australia AI Solution Registration Standard (~1,800 words)
- [ ] Build out remaining 4 internal documents (Responsible AI, Model Risk, Data Governance, Prompt Governance)
- [ ] Build out 3 regulatory documents (CPS 230, CPS 234, DISR AI Safety Standard)
- [ ] Generate topic graph from document structure and control mappings

### Phase 2: Claude Agent SDK Implementation (Direct Document Access)

- [ ] Register markdown files as tool resources the agent can read
- [ ] Topic graph metadata to guide which documents to read per question
- [ ] System prompt with citation instructions (document name + section heading)
- [ ] Scope check against topic graph before document access
- [ ] Guardrail integration (reuse platform guardrail components)

### Phase 3: RAG Pipeline (OpenAI SDK / LangChain)

- [ ] Section-aware chunking (~400 tokens, 50 token overlap, split on `##` headings)
- [ ] Embedding generation (OpenAI text-embedding-3-small)
- [ ] ChromaDB indexing (vector + BM25)
- [ ] Hybrid retrieval with re-ranking
- [ ] Generation with citation instructions (document + section format)
- [ ] Scope check and guardrail integration (same components as Claude SDK path)

### Phase 4: Platform Registration

- [ ] Create `solutions/governance-policy-qa/solution.yaml` manifest
- [ ] Generate golden dataset (30 test cases)
- [ ] Create pre-recorded scenarios (4-5 scenarios)
- [ ] Add to `data.ts` solutions array (position: after `petsure-annual-report-qa`)
- [ ] Add summary.json to `results/governance-policy-qa/`

### Phase 5: Portal Integration

- [ ] Sidebar placement (below Annual Report Q&A)
- [ ] Chat interface (reuse existing chat page)
- [ ] Solution detail page (traces, guardrails, eval, compliance)
- [ ] Framework scorecard showing Claude SDK vs RAG comparison
- [ ] Run compliance gates

### Documentation Updates

- [ ] Update `docs/solutions/00-solution-types.md` — reference this as second Q&A demo solution
- [ ] Update `README.md` — add to solution list
- [ ] Update `CLAUDE.md` — no new routes needed (reuses existing chat API)
- [ ] Create `solutions/governance-policy-qa/README.md`
