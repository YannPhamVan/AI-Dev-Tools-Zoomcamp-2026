# Snake Arena — Product Specification

## 1. Vision

Snake Arena is a classic Snake game played on a square 20 × 20 grid.

The player controls a snake that moves one cell at a time. The snake grows by one cell every time it eats food. The snake's body is the only obstacle in the game, apart from the arena boundaries.

The objective is to eat as much food as possible without hitting the snake's own body or the arena boundaries.

The game also allows players to create an account, keep track of their personal high score, and view the global Top 10 leaderboard.

## 2. Target User

The player is an authenticated user who logs into the application with a username and password.

## 3. MVP Features

### 3.1 Authentication

The application allows a player to:
- Create an account with a username and password;
- Log in using their username and password;
- Access the game after authentication.

Each player has their own personal high score.

### 3.2 Starting a Game

When a new game is ready to start:
- The snake is placed in the center of the arena;
- The snake initially has a length of 3 cells;
- The game is waiting to start;
- No movement occurs until the player presses a direction key.

The direction keys are the four arrow keys:
- ↑
- ↓
- ←
- →

The first arrow key pressed:
- Immediately starts the game;
- Determines the initial movement direction of the snake's head.

The initial orientation of the other two body segments has no functional significance.

### 3.3 Movement

The snake:
- Moves automatically;
- Advances one cell at each fixed time interval;
- Maintains a constant speed throughout the game;
- Never accelerates, regardless of its length or score.

The player only controls the movement direction.

An immediate 180-degree turn is not allowed. If the snake is moving right and the player presses ←, the command is ignored. The snake continues moving in its current direction.

### 3.4 Food

- Only one piece of food is present in the arena at a time.
- When food is consumed:
  - The player gains 1 point;
  - The snake grows by one cell;
  - A new piece of food appears randomly on a free cell.
- Food can never appear on a cell occupied by the snake.

### 3.5 Score

- The score is exactly equal to the number of pieces of food consumed during the game (+1 point per piece of food).
- The score starts at 0 at the beginning of each game.

### 3.6 Collisions

The game immediately ends when the snake's head:
- Hits its own body;
- Hits an arena boundary.

There are no additional obstacles in the arena.

### 3.7 Victory

- The game is won when the snake occupies all cells in the arena and there is therefore no free cell available for a new piece of food.
- The final score is then displayed.

### 3.8 End of Game

At the end of a game, whether the player wins or loses:
- The game stops;
- The final score is displayed;
- The personal high score is updated if the new score is higher;
- The result may be recorded in the global leaderboard;
- A "Play Again" button allows the player to immediately start a new game.

### 3.9 Personal High Score

- The player's high score is retained between games and after closing the application.
- Whenever a player achieves a score higher than their previous high score, the high score is updated.

### 3.10 Global Leaderboard

The application stores the players' high scores and displays a global leaderboard limited to the Top 10 scores.
Each leaderboard entry contains at least:
- The rank;
- The player's username;
- Their score.

The leaderboard is shared by all players of the application.

### 3.11 Pause

The player can pause a game using the **Spacebar**.
While paused:
- The snake does not move;
- The entire game logic is frozen;
- No food is consumed;
- No game state changes.

To resume the game, the player presses one of the four arrow keys.
The arrow key used to resume:
- Immediately resumes the game;
- Becomes the snake's new direction;
- Remains subject to the no-180-degree-turn rule.

---

## 4. User Stories

### US-01 — Create an Account
As a new player, I want to create an account with a username and password, so that I can play and keep track of my scores.
- **Acceptance Criteria**:
  - A player can enter a username and password.
  - An account is created if the information is valid.
  - A username that is already in use cannot be reused.
  - The player can then log in using their credentials.

### US-02 — Log In
As a registered player, I want to log in with my username and password, so that I can access the game and my scores.
- **Acceptance Criteria**:
  - A player can enter their username and password.
  - Valid credentials grant access to the application.
  - Invalid credentials prevent access to the game.

### US-03 — Start a Game
As a logged-in player, I want to start a game by pressing an arrow key, so that I can immediately choose my initial direction.
- **Acceptance Criteria**:
  - The snake appears in the center of the arena.
  - Its initial length is 3 cells.
  - No movement occurs before an arrow key is pressed.
  - The first arrow key starts the game and determines the initial direction.

