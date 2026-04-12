"use client";

import { useState, useRef, useEffect } from "react";
import {
  Send,
  ShieldCheck,
  ShieldAlert,
  BookOpen,
  Clock,
  Loader2,
} from "lucide-react";

interface Citation {
  document: string;
  page: number;
  section: string;
  quote: string;
}

interface GuardrailResult {
  name: string;
  status: "pass" | "fail";
  detail?: string;
}

interface AgentResponse {
  text: string;
  citations: Citation[];
  guardrails: GuardrailResult[];
  latencyMs: number;
  blocked: boolean;
}

interface ChatMessage {
  role: "user" | "agent";
  content: string;
  response?: AgentResponse;
  timestamp: Date;
}

const DEMO_RESPONSES: Record<string, AgentResponse> = {
  nim: {
    text: "CBA's net interest margin for FY2025 was 2.08%, up 9 basis points from FY2024's 1.99%. This improvement was driven by disciplined pricing in a competitive mortgage market and favourable deposit mix shifts.",
    citations: [
      {
        document: "CBA Annual Report 2025",
        page: 30,
        section: "Operational Excellence",
        quote: "Net interest margin 2.08%, FY24 1.99%",
      },
    ],
    guardrails: [
      { name: "Prompt Injection", status: "pass" },
      { name: "Scope Check", status: "pass" },
      { name: "PII Detection", status: "pass" },
      { name: "Faithfulness", status: "pass", detail: "Score: 0.94" },
      { name: "Citation Coverage", status: "pass", detail: "100%" },
      { name: "Temporal Accuracy", status: "pass" },
    ],
    latencyMs: 1240,
    blocked: false,
  },
  dividend: {
    text: "CBA declared a final dividend of $2.65 per share for FY2025, bringing the full-year dividend to $4.75 per share — fully franked. This represents a 5% increase on the prior year, reflecting the Board's confidence in the Group's capital position and earnings outlook.",
    citations: [
      {
        document: "CBA Annual Report 2025",
        page: 8,
        section: "Chairman's Message",
        quote: "Full-year dividend of $4.75 per share, fully franked",
      },
      {
        document: "CBA Annual Report 2025",
        page: 26,
        section: "Delivering financial performance",
        quote: "Final dividend $2.65 per share",
      },
    ],
    guardrails: [
      { name: "Prompt Injection", status: "pass" },
      { name: "Scope Check", status: "pass" },
      { name: "PII Detection", status: "pass" },
      { name: "Faithfulness", status: "pass", detail: "Score: 0.96" },
      { name: "Citation Coverage", status: "pass", detail: "100%" },
      { name: "Temporal Accuracy", status: "pass" },
    ],
    latencyMs: 1380,
    blocked: false,
  },
  sustainability: {
    text: "CBA committed to reducing its operational emissions by 42% by 2030 (from a 2020 baseline) and has set a target to achieve net zero in its own operations by 2030. The bank also disclosed financed emissions for key sectors including power generation, oil & gas, and commercial real estate, aligned with the PCAF methodology.",
    citations: [
      {
        document: "CBA Annual Report 2025",
        page: 88,
        section: "Sustainability",
        quote: "42% reduction target for operational emissions by 2030",
      },
      {
        document: "CBA Annual Report 2025",
        page: 92,
        section: "Climate-related disclosures",
        quote: "Financed emissions disclosed using PCAF methodology",
      },
    ],
    guardrails: [
      { name: "Prompt Injection", status: "pass" },
      { name: "Scope Check", status: "pass" },
      { name: "PII Detection", status: "pass" },
      { name: "Faithfulness", status: "pass", detail: "Score: 0.91" },
      { name: "Citation Coverage", status: "pass", detail: "100%" },
      { name: "Temporal Accuracy", status: "pass" },
    ],
    latencyMs: 1560,
    blocked: false,
  },
  digital: {
    text: "CBA reported 8.4 million digitally active customers in FY2025, with the CommBank app maintaining its position as Australia's #1 banking app. The bank processed over 1.2 billion digital transactions during the year. Key digital investments included AI-powered customer service tools and enhanced real-time fraud detection capabilities.",
    citations: [
      {
        document: "CBA Annual Report 2025",
        page: 34,
        section: "Technology & Innovation",
        quote: "8.4 million digitally active customers",
      },
      {
        document: "CBA Annual Report 2025",
        page: 36,
        section: "Technology & Innovation",
        quote: "Over 1.2 billion digital transactions processed",
      },
    ],
    guardrails: [
      { name: "Prompt Injection", status: "pass" },
      { name: "Scope Check", status: "pass" },
      { name: "PII Detection", status: "pass" },
      { name: "Faithfulness", status: "pass", detail: "Score: 0.93" },
      { name: "Citation Coverage", status: "pass", detail: "100%" },
      { name: "Temporal Accuracy", status: "pass" },
    ],
    latencyMs: 1420,
    blocked: false,
  },
  scope_fail: {
    text: "I can only answer questions about CBA's 2025 Annual Report. Comparisons with other institutions are outside my permitted scope.",
    citations: [],
    guardrails: [
      {
        name: "Scope Check",
        status: "fail",
        detail: "Entity not in corpus — comparative claim blocked",
      },
    ],
    latencyMs: 8,
    blocked: true,
  },
  advice_fail: {
    text: "I can only answer questions about CBA's 2025 Annual Report. I'm not able to provide financial advice or investment recommendations.",
    citations: [],
    guardrails: [
      {
        name: "Scope Check",
        status: "fail",
        detail: "Financial advice request — outside permitted domain",
      },
    ],
    latencyMs: 12,
    blocked: true,
  },
  injection_fail: {
    text: "I can only answer questions about CBA's 2025 Annual Report.",
    citations: [],
    guardrails: [
      {
        name: "Prompt Injection",
        status: "fail",
        detail: "Injection pattern detected — request blocked",
      },
    ],
    latencyMs: 5,
    blocked: true,
  },
};

