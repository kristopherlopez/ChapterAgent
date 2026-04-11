# Knowledge Base Content (To Be Written)

These documents form the RAG corpus. Each becomes a source the agent retrieves from and cites.

## Document 1: Chapter Vision & Strategy

- Mission: build the reusable AI capability layer for Risk Management
- 2nd-line positioning: tooling, governance, and platforms -- not model building
- Relationship to centralised AI teams and 1st-line crews
- The "build for the future" philosophy: framework-agnostic, provider-agnostic, pattern-first

## Document 2: Team Build Plan

- Phase 1 (months 1-3): hire 3 -- senior data scientist (eval/guardrails), ML engineer (platform/CI-CD), data scientist (RAG/agents)
- Phase 2 (months 4-6): hire 2 -- data scientist (India, evaluation), ML engineer (India, tooling)
- Phase 3 (months 7-12): grow to 10 based on demand -- likely: 2 more data scientists, 1 product manager for the portal
- Onshore/offshore split: Australia owns architecture decisions and stakeholder engagement. India owns implementation velocity and testing depth.
- Culture: builder mentality, ship early, iterate, everything is a reusable component

## Document 3: Reusable Component Architecture

- Source: `reusable-components.md` (sections 1-7)
- The four criteria for reusability
- Evaluation framework (four layers)
- Guardrail framework (foundation + agentic-specific)
- RAG evaluation harness
- Framework evaluation template
- CI/CD consistency strategy
- Compliance-as-code

## Document 4: Unified Portal Design

- Source: `strategic-transformation-prep.md` (section 2)
- Five layers: model registry, monitoring, GenAI quality, guidance, workflow
- Design principle: portal population is a byproduct of following the paved road
- Stakeholder views: data scientist vs crew lead vs model risk analyst vs auditor

## Document 5: 90/180/365 Day Roadmap

- **Days 1-90:** Listen, assess, hire first 3. Deliver one quick win (evaluation harness MVP). Map existing landscape.
- **Days 91-180:** Ship guardrail library v1. Stand up observability. Begin portal design. Hire India team.
- **Days 181-365:** Portal MVP live. Compliance-as-code gates in CI/CD. Framework evaluation template in use. 3+ squads consuming reusable components. Grow to 10.

## Document 6: Governance & Responsible AI Approach

- AI governance as enabler, not bureaucracy
- APRA alignment: evidence of controls, not just policies
- Compliance-as-code: every policy maps to an automated check
- Model risk governance for GenAI (different from traditional ML -- evaluation harness, guardrails, traceability)
- PetSure proof points: Governance Policy, Responsible Use Policy, Acceptable Use Standard, AI Steering Committee

## Document 7: Stakeholder Engagement Model

- Alex Mendes (direct manager): weekly 1:1, monthly strategy review
- BU/SU-aligned data scientists: component adoption, feedback loops, training
- Centralised AI teams: alignment on standards, avoid duplication, share patterns
- Internal audit / 2nd-3rd line: compliance evidence, portal access, automated reporting
- GMs / EGMs: quarterly capability reviews, portal dashboards, strategic alignment
- Influence without authority: make the right thing the easy thing

## Document 8: Kris's Background & Proof Points

- PetSure (2019-present): Head of AI. Grew team 5->15. Built AI capability from scratch. GenAI operating model. CEO award.
- Chubb Fire & Security (2010-2019): Built data & analytics capability from zero. Greenfield environment.
- Two greenfield builds: the core differentiator. Proven ability to start from nothing, influence executives, deliver outcomes.
- Technical: Python, AWS, Azure, Docker, CI/CD, RAG, agentic architectures, LLM evaluation
- Leadership: executive influence, team building, governance design, operating model creation
