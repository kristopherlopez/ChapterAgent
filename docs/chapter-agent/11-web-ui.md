# Web UI

## Layout

```
+-------------------------------------------+----------------------------+
|                                            |                            |
|   CHAPTER CAPABILITY AGENT                 |   CONTEXT RETRIEVAL        |
|                                            |                            |
|   [LangChain] [LangGraph] [CrewAI]         |   Strategy: Hybrid Search  |
|   [Semantic Kernel] [OpenAI] [Claude]      |   Reason: "single topic,   |
|                                            |   specific terms"          |
|   +---------------------------------+      |   - Chunk 1: [doc] (0.92) |
|   |                                 |      |   - Chunk 2: [doc] (0.87) |
|   |  Chat history                   |      |   - Chunk 3: [doc] (0.71) |
|   |                                 |      |   Retrieval: 120ms         |
|   |  User: How would you build      |      |                            |
|   |  the team in the first 90 days? |      |   COMPLIANCE PIPELINE      |
|   |                                 |      |   [PASS] Scope (custom)    |
|   |  Agent: Based on the chapter    |      |   [PASS] Citations (custom)|
|   |  strategy [1], I'd hire three   |      |   [PASS] PII (custom)      |
|   |  roles first...                 |      |   [PASS] Faithful (0.94)   |
|   |                                 |      |   [PASS] Bias (0.02)       |
|   |  [1] team-build-plan.md, chunk 3|      |   [PASS] Toxicity (0.00)   |
|   |                                 |      |   AUTO-APPROVED (187ms)    |
|   +---------------------------------+      |                            |
|                                            |   PERFORMANCE              |
|   [Ask a question...]          [Send]      |   - Retrieval: 120ms       |
|                                            |   - LLM: 1,340ms          |
|   +-------------------------------------+  |   - Compliance: 187ms      |
|   | EVALUATION SCORECARD                 |  |   - Total: 1,647ms        |
|   | Ctx Precision: 0.85 | Faith: 0.93    |  |   - Tokens: 1,847         |
|   | Ctx Recall: 0.79    | Grounded: 0.91 |  |   - Cost: $0.0034         |
|   | [View Full Scorecard] [Compare All]  |  |                            |
|   +-------------------------------------+  |   [Export Evidence Report] |
+-------------------------------------------+----------------------------+
```

## Key UI Features

- **Platform selector:** switch between all six implementations mid-conversation
- **Component trace panel:** real-time visibility into which reusable components fired and what they did
- **Citation links:** every claim traces back to a source document and chunk
- **Cross-platform comparison mode:** ask the same question on all six, see results side by side
- **Evaluation scorecard:** always visible, updates in real-time as the golden dataset runs
- **"How was this built?" button:** meta-explanation of the architecture -- the agent explains its own reusable component structure
