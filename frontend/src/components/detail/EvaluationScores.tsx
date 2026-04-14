import { EvaluationScore } from "@/lib/types";
import HealthBadge from "@/components/dashboard/HealthBadge";
import { Info } from "lucide-react";

const METRIC_TOOLTIPS: Record<string, string> = {
  "AUC-ROC":
    "Area Under the Receiver Operating Characteristic curve. Measures how well the model distinguishes between classes. 1.0 = perfect, 0.5 = random chance.",
  "Gini":
    "Gini coefficient (2 × AUC − 1). Measures the model's discriminatory power. Higher is better; 0 = no discrimination, 1 = perfect.",
  "Brier Score":
    "Mean squared error of predicted probabilities vs actual outcomes. Lower is better; 0 = perfect calibration, 1 = worst.",
  "ECE":
    "Expected Calibration Error. Measures how well predicted probabilities match observed frequencies. Lower is better; 0 = perfectly calibrated.",
  "Demographic Parity Diff":
    "Difference in positive prediction rates across demographic groups. Lower is fairer; 0 = equal rates across groups.",
  "Equalised Odds Diff":
    "Difference in true positive and false positive rates across groups. Lower is fairer; 0 = equal error rates.",
  "Disparate Impact Ratio":
    "Ratio of positive prediction rates between groups. Values close to 1.0 indicate fairness; below 0.8 is typically flagged.",
  "PSI":
    "Population Stability Index. Detects distribution shift between training and scoring data. < 0.1 = stable, 0.1–0.25 = moderate shift, > 0.25 = significant drift.",
  "SHAP Coverage":
    "Proportion of predictions with SHAP explanations available. 1.0 = every prediction is fully explainable.",
  "Hosmer-Lemeshow p":
    "Hosmer-Lemeshow goodness-of-fit test p-value. Higher means better calibration; p < 0.05 suggests poor fit.",
  "Bootstrap CI Width (AUC)":
    "Width of the bootstrapped confidence interval for AUC. Narrower = more stable performance estimate.",
  "Subgroup Approval Variance":
    "Variance in approval rates across demographic subgroups. Lower is fairer; high values indicate disparate treatment.",
  "Faithfulness":
    "Measures whether the answer is grounded in the provided context. Higher is better; 1.0 = fully faithful to source material.",
  "Answer Relevancy":
    "Measures how relevant the generated answer is to the question asked. Higher is better.",
  "Context Precision":
    "Proportion of retrieved context chunks that are actually relevant to the question. Higher is better.",
  "Context Recall":
    "Proportion of relevant information from the ground truth that appears in retrieved context. Higher is better.",
  "Hallucination":
    "Rate of generated claims not supported by the provided context. Lower is better; 0 = no hallucinations.",
  "Citation Coverage":
    "Proportion of claims in the answer that are backed by a citation. Higher is better; 1.0 = every claim cited.",
  "Boundary Adherence":
    "How well the model stays within its defined scope and refuses out-of-scope questions. Higher is better.",
  "Temporal Accuracy":
    "Accuracy of date and time references in generated answers. Higher is better.",
  "Bias":
    "Rate of biased or prejudiced content in model outputs. Lower is better; 0 = no detected bias.",
  "Toxicity":
    "Rate of toxic or harmful content in model outputs. Lower is better; 0 = no detected toxicity.",
};

export default function EvaluationScores({ scores }: { scores: EvaluationScore[] }) {
  return (
    <div className="bg-white border border-zinc-200 rounded-lg">
      <div className="px-6 py-4 border-b border-zinc-100">
        <h3 className="text-sm font-semibold text-zinc-900">Evaluation Scores</h3>
      </div>
      <div className="divide-y divide-zinc-100">
        {scores.map((s) => (
          <div key={s.metric} className="grid grid-cols-[1fr_80px_80px_80px] items-center gap-4 px-6 py-3">
            <div className="flex items-center gap-1.5">
              <p className="text-sm text-zinc-700">{s.metric}</p>
              {METRIC_TOOLTIPS[s.metric] && (
                <div className="relative group">
                  <Info className="w-3.5 h-3.5 text-zinc-400 cursor-help" />
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50">
                    <div className="bg-zinc-900 text-white text-xs rounded-lg px-3 py-2 w-64 shadow-lg leading-relaxed">
                      {METRIC_TOOLTIPS[s.metric]}
                      <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-zinc-900" />
                    </div>
                  </div>
                </div>
              )}
            </div>
            <p className="text-sm font-mono text-zinc-900">
              {s.score === 0 && s.status === "warn" ? "—" : s.score.toFixed(2)}
            </p>
            <p className="text-xs text-zinc-400">min {s.threshold.toFixed(2)}</p>
            <HealthBadge status={s.status} />
          </div>
        ))}
      </div>
    </div>
  );
}
