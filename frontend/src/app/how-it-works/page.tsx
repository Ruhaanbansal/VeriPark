import { BadgeCheck, Radar, Scale, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { BackHeader, Card, Screen } from "@/components/ui/Screen";

const POINTS = [
  {
    icon: Scale,
    title: "1. Materiality-guided verification",
    subtitle: "Component 1 (Patent-Critical)",
    body: "A small detail that barely changes your price gets a quick single-source glance. A factor that heavily swings your price gets routed to deep verification.",
    tone: "bg-[--color-brand-50] text-[--color-brand-mid] border-[--color-brand-100]",
  },
  {
    icon: Radar,
    title: "2. Live re-grounding from original sensors",
    subtitle: "Component 2 (Patent-Critical)",
    body: "For the highest-materiality factors, we never rely on stale cached snapshots. We query the original camera stream, gate sensor, or municipal schedule live.",
    tone: "bg-[--color-live-50] text-[--color-live] border-[--color-live-100]",
  },
  {
    icon: ShieldCheck,
    title: "3. Self-correcting decision clamping",
    subtitle: "Component 3 (Patent-Critical)",
    body: "If any reason fails our check, it is stripped from your bill automatically. The explanation and the decision cannot disagree.",
    tone: "bg-[--color-verified-50] text-[--color-verified] border-[--color-verified-100]",
  },
  {
    icon: BadgeCheck,
    title: "4. Cryptographically sealed audit ledger",
    subtitle: "Component 4 (Patent-Critical)",
    body: "The price, the reasons, and the verification hashes are sealed into an append-only SHA-256 ledger. Tampering is mathematically impossible.",
    tone: "bg-[--color-accent-50] text-[--color-accent-dark] border-[--color-accent-100]",
  },
];

export default function HowItWorksPage() {
  return (
    <Screen>
      <BackHeader backHref="/" title="How VeriPark works" />
      <div className="flex-1 space-y-4 px-5 py-6">
        <div className="rounded-2xl border border-[--color-border-soft] bg-[--color-brand-50] p-4 text-center">
          <p className="text-xs font-bold uppercase tracking-wider text-[--color-brand-mid]">VeriCore™ Assurance Engine</p>
          <p className="mt-1 text-sm font-semibold text-[--color-brand-dark]">
            Most apps show you a price. VeriPark shows you a price it can prove.
          </p>
        </div>

        {POINTS.map((point) => (
          <Card key={point.title} className="flex gap-4 p-4 hover:shadow-soft-lg transition-shadow">
            <span className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl border ${point.tone} shadow-soft`}>
              <point.icon size={21} strokeWidth={2.2} />
            </span>
            <div className="min-w-0">
              <p className="text-[10px] font-bold uppercase tracking-wider text-[--color-slate-light]">{point.subtitle}</p>
              <p className="text-[14px] font-bold text-[--color-charcoal]">{point.title}</p>
              <p className="mt-1 text-[13px] leading-relaxed text-[--color-slate] font-medium">{point.body}</p>
            </div>
          </Card>
        ))}
      </div>
      <div className="px-5 pb-8">
        <Button href="/search" fullWidth size="lg">
          Find Parking
        </Button>
      </div>
    </Screen>
  );
}
