"use strict";

// Mapping of API-Football team names (lowercase) to flagcdn.com ISO codes.
// Covers all 48 World Cup 2026 qualified nations plus common API name variants.
const FLAG_CODES = {
  // CONMEBOL
  "argentina":              "ar",
  "brazil":                 "br",
  "colombia":               "co",
  "ecuador":                "ec",
  "uruguay":                "uy",
  "venezuela":              "ve",
  "chile":                  "cl",
  "paraguay":               "py",
  "peru":                   "pe",
  "bolivia":                "bo",
  // UEFA
  "france":                 "fr",
  "germany":                "de",
  "spain":                  "es",
  "england":                "gb-eng",
  "portugal":               "pt",
  "netherlands":            "nl",
  "belgium":                "be",
  "italy":                  "it",
  "switzerland":            "ch",
  "croatia":                "hr",
  "serbia":                 "rs",
  "poland":                 "pl",
  "denmark":                "dk",
  "austria":                "at",
  "turkey":                 "tr",
  "slovakia":               "sk",
  "scotland":               "gb-sct",
  "wales":                  "gb-wls",
  "northern ireland":       "gb-nir",
  "hungary":                "hu",
  "romania":                "ro",
  "ukraine":                "ua",
  "greece":                 "gr",
  "czech republic":         "cz",
  "czechia":                "cz",
  "sweden":                 "se",
  "norway":                 "no",
  "finland":                "fi",
  "ireland":                "ie",
  "republic of ireland":    "ie",
  "slovenia":               "si",
  "albania":                "al",
  // CONCACAF
  "usa":                    "us",
  "united states":          "us",
  "mexico":                 "mx",
  "canada":                 "ca",
  "costa rica":             "cr",
  "panama":                 "pa",
  "honduras":               "hn",
  "jamaica":                "jm",
  "el salvador":            "sv",
  "haiti":                  "ht",
  "trinidad and tobago":    "tt",
  "cuba":                   "cu",
  "suriname":               "sr",
  // CAF
  "morocco":                "ma",
  "senegal":                "sn",
  "nigeria":                "ng",
  "egypt":                  "eg",
  "cameroon":               "cm",
  "ivory coast":            "ci",
  "côte d'ivoire":          "ci",
  "cote d'ivoire":          "ci",
  "algeria":                "dz",
  "south africa":           "za",
  "ghana":                  "gh",
  "mali":                   "ml",
  "guinea":                 "gn",
  "tunisia":                "tn",
  "dr congo":               "cd",
  "congo dr":               "cd",
  "congo":                  "cg",
  "bosnia & herzegovina":   "ba",
  "bosnia and herzegovina": "ba",
  "curaçao":                "cw",
  "curacao":                "cw",
  "türkiye":                "tr",
  "zambia":                 "zm",
  "kenya":                  "ke",
  "ethiopia":               "et",
  "tanzania":               "tz",
  "cape verde":             "cv",
  "cape verde islands":     "cv",
  // AFC
  "japan":                  "jp",
  "south korea":            "kr",
  "korea republic":         "kr",
  "iran":                   "ir",
  "australia":              "au",
  "saudi arabia":           "sa",
  "uzbekistan":             "uz",
  "jordan":                 "jo",
  "iraq":                   "iq",
  "qatar":                  "qa",
  "china":                  "cn",
  "china pr":               "cn",
  "united arab emirates":   "ae",
  "uae":                    "ae",
  "bahrain":                "bh",
  "oman":                   "om",
  "indonesia":              "id",
  "india":                  "in",
  "vietnam":                "vn",
  "thailand":               "th",
  // OFC
  "new zealand":            "nz",
};

function flagImg(teamName) {
  const code = FLAG_CODES[teamName.toLowerCase()];
  if (!code) return "";
  return `<img src="https://flagcdn.com/w20/${code}.png" width="20" height="15" alt="" class="flag" loading="lazy">`;
}

