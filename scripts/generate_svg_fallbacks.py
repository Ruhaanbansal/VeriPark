import os

TARGET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "public", "images", "lots")
os.makedirs(TARGET_DIR, exist_ok=True)

lots = [
    ("lot-metro-hub", "MG Road Metro Transit Hub Deck", "#d97706", "#92400e"),
    ("lot-commercial-tower", "Prestige Commercial Plaza Deck", "#047857", "#065f46"),
    ("lot-civic-center", "Town Hall Civic Underground", "#d97706", "#b45309"),
    ("lot-indiranagar", "Indiranagar 100ft Smart Vault", "#1d4ed8", "#1e40af"),
    ("lot-hospital", "Manipal Hospital Emergency Deck", "#b91c1c", "#991b1b"),
    ("lot-koramangala", "Koramangala Nexus Transit Plaza", "#047857", "#065f46"),
    ("lot-express-deck", "Richmond Circle Automated Deck", "#b45309", "#78350f"),
]

for lid, title, c1, c2 in lots:
    svg = f"""<svg width="600" height="360" viewBox="0 0 600 360" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg_{lid}" x1="0" y1="0" x2="600" y2="360" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="600" height="360" fill="url(#bg_{lid})"/>
  <rect x="30" y="30" width="540" height="300" rx="16" fill="white" fill-opacity="0.08" stroke="white" stroke-opacity="0.2" stroke-width="2"/>
  <line x1="60" y1="100" x2="540" y2="100" stroke="white" stroke-opacity="0.15" stroke-width="1.5" stroke-dasharray="6 6"/>
  <line x1="60" y1="180" x2="540" y2="180" stroke="white" stroke-opacity="0.15" stroke-width="1.5" stroke-dasharray="6 6"/>
  <line x1="60" y1="260" x2="540" y2="260" stroke="white" stroke-opacity="0.15" stroke-width="1.5" stroke-dasharray="6 6"/>
  <rect x="80" y="120" width="60" height="40" rx="6" fill="white" fill-opacity="0.18"/>
  <rect x="160" y="120" width="60" height="40" rx="6" fill="white" fill-opacity="0.12"/>
  <rect x="240" y="120" width="60" height="40" rx="6" fill="white" fill-opacity="0.2"/>
  <rect x="320" y="120" width="60" height="40" rx="6" fill="white" fill-opacity="0.15"/>
  <rect x="400" y="120" width="60" height="40" rx="6" fill="white" fill-opacity="0.12"/>
  <circle cx="300" cy="80" r="26" fill="white" fill-opacity="0.22"/>
  <path d="M300 66 L314 72 V84 C314 93 307 100 300 103 C293 100 286 93 286 84 V72 Z" fill="white" fill-opacity="0.9"/>
  <text x="300" y="225" text-anchor="middle" fill="white" font-family="system-ui, sans-serif" font-size="20" font-weight="bold">{title}</text>
  <text x="300" y="255" text-anchor="middle" fill="white" fill-opacity="0.8" font-family="system-ui, sans-serif" font-size="13" font-weight="500">VeriPark™ Cryptographically Verified Deck</text>
</svg>"""
    file_path = os.path.join(TARGET_DIR, f"{lid}.svg")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {file_path}")
