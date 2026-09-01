const API = "/api";
let genomes = [];
let currentGenome = null;
let viewStart = 1200000, viewEnd = 1260000;

const canvas = document.getElementById("trackCanvas");
const ctx = canvas.getContext("2d");

// ---------- Load genome list ----------
let searchDebounce = null;

async function loadGenomes(preserveFocus = false) {
  const params = new URLSearchParams();
  const searchBox = document.getElementById("searchBox");
  const q = searchBox.value;
  const host = document.getElementById("hostFilter").value;
  const env = document.getElementById("envFilter").value;
  if (q) params.append("q", q);
  if (host) params.append("host_plant", host);
  if (env) params.append("environment", env);

  const res = await fetch(`${API}/genomes?${params}`);
  genomes = await res.json();
  renderGenomeList();
  populateFilters();
  document.getElementById("totalCount").innerText = genomes.length;

  if (!currentGenome && genomes.length) selectGenome(genomes[0].id);

  // Restore focus + cursor position after re-render (fixes search losing focus)
  if (preserveFocus) {
    searchBox.focus();
    const val = searchBox.value;
    searchBox.value = "";
    searchBox.value = val;
  }
}

function populateFilters() {
  const hostSel = document.getElementById("hostFilter");
  const envSel = document.getElementById("envFilter");
  const droughtSel = document.getElementById("droughtFilter");
  if (hostSel.options.length > 1) return;
  const hosts = [...new Set(genomes.map(g => g.host_plant).filter(Boolean))];
  const envs = [...new Set(genomes.map(g => g.environment).filter(Boolean))];
  const droughts = [...new Set(genomes.map(g => g.drought_treatment).filter(Boolean))];
  hosts.forEach(h => hostSel.add(new Option(h, h)));
  envs.forEach(e => envSel.add(new Option(e, e)));
}

function renderGenomeList() {
  const ul = document.getElementById("genomeList");
  ul.innerHTML = "";
  if (genomes.length === 0) {
    const li = document.createElement("li");
    li.textContent = "No genomes match your search.";
    li.style.color = "#888";
    li.style.cursor = "default";
    ul.appendChild(li);
    return;
  }
  genomes.forEach(g => {
    const li = document.createElement("li");
    li.textContent = g.name;
    li.dataset.id = g.id;
    if (currentGenome && currentGenome.id === g.id) li.classList.add("active");
    li.onclick = () => selectGenome(g.id);
    ul.appendChild(li);
  });
}

// ---------- Select genome ----------
async function selectGenome(id) {
  const res = await fetch(`${API}/genomes/${id}`);
  currentGenome = await res.json();
  document.getElementById("gName").innerText = currentGenome.name;
  document.getElementById("gAssembly").innerText = currentGenome.assembly_accession || "-";
  document.getElementById("gLength").innerText = (currentGenome.genome_size || 0).toLocaleString() + " bp";
  document.getElementById("gGC").innerText = (currentGenome.gc_content ?? "-") + "%";

  if (currentGenome.name.includes("Pf0-1")) {
    // Curated demo genome — use fixed showcase window
    viewStart = 1200000; viewEnd = 1260000;
  } else {
    // Real NCBI genome — auto-locate a gene-dense starting window
    const firstGenesRes = await fetch(`${API}/genomes/${id}/first_genes`);
    const firstGenes = await firstGenesRes.json();

    if (firstGenes.length > 0) {
      const firstStart = firstGenes[0].start;
      viewStart = Math.max(0, firstStart - 2000);
      viewEnd = viewStart + 40000; // ~40kb window, should contain several genes
    } else {
      // Fallback if genome somehow has no genes at all
      viewStart = 0;
      viewEnd = Math.min(60000, currentGenome.genome_size || 60000);
    }
  }

  document.getElementById("startInput").value = viewStart;
  document.getElementById("endInput").value = viewEnd;

  renderGenomeList();
  await loadAndRenderTracks();
}

// ---------- Fetch + render tracks ----------
async function loadAndRenderTracks() {
  if (!currentGenome) return;
  const id = currentGenome.id;
  const qs = `?start=${viewStart}&end=${viewEnd}`;

  const [genes, rna, mge, snps, gc, cov] = await Promise.all([
    fetch(`${API}/genomes/${id}/genes${qs}`).then(r => r.json()),
    fetch(`${API}/genomes/${id}/rna${qs}`).then(r => r.json()),
    fetch(`${API}/genomes/${id}/mobile_elements${qs}`).then(r => r.json()),
    fetch(`${API}/genomes/${id}/snps${qs}`).then(r => r.json()),
    fetch(`${API}/genomes/${id}/gc${qs}`).then(r => r.json()),
    fetch(`${API}/genomes/${id}/coverage${qs}`).then(r => r.json()),
  ]);

  drawTracks({ genes, rna, mge, snps, gc, cov });
}