function nextMatchCell(row) {
  if (!row.next_match_utc) {
    return `<td class="next-match knocked-out">Out</td>`;
  }
  const dt = new Date(row.next_match_utc);
  const diffMs = dt - Date.now();
  if (diffMs < 0) {
    return `<td class="next-match">—</td>`;
  }
  const totalMins  = Math.floor(diffMs / 60000);
  const days  = Math.floor(totalMins / 1440);
  const hours = Math.floor((totalMins % 1440) / 60);
  const mins  = totalMins % 60;

  let timeStr;
  if (days > 0)       timeStr = `${days}d ${hours}h`;
  else if (hours > 0) timeStr = `${hours}h ${mins}m`;
  else                timeStr = `${mins}m`;

  const vs = row.next_match_vs
    ? `<span class="next-vs">vs ${flagImg(row.next_match_vs)}</span>`
    : "";
  return `<td class="next-match"><span class="next-time">${timeStr}</span>${vs}</td>`;
}

const COLS = [
  { key: "rank",         label: "#",      sortable: false, cls: "rank" },
  { key: "colleague",    label: "Player", sortable: true  },
  { key: "team",         label: "Team",   sortable: true  },
  { key: "next_match",   label: "Next",   sortable: false },
  { key: "points",       label: "Pts",    sortable: true,  cls: "pts"  },
  { key: "played",       label: "P",      sortable: true  },
  { key: "wins",         label: "W",      sortable: true  },
  { key: "draws",        label: "D",      sortable: true  },
  { key: "losses",       label: "L",      sortable: true  },
  { key: "goals_for",    label: "GF",     sortable: true  },
  { key: "clean_sheets", label: "CS",     sortable: true  },
  { key: "upset_bonus",  label: "Upset",  sortable: true,  cls: "ub"   },
  { key: "yellow_cards", label: "YC",     sortable: true,  cls: "yc"   },
  { key: "red_cards",    label: "RC",     sortable: true,  cls: "rc"   },
];

let sortKey = "points";
let sortDir = -1;
let allRows = [];
let query = "";

async function load() {
  try {
    const res = await fetch("data.json");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.updated_at) {
      document.getElementById("updated").textContent =
        "Last updated: " + new Date(data.updated_at).toLocaleString("en-GB", { timeZone: "Europe/Zurich", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) + " Geneva";
    }

    if (!data.leaderboard || data.leaderboard.length === 0) {
      document.getElementById("status").textContent =
        "No data yet — check back once the tournament starts.";
      return;
    }

    // data.json arrives sorted by points — stamp that as the permanent rank
    allRows = data.leaderboard.map((r, i) => ({
      ...r,
      rank: i + 1,
      losses: r.played - r.wins - r.draws,
    }));

    document.getElementById("search").addEventListener("input", function () {
      query = this.value.toLowerCase();
      render();
    });

    render();
    renderAvailable(data.available_teams || []);
    renderUpcoming(data.upcoming_fixtures || []);
    renderFifaGroups(data.fifa_groups || {});
    setInterval(render, 60000); // refresh countdown every minute
  } catch (e) {
    document.getElementById("status").textContent =
      "Could not load leaderboard: " + e.message;
  }
}

