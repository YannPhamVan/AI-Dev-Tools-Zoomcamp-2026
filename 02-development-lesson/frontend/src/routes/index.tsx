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
  type LeaderboardEntry,
  type Player,
} from "@/lib/api";

export const Route = createFileRoute("/")({
  component: IndexPage,
});

function IndexPage() {
  const [player, setPlayer] = useState<Player | null>(null);
  const [board, setBoard] = useState<Leader