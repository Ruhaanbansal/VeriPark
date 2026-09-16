"""Generate clean, elegant SVG cards for each parking facility."""
import os

LOT_CARDS = {
    "lot-metro-hub.svg": {
        "title": "MG Road Metro Hub",
        "badge": "Covered Deck · 24/7",
        "gradient": ("#fffbeb", "#fef3c7", "#fde68a"),
        "accent": "#d97706",
        "icon": "metro"
    },
    "lot-commercial-tower.svg": {
        "title": "Prestige Commercial Plaza",
        "badge": "Automated Stacker · Valet",
        "gradient": ("#ecfdf5", "#d1fae5", "#a7f3d0"),
        "accent": "#059669",
        "icon": "tower"
    },
    "lot-civic-center.svg": {
        "title": "Town Hall Civic Underground",
        "badge": "Municipal Standard Rate",
        "gradient": ("#eff6ff", "#dbeafe", "#bfdbfe"),
        "accent": "#2563eb",
        "icon": "civic"
    },
    "lot-express-deck.svg": {
        "title": "Richmond Circle Automated Deck",
        "badge": "Express Turntable Access",
        "gradient": ("#f5f3ff", "#ede9fe", "#ddd6fe"),
        "accent": "#7c3aed",
        "icon": "express"
    },
    "lot-indiranagar.svg": {
        "title": "Indiranagar 100ft Smart Vault",
        "badge": "FastTag · Robotic Retrieval",
        "gradient": ("#fff7ed", "#ffedd5", "#fed7aa"),
        "accent": "#ea580c",
        "icon": "vault"
    },
    "lot-koramangala.svg": {
        "title": "Koramangala Nexus Transit Plaza",
        "badge": "Mall Walkway · EV Supercharge",
        "gradient": ("#f0fdfa", "#ccfbf1", "#99f6e4"),
        "accent": "#0d9488",
        "icon": "nexus"
    },
    "lot-hospital.svg": {
        "title": "Manipal Emergency & OPD Deck",
        "badge": "Hospital Priority Zone",
        "gradient": ("#fef2f2", "#fee2e2", "#fecaca"),
        "accent": "#dc2626",
        "icon": "hospital"
    },
    "lot-techpark.svg": {
        "title": "ITPB International Tech Park",
        "badge": "Solar Canopy · 40x EV Bays",
        "gradient": ("#f0fdf4", "#dcfce7", "#bbf7d0"),
        "accent": "#16a34a",
        "icon": "tech"
    }
}

def generate_svg(filename, data):
    g0, g1, g2 = data["gradient"]
    accent = data["accent"]
    title = data["title"]
    badge = data["badge"]
    
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 220" width="100%" height="100%">
  <defs>
    <linearGradient id="bg_{filename[:4]}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{g0}"/>
      <stop offset="60%" stop-color="{g1}"/>
      <stop offset="100%" stop-color="{g2}"/>
    </linearGradient>
    <filter id="shadow_{filename[:4]}" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0f172a" flood-opacity="0.08"/>
    </filter>
  </defs>
  
  <!-- Card Background -->
  <rect width="400" height="220" rx="16" fill="url(#bg_{filename[:4]})"/>
  
  <!-- Geometric Structure Motif -->
  <g opacity="0.45">
    <line x1="0" y1="140" x2="400" y2="140" stroke="{accent}" stroke-width="1.5" stroke-dasharray="6 4"/>
    <line x1="120" y1="0" x2="120" y2="220" stroke="{accent}" stroke-width="1" opacity="0.3"/>
    <line x1="280" y1="0" x2="280" y2="220" stroke="{accent}" stroke-width="1" opacity="0.3"/>
    <!-- Parking Bays -->
    <rect x="40" y="155" width="45" height="50" rx="4" fill="none" stroke="{accent}" stroke-width="2"/>
    <rect x="95" y="155" width="45" height="50" rx="4" fill="none" stroke="{accent}" stroke-width="2"/>
    <rect x="150" y="155" width="45" height="50" rx="4" fill="none" stroke="{accent}" stroke-width="2"/>
    <rect x="205" y="155" width="45" height="50" rx="4" fill="{accent}" fill-opacity="0.2" stroke="{accent}" stroke-width="2"/>
    <rect x="260" y="155" width="45" height="50" rx="4" fill="none" stroke="{accent}" stroke-width="2"/>
    <rect x="315" y="155" width="45" height="50" rx="4" fill="none" stroke="{accent}" stroke-width="2"/>
  </g>

  <!-- Central Building Icon Container -->
  <g transform="translate(40, 45)">
    <rect width="52" height="52" rx="12" fill="#ffffff" filter="url(#shadow_{filename[:4]})"/>
    <!-- Facility P Sign & Building Badge -->
    <rect x="10" y="10" width="32" height="32" rx="8" fill="{accent}"/>
    <text x="26" y="32" text-anchor="middle" fill="#ffffff" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="900">P</text>
  </g>

  <!-- Facility Title & Badge -->
  <g transform="translate(108, 55)">
    <rect x="0" y="0" width="160" height="22" rx="11" fill="#ffffff" filter="url(#shadow_{filename[:4]})"/>
    <circle cx="10" cy="11" r="4" fill="{accent}"/>
    <text x="22" y="15" fill="{accent}" font-family="system-ui, sans-serif" font-size="11" font-weight="700">{badge}</text>
    <text x="0" y="42" fill="#0f172a" font-family="system-ui, sans-serif" font-size="16" font-weight="800">{title}</text>
  </g>

  <!-- Live Verified Badge -->
  <g transform="translate(320, 25)">
    <rect x="-35" y="-10" width="70" height="22" rx="11" fill="#059669"/>
    <text x="0" y="5" text-anchor="middle" fill="#ffffff" font-family="system-ui, sans-serif" font-size="10" font-weight="700">VERIFIED</text>
  </g>
</svg>"""

out_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "images", "lots")
os.makedirs(out_dir, exist_ok=True)

for fname, meta in LOT_CARDS.items():
    fpath = os.path.join(out_dir, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(generate_svg(fname, meta))
    print(f"Generated {fpath}")
