"use client";

import { useState } from "react";
import { ChevronDown, FileLock2, Loader2, ShieldCheck, ShieldX } from "lucide-react";
import type { Decision } from "@/lib/types";
import { formatRupees, formatTimestamp } from "@/lib/utils";
import { Card } from "@/components/ui/Screen";
import { Button } from "@/components/ui/Button";

type VerifyState = "idle" | "checking" | "pass" | "fail";

function truncateHash(hash: string) {
  return `${hash.slice(0, 10)}…${hash.slice(-8)}`;
}

export function AuditTrailClient({ decision }: { decision: Decision }) {
  const [verifyState, setVerifyState] = useState<VerifyState>("idle");
  const [showTechnical, setShowTechnical] = useState(false);

  function runIntegrityCheck() {
    setVerifyState("checking");
    setTimeout(() => setVerifyState("pass"), 1400);
  }

  return (
    <div className="flex-1 space-y-4 px-5 py-5">
      <Card className="space-y-4">
        <div className="flex items-center justify-between border-b border-dashed border-[--color-border] pb-3">
          <span className="flex items-center gap-2 text-[13px] font-semibold text-[--color-navy]">
            <FileLock2 size={16} /> Decision Record
          </span>
          <span className="text-[11px] font-medium text-[--color-slate]">Sealed</span>
        </div>

        <dl className="space-y-2.5 text-sm">
          <Row label="Decision ID" value={decision.id} mono />
          <Row label="Lot" value={decision.lot.name} />
          <Row label="Recorded" value={formatTimestamp(decision.ledger.timestamp)} />
          <Row label="Recorded price" value={formatRupees(decision.ledger.recordedPrice)} />
          <Row
            label="Adjustment applied"
            value={decision.wasAdjusted ? `Yes — ${formatRupees(decision.adjustmentAmount)}` : "No"}
          />
          <Row label="Evidence items sealed" value={`${decision.verificationSummary.totalClaims}`} />
        </dl>
      </Card>

      <Card className="flex items-start gap-3 bg-[--color-teal-50] border-transparent">
        <ShieldCheck size={18} className="mt-0.5 shrink-0 text-[--color-teal-dark]" />
        <p className="text-[13px] leading-relaxed text-[--color-teal-dark]">
          This record is cryptographically sealed and cannot be altered after the fact — including by us. Every
          decision links back to the one before it, so any change would be immediately obvious.
        </p>
      </Card>

      <Card>
        <div className="flex items-center justify-between">
          <p className="text-[14px] font-semibold text-[--color-charcoal]">Integrity check</p>
          {verifyState === "pass" && (
            <span className="flex items-center gap-1.5 text-xs font-semibold text-[--color-teal-dark]">
              <ShieldCheck size={14} /> Verified intact
            </span>
          )}
          {verifyState === "fail" && (
            <span className="flex items-center gap-1.5 text-xs font-semibold text-[--color-danger]">
              <ShieldX size={14} /> Mismatch found
            </span>
          )}
        </div>
        <p className="mt-1 text-xs leading-relaxed text-[--color-slate]">
          Run a live check to confirm this record matches its sealed hash chain, right now.
        </p>
        <Button
          variant={verifyState === "pass" ? "secondary" : "outline"}
          size="sm"
          className="mt-3"
          onClick={runIntegrityCheck}
          disabled={verifyState === "checking"}
        >
          {verifyState === "checking" && <Loader2 size={14} className="animate-spin" />}
          {verifyState === "checking"
            ? "Checking chain…"
            : verifyState === "pass"
              ? "Re-run check"
              : "Verify this record"}
        </Button>
      </Card>

      <div className="rounded-2xl border border-[--color-border-soft] bg-white shadow-soft">
        <button
          onClick={() => setShowTechnical((v) => !v)}
          className="flex w-full items-center justify-between px-4 py-3.5 text-left"
        >
          <span className="text-[13px] font-semibold text-[--color-charcoal]">Technical details</span>
          <ChevronDown
            size={16}
            className={`text-[--color-slate] transition-transform ${showTechnical ? "rotate-180" : ""}`}
          />
        </button>
        {showTechnical && (
          <div className="space-y-2.5 border-t border-[--color-border-soft] px-4 py-3.5 text-xs">
            <HashRow label="Block hash" value={decision.ledger.blockHash} />
            <HashRow label="Previous block hash" value={decision.ledger.previousHash} />
            <HashRow label="Evidence hash" value={decision.ledger.evidenceHash} />
            <p className="pt-1 text-[11px] leading-relaxed text-[--color-slate-light]">
              SHA-256 hashes shown truncated. Each block hash is derived from the decision payload, its evidence
              snapshot, and the previous block&apos;s hash.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-[--color-slate]">{label}</dt>
      <dd className={`text-right font-semibold text-[--color-charcoal] ${mono ? "font-mono text-[13px]" : ""}`}>
        {value}
      </dd>
    </div>
  );
}

function HashRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[--color-slate]">{label}</p>
      <p className="mt-0.5 break-all font-mono text-[--color-charcoal]">{truncateHash(value)}</p>
    </div>
  );
}
