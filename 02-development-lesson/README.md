# Snake Arena Classic

Je veux créer une application qui sera le frontend.  Pour ça, j'ai déjà réfléchi à créer le backend. Pour le backend, je veux juste implémenter des données mock et plus tard, j'implémenterai le backend moi-même.
Snake Arena — Product Specification

1. Vision

Snake Arena is a classic Snake game played on a square 20 × 20 grid.

The player controls a snake that moves one cell at a time. The snake grows by one cell every time it eats food. The snake's body is the only obstacle in the game, apart from the arena boundaries.

The objective is to eat as much food as possible without hitting the snake's own body or the arena boundaries.

The game also allows players to create an account, keep track of their personal high score, and view the global Top 10 leaderboard.

2. Target User

The player is an authenticated user who logs into the application with a username and password.

3. MVP Features

3.1 Authentication

The application allows a player to:

create an account with a username and password;

log in using their username and password;

access the game after authentication.

Each player has their own personal high score.

3.2 Starting a Game

When a new game is ready to start:

the snake is placed in the center of the arena;

the snake initially has a length of 3 cells;

the game is waiting to start;

no movement occurs until the player presses a direction key.

The direction keys are the four arrow keys:

↑

↓

←

→

The first arrow key pressed:

immediately starts the game;

determines the initial movement direction of the snake's head.

The initial orientation of the other two body segments has no functional significance.

3.3 Movement

The snake:

moves automatically;

advances one cell at each fixed time interval;

maintains a constant speed throughout the game;

never accelerates, regardless of its length or score.

The player only controls the movement direction.

An immediate 180-degree turn is not allowed.

If the snake is moving right and the player presses ←, the command is ignored. The snake continues moving in its current direction.

3.4 Food

Only one piece of food is present in the arena at a time.

When food is consumed:

the player gains 1 point;

the snake grows by one cell;

a new piece of food appears randomly on a free cell.

Food can never appear on a cell occupied by the snake.

3.5 Score

The score is exactly equal to the number of pieces of food consumed during the game.

Each piece of food consumed gives:

+1 point

The score starts at 0 at the beginning of each game.

3.6 Collisions

The game immediately ends when the snake's head:

hits its own body;

hits an arena boundary.

There are no additional obstacles in the arena.

3.7 Victory

The game is won when the snake occupies all cells in the arena and there is therefore no free cell available for a new piece of food.

The final score is then displayed.

3.8 End of Game

At the end of a game, whether the player wins or loses:

the game stops;

the final score is displayed;

the personal high score is updated if the new score is higher;

the result may be recorded in the global leaderboard;

a "Play Again" button allows the player to immediately start a new game.

3.9 Personal High Score

The player's high score is retained between games and after closing the application.

Whenever a player achieves a score higher than their previous high score, the high score is updated.

3.10 Global Leaderboard

The application stores the players' high scores.

It displays a global leaderboard limited to the Top 10 scores.

Each leaderboard entry contains at least:

the rank;

the player's username;

their score.

The leaderboard is shared by all players of the application.

3.11 Pause

The player can pause a game using the:

Spacebar

While paused:

the snake does not move;

the entire game logic is frozen;

no food is consumed;

no game state changes.

To resume the game, the player presses one of the four arrow keys.

The arrow key used to resume:

immediately resumes the game;

becomes the snake's new direction;

remains subject to the no-180-degree-turn rule.

4. User Stories

US-01 — Create an Account

As a new player,
I want to create an account with a username and password,
so that I can play and keep track of my scores.

Acceptance Criteria

A player can enter a username and password.

An account is created if the information is valid.

A username that is already in use cannot be reused.

The player can then log in using their credentials.

US-02 — Log In

As a registered player,
I want to log in with my username and password,
so that I can access the game and my scores.

Acceptance Criteria

A player can enter their username and password.

Valid credentials grant access to the application.

Invalid credentials prevent access to the game.

US-03 — Start a Game