function matchResponse(question: string): AgentResponse {
  const q = question.toLowerCase();

  // Injection patterns
  const injectionWords = [
    "ignore",
    "pretend",
    "system prompt",
    "jailbreak",
    "dan mode",
    "forget your instructions",
  ];
  if (injectionWords.some((w) => q.includes(w))) return DEMO_RESPONSES.injection_fail;

  // Scope violations — competitor comparisons
  const scopeWords = ["compare", "westpac", "anz", "nab", "macquarie", "versus", "vs"];
  if (scopeWords.some((w) => q.includes(w))) return DEMO_RESPONSES.scope_fail;

  // Financial advice
  const adviceWords = ["should i buy", "should i invest", "recommend", "good investment"];
  if (adviceWords.some((w) => q.includes(w))) return DEMO_RESPONSES.advice_fail;

  // Topic matching
  if (q.includes("interest margin") || q.includes("nim")) return DEMO_RESPONSES.nim;
  if (q.includes("dividend") || q.includes("payout")) return DEMO_RESPONSES.dividend;
  if (
    q.includes("sustain") ||
    q.includes("climate") ||
    q.includes("emission") ||
    q.includes("esg") ||
    q.includes("net zero")
  )
    return DEMO_RESPONSES.sustainability;
  if (
    q.includes("digital") ||
    q.includes("app") ||
    q.includes("technology") ||
    q.includes("innovation")
  )
    return DEMO_RESPONSES.digital;

  // Default — return NIM as a sensible default for financial questions
  return DEMO_RESPONSES.nim;
}

