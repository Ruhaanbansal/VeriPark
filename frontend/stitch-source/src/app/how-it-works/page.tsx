import { BadgeCheck, Radar, Scale, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { BackHeader, Card, Screen } from "@/components/ui/Screen";

const POINTS = [
  {
    icon: Scale,
    title: "We weigh every reason by how much it matters",
    body: "A small detail that barely changes your price gets a quick glance. A factor that swings your price a lot gets checked much more carefully.",
  },
  {
    icon: Radar,
    title: "The biggest factors get rechecked live",
    body: "For anything with real weight on your price, we don't rely on old data — we ask the original source again, right now.",
  },
  {
    icon: ShieldCheck,
    title: "If a reason doesn't hold up, the price changes too",
    body: "We never let an explanation and a price disagree. If evidence for part of the price fails our check, that part is removed from the price itself, automatically.",
  },
  {
    icon: BadgeCheck,
    title: "Every decision is sealed, permanently",
    body: "The price, the reasons, and the checks are all recorded in a tamper-evident way — so the record can't quietly change later, by anyone, including us.",
  },
];

export default function HowItWorksPage() {
  return (
    <Screen>
      <BackHeader backHref="/" title="How VeriPark works" />
      <div className="flex-1 space-y-4 px-5 py-6">
        <p className="text-sm leading-relaxed text-[--color-slate]">
          Most apps show you a price. VeriPark shows you a price it can prove.
        </p>
        {POINTS.map((point) => (
          <Card key={point.title} className="flex gap-3.5">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[--color-teal-50] text-[--color-teal-dark]">
              <point.icon size={19} strokeWidth={2} />
            </span>
            <div>
              <p className="text-[14px] font-semibold text-[--color-charcoal]">{point.title}</p>
              <p className="mt-1 text-[13px] leading-relaxed text-[--color-slate]">{point.body}</p>
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
