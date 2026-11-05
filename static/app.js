let state = {songs: [], ratings: {}};
const $ = (selector) => document.querySelector(selector);

async function load() {
  const response = await fetch("/api/songs");
  state = await response.json();
  $("#status").textContent = state.songs.length ? `${state.songs.length} songs in your arena` : "No library loaded";
  renderFavorites();
  nextDuel("duel");
}

function card(song) {
  return `<button class="song-card" data-id="${song.id}"><small>${song.genre || "Your library"}</small><h3>${escapeHtml(song.title)}</h3><p>${escapeHtml(song.artist)}${song.album ? ` · ${escapeHtml(song.album)}` : ""}</p></button>`;
}
function escapeHtml(value) { return value.replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char])); }
async function nextDuel(target, question) {
  if (state.songs.length < 2) return;
  const response = await fetch("/api/sample");
  const data = await response.json();
  const element = document.getElementById(target);
  element.classList.remove("empty");
  element.innerHTML = data.songs.map(card).join("");
  element.querySelectorAll(".song-card").forEach((button) => button.addEventListener("click", async () => {
    await fetch("/api/rate", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({song_id: button.dataset.id, score: question ? 4 : 5}) });
    await load();
    if (question) document.getElementById(target).scrollIntoView({ behavior: "smooth", block: "center" });
  }));
}
function renderFavorites() {
  const rows = state.songs.map((song) => ({song, rating: state.ratings[song.id]})).filter((row) => row.rating).sort((a,b) => b.rating.score - a.rating.score || b.rating.votes - a.rating.votes);
  $("#favorite-list").innerHTML = rows.length ? rows.map((row) => `<li><strong>${escapeHtml(row.song.title)}</strong><span>${escapeHtml(row.song.artist)} · ${row.rating.score}/5 signal · ${row.rating.votes} choice${row.rating.votes === 1 ? "" : "s"}</span></li>`).join("") : "<li>Make a few choices and your list will appear here.</li>";
}
document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => {
  document.querySelectorAll(".tab,.panel").forEach((item) => item.classList.remove("active"));
  tab.classList.add("active"); document.getElementById(tab.dataset.mode).classList.add("active");
  if (tab.dataset.mode === "tournament") nextDuel("bracket");
}));
document.querySelectorAll(".question").forEach((button) => button.addEventListener("click", () => nextDuel("question-duel", button.dataset.question)));
$("#import-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(); form.append("file", $("#csv").files[0]);
  const response = await fetch("/api/songs/import", {method:"POST", body:form});
  const data = await response.json();
  $("#message").textContent = response.ok ? `Imported ${data.count} songs. Let the games begin.` : data.error;
  if (response.ok) await load();
});
load();