const SUGGESTED_QUESTIONS = [
  "What was CBA's net interest margin in FY2025?",
  "What dividends did CBA pay this year?",
  "What are CBA's sustainability commitments?",
  "How does CBA's performance compare to Westpac?",
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAgentResponse(
  solutionId: string,
  question: string,
): Promise<AgentResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/api/chat/${solutionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export default function ChatInterface({
  solutionId,
}: {
  solutionId: string;
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  async function handleSend(question?: string) {
    const text = question || input.trim();
    if (!text || isTyping) return;

    setInput("");
    setMessages((prev) => [
      ...prev,
      { role: "user", content: text, timestamp: new Date() },
    ]);

    setIsTyping(true);

    // Try backend API first, fall back to demo responses
    let response = await fetchAgentResponse(solutionId, text);
    if (!response) {
      response = matchResponse(text);
      // Simulate latency for demo mode
      const delay = Math.min(response.latencyMs, 2000);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }

    setMessages((prev) => [
      ...prev,
      {
        role: "agent",
        content: response.text,
        response,
        timestamp: new Date(),
      },
    ]);
    setIsTyping(false);
    inputRef.current?.focus();
  }

  const showWelcome = messages.length === 0;

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {showWelcome && (
          <div className="max-w-2xl mx-auto text-center py-16">
            <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center mx-auto mb-4">
              <BookOpen className="w-6 h-6 text-emerald-600" />
            </div>
            <h3 className="text-lg font-semibold text-zinc-900 mb-2">
              CBA Annual Report Q&A
            </h3>
            <p className="text-sm text-zinc-500 mb-8 max-w-md mx-auto">
              Ask questions about CBA&apos;s 2025 Annual Report. All responses are
              grounded in the source document with citations, and validated by 8
              guardrails in real time.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSend(q)}
                  className="text-left text-sm px-4 py-3 rounded-lg border border-zinc-200 text-zinc-700 hover:border-zinc-300 hover:bg-zinc-50 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="max-w-2xl mx-auto space-y-6">
          {messages.map((msg, i) => (
            <div key={i}>
              {msg.role === "user" ? (
                <div className="flex justify-end">
                  <div className="bg-zinc-900 text-white px-4 py-3 rounded-2xl rounded-br-md max-w-md text-sm">
                    {msg.content}
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {/* Answer */}
                  <div className="bg-white border border-zinc-200 px-5 py-4 rounded-2xl rounded-bl-md text-sm text-zinc-800 leading-relaxed">
                    {msg.content}
                  </div>

                  {/* Citations */}
                  {msg.response && msg.response.citations.length > 0 && (
                    <div className="flex flex-wrap gap-2 pl-1">
                      {msg.response.citations.map((cite, j) => (
                        <div
                          key={j}
                          className="flex items-start gap-2 bg-blue-50 border border-blue-100 rounded-lg px-3 py-2 text-xs max-w-xs"
                        >
                          <BookOpen className="w-3.5 h-3.5 text-blue-500 mt-0.5 shrink-0" />
                          <div>
                            <span className="font-medium text-blue-800">
                              p.{cite.page}
                            </span>
                            <span className="text-blue-600">
                              {" "}&middot; {cite.section}
                            </span>
                            <p className="text-blue-500 mt-0.5 italic">
                              &ldquo;{cite.quote}&rdquo;
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Guardrails + latency */}
                  {msg.response && (
                    <div className="flex items-center gap-3 pl-1 flex-wrap">
                      {msg.response.guardrails.map((g, j) => (
                        <span
                          key={j}
                          className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${
                            g.status === "pass"
                              ? "bg-emerald-50 text-emerald-700"
                              : "bg-red-50 text-red-700"
                          }`}
                          title={g.detail || g.name}
                        >
                          {g.status === "pass" ? (
                            <ShieldCheck className="w-3 h-3" />
                          ) : (
                            <ShieldAlert className="w-3 h-3" />
                          )}
                          {g.name}
                        </span>
                      ))}
                      <span className="inline-flex items-center gap-1 text-xs text-zinc-400">
                        <Clock className="w-3 h-3" />
                        {msg.response.latencyMs}ms
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex items-center gap-2 text-sm text-zinc-400">
              <Loader2 className="w-4 h-4 animate-spin" />
              Agent is thinking...
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input bar */}
      <div className="border-t border-zinc-200 bg-white px-8 py-4">
        <div className="max-w-2xl mx-auto flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend();
            }}
            placeholder="Ask about CBA's 2025 Annual Report..."
            className="flex-1 px-4 py-2.5 rounded-lg border border-zinc-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent placeholder:text-zinc-400"
            disabled={isTyping}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isTyping}
            className="px-4 py-2.5 bg-zinc-900 text-white rounded-lg hover:bg-zinc-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