### US-04 — Control the Snake
As a player, I want to control the snake using the keyboard arrow keys, so that I can guide it toward the food.
- **Acceptance Criteria**:
  - The four arrow keys allow the player to change direction.
  - The snake moves one cell at each fixed time interval.
  - Its speed remains constant.
  - A command corresponding to the opposite direction is ignored.

### US-05 — Eat Food
As a player, I want the snake to grow when it eats food, so that I can progress through the game.
- **Acceptance Criteria**:
  - Only one piece of food is present at a time.
  - Food always appears on a free cell.
  - When the snake's head reaches the food, it is consumed.
  - The score increases by 1 and the snake grows by one cell.
  - A new piece of food appears on a free cell.

### US-06 — Avoid Collisions
As a player, I want to lose when the snake collides with itself or the arena boundary, so that the game follows the classic Snake rules.
- **Acceptance Criteria**:
  - Hitting the snake's own body immediately ends the game.
  - Hitting an arena boundary immediately ends the game.
  - The snake cannot cross the arena boundaries.

### US-07 — Pause the Game
As a player, I want to pause the game, so that I can temporarily interrupt gameplay.
- **Acceptance Criteria**:
  - Pressing the Spacebar pauses the game.
  - The snake's movement stops immediately and game logic is frozen.
  - Pressing an arrow key resumes the game in that direction.

### US-08 — View My Score
As a player, I want to see my current score and high score, so that I can track my performance.
- **Acceptance Criteria**:
  - Current score is accessible during the game.
  - Final score is displayed at the end of the game.
  - Personal high score is retained after the game and after restart.

### US-09 — View the Leaderboard
As a player, I want to view the application's Top 10 scores, so that I can compare my performance with other players.
- **Acceptance Criteria**:
  - The leaderboard is shared among all players.
  - It contains at most 10 entries sorted from highest to lowest score.
  - Each entry displays the player's username and score.

### US-10 — Play Again
As a player, I want to be able to play again immediately after a game, so that I can try to improve my score.
- **Acceptance Criteria**:
  - A "Play Again" button is available after the game ends.
  - Resetting the game restores the snake to 3 cells at the center and resets score to 0.
  - Personal high score is retained.

---

## 5. Functional Rules Summary

| Element | Rule |
| :--- | :--- |
| **Arena** | 20 × 20 cells |
| **Obstacles** | Snake's body only |
| **Initial length** | 3 cells |
| **Initial position** | Center of the arena |
| **Food** | 1 at a time, always placed on a free cell |
| **Growth** | +1 cell per piece of food |
| **Score** | +1 point per piece of food |
| **Movement** | 1 cell per fixed time interval |
| **Acceleration** | None (constant speed) |
| **Controls** | Keyboard arrow keys (↑, ↓, ←, →) |
| **180-degree turn** | Not allowed (command ignored) |
| **Body collision** | Immediate defeat |
| **Boundary collision** | Immediate defeat |
| **Victory** | Entire arena filled (no free cell left) |
| **Pause** | Spacebar |
| **Resume** | Arrow key (becomes new direction) |
| **Play Again** | Button available after game ends |
| **High score** | Persistent per player |
| **Leaderboard** | Global Top 10 |
| **Authentication** | Username + password |

---

## 6. Non-Goals / Out of Scope for the MVP

The following features are not part of the MVP:
- Fixed or moving obstacles in the arena
- Multiple snakes simultaneously / real-time multiplayer
- AI-controlled snakes
- Progressive acceleration
- Multiple levels or difficulty settings
- Bonuses, power-ups, or penalties
- Multiple pieces of food simultaneously
- Teleportation through / crossing arena boundaries
- Immediate 180-degree turns
- Lives system
- Saving an ongoing game
- Detailed game history or advanced statistics
- Leaderboards beyond the Top 10
- Points, rewards, or achievement systems
- Notifications
- Advanced snake customization
- Mandatory sound effects
- Predefined graphical design
- Choice of frontend technology (left to Lovable / modern web stack)
