"""Builds the profile's SVG cards from live GitHub data.

Run by .github/workflows/cards.yml every day. Needs GH_TOKEN (the default
GITHUB_TOKEN is enough, it only reads public data).
"""
import datetime as dt
import html
import json
import os
import urllib.request

USER = "Ayesha-Ramzan"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")

INK, INK2, MUTED = "#3F3533", "#5C514D", "#8A7E74"
ACC, ACC2, LINE, CARD = "#C98A72", "#7A5C48", "#EEE6DE", "#FFFDF9"
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
SERIF = "Georgia,'Times New Roman',serif"

QUERY = """
query($login:String!){
  user(login:$login){
    name followers{totalCount}
    repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100, orderBy:{field:PUSHED_AT, direction:DESC}){
      totalCount
      nodes{ name description stargazerCount forkCount isFork pushedAt url
             primaryLanguage{name color}
             languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{name color} } } }
    }
    contributionsCollection{
      totalCommitContributions totalPullRequestContributions totalIssueContributions totalRepositoriesWithContributedCommits
      contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } }
    }
  }
}"""

DESCRIPTIONS = {
    "Mehfil-Restaurant-Lahore": "Editorial restaurant site for slow-fired Lahori cooking, with menu, story and booking.",
    "Mealio_Bite-_Bliss": "Halal Pakistani food & seafood delivery landing page with WhatsApp ordering.",
    "Habit-Tracker": "Monthly habit grid with streaks, time ranges and analytics charts.",
    "Dar-ul-Falah-App": "Installable companion to track daily prayers, Quran recitation and Adhkar.",
    "Restaurant-WA-Order-Bot": "WhatsApp ordering bot with menu, orders and COD / JazzCash payments.",
    "Jarvis-AI-COO": "Multi-tenant FastAPI backend for AI skills with strict tenant isolation.",
    "J.A.R.V.I.S.-AI-Voice-Assistant": "Wake-word voice assistant that controls apps, media, files and mail.",
    "wa-auto-reply-bot": "WhatsApp auto-reply bot that answers in my own voice, with per-chat memory.",
}

