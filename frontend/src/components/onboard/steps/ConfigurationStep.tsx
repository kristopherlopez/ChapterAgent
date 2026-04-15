import { Plus, X } from "lucide-react";
import type { OnboardFormData, CorpusDocument, FrameworkEntry } from "@/app/onboard/page";

interface Props {
  data: OnboardFormData;
  onChange: (patch: Partial<OnboardFormData>) => void;
}

const inputClass =
  "w-full px-3 py-2 border border-zinc-200 rounded-md text-sm text-zinc-900 bg-white focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:border-transparent";

const FRAMEWORK_OPTIONS = ["claude-agent-sdk", "openai-sdk", "langchain-langgraph"];
const RETRIEVAL_OPTIONS = ["vector", "hybrid", "agentic"];

function EndpointFields({ data, onChange }: Props) {
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-zinc-700 mb-1">Endpoint URL</label>
        <input
          type="text"
          value={data.endpoint_url}
          onChange={(e) => onChange({ endpoint_url: e.target.value })}
          placeholder="http://localhost:8002/classify"
          className={inputClass}
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">HTTP Method</label>
          <select
            value={data.endpoint_method}
            onChange={(e) => onChange({ endpoint_method: e.target.value })}
            className={inputClass}
          >
            <option value="POST">POST</option>
            <option value="GET">GET</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">Timeout (ms)</label>
          <input
            type="number"
            value={data.endpoint_timeout_ms}
            onChange={(e) => onChange({ endpoint_timeout_ms: parseInt(e.target.value) || 30000 })}
            className={inputClass}
          />
        </div>
      </div>
    </div>
  );
}

function ScoringFields({ data, onChange }: Props) {
  return (
    <div className="space-y-4">
      <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Model</p>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">Model Type</label>
          <input
            type="text"
            value={data.model_type}
            onChange={(e) => onChange({ model_type: e.target.value })}
            placeholder="e.g. LogisticRegression"
            className={inputClass}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">Framework</label>
          <input
            type="text"
            value={data.model_framework}
            onChange={(e) => onChange({ model_framework: e.target.value })}
            placeholder="e.g. scikit-learn"
            className={inputClass}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">Explainability</label>
          <select
            value={data.model_explainability}
            onChange={(e) => onChange({ model_explainability: e.target.value })}
            className={inputClass}
          >
            <option value="SHAP">SHAP</option>
            <option value="LIME">LIME</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">Training Split</label>
          <input
            type="number"
            step="0.05"
            min="0.5"
            max="0.9"
            value={data.model_training_split}
            onChange={(e) => onChange({ model_training_split: parseFloat(e.target.value) || 0.7 })}
            className={inputClass}
          />
        </div>
      </div>

      <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider pt-4">Dataset</p>
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <label className="block text-sm font-medium text-zinc-700 mb-1">Data Source</label>
          <input
            type="text"
            value={data.dataset_source}
            onChange={(e) => onChange({ dataset_source: e.target.value })}
            placeholder="e.g. UCI Machine Learning Repository"
            className={inputClass}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">Records</label>
          <input
            type="number"
            value={data.dataset_records}
            onChange={(e) => onChange({ dataset_records: parseInt(e.target.value) || 0 })}
            className={inputClass}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">Features</label>
          <input
            type="number"
            value={data.dataset_features}
            onChange={(e) => onChange({ dataset_features: parseInt(e.target.value) || 0 })}
            className={inputClass}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">Target Column</label>
          <input
            type="text"
            value={data.dataset_target}
            onChange={(e) => onChange({ dataset_target: e.target.value })}
            placeholder="e.g. A15"
            className={inputClass}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-700 mb-1">Protected Attributes</label>
          <input
            type="text"
            value={data.dataset_protected_attributes}
            onChange={(e) => onChange({ dataset_protected_attributes: e.target.value })}
            placeholder="Comma-separated (e.g. gender, age)"
            className={inputClass}
          />
        </div>
      </div>
    </div>
  );
}

