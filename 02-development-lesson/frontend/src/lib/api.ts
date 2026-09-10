export interface Player {
  username: string;
  highScore: number;
}

export interface LeaderboardEntry {
  rank: number;
  username: string;
  score: number;
}

interface AuthResponse {
  player: Player;
  token: string;
}

interface SubmitScoreResponse {
  player: Player;
  isNewHighScore: boolean;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const TOKEN_KEY = "snake-arena:token";
const PLAYER_KEY = "snake-arena:player";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

function setSession(token: string, player: Player) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(PLAYER_KEY, JSON.stringify(player));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(PLAYER_KEY);
}

export function currentPlayer(): Player | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(PLAYER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Player;
  } catch {
    return null;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  requireAuth = false,
): Promise<{ data?: T; error?: string }> {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (requireAuth) {
    const token = getToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    });

    const body = await res.json().catch(() => null);

    if (!res.ok) {
      const msg = body?.error || body?.detail || "Une erreur est survenue.";
      return { error: typeof msg === "string" ? msg : JSON.stringify(msg) };
    }

    return { data: body as T };
  } catch (err) {
    return { error: "Impossible de joindre le serveur API." };
  }
}

export async function signUp(
  username: string,
  password: string,
): Promise<{ player?: Player; error?: string }> {
  const res = await request<AuthResponse>("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

  if (res.error || !res.data) {
    return { error: res.error || "Échec de l'inscription." };
  }

  setSession(res.data.token, res.data.player);
  return { player: res.data.player };
}

export async function signIn(
  username: string,
  password: string,
): Promise<{ player?: Player; error?: string }> {
  const res = await request<AuthResponse>("/api/auth/signin", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

  if (res.error || !res.data) {
    return { error: res.error || "Échec de la connexion." };
  }

  setSession(res.data.token, res.data.player);
  return { player: res.data.player };
}

export function signOut(): void {
  clearSession();
}

export async function leaderboard(): Promise<LeaderboardEntry[]> {
  const res = await request<LeaderboardEntry[]>("/api/leaderboard");
  if (res.data && Array.isArray(res.data)) {
    return res.data;
  }
  return [];
}

export async function submitScore(score: number): Promise<Player | null> {
  const res = await request<SubmitScoreResponse>(
    "/api/scores",
    {
      method: "POST",
      body: JSON.stringify({ score }),
    },
    true,
  );

  if (res.data?.player) {
    const updated: Player = {
      username: res.data.player.username,
      highScore: res.data.player.highScore,
    };
    if (typeof window !== "undefined") {
      localStorage.setItem(PLAYER_KEY, JSON.stringify(updated));
    }
    return updated;
  }

  return null;
}