// ---------- Canvas rendering ----------
const TRACKS = [
  { name: "GC Content", h: 50 },
  { name: "Genes (CDS)", h: 60 },
  { name: "tRNA / rRNA", h: 40 },
  { name: "Mobile Elements", h: 30 },
  { name: "SNPs", h: 30 },
  { name: "Coverage", h: 60 },
];

let geneHitboxes = [];

function xScale(pos) {
  const w = canvas.width - 140;
  return 120 + ((pos - viewStart) / (viewEnd - viewStart)) * w;
}

function drawTracks(data) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  geneHitboxes = [];
  let y = 10;

  drawRuler(y);
  y += 30;

  drawLabel(TRACKS[0].name, y);
  drawGC(data.gc, y);
  y += TRACKS[0].h;

  drawLabel(TRACKS[1].name, y);
  drawGenes(data.genes, y);
  y += TRACKS[1].h;

  drawLabel(TRACKS[2].name, y);
  drawRNA(data.rna, y);
  y += TRACKS[2].h;

  drawLabel(TRACKS[3].name, y);
  drawBlocks(data.mge.map(m => [m.start, m.end]), y, "#f0a94e");
  y += TRACKS[3].h;

  drawLabel(TRACKS[4].name, y);
  drawTicks(data.snps.map(s => s.position), y, "red");
  y += TRACKS[4].h;

  drawLabel(TRACKS[5].name, y);
  drawCoverage(data.cov, y);

  if (data.genes.length === 0) {
    ctx.fillStyle = "#999";
    ctx.font = "12px Arial";
    ctx.fillText("No annotated genes in this region for this genome yet.", 130, 90);
  }
}

function drawLabel(text, y) {
  ctx.fillStyle = "#333";
  ctx.font = "11px Arial";
  ctx.fillText(text, 5, y + 12);
}

function drawRuler(y) {
  ctx.strokeStyle = "#999";
  ctx.beginPath();
  ctx.moveTo(120, y + 10); ctx.lineTo(canvas.width - 20, y + 10);
  ctx.stroke();
  const span = viewEnd - viewStart;
  const step = Math.pow(10, Math.floor(Math.log10(Math.max(span / 6, 1))));
  for (let p = Math.ceil(viewStart / step) * step; p < viewEnd; p += step) {
    const x = xScale(p);
    ctx.beginPath(); ctx.moveTo(x, y + 5); ctx.lineTo(x, y + 15); ctx.stroke();
    ctx.fillStyle = "#555"; ctx.font = "10px Arial";
    ctx.fillText(Math.round(p).toLocaleString(), x - 15, y);
  }
}

function drawGC(rows, y) {
  if (!rows.length) return;
  ctx.strokeStyle = "#555"; ctx.beginPath();
  rows.forEach((r, i) => {
    const x = xScale(r.position);
    const val = y + 45 - (r.gc_percent / 100) * 40;
    i === 0 ? ctx.moveTo(x, val) : ctx.lineTo(x, val);
  });
  ctx.stroke();
}

function drawGenes(genes, y) {
  genes.forEach(g => {
    const x1 = xScale(g.start), x2 = xScale(g.end);
    const color = g.gene_name === "pflD" ? "#e8b400" : "#2f7d32";
    ctx.fillStyle = color;
    ctx.fillRect(x1, y + 10, Math.max(x2 - x1, 2), 20);
    ctx.fillStyle = "#000"; ctx.font = "10px Arial";
    ctx.fillText(g.gene_name || g.locus_tag, x1, y + 42);
    // Store hitbox in INTERNAL canvas coordinates (not CSS pixels)
    geneHitboxes.push({ x1, x2, y1: y + 10, y2: y + 30, gene: g });
  });
}

function drawRNA(rna, y) {
  rna.forEach(r => {
    const x1 = xScale(r.start), x2 = xScale(r.end);
    if (r.rna_type === "tRNA") {
      ctx.fillStyle = "#9c27b0";
      ctx.fillRect(x1, y + 5, 3, 15);
    } else {
      ctx.fillStyle = "#2196f3";
      ctx.fillRect(x1, y + 5, Math.max(x2 - x1, 4), 15);
    }
  });
}

