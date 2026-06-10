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
  "congo":                  "cg",
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

const COLS = [
  { key: "rank",         label: "#",      sortable: false, cls: "rank" },
  { key: "colleague",    label: "Player", sortable: true  },
  { key: "team",         label: "Team",   sortable: true  },
  { key: "points",       label: "Pts",    sortable: true,  cls: "pts"  },
  { key: "played",       label: "P",      sortable: true  },
  { key: "wins",         label: "W",      sortable: true  },
  { key: "draws",        label: "D",      sortable: true  },
  { key: "losses",       label: "L",      sortable: true  },
  { key: "goals_for",    label: "GF",     sortable: true  },
  { key: "clean_sheets", label: "CS",     sortable: true  },
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
        "Last updated: " + new Date(data.updated_at).toLocaleString();
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
  } catch (e) {
    document.getElementById("status").textContent =
      "Could not load leaderboard: " + e.message;
  }
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
          if (c.key === "rank") return `<td${cls}>${row.rank}</td>`;
          if (c.key === "team") return `<td>${flagImg(row.team)}${row.team}</td>`;
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
