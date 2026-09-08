import { useCallback, useEffect, useRef, useState } from "react";

export const SIZE = 20;
type Cell = { x: number; y: number };
type Dir = "up" | "down" | "left" | "right";
type Status = "ready" | "running" | "paused" | "lost" | "won";

const VECTORS: Record<Dir, Cell> = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};
const KEYS: Record<string, Dir> = {
  ArrowUp: "up",
  ArrowDown: "down",
  ArrowLeft: "left",
  ArrowRight: "right",
};
const OPPOSITE: Record<Dir, Dir> = { up: "down", down: "up", left: "right", right: "left" };
const TICK_MS = 130;

function initialSnake(): Cell[] {
  const c = Math.floor(SIZE / 2);
  return [
    { x: c, y: c },
    { x: c - 1, y: c },
    { x: c - 2, y: c },
  ];
}

function randomFood(snake: Cell[]): Cell | null {
  const free: Cell[] = [];
  for (let y = 0; y < SIZE; y++) {
    for (let x = 0; x < SIZE; x++) {
      if (!snake.some((s) => s.x === x && s.y === y)) free.push({ x, y });
    }
  }
  if (free.length === 0) return null;
  return free[Math.floor(Math.random() * free.length)] ?? null;
}

export function SnakeGame({
  onGameOver,
  highScore,
}: {
  onGameOver: (score: number) => void;
  highScore: number;
}) {
  const [snake, setSnake] = useState<Cell[]>(initialSnake);
  const [food, setFood] = useState<Cell>({ x: 4, y: 4 });
  const [status, setStatus] = useState<Status>("ready");
  const [score, setScore] = useState(0);
  const dirRef = useRef<Dir>("right");
  const queuedRef = useRef<Dir | null>(null);
  const reported = useRef(false);

  const reset = useCallback(() => {
    const s = initialSnake();
    setSnake(s);
    setFood(randomFood(s) ?? { x: 0, y: 0 });
    setScore(0);
    setStatus("ready");
    dirRef.current = "right";
    queuedRef.current = null;
    reported.current = false;
  }, []);

  useEffect(() => {
    setFood(randomFood(initialSnake()) ?? { x: 0, y: 0 });
  }, []);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.code === "Space") {
        e.preventDefault();
        setStatus((s) => (s === "running" ? "paused" : s));
        return;
      }
      const dir = KEYS[e.key];
      if (!dir) return;
      e.preventDefault();
      setStatus((s) => {
        if (s === "lost" || s === "won") return s;
        if (s === "ready") {
          dirRef.current = dir;
          return "running";
        }
        if (s === "paused") {
          if (dir !== OPPOSITE[dirRef.current]) dirRef.current = dir;
          return "running";
        }
        if (dir !== OPPOSITE[dirRef.current]) queuedRef.current = dir;
        return s;
      });
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (status !== "running") return;
    const id = setInterval(() => {
      setSnake((prev) => {
        const next = queuedRef.current;
        if (next && next !== OPPOSITE[dirRef.current]) dirRef.current = next;
        queuedRef.current = null;

        const v = VECTORS[dirRef.current];
        const cur = prev[0]!;
        const head = { x: cur.x + v.x, y: cur.y + v.y };

        if (head.x < 0 || head.y < 0 || head.x >= SIZE || head.y >= SIZE) {
          setStatus("lost");
          return prev;
        }
        const ate = head.x === food.x && head.y === food.y;
        const body = ate ? prev : prev.slice(0, -1);
        if (body.some((c) => c.x === head.x && c.y === head.y)) {
          setStatus("lost");
          return prev;
        }
        const grown = [head, ...body];
        if (ate) {
          setScore((s) => s + 1);
          const nf = randomFood(grown);
          if (!nf) {
            setStatus("won");
          } else {
            setFood(nf);
          }
        }
        return grown;
      });
    }, TICK_MS);
    return () => clearInterval(id);
  }, [status, food]);

  useEffect(() => {
    if ((status === "lost" || status === "won") && !reported.current) {
      reported.current = true;
      onGameOver(score);
    }
  }, [status, score, onGameOver]);

  const cells = Array.from({ length: SIZE * SIZE }, (_, i) => {
    const x = i % SIZE;
    const y = Math.floor(i / SIZE);
    const isHead = snake[0]!.x === x && snake[0]!.y === y;
    const isBody = !isHead && snake.some((c) => c.x === x && c.y === y);
    const isFood = food.x === x && food.y === y;
    return { i, isHead, isBody, isFood };
  });

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex w-full items-center justify-between gap-4 text-sm">
        <div className="panel px-4 py-2">
          <span className="text-muted-foreground">Score</span>{" "}
          <span className="text-2xl font-bold text-primary tabular-nums">{score}</span>
        </div>
        <div className="panel px-4 py-2">
          <span className="text-muted-foreground">Record</span>{" "}
          <span className="text-2xl font-bold text-accent tabular-nums">
            {Math.max(highScore, score)}
          </span>
        </div>
      </div>

      <div className="panel relative p-3">
        <div
          className="grid gap-px"
          style={{
            gridTemplateColumns: `repeat(${SIZE}, minmax(0,1fr))`,
            width: "min(76vw, 520px)",
            aspectRatio: "1 / 1",
          }}
        >
          {cells.map((c) => (
            <div
              key={c.i}
              className={
                c.isHead
                  ? "rounded-[2px] bg-snake-head"
                  : c.isBody
                    ? "rounded-[2px] bg-snake"
                    : c.isFood
                      ? "animate-pulse rounded-full bg-food"
                      : "rounded-[2px] bg-grid"
              }
            />
          ))}
        </div>

        {status !== "running" && (
          <div className="absolute inset-3 flex flex-col items-center justify-center gap-3 rounded-lg bg-background/85 text-center backdrop-blur-sm">
            {status === "ready" && (
              <>
                <p className="text-xl font-semibold">Prêt ?</p>
                <p className="text-sm text-muted-foreground">
                  Appuie sur une flèche pour démarrer.
                </p>
              </>
            )}
            {status === "paused" && (
              <>
                <p className="text-xl font-semibold">Pause</p>
                <p className="text-sm text-muted-foreground">
                  Une flèche pour reprendre (elle devient ta direction).
                </p>
              </>
            )}
            {(status === "lost" || status === "won") && (
              <>
                <p className="text-2xl font-bold">
                  {status === "won" ? "Arène remplie, victoire !" : "Partie terminée"}
                </p>
                <p className="text-sm text-muted-foreground">
                  Score final : <span className="text-primary font-bold">{score}</span>
                </p>
                <button className="btn-primary hover:btn-primary-hover" onClick={reset}>
                  Rejouer
                </button>
              </>
            )}
          </div>
        )}
      </div>

      <p className="text-xs text-muted-foreground">
        Flèches pour diriger · Espace pour mettre en pause · demi-tour interdit
      </p>
    </div>
  );
}
