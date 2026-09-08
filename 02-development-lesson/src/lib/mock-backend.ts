// Mock backend — replace with real API calls later.
// Everything is persisted in localStorage.

export type Player = { username: string; password: string; highScore: number };

const KEY = "snake-arena:players";
const SESSION = "snake-arena:session";

function read(): Record<string, Player> {
  if (typeof window === "undefined") return {};
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "{}");
  } catch {
    return {};
  }
}

function write(players: Record<string, Player>) {
  localStorage.setItem(KEY, JSON.stringify(players));
}

function seed() {
  const players = read();
  if (Object.keys(players).length > 0) return;
  const demo: Array<[string, number]> = [
    ["cobra_kai", 87],
    ["viper", 74],
    ["mamba", 66],
    ["python42", 58],
    ["slither", 51],
    ["anaconda", 44],
    ["boa", 37],
    ["adder", 29],
    ["rattler", 22],
    ["garter", 15],
    ["newbie", 8],
  ];
  const next: Record<string, Player> = {};
  for (const [username, highScore] of demo) {
    next[username] = { username, password: "demo", highScore };
  }
  write(next);
}

export function signUp(username: string, password: string) {
  seed();
  const u = username.trim();
  if (u.length < 3) return { error: "Le pseudo doit faire au moins 3 caractères." };
  if (password.length < 4) return { error: "Le mot de passe doit faire au moins 4 caractères." };
  const players = read();
  if (players[u.toLowerCase()] || players[u]) return { error: "Ce pseudo est déjà utilisé." };
  players[u] = { username: u, password, highScore: 0 };
  write(players);
  localStorage.setItem(SESSION, u);
  return { player: players[u] };
}

export function signIn(username: string, password: string) {
  seed();
  const players = read();
  const player = players[username.trim()];
  if (!player || player.password !== password) return { error: "Identifiants invalides." };
  localStorage.setItem(SESSION, player.username);
  return { player };
}

export function signOut() {
  localStorage.removeItem(SESSION);
}

export function currentPlayer(): Player | null {
  if (typeof window === "undefined") return null;
  seed();
  const name = localStorage.getItem(SESSION);
  if (!name) return null;
  return read()[name] ?? null;
}

export function submitScore(username: string, score: number): Player | null {
  const players = read();
  const player = players[username];
  if (!player) return null;
  if (score > player.highScore) {
    player.highScore = score;
    write(players);
  }
  return player;
}

export function leaderboard(): Array<{ rank: number; username: string; score: number }> {
  seed();
  return Object.values(read())
    .sort((a, b) => b.highScore - a.highScore)
    .slice(0, 10)
    .map((p, i) => ({ rank: i + 1, username: p.username, score: p.highScore }));
}