QUOTES = [
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("Programs must be written for people to read.", "Harold Abelson"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Any sufficiently advanced technology is indistinguishable from magic.", "Arthur C. Clarke"),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ("Quality is not an act, it is a habit.", "Aristotle"),
    ("The details are not the details. They make the design.", "Charles Eames"),
    ("Done is better than perfect.", "Sheryl Sandberg"),
    ("Small steps every day add up to big results.", "Unknown"),
]


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def esc(s):
    return html.escape(str(s))


def text(x, y, s, size=14, fill=INK2, weight=400, family=SANS, anchor="start", ls=0, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{esc(s)}</text>')


def card(w, h, inner, glow=False):
    g = ""
    if glow:
        g = (f'<rect x="8" y="6" width="{w-16}" height="{h-20}" rx="22" fill="url(#gl)"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
<filter id="sh" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#3F3533" flood-opacity=".10"/></filter>
<radialGradient id="gl" cx="90%" cy="0%" r="75%"><stop offset="0" stop-color="#F6D3C6" stop-opacity=".85"/><stop offset="1" stop-color="#F6D3C6" stop-opacity="0"/></radialGradient>
<linearGradient id="ln" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACC}" stop-opacity=".35"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></linearGradient>
<style>@keyframes up{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}} .a{{animation:up .8s ease-out both}}</style>
</defs>
<rect x="8" y="6" width="{w-16}" height="{h-20}" rx="22" fill="{CARD}" stroke="{LINE}" filter="url(#sh)"/>{g}
{inner}</svg>'''


def save(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)


def label(x, y, s):
    return text(x, y, s.upper(), 11.5, ACC2, 700, ls=3)


# ---------------------------------------------------------------- cards
def stats_card(u, streak):
    c = u["contributionsCollection"]
    repos = u["repositories"]
    stars = sum(n["stargazerCount"] for n in repos["nodes"])
    rows = [
        ("Total contributions", c["contributionCalendar"]["totalContributions"]),
        ("Commits this year", c["totalCommitContributions"]),
        ("Public repositories", repos["totalCount"]),
        ("Stars earned", stars),
        ("Pull requests", c["totalPullRequestContributions"]),
        ("Longest streak", f"{streak} days"),
    ]
    inner = label(36, 52, "GitHub stats")
    inner += f'<text x="34" y="92" font-family="{SERIF}" font-style="italic" font-size="26" font-weight="600" fill="{INK}">Always shipping.</text>'
    for i, (k, v) in enumerate(rows):
        x = 36 + (i % 2) * 196
        y = 134 + (i // 2) * 52
        inner += f'<g class="a" style="animation-delay:{i*0.08:.2f}s">'
        inner += f'<line x1="{x}" y1="{y-24}" x2="{x+176}" y2="{y-24}" stroke="{LINE}"/>'
        inner += text(x, y, v, 22, INK, 800) + text(x, y + 18, k, 11.5, MUTED)
        inner += "</g>"
    save("stats.svg", card(440, 300, inner, glow=True))


def languages_card(u):
    totals = {}
    for n in u["repositories"]["nodes"]:
        if n["isFork"]:
            continue
        for e in n["languages"]["edges"]:
            name, color = e["node"]["name"], e["node"]["color"] or "#999"
            s, _ = totals.get(name, (0, color))
            totals[name] = (s + e["size"], color)
    top = sorted(totals.items(), key=lambda kv: -kv[1][0])[:6]
    whole = sum(v[0] for _, v in top) or 1
    inner = label(36, 52, "Top languages")
    inner += f'<text x="34" y="92" font-family="{SERIF}" font-style="italic" font-size="26" font-weight="600" fill="{INK}">What I write most.</text>'
    x = 36
    bar = ""
    for name, (size, color) in top:
        w = max(4, 368 * size / whole)
        bar += f'<rect x="{x:.1f}" y="114" width="{w:.1f}" height="10" fill="{color}"/>'
        x += w
    inner += f'<clipPath id="bc"><rect x="36" y="114" width="368" height="10" rx="5"/></clipPath><g clip-path="url(#bc)">{bar}</g>'
    for i, (name, (size, color)) in enumerate(top):
        cx = 36 + (i % 2) * 196
        cy = 160 + (i // 2) * 34
        inner += f'<circle cx="{cx+5}" cy="{cy-4}" r="5" fill="{color}"/>'
        inner += text(cx + 18, cy, name, 13.5, INK, 600) + text(cx + 176, cy, f"{100*size/whole:.1f}%", 12.5, MUTED, anchor="end")
    save("languages.svg", card(440, 300, inner))


def latest_card(u):
    repo = next(n for n in u["repositories"]["nodes"]
                if not n["isFork"] and n["name"].lower() not in (USER.lower(), "portfolio"))
    desc = repo["description"] or DESCRIPTIONS.get(repo["name"], "Latest work in progress — see the repository for details.")
    words, lines, cur = desc.split(), [], ""
    for w in words:
        if len(cur) + len(w) > 46:
            lines.append(cur.strip()); cur = ""
        cur += w + " "
    lines.append(cur.strip())
    lang = repo["primaryLanguage"] or {"name": "—", "color": "#999"}
    when = dt.datetime.fromisoformat(repo["pushedAt"].replace("Z", "+00:00")).strftime("%d %b %Y")
    inner = label(36, 52, "Latest project")
    inner += text(36, 96, repo["name"].replace("-", " ").replace("_", " "), 21, INK, 800)
    for i, l in enumerate(lines[:3]):
        inner += text(36, 128 + i * 21, l, 13.5, INK2)
    y = 196
    inner += f'<circle cx="41" cy="{y-4}" r="5" fill="{lang["color"] or "#999"}"/>' + text(54, y, lang["name"], 13, INK, 600)
    inner += text(160, y, f"★ {repo['stargazerCount']}", 13, INK, 600) + text(220, y, f"⑂ {repo['forkCount']}", 13, INK, 600)
    inner += text(404, y, f"Updated {when}", 12, MUTED, anchor="end")
    inner += f'<circle cx="392" cy="54" r="15" fill="{INK}"/>' + text(392, 59, "↗", 14, CARD, 700, anchor="middle")
    save("latest.svg", card(440, 236, inner))
    return repo["url"]


def graph_card(days):
    last = days[-31:]
    W, H = 900, 300
    x0, x1, y0, y1 = 64, 860, 92, 236
    mx = max([d["contributionCount"] for d in last] + [4])
    pts = []
    for i, d in enumerate(last):
        x = x0 + (x1 - x0) * i / (len(last) - 1)
        y = y1 - (y1 - y0) * d["contributionCount"] / mx
        pts.append((x, y, d))
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)
    area = path + f" L{x1},{y1} L{x0},{y1} Z"
    total = sum(d["contributionCount"] for d in last)
    inner = text(864, 52, f"{total} contributions · last 31 days", 12.5, MUTED, anchor="end")
    for k in range(5):
        gy = y1 - (y1 - y0) * k / 4
        inner += f'<line x1="{x0}" y1="{gy:.1f}" x2="{x1}" y2="{gy:.1f}" stroke="{LINE}" stroke-dasharray="{"0" if k == 0 else "3 5"}"/>'
        inner += text(x0 - 12, gy + 4, round(mx * k / 4), 11, MUTED, anchor="end")
    inner += f'<path d="{area}" fill="url(#ln)"/>'
    inner += (f'<path d="{path}" fill="none" stroke="{ACC}" stroke-width="2.5" stroke-linejoin="round" '
              f'stroke-dasharray="2600" stroke-dashoffset="2600"><animate attributeName="stroke-dashoffset" to="0" dur="2s" fill="freeze"/></path>')
    for i, (x, y, d) in enumerate(pts):
        inner += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4 if d["contributionCount"] else 2.5}" fill="{CARD}" stroke="{ACC if d["contributionCount"] else MUTED}" stroke-width="2"/>'
        if i % 5 == 0 or i == len(pts) - 1:
            inner += text(x, y1 + 24, dt.date.fromisoformat(d["date"]).strftime("%d %b"), 10.5, MUTED, anchor="middle")
    save("graph.svg", card(W, H, inner))


def trophies_card(u, streak):
    c = u["contributionsCollection"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    langs = {e["node"]["name"] for n in u["repositories"]["nodes"] for e in n["languages"]["edges"]}
    data = [
        ("Commits", c["totalCommitContributions"], [10, 50, 100, 200, 500, 1000]),
        ("Repositories", u["repositories"]["totalCount"], [1, 5, 10, 20, 50, 100]),
        ("Contributions", c["contributionCalendar"]["totalContributions"], [10, 50, 100, 200, 500, 1000]),
        ("Languages", len(langs), [2, 4, 6, 8, 10, 15]),
        ("Stars", stars, [1, 5, 10, 25, 50, 100]),
        ("Streak", streak, [2, 4, 7, 14, 30, 60]),
    ]
    ranks = ["C", "B", "A", "AA", "AAA", "S"]
    inner = ""
    for i, (name, val, th) in enumerate(data):
        lvl = sum(val >= t for t in th)
        rank = ranks[max(0, lvl - 1)] if lvl else "—"
        cx = 100 + i * 140
        cy = 106
        pct = min(1, lvl / len(th))
        circ = 2 * 3.14159 * 38
        inner += f'<g class="a" style="animation-delay:{i*0.1:.1f}s">'
        inner += f'<circle cx="{cx}" cy="{cy}" r="38" fill="#F8F2EC" stroke="{LINE}" stroke-width="6"/>'
        inner += (f'<circle cx="{cx}" cy="{cy}" r="38" fill="none" stroke="{ACC}" stroke-width="6" stroke-linecap="round" '
                  f'stroke-dasharray="{circ*pct:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>')
        inner += f'<text x="{cx}" y="{cy+9}" font-family="{SERIF}" font-style="italic" font-size="26" font-weight="600" fill="{INK}" text-anchor="middle">{rank}</text>'
        inner += text(cx, cy + 66, name, 13.5, INK, 700, anchor="middle") + text(cx, cy + 84, val, 12, MUTED, anchor="middle")
        inner += "</g>"
    save("trophies.svg", card(900, 230, inner, glow=True))


def quote_card():
    q, who = QUOTES[dt.date.today().toordinal() % len(QUOTES)]
    words, lines, cur = q.split(), [], ""
    for w in words:
        if len(cur) + len(w) > 42:
            lines.append(cur.strip()); cur = ""
        cur += w + " "
    lines.append(cur.strip())
    inner = ""
    inner += f'<text x="30" y="88" font-family="{SERIF}" font-size="72" fill="{ACC}" fill-opacity=".35">“</text>'
    for i, l in enumerate(lines[:3]):
        inner += f'<text x="80" y="{70 + i*32}" font-family="{SERIF}" font-style="italic" font-size="23" fill="{INK}">{esc(l)}</text>'
    y = 78 + len(lines[:3]) * 32
    inner += f'<line x1="80" y1="{y}" x2="108" y2="{y}" stroke="{ACC}" stroke-width="2"/>' + text(118, y + 5, who, 13, ACC2, 600)
    save("quote.svg", card(600, y + 46, inner, glow=True))


def longest_streak(days):
    best = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] else 0
        best = max(best, cur)
    return best


def main():
    u = fetch()
    days = [d for w in u["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    streak = longest_streak(days)
    stats_card(u, streak)
    languages_card(u)
    latest_card(u)
    graph_card(days)
    trophies_card(u, streak)
    quote_card()


if __name__ == "__main__":
    main()
