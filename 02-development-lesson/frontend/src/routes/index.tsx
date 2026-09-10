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