function drawBlocks(pairs, y, color) {
  ctx.fillStyle = color;
  pairs.forEach(([s, e]) => {
    const x1 = xScale(s), x2 = xScale(e);
    ctx.fillRect(x1, y + 8, Math.max(x2 - x1, 4), 12);
  });
}

function drawTicks(positions, y, color) {
  ctx.strokeStyle = color;
  positions.forEach(p => {
    const x = xScale(p);
    ctx.beginPath(); ctx.moveTo(x, y + 5); ctx.lineTo(x, y + 20); ctx.stroke();
  });
}

function drawCoverage(rows, y) {
  if (!rows.length) return;
  ctx.fillStyle = "rgba(74,144,226,0.5)";
  ctx.strokeStyle = "#4a90e2";
  ctx.beginPath();
  ctx.moveTo(xScale(rows[0].position), y + 50);
  rows.forEach(r => {
    const x = xScale(r.position);
    const val = y + 50 - Math.min(r.depth, 100) * 0.4;
    ctx.lineTo(x, val);
  });
  ctx.lineTo(xScale(rows[rows.length - 1].position), y + 50);
  ctx.closePath();
  ctx.fill(); ctx.stroke();
}

// ---------- FIXED: Gene click -> detail panel ----------
// Converts CSS pixel click coordinates into internal canvas coordinate space,
// since canvas is drawn at 1000x560 internally but displayed at a different CSS size.
canvas.addEventListener("click", async (e) => {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;

  const x = (e.clientX - rect.left) * scaleX;
  const y = (e.clientY - rect.top) * scaleY;

  const hit = geneHitboxes.find(h => x >= h.x1 && x <= h.x2 && y >= h.y1 && y <= h.y2);
  if (!hit) return;

  const res = await fetch(`${API}/genes/${hit.gene.id}`);
  const detail = await res.json();
  renderDetail(detail);
});

// Optional: change cursor to pointer when hovering over a gene
canvas.addEventListener("mousemove", (e) => {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  const x = (e.clientX - rect.left) * scaleX;
  const y = (e.clientY - rect.top) * scaleY;
  const hit = geneHitboxes.find(h => x >= h.x1 && x <= h.x2 && y >= h.y1 && y <= h.y2);
  canvas.style.cursor = hit ? "pointer" : "default";
});

function renderDetail(d) {
  const kegg = d.kegg_pathways.map(k => `${k.kegg_id} (${k.pathway_name})`).join(", ") || "-";
  const cog = d.cog_categories.map(c => `${c.cog_id}: ${c.category_desc}`).join(", ") || "-";
  const expr = d.expression.map(e => `${e.condition}: ${e.tpm} TPM`).join(", ") || "-";

  document.getElementById("detailPanel").innerHTML = `
    <div class="detail-row"><b>Gene:</b> ${d.gene_name || d.locus_tag}</div>
    <div class="detail-row"><b>Location:</b> ${d.start.toLocaleString()} - ${d.end.toLocaleString()}</div>
    <div class="detail-row"><b>Strand:</b> ${d.strand}</div>
    <div class="detail-row"><b>Product:</b> ${d.product || "-"}</div>
    <div class="detail-row"><b>EC Number:</b> ${d.ec_number || "-"}</div>
    <div class="detail-row"><b>Function:</b> ${d.function || "-"}</div>
    <div class="detail-row"><b>KEGG:</b> ${kegg}</div>
    <div class="detail-row"><b>COG:</b> ${cog}</div>
    <div class="detail-row"><b>Expression:</b> ${expr}</div>
    <div class="detail-row"><b>Host Plant:</b> ${d.genome?.host_plant || "-"}</div>
    <div class="detail-row"><b>Environment:</b> ${d.genome?.environment || "-"}</div>
  `;
}

// ---------- Navigation controls ----------
document.getElementById("goBtn").onclick = () => {
  viewStart = parseInt(document.getElementById("startInput").value);
  viewEnd = parseInt(document.getElementById("endInput").value);
  loadAndRenderTracks();
};
document.getElementById("zoomInBtn").onclick = () => zoom(0.5);
document.getElementById("zoomOutBtn").onclick = () => zoom(2);
document.getElementById("prevBtn").onclick = () => shift(-0.5);
document.getElementById("nextBtn").onclick = () => shift(0.5);

