"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield,
  BarChart3,
  Activity,
  LayoutDashboard,
} from "lucide-react";
import { solutions } from "@/lib/data";

const navItems = [
  { href: "/", label: "Compliance Health", icon: LayoutDashboard },
  { href: "/scorecard", label: "Framework Scorecard", icon: BarChart3 },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-zinc-200 bg-zinc-50 flex flex-col h-full">
      <div className="p-6 border-b border-zinc-200">
        <h1 className="text-lg font-semibold text-zinc-900">
          Chapter AI Platform
        </h1>
        <p className="text-xs text-zinc-500 mt-1">Risk Management</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
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

        <div className="pt-4 pb-2">
          <p className="px-3 text-xs font-medium text-zinc-400 uppercase tracking-wider">
            Solutions
          </p>
        </div>

        {solutions.map((solution) => {
          const isActive = pathname === `/solutions/${solution.id}`;
          const traceActive = pathname === `/traces/${solution.id}`;
          return (
            <div key={solution.id}>
              <Link
                href={`/solutions/${solution.id}`}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive
                    ? "bg-zinc-900 text-white"
                    : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                }`}
              >
                <Shield className="w-4 h-4" />
                {solution.name}
              </Link>
              <Link
                href={`/traces/${solution.id}`}
                className={`flex items-center gap-3 px-3 py-2 pl-10 rounded-md text-xs transition-colors ${
                  traceActive
                    ? "bg-zinc-900 text-white"
                    : "text-zinc-400 hover:bg-zinc-100 hover:text-zinc-600"
                }`}
              >
                <Activity className="w-3 h-3" />
                Traces
              </Link>
            </div>
          );
        })}
      </nav>
    </aside>
  );
}