function QAFields({ data, onChange }: Props) {
  const addDocument = () => {
    onChange({
      corpus_documents: [
        ...data.corpus_documents,
        { name: "", format: "pdf", pages: 0 },
      ],
    });
  };

  const removeDocument = (i: number) => {
    onChange({
      corpus_documents: data.corpus_documents.filter((_, idx) => idx !== i),
    });
  };

  const updateDocument = (i: number, patch: Partial<CorpusDocument>) => {
    const updated = data.corpus_documents.map((d, idx) =>
      idx === i ? { ...d, ...patch } : d,
    );
    onChange({ corpus_documents: updated });
  };

  const toggleFramework = (name: string) => {
    const exists = data.frameworks.find((f) => f.name === name);
    if (exists) {
      onChange({ frameworks: data.frameworks.filter((f) => f.name !== name) });
    } else {
      onChange({
        frameworks: [...data.frameworks, { name, retrieval_strategies: ["vector"] }],
      });
    }
  };

  const toggleStrategy = (fwName: string, strategy: string) => {
    const updated: FrameworkEntry[] = data.frameworks.map((f) => {
      if (f.name !== fwName) return f;
      const has = f.retrieval_strategies.includes(strategy);
      return {
        ...f,
        retrieval_strategies: has
          ? f.retrieval_strategies.filter((s) => s !== strategy)
          : [...f.retrieval_strategies, strategy],
      };
    });
    onChange({ frameworks: updated });
  };

  return (
    <div className="space-y-4">
      <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Corpus</p>
      <div>
        <label className="block text-sm font-medium text-zinc-700 mb-1">Source</label>
        <input
          type="text"
          value={data.corpus_source}
          onChange={(e) => onChange({ corpus_source: e.target.value })}
          placeholder="e.g. PetSure Australia Investor Relations"
          className={inputClass}
        />
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-zinc-700">Documents</label>
          <button
            type="button"
            onClick={addDocument}
            className="inline-flex items-center gap-1 text-xs text-zinc-600 hover:text-zinc-900"
          >
            <Plus className="w-3 h-3" /> Add
          </button>
        </div>
        {data.corpus_documents.map((doc, i) => (
          <div key={i} className="flex items-center gap-2 mb-2">
            <input
              type="text"
              value={doc.name}
              onChange={(e) => updateDocument(i, { name: e.target.value })}
              placeholder="Document name"
              className={`flex-1 ${inputClass}`}
            />
            <select
              value={doc.format}
              onChange={(e) => updateDocument(i, { format: e.target.value })}
              className={`w-24 ${inputClass}`}
            >
              <option value="pdf">PDF</option>
              <option value="markdown">Markdown</option>
              <option value="csv">CSV</option>
            </select>
            <input
              type="number"
              value={doc.pages}
              onChange={(e) => updateDocument(i, { pages: parseInt(e.target.value) || 0 })}
              placeholder="Pages"
              className={`w-20 ${inputClass}`}
            />
            <button type="button" onClick={() => removeDocument(i)} className="text-zinc-400 hover:text-red-500">
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>

      <p className="text-xs font-medium text-zinc-400 uppercase tracking-wider pt-4">Frameworks</p>
      <div className="space-y-3">
        {FRAMEWORK_OPTIONS.map((fw) => {
          const selected = data.frameworks.find((f) => f.name === fw);
          return (
            <div key={fw}>
              <button
                type="button"
                onClick={() => toggleFramework(fw)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium border transition-colors ${
                  selected
                    ? "bg-zinc-900 text-white border-zinc-900"
                    : "bg-white text-zinc-500 border-zinc-200 hover:border-zinc-300"
                }`}
              >
                {fw}
              </button>
              {selected && (
                <div className="flex gap-2 mt-2 ml-4">
                  {RETRIEVAL_OPTIONS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => toggleStrategy(fw, s)}
                      className={`px-2 py-1 rounded text-xs border transition-colors ${
                        selected.retrieval_strategies.includes(s)
                          ? "bg-zinc-700 text-white border-zinc-700"
                          : "bg-white text-zinc-400 border-zinc-200 hover:border-zinc-300"
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function ConfigurationStep({ data, onChange }: Props) {
  return (
    <div>
      {data.type === "endpoint" && <EndpointFields data={data} onChange={onChange} />}
      {data.type === "scoring" && <ScoringFields data={data} onChange={onChange} />}
      {data.type === "qa" && <QAFields data={data} onChange={onChange} />}
    </div>
  );
}
