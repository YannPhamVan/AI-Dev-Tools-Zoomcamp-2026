import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useState } from "react";
import { SnakeGame } from "@/components/SnakeGame";
import {
  currentPlayer,
  leaderboard,
  signIn,
  signOut,
  signUp,
  submitScore,
  type Player,
} from "@/lib/mock-backend";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Snake Arena — Jeu du serpent 20x20 et classement Top 10" },
      {
        name: "description",
        content:
          "Joue au Snake classique sur une arène 20x20, garde ton meilleur score et compare-toi au Top 10 mondial.",
      },
      { property: "og:title", content: "Snake Arena — Jeu du serpent et classement Top 10" },
      {
        property: "og:description",
        content:
          "Snake classique 20x20 : mange, grandis, évite les murs et ton propre corps. Record personnel et Top 10.",
      },
    ],
  }),
  component: Home,
});

function Home() {
  const [player, setPlayer] = useState<Player | null>(null);
  const [ready, setReady] = useState(false);
  const [board, setBoard] = useState<Array<{ rank: number; username: string; score: number }>>([]);

  useEffect(() => {
    setPlayer(currentPlayer());
    setBoard(leaderboard());
    setReady(true);
  }, []);

  const handleGameOver = useCallback(
    (score: number) => {
      if (!player) return;
      const updated = submitScore(player.username, score);
      if (updated) setPlayer({ ...updated });
      setBoard(leaderboard());
    },
    [player],
  );

  if (!ready) return null;

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-5 py-8">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Snake <span className="text-primary">Arena</span>
          </h1>
          <p className="text-sm text-muted-foreground">Arène 20 × 20 · vitesse constante</p>
        </div>
        {player && (
          <div className="flex items-center gap-3 text-sm">
            <span className="text-muted-foreground">
              Connecté : <span className="text-foreground font-semibold">{player.username}</span>
            </span>
            <button
              className="btn-ghost"
              onClick={() => {
                signOut();
                setPlayer(null);
              }}
            >
              Se déconnecter
            </button>
          </div>
        )}
      </header>

      <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
        <section>
          {player ? (
            <SnakeGame onGameOver={handleGameOver} highScore={player.highScore} />
          ) : (
            <AuthPanel
              onAuth={(p) => {
                setPlayer(p);
                setBoard(leaderboard());
              }}
            />
          )}
        </section>

        <aside className="panel h-fit p-5">
          <h2 className="text-lg font-semibold">Top 10 mondial</h2>
          <ol className="mt-4 space-y-1">
            {board.map((row) => (
              <li
                key={row.username}
                className={`flex items-center justify-between rounded-md px-3 py-2 text-sm ${
                  player?.username === row.username ? "bg-secondary" : ""
                }`}
              >
                <span className="flex items-center gap-3">
                  <span className="w-5 text-muted-foreground tabular-nums">{row.rank}</span>
                  <span className="font-medium">{row.username}</span>
                </span>
                <span className="font-bold text-primary tabular-nums">{row.score}</span>
              </li>
            ))}
          </ol>
        </aside>
      </div>
    </main>
  );
}

function AuthPanel({ onAuth }: { onAuth: (p: Player) => void }) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const res = mode === "login" ? signIn(username, password) : signUp(username, password);
    if ("error" in res && res.error) {
      setError(res.error);
      return;
    }
    if ("player" in res && res.player) onAuth(res.player);
  }

  return (
    <div className="panel mx-auto max-w-md p-6">
      <div className="mb-5 flex gap-2">
        <button
          className={mode === "login" ? "btn-primary" : "btn-ghost"}
          onClick={() => {
            setMode("login");
            setError(null);
          }}
        >
          Connexion
        </button>
        <button
          className={mode === "signup" ? "btn-primary" : "btn-ghost"}
          onClick={() => {
            setMode("signup");
            setError(null);
          }}
        >
          Créer un compte
        </button>
      </div>
      <form onSubmit={submit} className="space-y-3">
        <div>
          <label className="text-sm text-muted-foreground" htmlFor="u">
            Pseudo
          </label>
          <input
            id="u"
            className="field focus:field-focus mt-1"
            value={username}
            maxLength={20}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          />
        </div>
        <div>
          <label className="text-sm text-muted-foreground" htmlFor="p">
            Mot de passe
          </label>
          <input
            id="p"
            type="password"
            className="field focus:field-focus mt-1"
            value={password}
            maxLength={64}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <button type="submit" className="btn-primary hover:btn-primary-hover w-full">
          {mode === "login" ? "Se connecter" : "Créer mon compte"}
        </button>
      </form>
      <p className="mt-4 text-xs text-muted-foreground">
        Données de démonstration locales — le vrai backend viendra plus tard. Compte de test :
        cobra_kai / demo
      </p>
    </div>
  );
}
