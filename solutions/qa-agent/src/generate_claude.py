"""Answer generation — Claude Agent SDK.

Uses the Claude Agent SDK with tool use: Claude calls retrieval and
citation tools autonomously, deciding what to search for and how to
cite. This is the agentic retrieval pattern from doc 09.

Two modes:
    - **agentic**: Claude Agent SDK with MCP tools (full agent loop)
    - **direct**: Anthropic SDK direct call (simple, no tool use)

Usage:
    # Agentic (tool use)
    generator = ClaudeAgentGenerator(chunks=chunks)
    response = generator.generate("What was CBA's NIM?", chunks)

    # Direct (no tool use, same as before)
    generator = ClaudeDirectGenerator()
    response = generator.generate("What was CBA's NIM?", chunks)
"""

from __future__ import annotations

import json
import os
from typing import Any

from pydantic import BaseModel

try:
    from solutions.qa_agent.src.generate import (
        SYSTEM_PROMPT,
        AnswerPayload,
        Citation,
        QAResponse,
    )
    from solutions.qa_agent.src.retrieve import RetrievedChunk
except ImportError:
    from generate import (  # type: ignore[no-redef]
        SYSTEM_PROMPT,
        AnswerPayload,
        Citation,
        QAResponse,
    )
    from retrieve import RetrievedChunk  # type: ignore[no-redef]


# ---------------------------------------------------------------------------
# Claude Agent SDK — agentic tool-use implementation
# ---------------------------------------------------------------------------

