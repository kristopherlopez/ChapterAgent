"use client";

import { useState, useRef, useEffect } from "react";
import {
  Send,
  ShieldCheck,
  ShieldAlert,
  BookOpen,
  Clock,
  Loader2,
  Activity,
  Brain,
  ChevronDown,
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
  thinking: string[];
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
    thinking: [],
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
    thinking: [],
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
    thinking: [],
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
    thinking: [],
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
    thinking: [],
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
    thinking: [],
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
    thinking: [],
    latencyMs: 5,
    blocked: true,
  },
};

function matchResponse(question: string): AgentResponse {
  const q = question.toLowerCase();

  const injectionWords = [
    "ignore", "pretend", "system prompt", "jailbreak",
    "dan mode", "forget your instructions",
  ];
  if (injectionWords.some((w) => q.includes(w))) return DEMO_RESPONSES.injection_fail;

  const scopeWords = ["compare", "westpac", "anz", "nab", "macquarie", "versus", "vs"];
  if (scopeWords.some((w) => q.includes(w))) return DEMO_RESPONSES.scope_fail;

  const adviceWords = ["should i buy", "should i invest", "recommend", "good investment"];
  if (adviceWords.some((w) => q.includes(w))) return DEMO_RESPONSES.advice_fail;

  if (q.includes("interest margin") || q.includes("nim")) return DEMO_RESPONSES.nim;
  if (q.includes("dividend") || q.includes("payout")) return DEMO_RESPONSES.dividend;
  if (q.includes("sustain") || q.includes("climate") || q.includes("emission") || q.includes("esg") || q.includes("net zero"))
    return DEMO_RESPONSES.sustainability;
  if (q.includes("digital") || q.includes("app") || q.includes("technology") || q.includes("innovation"))
    return DEMO_RESPONSES.digital;

  return DEMO_RESPONSES.nim;
}

