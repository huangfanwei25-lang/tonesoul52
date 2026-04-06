import Link from "next/link";
import { Compass, Gauge, Layers3, Shield } from "lucide-react";

type TierModelPublicCueProps = {
  variant?: "compact" | "full";
};

const tierItems = [
  {
    icon: Gauge,
    label: "Tier 0",
    title: "Instant Gate",
    body: "Use this for the first safe move: readiness, track, mode, and the next bounded action.",
  },
  {
    icon: Compass,
    label: "Tier 1",
    title: "Orientation Shell",
    body: "Use this when continuation needs subsystem parity, canonical center, and closeout awareness without opening the whole stack.",
  },
  {
    icon: Layers3,
    label: "Tier 2",
    title: "Deep Governance",
    body: "Open this only for contested, risky, or system-track work. It is explicit pull, not default overhead.",
  },
];

export default function TierModelPublicCue({
  variant = "full",
}: TierModelPublicCueProps) {
  if (variant === "compact") {
    return (
      <section className="rounded-2xl border border-slate-200 bg-white px-4 py-4 shadow-sm">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-medium tracking-wide text-slate-600">
              <Shield className="h-3.5 w-3.5" />
              Demo-First Tier Cue
            </div>
            <p className="text-sm font-semibold text-slate-900">
              This page stays demo-first. It explains the tier model, but it is
              not the canonical operator console.
            </p>
            <p className="text-sm text-slate-600">
              Operator truth lives in the dashboard workspace and CLI entry
              flow. Deep governance remains explicit pull only.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
              Tier 0 | Gate
            </span>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
              Tier 1 | Orientation
            </span>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
              Tier 2 | Deep Pull
            </span>
            <Link
              href="/docs#workspace-tiers"
              className="rounded-full border border-slate-300 px-3 py-1 text-xs font-medium text-slate-800 transition-colors hover:bg-slate-100"
            >
              Learn the tiers
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section
      id="workspace-tiers"
      className="scroll-mt-28 rounded-2xl border border-slate-700/45 bg-slate-900/25 p-8"
    >
      <div className="mb-6 space-y-3">
        <div className="inline-flex items-center gap-2 rounded-full border border-slate-700/55 bg-slate-900/35 px-3 py-1 text-xs tracking-wide text-slate-300">
          <Shield className="h-4 w-4 text-sky-300" />
          Tiered Operator Boundary
        </div>
        <h2 className="text-2xl font-bold text-white">
          Tier Model | Public explanation, not operator truth
        </h2>
        <p className="max-w-3xl text-sm text-slate-300">
          ToneSoul uses a tiered operator model to keep reaction time low and
          governance boundaries visible. This docs surface explains the tiers,
          but live operator state still belongs to the dashboard workspace and
          CLI entry flow.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {tierItems.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.label}
              className="rounded-xl border border-slate-700/55 bg-slate-950/35 p-5"
            >
              <div className="mb-4 flex items-center gap-3">
                <div className="rounded-lg bg-sky-500/10 p-2 text-sky-300">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    {item.label}
                  </div>
                  <div className="font-semibold text-white">{item.title}</div>
                </div>
              </div>
              <p className="text-sm leading-6 text-slate-300">{item.body}</p>
            </div>
          );
        })}
      </div>

      <div className="mt-6 rounded-xl border border-amber-400/30 bg-amber-500/10 p-4">
        <p className="text-sm text-amber-100">
          Public and demo surfaces may teach the tier model and route readers
          correctly, but they must not impersonate the operator shell, render
          live session-start bundles, or treat descriptive summaries as verified
          governance truth.
        </p>
      </div>
    </section>
  );
}