As a logged-in player,
I want to start a game by pressing an arrow key,
so that I can immediately choose my initial direction.

Acceptance Criteria

The snake appears in the center of the arena.

Its initial length is 3 cells.

No movement occurs before an arrow key is pressed.

The first arrow key starts the game.

The first arrow key determines the initial direction.

US-04 — Control the Snake

As a player,
I want to control the snake using the keyboard arrow keys,
so that I can guide it toward the food.

Acceptance Criteria

The four arrow keys allow the player to change direction.

The snake moves one cell at each fixed time interval.

Its speed remains constant.

A command corresponding to the opposite direction is ignored.

US-05 — Eat Food

As a player,
I want the snake to grow when it eats food,
so that I can progress through the game.

Acceptance Criteria

Only one piece of food is present at a time.

Food always appears on a free cell.

When the snake's head reaches the food, it is consumed.

The score increases by 1.

The snake grows by one cell.

A new piece of food appears on a free cell.

US-06 — Avoid Collisions

As a player,
I want to lose when the snake collides with itself or the arena boundary,
so that the game follows the classic Snake rules.

Acceptance Criteria

Hitting the snake's own body immediately ends the game.

Hitting an arena boundary immediately ends the game.

The snake cannot cross the arena boundaries.

US-07 — Pause the Game

As a player,
I want to pause the game,
so that I can temporarily interrupt gameplay.

Acceptance Criteria

Pressing the Spacebar pauses the game.

The snake's movement stops immediately.

The entire game logic is frozen.

Pressing an arrow key resumes the game.

The arrow key used to resume becomes the new direction.

US-08 — View My Score

As a player,
I want to see my current score and high score,
so that I can track my performance.

Acceptance Criteria

The current game score is accessible during the game.

The final score is displayed at the end of the game.

The personal high score is retained after the game.

The high score is retained after closing and reopening the application.

US-09 — View the Leaderboard

As a player,
I want to view the application's Top 10 scores,
so that I can compare my performance with other players.

Acceptance Criteria

The leaderboard is shared among all players.

It contains at most 10 entries.

Scores are sorted from highest to lowest.

Each entry displays at least the player's username and score.

US-10 — Play Again

As a player,
I want to be able to play again immediately after a game,
so that I can try to improve my score.

Acceptance Criteria

A "Play Again" button is available after the game ends.

A new game resets the snake to 3 cells.

The new score starts at 0.

The personal high score is retained.

5. Functional Rules Summary

ElementRuleArena20 × 20 cellsObstaclesSnake's body onlyInitial length3 cellsInitial positionCenterFood1 at a timeGrowth+1 cell per piece of foodScore+1 per piece of foodMovement1 cell per fixed time intervalAccelerationNoneControlsKeyboard arrow keys180-degree turnNot allowedBody collisionImmediate defeatBoundary collisionImmediate defeatFood placementAlways on a free cellEntire arena filledVictoryPauseSpacebarResumeArrow keyPlay AgainButton after the gameHigh scorePersistent per playerLeaderboardGlobal Top 10AuthenticationUsername + password

6. Non-Goals / Out of Scope for the MVP

The following features are not part of the MVP:

fixed or moving obstacles in the arena;

multiple snakes simultaneously;

real-time multiplayer;

AI-controlled snakes;

progressive acceleration;

multiple levels or difficulty settings;

bonuses or penalties;

multiple pieces of food simultaneously;

teleportation through arena boundaries;

crossing the arena boundaries;

immediate 180-degree turns;

lives system;

saving an ongoing game;

detailed game history;

advanced statistics;

leaderboards beyond the Top 10;

points, rewards, or achievement systems;

notifications;

advanced snake customization;

mandatory sound effects;

predefined graphical design;

choice of frontend technology.

The frontend and its visual experience are left to Lovable. This specification primarily defines the expected functional behavior of the game.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/72426c22-85cc-4427-bfd3-196c0571541d).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