function renderAvailable(teams) {
  const section = document.getElementById("available-section");
  if (!teams.length) {
    section.hidden = true;
    return;
  }

  const rows = teams.map(t =>
    `<tr><td>${flagImg(t.team)}${t.team}</td></tr>`
  ).join("");

  section.innerHTML = `
    <h2 class="section-heading">Teams still to be picked <span class="count">${teams.length}</span></h2>
    <div id="available-wrap">
      <table class="available-table">
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function renderUpcoming(fixtures) {
  const section = document.getElementById("upcoming-section");
  if (!fixtures || !fixtures.length) return;

  const show = fixtures.slice(0, 12);

  const grpCls = { A: "grp-a", B: "grp-b", C: "grp-c", D: "grp-d" };

  function grpBadge(grp) {
    if (!grp) return "";
    return `<span class="grp-badge ${grpCls[grp] || ""}">${grp}</span>`;
  }

  const cards = show.map(fx => {
    const dt = new Date(fx.date);
    const tz = "Europe/Zurich";
    const dateStr = dt.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: tz });
    const timeStr = dt.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: tz });
    const venue = [fx.venue, fx.city].filter(Boolean).join(", ");

    return `
      <div class="match-card">
        <div class="match-card-meta">
          <span class="match-card-time">${dateStr} &middot; ${timeStr}</span>
          <span class="match-card-venue">${venue}</span>
        </div>
        <div class="match-teams">
          <div class="match-team">
            <div class="match-team-name">${flagImg(fx.home_team)}${fx.home_team}</div>
            ${grpBadge(fx.home_group)}
          </div>
          <div class="match-team">
            <div class="match-team-name">${flagImg(fx.away_team)}${fx.away_team}</div>
            ${grpBadge(fx.away_group)}
          </div>
        </div>
      </div>`;
  }).join("");

  section.innerHTML = `
    <h2 class="section-heading">Upcoming Fixtures <span class="count">${show.length}</span></h2>
    <div class="match-grid">${cards}</div>`;
}

function renderFifaGroups(groups) {
  const section = document.getElementById("fifa-section");
  if (!groups || !Object.keys(groups).length) return;

  const GROUP_META = {
    A: { label: "Group A — Top Tier",  cls: "grp-a" },
    B: { label: "Group B",             cls: "grp-b" },
    C: { label: "Group C",             cls: "grp-c" },
    D: { label: "Group D — Underdogs", cls: "grp-d" },
  };

  const cols = Object.entries(groups).map(([key, teams]) => {
    const meta = GROUP_META[key] || { label: `Group ${key}`, cls: "" };
    const rows = teams.map(t =>
      `<div class="grp-team">${flagImg(t)}${t}</div>`
    ).join("");
    return `
      <div class="grp-col">
        <div class="grp-header ${meta.cls}">${meta.label}</div>
        ${rows}
      </div>`;
  }).join("");

  section.innerHTML = `
    <h2 class="section-heading">FIFA Ranking Groups</h2>
    <p class="upset-note">
      <strong>Upset bonus</strong> — if your team beats a team from a higher-ranked group, you earn bonus points based on how many groups above them you are:
      1 group above&nbsp;<strong>+1&nbsp;pt</strong> &middot;
      2 groups above&nbsp;<strong>+3&nbsp;pts</strong> &middot;
      3 groups above&nbsp;<strong>+5&nbsp;pts</strong>.
    </p>
    <div class="grp-grid">${cols}</div>`;
}

function render() {
  const filtered = query
    ? allRows.filter(r =>
        r.colleague.toLowerCase().includes(query) ||
        r.team.toLowerCase().includes(query)
      )
    : allRows;

  const sorted = [...filtered].sort((a, b) => {
    const av = a[sortKey];
    const bv = b[sortKey];
    if (typeof av === "string") return av.localeCompare(bv) * sortDir;
    return (av - bv) * sortDir;
  });

  const thead = COLS.map(c => {
    const classes = [
      c.sortable ? "sortable" : "",
      c.key === sortKey ? "active" : "",
    ].filter(Boolean).join(" ");
    const arrow = c.key === sortKey ? (sortDir === -1 ? " &#9660;" : " &#9650;") : "";
    return `<th class="${classes}" data-key="${c.key}">${c.label}${arrow}</th>`;
  }).join("");

  const tbody = sorted.length === 0
    ? `<tr><td colspan="${COLS.length}" class="message">No results for "${query}"</td></tr>`
    : sorted.map((row) => {
        const rankCls = row.rank <= 3 ? ` class="r${row.rank}"` : "";
        const cells = COLS.map(c => {
          const cls = c.cls ? ` class="${c.cls}"` : "";
          if (c.key === "rank")        return `<td${cls}>${row.rank}</td>`;
          if (c.key === "team")        return `<td>${flagImg(row.team)}${row.team}</td>`;
          if (c.key === "next_match")  return nextMatchCell(row);
          return `<td${cls}>${row[c.key] ?? ""}</td>`;
        }).join("");
        return `<tr${rankCls}>${cells}</tr>`;
      }).join("");

  const table = `<table><thead><tr>${thead}</tr></thead><tbody>${tbody}</tbody></table>`;
  const wrap = document.getElementById("leaderboard-wrap");
  wrap.innerHTML = table;

  wrap.querySelectorAll("th.sortable").forEach(th => {
    th.addEventListener("click", () => {
      const k = th.dataset.key;
      sortDir = k === sortKey ? sortDir * -1 : -1;
      sortKey = k;
      render();
    });
  });
}

load();
