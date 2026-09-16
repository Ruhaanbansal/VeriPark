/**
 * Server-compatible venue image component.
 * Uses a plain <img> without onError (which is client-only).
 * Falls back gracefully via CSS if the image 404s (browser shows nothing, which
 * is acceptable vs. crashing the server render).
 * For client components, use VenueImage from VenueImage.tsx instead.
 */
export function VenueImageServer({
  lotId,
  name,
  height = "h-32",
}: {
  lotId: string;
  name: string;
  height?: string;
}) {
  const cleanLotId = lotId.replace(/^dec-/, "");
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={`/images/lots/${cleanLotId}.jpg`}
      alt={name}
      className={`${height} w-full object-cover`}
    />
  );
}