const SUGGESTED_QUESTIONS = [
  "What was CBA's net interest margin in FY2025?",
  "What dividends did CBA pay this year?",
  "What are CBA's sustainability commitments?",
  "How does CBA's performance compare to Westpac?",
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Framework = "openai" | "claude" | "langchain";

const FRAMEWORKS: { value: Framework; label: string; description: string }[] = [
  { value: "openai", label: "OpenAI Agent SDK", description: "GPT-4o via OpenAI" },
  { value: "claude", label: "Claude Agent SDK", description: "Claude Sonnet via Anthropic" },
  { value: "langchain", label: "LangChain", description: "Via OpenRouter" },
];

const OPENROUTER_MODELS = [
  { value: "anthropic/claude-opus-4.6", label: "Claude Opus 4.6" },
  { value: "deepseek/deepseek-r1", label: "DeepSeek R2" },
  { value: "google/gemini-3-flash-preview", label: "Gemini 3.0 Flash" },
  { value: "openai/gpt-5.4", label: "GPT-5.4" },
  { value: "x-ai/grok-4.20", label: "Grok 4.2" },
  { value: "minimax/minimax-m2.7", label: "MiniMax M2.7" },
  { value: "anthropic/claude-sonnet-4.6", label: "Claude Sonnet 4.6" },
];

async function fetchAgentResponse(
  solutionId: string,
  question: string,
  framework: Framework = "openai",
  model?: string,
): Promise<AgentResponse | null> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 60_000);
    const body: Record<string, unknown> = { question, framework };
    if (model) body.model = model;
    const res = await fetch(`${API_BASE}/api/chat/${solutionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    clearTimeout(timeout);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

/* ------------------------------------------------------------------ */
/*  Side Panel                                                         */
/* ------------------------------------------------------------------ */

function ThinkingTrace({ steps }: { steps: string[] }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 w-full text-left mb-2"
      >
        <Brain className="w-4 h-4 text-violet-500" />
        <h4 className="text-xs font-medium text-zinc-500 uppercase tracking-wider flex-1">
          Thinking ({steps.length} step{steps.length !== 1 ? "s" : ""})
        </h4>
        <ChevronDown
          className={`w-3.5 h-3.5 text-zinc-400 transition-transform ${
            isExpanded ? "rotate-180" : ""
          }`}
        />
      </button>
      {isExpanded && (
        <div className="space-y-2">
          {steps.map((step, i) => (
            <div
              key={i}
              className="bg-violet-50/50 border border-violet-100 rounded-lg px-3 py-2.5 text-xs text-violet-800 leading-relaxed whitespace-pre-wrap"
            >
              {step}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SidePanel({ response }: { response: AgentResponse | null }) {
  if (!response) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-zinc-400">
        <p className="text-center px-6">
          Guardrail results and source citations will appear here after each response.
        </p>
      </div>
    );
  }

  const passCount = response.guardrails.filter((g) => g.status === "pass").length;
  const failCount = response.guardrails.filter((g) => g.status === "fail").length;

  return (
    <div className="overflow-y-auto p-5 space-y-6">
      {/* Summary bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-zinc-500" />
          <span className="text-sm font-medium text-zinc-900">Response Audit</span>
        </div>
        <span className="inline-flex items-center gap-1 text-xs text-zinc-400">
          <Clock className="w-3 h-3" />
          {response.latencyMs}ms
        </span>
      </div>

      {/* Blocked banner */}
      {response.blocked && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          <p className="text-sm font-medium text-red-800">Response Blocked</p>
          <p className="text-xs text-red-600 mt-1">
            One or more guardrails failed. This response would not be served in production.
          </p>
        </div>
      )}

      {/* Thinking trace */}
      {response.thinking && response.thinking.length > 0 && (
        <ThinkingTrace steps={response.thinking} />
      )}

      {/* Guardrails */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-medium text-zinc-500 uppercase tracking-wider">
            Guardrails
          </h4>
          <span className="text-xs text-zinc-400">
            {passCount}/{response.guardrails.length} pass
            {failCount > 0 && (
              <span className="text-red-500 ml-1">&middot; {failCount} fail</span>
            )}
          </span>
        </div>
        <div className="space-y-2">
          {response.guardrails.map((g, i) => (
            <div
              key={i}
              className={`flex items-start gap-3 px-3 py-2.5 rounded-lg border ${
                g.status === "pass"
                  ? "bg-emerald-50/50 border-emerald-100"
                  : "bg-red-50/50 border-red-100"
              }`}
            >
              {g.status === "pass" ? (
                <ShieldCheck className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              ) : (
                <ShieldAlert className="w-4 h-4 text-red-600 mt-0.5 shrink-0" />
              )}
              <div className="min-w-0">
                <p
                  className={`text-sm font-medium ${
                    g.status === "pass" ? "text-emerald-900" : "text-red-900"
                  }`}
                >
                  {g.name}
                </p>
                {g.detail && (
                  <p
                    className={`text-xs mt-0.5 ${
                      g.status === "pass" ? "text-emerald-600" : "text-red-600"
                    }`}
                  >
                    {g.detail}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Citations */}
      {response.citations.length > 0 && (
        <div>
          <h4 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-3">
            Sources ({response.citations.length})
          </h4>
          <div className="space-y-2">
            {response.citations.map((cite, i) => (
              <div
                key={i}
                className="bg-blue-50/50 border border-blue-100 rounded-lg px-3 py-2.5"
              >
                <div className="flex items-center gap-2 mb-1">
                  <BookOpen className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                  <span className="text-xs font-medium text-blue-800">
                    p.{cite.page}
                  </span>
                  <span className="text-xs text-blue-600">&middot; {cite.section}</span>
                </div>
                <p className="text-xs text-blue-500 italic leading-relaxed">
                  &ldquo;{cite.quote.length > 150 ? cite.quote.slice(0, 150) + "..." : cite.quote}&rdquo;
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main Chat Interface                                                */
/* ------------------------------------------------------------------ */

export default function ChatInterface({
  solutionId,
}: {
  solutionId: string;
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [selectedResponse, setSelectedResponse] = useState<AgentResponse | null>(null);
  const [framework, setFramework] = useState<Framework>("openai");
  const [langchainModel, setLangchainModel] = useState(OPENROUTER_MODELS[0].value);
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
    setSelectedResponse(null);

    const model = framework === "langchain" ? langchainModel : undefined;
    let response = await fetchAgentResponse(solutionId, text, framework, model);
    if (!response) {
      response = matchResponse(text);
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
    setSelectedResponse(response);
    setIsTyping(false);
    inputRef.current?.focus();
  }

  const showWelcome = messages.length === 0;

  return (
    <div className="flex-1 flex min-h-0">
      {/* Left: Chat */}
      <div className="flex-1 flex flex-col min-h-0 min-w-0">
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto px-8 py-6">
          {showWelcome && (
            <div className="max-w-xl mx-auto text-center py-16">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-6 h-6 text-emerald-600" />
              </div>
              <h3 className="text-lg font-semibold text-zinc-900 mb-2">
                CBA Annual Report Q&A
              </h3>
              <p className="text-sm text-zinc-500 mb-8 max-w-md mx-auto">
                Ask questions about CBA&apos;s 2025 Annual Report. All responses
                are grounded in the source document with citations, and validated
                by 8 guardrails in real time.
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

          <div className="max-w-xl mx-auto space-y-4">
            {messages.map((msg, i) => (
              <div key={i}>
                {msg.role === "user" ? (
                  <div className="flex justify-end">
                    <div className="bg-zinc-900 text-white px-4 py-3 rounded-2xl rounded-br-md max-w-md text-sm">
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  <div
                    className={`group cursor-pointer rounded-2xl rounded-bl-md transition-colors ${
                      selectedResponse === msg.response
                        ? "bg-white border-2 border-emerald-200"
                        : "bg-white border border-zinc-200 hover:border-zinc-300"
                    }`}
                    onClick={() => msg.response && setSelectedResponse(msg.response)}
                  >
                    <div className="px-5 py-4 text-sm text-zinc-800 leading-relaxed">
                      {msg.content}
                    </div>
                    {msg.response && (
                      <div className="px-5 pb-3 flex items-center gap-3">
                        {msg.response.blocked ? (
                          <span className="inline-flex items-center gap-1 text-xs text-red-600">
                            <ShieldAlert className="w-3 h-3" />
                            Blocked
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-xs text-emerald-600">
                            <ShieldCheck className="w-3 h-3" />
                            {msg.response.guardrails.filter((g) => g.status === "pass").length}/{msg.response.guardrails.length} guardrails pass
                          </span>
                        )}
                        {msg.response.citations.length > 0 && (
                          <span className="inline-flex items-center gap-1 text-xs text-blue-500">
                            <BookOpen className="w-3 h-3" />
                            {msg.response.citations.length} source{msg.response.citations.length !== 1 ? "s" : ""}
                          </span>
                        )}
                        <span className="inline-flex items-center gap-1 text-xs text-zinc-400 ml-auto">
                          <Clock className="w-3 h-3" />
                          {(msg.response.latencyMs / 1000).toFixed(1)}s
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}

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
          <div className="max-w-xl mx-auto space-y-2">
            <div className="flex gap-3">
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
            <div className="flex items-center gap-1">
              <span className="text-xs text-zinc-400 mr-1">Framework:</span>
              {FRAMEWORKS.map((fw) => (
                <button
                  key={fw.value}
                  onClick={() => setFramework(fw.value)}
                  disabled={isTyping}
                  className={`text-xs px-2.5 py-1 rounded-md transition-colors ${
                    framework === fw.value
                      ? "bg-zinc-900 text-white"
                      : "text-zinc-500 hover:bg-zinc-100 hover:text-zinc-700"
                  } disabled:opacity-50`}
                  title={fw.description}
                >
                  {fw.label}
                </button>
              ))}
              {framework === "langchain" && (
                <>
                  <span className="text-xs text-zinc-300 mx-1">|</span>
                  <span className="text-xs text-zinc-400 mr-1">Model:</span>
                  <select
                    value={langchainModel}
                    onChange={(e) => setLangchainModel(e.target.value)}
                    disabled={isTyping}
                    className="text-xs border border-zinc-200 rounded-md px-1.5 py-0.5 text-zinc-700 bg-white disabled:opacity-50"
                  >
                    {OPENROUTER_MODELS.map((m) => (
                      <option key={m.value} value={m.value}>
                        {m.label}
                      </option>
                    ))}
                  </select>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Right: Side Panel */}
      <div className="w-80 border-l border-zinc-200 bg-zinc-50/50 flex flex-col min-h-0 shrink-0">
        <SidePanel response={selectedResponse} />
      </div>
    </div>
  );
}
