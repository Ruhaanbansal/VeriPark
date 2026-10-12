import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatRupees(amount: number): string {
  const sign = amount < 0 ? "-" : "";
  return `${sign}₹${Math.abs(Math.round(amount))}`;
}

export function formatDistance(meters: number): string {
  if (meters < 1000) return `${meters} m`;
  return `${(meters / 1000).toFixed(1)} km`;
}

export function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatShortTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-IN", { hour: "2-digit", minute: "2-digit" });
}
