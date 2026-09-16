export const dynamic = "force-dynamic";

export async function GET() {
  return Response.json({
    status: "ok",
    service: "veripark-frontend",
    timestamp: new Date().toISOString()
  });
}
