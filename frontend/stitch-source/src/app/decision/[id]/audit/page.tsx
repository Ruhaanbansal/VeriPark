import { notFound } from "next/navigation";
import { getDecisionByLotId } from "@/lib/mock-data";
import { BackHeader, Screen } from "@/components/ui/Screen";
import { AuditTrailClient } from "./AuditTrailClient";

export default async function AuditTrailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const decision = getDecisionByLotId(id);
  if (!decision) notFound();

  return (
    <Screen>
      <BackHeader backHref={`/decision/${id}`} title="Audit record" />
      <AuditTrailClient decision={decision} />
    </Screen>
  );
}
