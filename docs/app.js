"use strict";

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

    allRows = data.leaderboard.map(r => ({
      ...r,
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
    : sorted.map((row, i) => {
        const cells = COLS.map(c => {
          const cls = c.cls ? ` class="${c.cls}"` : "";
          if (c.key === "rank") return `<td${cls}>${i + 1}</td>`;
          return `<td${cls}>${row[c.key] ?? ""}</td>`;
        }).join("");
        return `<tr>${cells}</tr>`;
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
