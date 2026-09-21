"use client";

import { useState } from "react";
import { ChevronDown, FileLock2, Loader2, ShieldCheck, ShieldX } from "lucide-react";
import type { Decision } from "@/lib/types";
import { formatRupees, formatTimestamp } from "@/lib/utils";
import { Card } from "@/components/ui/Screen";
import { Button } from "@/components/ui/Button";

import { verifyLedgerChain } from "@/lib/api";

type VerifyState = "idle" | "checking" | "pass" | "fail";

function truncateHash(hash: string) {
  return `${hash.slice(0, 10)}…${hash.slice(-8)}`;
}

export function AuditTrailClient({ decision }: { decision: Decision }) {
  const [verifyState, setVerifyState] = useState<VerifyState>("idle");
  const [verifyMessage, setVerifyMessage] = useState<string>("");
  const [showTechnical, setShowTechnical] = useState(false);

  async function runIntegrityCheck() {
    setVerifyState("checking");
    const result = await verifyLedgerChain(decision.id);
    if (result.valid) {
      setVerifyState("pass");
      setVerifyMessage(result.detail);
    } else {
      setVerifyState("fail");
      setVerifyMessage(result.detail);
    }
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

      <div className="flex items-start gap-3 rounded-2xl border border-[--color-verified-100] bg-[--color-verified-50] p-4 shadow-soft">
        <ShieldCheck size={20} className="mt-0.5 shrink-0 text-[--color-verified]" />
        <p className="text-[13px] leading-relaxed font-medium text-[--color-verified]">
          This record is cryptographically sealed and cannot be altered after the fact — including by us. Every
          decision links back to the one before it, so any change would be immediately obvious.
        </p>
      </div>

      <Card>
        <div className="flex items-center justify-between">
          <p className="text-[14px] font-bold text-[--color-charcoal]">Integrity check</p>
          {verifyState === "pass" && (
            <span className="flex items-center gap-1.5 text-xs font-bold text-[--color-verified]">
              <ShieldCheck size={15} /> Verified intact
            </span>
          )}
          {verifyState === "fail" && (
            <span className="flex items-center gap-1.5 text-xs font-bold text-[--color-danger]">
              <ShieldX size={15} /> Mismatch found
            </span>
          )}
        </div>
        <p className="mt-1 text-xs leading-relaxed text-[--color-slate]">
          Run a live check to confirm this record matches its sealed hash chain, right now.
        </p>
        <Button
          variant={verifyState === "pass" ? "secondary" : "primary"}
          size="sm"
          className="mt-3.5"
          onClick={runIntegrityCheck}
          disabled={verifyState === "checking"}
        >
          {verifyState === "checking" && <Loader2 size={14} className="animate-spin" />}
          {verifyState === "checking"
            ? "Checking chain…"
            : verifyState === "pass"
              ? "Re-run verification check"
              : "Verify this record now"}
        </Button>

        {verifyMessage && (
          <div
            className={`mt-3.5 rounded-xl border p-3 text-xs font-medium leading-relaxed break-words break-all ${
              verifyState === "pass"
                ? "border-[--color-verified-100] bg-[--color-verified-50] text-[--color-verified]"
                : "border-red-200 bg-red-50 text-red-700"
            }`}
          >
            {verifyMessage}
          </div>
        )}
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