function zoom(factor) {
  const mid = (viewStart + viewEnd) / 2;
  const span = (viewEnd - viewStart) * factor;
  viewStart = Math.round(mid - span / 2);
  viewEnd = Math.round(mid + span / 2);
  syncInputs(); loadAndRenderTracks();
}
function shift(factor) {
  const span = viewEnd - viewStart;
  viewStart += Math.round(span * factor);
  viewEnd += Math.round(span * factor);
  syncInputs(); loadAndRenderTracks();
}
function syncInputs() {
  document.getElementById("startInput").value = viewStart;
  document.getElementById("endInput").value = viewEnd;
}

// ---------- FIXED: Search / filters (debounced, focus-preserving) ----------
document.getElementById("searchBox").addEventListener("input", () => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => loadGenomes(true), 250);
});
document.getElementById("hostFilter").addEventListener("change", () => loadGenomes());
document.getElementById("envFilter").addEventListener("change", () => loadGenomes());


// ---------- Global gene search across all genomes (Phase 6) ----------
let globalSearchDebounce = null;
document.getElementById("globalSearchBox").addEventListener("input", (e) => {
  clearTimeout(globalSearchDebounce);
  const q = e.target.value;
  if (!q) {
    document.getElementById("globalSearchResults").innerHTML = "";
    return;
  }
  globalSearchDebounce = setTimeout(async () => {
    const res = await fetch(`${API}/search?q=${encodeURIComponent(q)}`);
    const results = await res.json();
    renderGlobalSearchResults(results);
  }, 300);
});

function renderGlobalSearchResults(results) {
  const container = document.getElementById("globalSearchResults");
  if (results.length === 0) {
    container.innerHTML = "No matches found.";
    return;
  }
  container.innerHTML = results.slice(0, 8).map(r =>
    `<span style="cursor:pointer; text-decoration:underline; margin-right:10px;"
       onclick="jumpToGeneResult(${r.genome_id}, ${r.start}, ${r.end}, ${r.id})">
       ${r.gene_name || r.locus_tag} (${r.genome_name})
     </span>`
  ).join("");
}

async function jumpToGeneResult(genomeId, start, end, geneId) {
  await selectGenome(genomeId);
  viewStart = Math.max(0, start - 3000);
  viewEnd = end + 3000;
  syncInputs();
  await loadAndRenderTracks();
  const res = await fetch(`${API}/genes/${geneId}`);
  const detail = await res.json();
  renderDetail(detail);
}

// ---------- Init ----------
loadGenomes();
// ---------- Auth ----------
async function checkAuth() {
  const res = await fetch(`${API}/auth/me`);
  const data = await res.json();
  const statusEl = document.getElementById("authStatus");
  if (data.user) {
    statusEl.innerText = `Logged in as ${data.user.username || data.username}`;
    document.getElementById("logoutBtn").style.display = "inline";
  } else {
    statusEl.innerText = "Not logged in";
    document.getElementById("logoutBtn").style.display = "none";
  }
}

document.getElementById("registerBtn").onclick = async () => {
  const username = document.getElementById("authUsername").value;
  const password = document.getElementById("authPassword").value;
  const res = await fetch(`${API}/auth/register`, {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  });
  const data = await res.json();
  if (res.ok) { alert(`Registered as ${data.username}`); checkAuth(); }
  else alert(data.error);
};

document.getElementById("loginBtn").onclick = async () => {
  const username = document.getElementById("authUsername").value;
  const password = document.getElementById("authPassword").value;
  const res = await fetch(`${API}/auth/login`, {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  });
  const data = await res.json();
  if (res.ok) { checkAuth(); } else alert(data.error);
};

document.getElementById("logoutBtn").onclick = async () => {
  await fetch(`${API}/auth/logout`, {method: "POST"});
  checkAuth();
};

document.getElementById("bookmarkBtn").onclick = async () => {
  if (!currentGenome) return alert("Select a genome first");
  const label = prompt("Bookmark label:", `${currentGenome.name} ${viewStart}-${viewEnd}`);
  if (label === null) return;
  const res = await fetch(`${API}/bookmarks`, {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({genome_id: currentGenome.id, start: viewStart, end: viewEnd, label})
  });
  if (res.ok) alert("Bookmarked!");
  else alert("Login required to bookmark views.");
};

checkAuth();