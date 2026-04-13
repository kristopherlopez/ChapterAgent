"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  ShieldCheck,
  BarChart3,
  LayoutDashboard,
  ClipboardList,
  FileText,
  BrainCircuit,
  TrendingUp,
  Package,
  Plus,
} from "lucide-react";
import { solutions } from "@/lib/data";

const navItems = [
  { href: "/", label: "Compliance Health", icon: LayoutDashboard },
  { href: "/scorecard", label: "Framework Scorecard", icon: BarChart3 },
];

const aiSolutions = solutions.filter((s) => s.category === "ai");
const mlSolutions = solutions.filter((s) => s.category === "ml");

function HealthDot({ health }: { health: string }) {
  const color =
    health === "pass"
      ? "bg-emerald-400"
      : health === "warn"
        ? "bg-amber-400"
        : "bg-red-400";
  return <span className={`w-2 h-2 rounded-full ${color} shrink-0`} />;
}

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-zinc-200 bg-zinc-50 flex flex-col h-full">
      <div className="p-6 border-b border-zinc-200">
        <h1 className="text-lg font-semibold text-zinc-900">
          Chapter AI Platform
        </h1>
        <p className="text-xs text-zinc-500 mt-1">
          Risk Management AI Capability
        </p>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-zinc-900 text-white"
                  : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}

        {/* Platform */}
        <div className="pt-4 pb-2">
          <p className="px-3 text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Platform
          </p>
        </div>

        <Link
          href="/onboard"
          className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
            pathname.startsWith("/onboard")
              ? "bg-zinc-900 text-white"
              : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
          }`}
        >
          <Plus className="w-4 h-4" />
          Onboard Solution
        </Link>

        <Link
          href="/registry"
          className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
            pathname === "/registry"
              ? "bg-zinc-900 text-white"
              : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
          }`}
        >
          <ClipboardList className="w-4 h-4" />
          Solution Registry
        </Link>

        <Link
          href="/controls"
          className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
            pathname === "/controls"
              ? "bg-zinc-900 text-white"
              : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Controls Register
        </Link>

        <Link
          href="/documents"
          className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
            pathname === "/documents"
              ? "bg-zinc-900 text-white"
              : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
          }`}
        >
          <FileText className="w-4 h-4" />
          Documents
        </Link>

        <Link
          href="/catalog"
          className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
            pathname.startsWith("/catalog")
              ? "bg-zinc-900 text-white"
              : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
          }`}
        >
          <Package className="w-4 h-4" />
          Component Catalog
        </Link>

        {/* AI Solutions */}
        <div className="pt-4 pb-2">
          <p className="px-3 text-xs font-medium text-zinc-400 uppercase tracking-wider flex items-center gap-2">
            <BrainCircuit className="w-3 h-3" />
            AI Solutions
          </p>
        </div>

        {aiSolutions.map((solution) => {
          const isActive = pathname.startsWith(`/solutions/${solution.id}`);
          return (
            <Link
              key={solution.id}
              href={`/solutions/${solution.id}`}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-zinc-900 text-white"
                  : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
              }`}
            >
              <Shield className="w-4 h-4 shrink-0" />
              <span className="truncate flex-1">{solution.name}</span>
              <HealthDot health={solution.health} />
            </Link>
          );
        })}

        {/* ML Solutions */}
        <div className="pt-4 pb-2">
          <p className="px-3 text-xs font-medium text-zinc-400 uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-3 h-3" />
            ML Solutions
          </p>
        </div>

        {mlSolutions.map((solution) => {
          const isActive = pathname.startsWith(`/solutions/${solution.id}`);
          return (
            <Link
              key={solution.id}
              href={`/solutions/${solution.id}`}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-zinc-900 text-white"
                  : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
              }`}
            >
              <Shield className="w-4 h-4 shrink-0" />
              <span className="truncate flex-1">{solution.name}</span>
              <HealthDot health={solution.health} />
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