class ClaudeAgentGenerator:
    """Agentic Q&A using Claude Agent SDK with tool use.

    Defines two tools that Claude can call:
        - search_corpus: searches the document chunks by keyword
        - cite_source: records a citation for a claim

    Claude decides what to search for, evaluates if it has enough
    context, and cites its sources — the full agentic retrieval pattern.
    """

    def __init__(
        self,
        *,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        *,
        scope_level: int = 1,
        query_id: str = "",
    ) -> QAResponse:
        """Generate answer using Claude with tool use.

        Provides retrieved chunks as a searchable corpus via tool calls.
        Claude decides which chunks to use and how to cite them.
        """
        if not chunks:
            return QAResponse(
                query_id=query_id,
                question=question,
                answer=AnswerPayload(
                    text="I cannot find this information "
                    "in the Annual Report.",
                    scope_level_used=scope_level,
                    grounding="none",
                ),
            )

        # Build the tool definitions
        tools = self._build_tools(chunks)

        # System prompt with instructions to use tools
        system = (
            "You are a Q&A agent for CBA's 2025 Annual Report.\n\n"
            "You have access to tools to search the document corpus "
            "and cite sources. Use the search_corpus tool to find "
            "relevant information, then answer the question with "
            "citations.\n\n"
            "RULES:\n"
            "1. Use search_corpus to find relevant context.\n"
            "2. Cite every claim using cite_source.\n"
            "3. If you can't find the information, say so.\n"
            "4. Never provide financial advice.\n"
            "5. Be precise with numbers.\n"
        )

        try:
            import anthropic

            client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )

            # Run the agent loop with tool use
            answer_text, citations, token_usage = (
                self._run_agent_loop(
                    client, system, question, tools, chunks,
                )
            )

        except Exception as e:
            answer_text = self._fallback_answer(chunks)
            citations = self._extract_citations(chunks)
            token_usage = {"error": str(e)}

        return QAResponse(
            query_id=query_id,
            question=question,
            answer=AnswerPayload(
                text=answer_text,
                scope_level_used=scope_level,
                grounding="corpus",
            ),
            citations=citations,
            metadata={
                "framework": "claude-agent-sdk",
                "model": self.model,
                "retrieval_strategy": "agentic",
                "chunks_retrieved": len(chunks),
                "chunks_used": len(citations),
                "token_usage": token_usage,
            },
        )

    def _build_tools(
        self, chunks: list[RetrievedChunk],
    ) -> list[dict]:
        """Build tool definitions for Claude."""
        return [
            {
                "name": "search_corpus",
                "description": (
                    "Search the CBA Annual Report corpus. "
                    "Returns matching text chunks with page numbers "
                    "and section titles."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "cite_source",
                "description": (
                    "Record a citation for a factual claim. "
                    "Call this for every fact in your answer."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "Page number",
                        },
                        "section": {
                            "type": "string",
                            "description": "Section title",
                        },
                        "quote": {
                            "type": "string",
                            "description": "Relevant quote",
                        },
                    },
                    "required": ["page", "section"],
                },
            },
        ]

    def _run_agent_loop(
        self,
        client,
        system: str,
        question: str,
        tools: list[dict],
        chunks: list[RetrievedChunk],
    ) -> tuple[str, list[Citation], dict]:
        """Run the Claude agent loop with tool use."""
        messages = [{"role": "user", "content": question}]
        citations: list[Citation] = []
        total_input = 0
        total_output = 0
        max_iterations = 5

        for _ in range(max_iterations):
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system,
                tools=tools,
                messages=messages,
            )

            if response.usage:
                total_input += response.usage.input_tokens
                total_output += response.usage.output_tokens

            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Process tool calls
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._handle_tool_call(
                            block.name,
                            block.input,
                            chunks,
                            citations,
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                # Add assistant message and tool results
                messages.append({
                    "role": "assistant",
                    "content": response.content,
                })
                messages.append({
                    "role": "user",
                    "content": tool_results,
                })
            else:
                # Claude is done — extract final answer
                answer_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        answer_text += block.text
                break
        else:
            answer_text = "I was unable to complete the search."

        token_usage = {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "agent_iterations": min(
                _ + 1, max_iterations,
            ),
        }

        return answer_text, citations, token_usage

    def _handle_tool_call(
        self,
        tool_name: str,
        tool_input: dict,
        chunks: list[RetrievedChunk],
        citations: list[Citation],
    ) -> str:
        """Handle a tool call from Claude."""
        if tool_name == "search_corpus":
            query = tool_input.get("query", "")
            results = self._search_chunks(query, chunks)
            return json.dumps(results, indent=2)

        elif tool_name == "cite_source":
            citation = Citation(
                page=tool_input.get("page", 0),
                section=tool_input.get("section", ""),
                quote=tool_input.get("quote", ""),
            )
            citations.append(citation)
            return json.dumps({"status": "citation recorded"})

        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    @staticmethod
    def _search_chunks(
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int = 5,
    ) -> list[dict]:
        """Simple keyword search over pre-retrieved chunks."""
        query_words = set(query.lower().split())
        scored = []
        for chunk in chunks:
            text_lower = chunk.text.lower()
            matches = sum(1 for w in query_words if w in text_lower)
            if matches > 0:
                scored.append((matches, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "text": c.text[:300],
                "page": c.page,
                "section": c.section,
                "relevance": score,
            }
            for score, c in scored[:top_k]
        ]

    @staticmethod
    def _extract_citations(
        chunks: list[RetrievedChunk],
    ) -> list[Citation]:
        seen = set()
        citations = []
        for chunk in chunks[:3]:
            key = (chunk.page, chunk.section)
            if key not in seen:
                seen.add(key)
                citations.append(
                    Citation(
                        page=chunk.page,
                        section=chunk.section,
                        quote=chunk.text[:200],
                    )
                )
        return citations

    @staticmethod
    def _fallback_answer(chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return (
                "I cannot find this information "
                "in the Annual Report."
            )
        top = chunks[0]
        return (
            f"{top.text}\n\n"
            f"*Source: CBA Annual Report 2025, "
            f"p.{top.page} — {top.section}*"
        )


# ---------------------------------------------------------------------------
# Direct Anthropic SDK — simple call, no tool use
# ---------------------------------------------------------------------------

class ClaudeDirectGenerator:
    """Simple Claude generation without tool use.

    Same as the OpenAI generator pattern — sends context in the
    system prompt and gets back an answer. No agent loop.
    """

    def __init__(
        self,
        *,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        *,
        scope_level: int = 1,
        query_id: str = "",
    ) -> QAResponse:
        """Generate answer with a direct Claude call."""
        if not chunks:
            return QAResponse(
                query_id=query_id,
                question=question,
                answer=AnswerPayload(
                    text="I cannot find this information "
                    "in the Annual Report.",
                    scope_level_used=scope_level,
                    grounding="none",
                ),
            )

        context = self._build_context(chunks)
        system_message = SYSTEM_PROMPT.format(context=context)

        try:
            import anthropic

            client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_message,
                messages=[
                    {"role": "user", "content": question},
                ],
            )
            answer_text = response.content[0].text
            token_usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }
        except Exception as e:
            answer_text = self._fallback_answer(chunks)
            token_usage = {"error": str(e)}

        citations = self._extract_citations(chunks)

        return QAResponse(
            query_id=query_id,
            question=question,
            answer=AnswerPayload(
                text=answer_text,
                scope_level_used=scope_level,
                grounding="corpus",
            ),
            citations=citations,
            metadata={
                "framework": "claude-direct",
                "model": self.model,
                "retrieval_strategy": "hybrid",
                "chunks_retrieved": len(chunks),
                "chunks_used": len(citations),
                "token_usage": token_usage,
            },
        )

    @staticmethod
    def _build_context(chunks: list[RetrievedChunk]) -> str:
        blocks = []
        for i, chunk in enumerate(chunks, 1):
            blocks.append(
                f"[Context {i}] (p.{chunk.page}, {chunk.section})\n"
                f"{chunk.text}"
            )
        return "\n\n".join(blocks)

    @staticmethod
    def _extract_citations(
        chunks: list[RetrievedChunk],
    ) -> list[Citation]:
        seen = set()
        citations = []
        for chunk in chunks:
            key = (chunk.page, chunk.section)
            if key not in seen:
                seen.add(key)
                citations.append(
                    Citation(
                        page=chunk.page,
                        section=chunk.section,
                        quote=chunk.text[:200] + (
                            "..." if len(chunk.text) > 200 else ""
                        ),
                    )
                )
        return citations

    @staticmethod
    def _fallback_answer(chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return (
                "I cannot find this information "
                "in the Annual Report."
            )
        top = chunks[0]
        return (
            f"{top.text}\n\n"
            f"*Source: CBA Annual Report 2025, "
            f"p.{top.page} — {top.section}*"
        )


# Default export — agentic version
ClaudeQAGenerator = ClaudeAgentGenerator
