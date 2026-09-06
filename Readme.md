# Gaming Tournament Management System — Codebase Analysis

---

## Project Map

```
dbms/
├── app.py                    → Main Flask application (ALL routes, auth, logic)
├── schema.sql                → Database schema + sample data
├── fix_css.py                → Utility script to inject CSS link into templates
├── static/
│   └── style.css             → Full dark-theme UI styling
├── templates/
│   ├── login.html            → Login page
│   ├── index.html            → Dashboard (homepage after login)
│   ├── players.html          → List all players
│   ├── add_player.html       → Add player form
│   ├── teams.html            → List all teams
│   ├── add_team.html         → Add team form
│   ├── games.html            → List all games
│   ├── add_game.html         → Add game form
│   ├── tournaments.html      → List all tournaments
│   ├── add_tournament.html   → Add tournament form
│   ├── registrations.html    → List all registrations
│   ├── add_registration.html → Add registration form
│   ├── matches.html          → List all matches
│   ├── add_match.html        → Add/schedule match form
│   ├── results.html          → List all results
│   └── add_result.html       → Record match result form
└── Erd/
    └── Untitled-2026-01-22-1530.png → ER Diagram image
```

**Tech Stack:** Python + Flask + MySQL + Jinja2 + Bcrypt + HTML/CSS (no JS framework)

---

## Tech Stack & Configuration

| Component | Technology | Details |
|-----------|-----------|---------|
| Backend | Flask (Python) | Single file: `app.py` |
| Database | MySQL | Database: `tournament_db` |
| DB Connector | `mysql.connector` | Direct queries, no ORM |
| Password Hashing | `flask-bcrypt` | bcrypt hashes |
| Templating | Jinja2 | 16 HTML templates |
| Frontend | Plain HTML + CSS | Dark gaming theme, no JS |
| Config | Hardcoded in `app.py` | `db_config` dict at line 11 |

> `app.py:6-16` — App setup, bcrypt init, DB config with hardcoded credentials

---

## Database Schema (Quick Reference)

### Table: `users`

| Column | Type | Constraints |
|--------|------|-------------|
| **user_id** | INT | PK, AUTO_INCREMENT |
| username | VARCHAR(50) | NOT NULL, UNIQUE |
| password | VARCHAR(255) | NOT NULL (bcrypt hashed) |
| email | VARCHAR(100) | NOT NULL, UNIQUE |
| role | ENUM('admin','user') | DEFAULT 'user' |

### Table: `games`

| Column | Type | Constraints |
|--------|------|-------------|
| **game_id** | INT | PK, AUTO_INCREMENT |
| name | VARCHAR(100) | NOT NULL, UNIQUE |
| genre | VARCHAR(50) | — |

### Table: `players`

| Column | Type | Constraints |
|--------|------|-------------|
| **player_id** | INT | PK, AUTO_INCREMENT |
| user_id | INT | FK → users(user_id), ON DELETE CASCADE |
| name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(100) | NOT NULL, UNIQUE |
| team_id | INT | FK → teams(team_id), ON DELETE SET NULL |

### Table: `teams`

| Column | Type | Constraints |
|--------|------|-------------|
| **team_id** | INT | PK, AUTO_INCREMENT |
| name | VARCHAR(100) | NOT NULL, UNIQUE |
| captain_id | INT | FK → players(player_id), ON DELETE SET NULL |

### Table: `tournaments`

| Column | Type | Constraints |
|--------|------|-------------|
| **tournament_id** | INT | PK, AUTO_INCREMENT |
| name | VARCHAR(100) | NOT NULL, UNIQUE |
| start_date | DATE | NOT NULL |
| end_date | DATE | NOT NULL |
| game_id | INT | FK → games(game_id), ON DELETE SET NULL |
| — | — | CHECK (end_date >= start_date) |

### Table: `registrations`

| Column | Type | Constraints |
|--------|------|-------------|
| **registration_id** | INT | PK, AUTO_INCREMENT |
| tournament_id | INT | FK → tournaments, ON DELETE CASCADE |
| team_id | INT | FK → teams, ON DELETE CASCADE |
| registration_date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| — | — | UNIQUE(tournament_id, team_id) |

### Table: `matches`

| Column | Type | Constraints |
|--------|------|-------------|
| **match_id** | INT | PK, AUTO_INCREMENT |
| tournament_id | INT | FK → tournaments, ON DELETE CASCADE |
| team1_id | INT | FK → teams |
| team2_id | INT | FK → teams |
| match_date | DATETIME | NOT NULL |
| status | ENUM('scheduled','completed') | DEFAULT 'scheduled' |

### Table: `results`

| Column | Type | Constraints |
|--------|------|-------------|
| **result_id** | INT | PK, AUTO_INCREMENT |
| match_id | INT | FK → matches, ON DELETE CASCADE, UNIQUE |
| winner_team_id | INT | FK → teams |
| score_team1 | INT | NOT NULL, DEFAULT 0 |
| score_team2 | INT | NOT NULL, DEFAULT 0 |
| — | — | CHECK (score >= 0) |

---

## Relationships

```
users  ──<  players          (1 user → 1 player, via user_id FK)
teams  ──<  players          (1 team → many players, via team_id FK)
teams  ──<  teams.captain    (1 player → 1 team as captain)
games  ──<  tournaments      (1 game → many tournaments, via game_id FK)
tournaments ──< registrations (1 tournament → many registrations)
teams     ──< registrations  (1 team → many registrations)
tournaments ──< matches      (1 tournament → many matches)
teams     ──< matches        (2 FKs: team1_id, team2_id)
matches   ──< results        (1 match → 1 result, via match_id UNIQUE)
teams     ──< results        (winner_team_id FK)
```

**Chain:** `User → Player → Team → Registration/Match → Tournament → Game`

---

## Authentication & Authorization

### How Login Works

```
login.html form → POST /login → route:login() [app.py:39-59]
  → SELECT * FROM users WHERE username = %s
  → bcrypt.check_password_hash(stored_hash, input_password)
  → If match: session['user_id'] = user['user_id'], session['role'] = user['role']
  → Redirect to index (dashboard)
  → If fail: render login.html with error message
```

> `app.py:39-59` — Login route. Uses parameterized query. Bcrypt verification.

### How Logout Works

```
GET /logout → session.clear() → redirect to login
```

> `app.py:61-64`

### Two Decorator-Based Guards

| Decorator | File:Line | What It Does |
|-----------|-----------|-------------|
| `@login_required` | `app.py:22-28` | Checks `session['user_id']` exists. If not → redirect to `/login` |
| `@admin_required` | `app.py:30-37` | Checks `session['user_id']` exists AND `session['role'] == 'admin'`. If not → flash "Access Denied" → redirect to `/` |

### Role Storage

- Role is stored in the `users` table as ENUM('admin', 'user')
- On login, role is copied to `session['role']` (`app.py:54`)
- Every admin route checks `session.get('role') != 'admin'` (`app.py:33`)

---

## Permissions Matrix

Based on **actual code** (decorator usage on each route):

| Action | User | Admin | Route |
|--------|------|-------|-------|
| **Login** | ✅ | ✅ | `/login` — no decorator |
| **Logout** | ✅ | ✅ | `/logout` — no decorator |
| **View Dashboard** | ✅ | ✅ | `/` — `@login_required` |
| **View Players** | ✅ | ✅ | `/players` — `@login_required` |
| **Add Player** | ❌ | ✅ | `/players/add` — `@admin_required` |
| **Delete Player** | ❌ | ✅ | `/players/delete/<id>` — `@admin_required` |
| **View Teams** | ✅ | ✅ | `/teams` — `@login_required` |
| **Add Team** | ❌ | ✅ | `/teams/add` — `@admin_required` |
| **Delete Team** | ❌ | ✅ | `/teams/delete/<id>` — `@admin_required` |
| **View Games** | ✅ | ✅ | `/games` — `@login_required` |
| **Add Game** | ❌ | ✅ | `/games/add` — `@admin_required` |
| **Delete Game** | ❌ | ✅ | `/games/delete/<id>` — `@admin_required` |
| **View Tournaments** | ✅ | ✅ | `/tournaments` — `@login_required` |
| **Add Tournament** | ❌ | ✅ | `/tournaments/add` — `@admin_required` |
| **Delete Tournament** | ❌ | ✅ | `/tournaments/delete/<id>` — `@admin_required` |
| **View Registrations** | ✅ | ✅ | `/registrations` — `@login_required` |
| **Add Registration** | ✅ | ✅ | `/registrations/add` — `@login_required` ⚠️ |
| **Delete Registration** | ✅ | ✅ | `/registrations/delete/<id>` — `@login_required` ⚠️ |
| **View Matches** | ✅ | ✅ | `/matches` — `@login_required` |
| **Add Match** | ❌ | ✅ | `/matches/add` — `@admin_required` |
| **Delete Match** | ❌ | ✅ | `/matches/delete/<id>` — `@admin_required` |
| **View Results** | ✅ | ✅ | `/results` — `@login_required` |
| **Add Result** | ❌ | ✅ | `/results/add` — `@admin_required` |
| **Delete Result** | ❌ | ✅ | `/results/delete/<id>` — `@admin_required` |

> ⚠️ **Notable:** Registrations (add + delete) use `@login_required`, NOT `@admin_required`. Any logged-in user can register/unregister teams for tournaments.

### What Happens When User Tries Admin Action

```
User clicks "Add Player" button → GET /players/add
  → @admin_required decorator fires [app.py:30-37]
  → session['role'] is 'user', not 'admin'
  → flash('Access Denied: Admin role required for this action.')
  → redirect(url_for('index'))
  → User sees flash message on dashboard
```

> `app.py:34-36` — The exact access denied logic

---

## CRUD Operations Per Entity

### Players

| Operation | Implemented? | Route | Method | SQL |
|-----------|-------------|-------|--------|-----|
| **CREATE** | ✅ | `/players/add` | POST | `INSERT INTO players (name, email, user_id) VALUES (%s, %s, %s)` |
| **READ** | ✅ | `/players` | GET | `SELECT * FROM players` |
| **UPDATE** | ❌ Not implemented | — | — | — |
| **DELETE** | ✅ | `/players/delete/<id>` | GET | `DELETE FROM players WHERE player_id = %s` |

> `app.py:82-103` (add), `app.py:71-80` (list), `app.py:105-114` (delete)
> Roles: Add/Delete = Admin only, View = Any logged-in user

### Teams

| Operation | Implemented? | Route | Method | SQL |
|-----------|-------------|-------|--------|-----|
| **CREATE** | ✅ | `/teams/add` | POST | `INSERT INTO teams (name, captain_id) VALUES (%s, %s)` |
| **READ** | ✅ | `/teams` | GET | `SELECT * FROM teams` |
| **UPDATE** | ❌ Not implemented | — | — | — |
| **DELETE** | ✅ | `/teams/delete/<id>` | GET | `DELETE FROM teams WHERE team_id = %s` |

> `app.py:127-147` (add), `app.py:116-125` (list), `app.py:149-158` (delete)

### Games

| Operation | Implemented? | Route | Method | SQL |
|-----------|-------------|-------|--------|-----|
| **CREATE** | ✅ | `/games/add` | POST | `INSERT INTO games (name, genre) VALUES (%s, %s)` |
| **READ** | ✅ | `/games` | GET | `SELECT * FROM games` |
| **UPDATE** | ❌ Not implemented | — | — | — |
| **DELETE** | ✅ | `/games/delete/<id>` | GET | `DELETE FROM games WHERE game_id = %s` |

> `app.py:171-186` (add), `app.py:160-169` (list), `app.py:188-197` (delete)

### Tournaments

| Operation | Implemented? | Route | Method | SQL |
|-----------|-------------|-------|--------|-----|
| **CREATE** | ✅ | `/tournaments/add` | POST | `INSERT INTO tournaments (name, start_date, end_date, game_id) VALUES (%s, %s, %s, %s)` |
| **READ** | ✅ | `/tournaments` | GET | `SELECT * FROM tournaments` |
| **UPDATE** | ❌ Not implemented | — | — | — |
| **DELETE** | ✅ | `/tournaments/delete/<id>` | GET | `DELETE FROM tournaments WHERE tournament_id = %s` |

> `app.py:210-232` (add), `app.py:199-208` (list), `app.py:234-243` (delete)

### Registrations

| Operation | Implemented? | Route | Method | SQL |
|-----------|-------------|-------|--------|-----|
| **CREATE** | ✅ | `/registrations/add` | POST | `INSERT INTO registrations (tournament_id, team_id) VALUES (%s, %s)` |
| **READ** | ✅ | `/registrations` | GET | `SELECT * FROM registrations` |
| **UPDATE** | ❌ Not implemented | — | — | — |
| **DELETE** | ✅ | `/registrations/delete/<id>` | GET | `DELETE FROM registrations WHERE registration_id = %s` |

> `app.py:256-278` (add), `app.py:245-254` (list), `app.py:280-289` (delete)

### Matches

| Operation | Implemented? | Route | Method | SQL |
|-----------|-------------|-------|--------|-----|
| **CREATE** | ✅ | `/matches/add` | POST | `INSERT INTO matches (tournament_id, team1_id, team2_id, match_date) VALUES (%s, %s, %s, %s)` |
| **READ** | ✅ | `/matches` | GET | `SELECT * FROM matches` |
| **UPDATE** | ❌ Not implemented | — | — | — |
| **DELETE** | ✅ | `/matches/delete/<id>` | GET | `DELETE FROM matches WHERE match_id = %s` |

> `app.py:302-326` (add), `app.py:291-300` (list), `app.py:328-337` (delete)

### Results

| Operation | Implemented? | Route | Method | SQL |
|-----------|-------------|-------|--------|-----|
| **CREATE** | ✅ | `/results/add` | POST | `INSERT INTO results (match_id, winner_team_id, score_team1, score_team2) VALUES (%s, %s, %s, %s)` |
| **READ** | ✅ | `/results` | GET | `SELECT * FROM results` |
| **UPDATE** | ❌ Not implemented | — | — | — |
| **DELETE** | ✅ | `/results/delete/<id>` | GET | `DELETE FROM results WHERE result_id = %s` |

> `app.py:350-374` (add), `app.py:339-348` (list), `app.py:376-385` (delete)

### Summary: UPDATE is NOT implemented for any entity.

---

## Execution Flows

### Login Flow

```
User visits /login (GET)
  → login.html renders with username + password fields
  → User submits form (POST)
  → app.py:login() receives form data
  → Query: SELECT * FROM users WHERE username = %s
  → bcrypt.check_password_hash(db_hash, input_password)
  → If valid: session['user_id'] + session['role'] stored → redirect /
  → If invalid: re-render login.html with error="Invalid username or password"
```

### Adding a Player (Admin Flow)

```
Admin clicks "Add New Player" on /players
  → GET /players/add → @admin_required checks session role
  → Query: SELECT user_id, username FROM users (to populate dropdown)
  → add_player.html renders with user dropdown
  → Admin fills: name, email, selects user → POST
  → INSERT INTO players (name, email, user_id) VALUES (...)
  → conn.commit() → redirect /players
```

### User Tries to Add Player (Unauthorized Flow)

```
User clicks "Add New Player" on /players
  → GET /players/add → @admin_required fires
  → session['role'] == 'user' ≠ 'admin'
  → flash('Access Denied: Admin role required for this action.')
  → redirect(url_for('index'))
  → User sees red flash message on dashboard
```

### Registering a Team for a Tournament (Any User)

```
User goes to /registrations/add (GET) → @login_required only
  → Query: SELECT tournament_id, name FROM tournaments
  → Query: SELECT team_id, name FROM teams
  → add_registration.html renders with dropdowns
  → User selects tournament + team → POST
  → INSERT INTO registrations (tournament_id, team_id) VALUES (...)
  → redirect /registrations
```

---

## File-by-File Explanation

### `app.py` — The Entire Backend (389 lines)

| Lines | Responsibility |
|-------|---------------|
| 1-4 | Imports: Flask, mysql.connector, bcrypt, wraps |
| 6-8 | App init, secret key, bcrypt init |
| 10-16 | DB config dict (host, user, password, database) |
| 18-19 | `get_db_connection()` — returns MySQL connection |
| 22-28 | `@login_required` decorator — checks session has user_id |
| 30-37 | `@admin_required` decorator — checks session has user_id AND role=='admin' |
| 39-59 | `/login` route — authenticate user |
| 61-64 | `/logout` route — clear session |
| 66-69 | `/` (index) — dashboard page |
| 71-80 | `/players` — list all players |
| 82-103 | `/players/add` — admin adds player (links to user) |
| 105-114 | `/players/delete/<id>` — admin deletes player |
| 116-125 | `/teams` — list all teams |
| 127-147 | `/teams/add` — admin adds team with optional captain |
| 149-158 | `/teams/delete/<id>` — admin deletes team |
| 160-169 | `/games` — list all games |
| 171-186 | `/games/add` — admin adds game (name + genre) |
| 188-197 | `/games/delete/<id>` — admin deletes game |
| 199-208 | `/tournaments` — list all tournaments |
| 210-232 | `/tournaments/add` — admin adds tournament linked to a game |
| 234-243 | `/tournaments/delete/<id>` — admin deletes tournament |
| 245-254 | `/registrations` — list all registrations |
| 256-278 | `/registrations/add` — **any logged-in user** registers team to tournament |
| 280-289 | `/registrations/delete/<id>` — **any logged-in user** can delete |
| 291-300 | `/matches` — list all matches |
| 302-326 | `/matches/add` — admin schedules match between two teams |
| 328-337 | `/matches/delete/<id>` — admin deletes match |
| 339-348 | `/results` — list all results |
| 350-374 | `/results/add` — admin records match result with scores |
| 376-385 | `/results/delete/<id>` — admin deletes result |
| 387-388 | `app.run(debug=True)` |

**Key pattern:** Every route follows the same structure:
1. Open DB connection
2. Execute SQL query (parameterized with `%s`)
3. `conn.commit()` for writes
4. Close cursor + connection
5. Redirect or render template with data

### `schema.sql` — Database Definition (110 lines)

- Creates `tournament_db` database
- Creates 8 tables with PKs, FKs, UNIQUE constraints, CHECK constraints
- Includes `ON DELETE CASCADE` and `ON DELETE SET NULL` for referential integrity
- Pre-populates with sample data (admin user, 1 player user, 2 games, 2 teams, 1 tournament, 2 registrations)
- Sample passwords: admin='adminpass', player1='playerpass' (bcrypt hashed)

### `templates/*.html` — 16 Templates

| Template | Purpose |
|----------|---------|
| `login.html` | Standalone login page, no navbar, shows error flash |
| `index.html` | Dashboard with nav + hero section + 7 dash-cards linking to each entity |
| `players.html` | Table listing players, "Add New Player" button, delete links |
| `add_player.html` | Form: name + email + user dropdown → POST |
| `teams.html` | Table listing teams, delete links |
| `add_team.html` | Form: team name + captain dropdown (optional) → POST |
| `games.html` | Table listing games, delete links |
| `add_game.html` | Form: game name + genre → POST |
| `tournaments.html` | Table listing tournaments, delete links |
| `add_tournament.html` | Form: name + start_date + end_date + game dropdown → POST |
| `registrations.html` | Table listing registrations, delete links |
| `add_registration.html` | Form: tournament dropdown + team dropdown → POST |
| `matches.html` | Table listing matches with status, delete links |
| `add_match.html` | Form: tournament dropdown + team1 + team2 + datetime → POST |
| `results.html` | Table listing results, delete links |
| `add_result.html` | Form: match dropdown + winner team + scores → POST |

**Template pattern:** Every list page has:
- Same navbar with 7 links
- Flash message display (`get_flashed_messages()`)
- Page head with title + "Add" button
- HTML table with data loop (`{% for ... in ... %}`)
- Delete link per row with `onclick="return confirm('Are you sure?')"`
- Footer

> ⚠️ Nav "Add" buttons and Delete links are visible to ALL logged-in users in the HTML, even though the routes behind them enforce `@admin_required`. The UI does not hide admin-only actions from normal users (they just get redirected with an access denied message).

### `static/style.css` — Full Dark Gaming Theme (588 lines)

- CSS custom properties (variables) for theming
- Dark color scheme: navy/slate background, indigo primary, cyan accent
- Sticky navbar with blur backdrop
- Dashboard grid cards with hover animations
- Responsive design (mobile breakpoint at 720px)
- Styled forms, tables, alerts, login card

### `fix_css.py` — Utility Script (22 lines)

- Script to batch-inject `<link rel="stylesheet" href="/static/style.css">` into all HTML templates
- One-time utility, not part of the running application

---

## DBMS Concepts Demonstrated

| Concept | Where It Appears |
|---------|-----------------|
| **Primary Key (PK)** | All 8 tables have `INT AUTO_INCREMENT PRIMARY KEY` |
| **Foreign Key (FK)** | `players.user_id → users`, `teams.captain_id → players`, `players.team_id → teams`, `tournaments.game_id → games`, `registrations` has 2 FKs, `matches` has 3 FKs, `results` has 3 FKs |
| **ON DELETE CASCADE** | `players.user_id`, `registrations` (both FKs), `matches.tournament_id`, `results.match_id` |
| **ON DELETE SET NULL** | `teams.captain_id`, `players.team_id`, `tournaments.game_id` |
| **UNIQUE Constraint** | `users.username`, `users.email`, `games.name`, `players.email`, `teams.name`, `tournaments.name`, `registrations(tournament_id, team_id)` composite unique, `results.match_id` |
| **CHECK Constraint** | `tournaments`: `end_date >= start_date`, `results`: `score_team1 >= 0 AND score_team2 >= 0` |
| **ENUM Type** | `users.role` = ENUM('admin','user'), `matches.status` = ENUM('scheduled','completed') |
| **DEFAULT Values** | `users.role DEFAULT 'user'`, `matches.status DEFAULT 'scheduled'`, `results.scores DEFAULT 0`, `registrations.registration_date DEFAULT CURRENT_TIMESTAMP` |
| **NOT NULL** | Enforced on most important fields |
| **Composite Unique** | `UNIQUE(tournament_id, team_id)` in registrations — prevents duplicate team registrations |
| **1:1 Relationship** | `users ↔ players` (one user has one player profile) |
| **1:N Relationship** | `teams → players`, `games → tournaments`, `tournaments → matches`, `tournaments → registrations` |
| **M:N (via junction)** | Teams ↔ Tournaments (through `registrations` table — classic junction/bridge table) |
| **Parameterized Queries** | All SQL uses `%s` placeholders — prevents SQL injection |
| **Transactions** | `conn.commit()` called after every INSERT/DELETE — atomic writes |
| **Normalization** | Data is normalized: games stored separately, linked to tournaments via FK; players linked to users; teams linked to players |
| **Auto Increment** | All PKs use `AUTO_INCREMENT` |
| **Timestamp** | `registrations.registration_date` uses `DEFAULT CURRENT_TIMESTAMP` |

---

## Notable Observations & Issues

### What's Missing

- ❌ **No UPDATE operations** — You can only Create, Read, and Delete. No edit/update for any entity.
- ❌ **No user registration** — Users cannot sign up. Must be created directly in DB.
- ❌ **No JOIN queries in app.py** — All list queries are simple `SELECT *`. FK IDs are shown raw (e.g., `game_id` instead of game name). JOINs exist in schema but aren't used in app.py.
- ❌ **No input validation in backend** — Only HTML `required` attribute. No server-side validation beyond DB constraints.
- ❌ **No session timeout** — Sessions persist until logout or browser close.
- ❌ **No password change / profile edit**

### Potential Issues

- ⚠️ **Delete via GET request** — All deletes use GET (`/players/delete/1`), not DELETE or POST. Not RESTful and vulnerable to CSRF via link/image tags.
- ⚠️ **No CSRF protection** — Forms have no CSRF tokens.
- ⚠️ **Hardcoded secret key** — `app.secret_key = 'your_secret_key_here'` (`app.py:7`)
- ⚠️ **Hardcoded DB password** — `password: 'jelly123'` in source (`app.py:14`)
- ⚠️ **Debug mode on** — `app.run(debug=True)` in production (`app.py:388`)
- ⚠️ **UI shows admin buttons to all users** — The "Add" and "Delete" buttons appear in HTML for all users. Only the route enforces the restriction. User sees a flash redirect instead of a clean denied page.
- ⚠️ **`registration` and `registration` deletion is open to any user** — These routes use `@login_required` not `@admin_required`.

---

## How My Whole Project Works

```
1. User opens app → lands on /login page
2. Enters username + password
3. Backend queries users table → finds user → bcrypt checks password
4. If valid → session created (user_id + role stored) → redirected to Dashboard (/)
5. Dashboard shows 7 cards: Players, Teams, Games, Tournaments, Registrations, Matches, Results

6. User clicks any card → sees a list (table) of that entity
7. For ADD/DELETE actions:
   - Admin → @admin_required passes → operation completes → redirected back to list
   - Normal User → @admin_required fails → flash "Access Denied" → redirected to dashboard
   - Exception: Registrations add/delete → any logged-in user can do it

8. Each ADD form loads dropdown data from related tables (e.g., add_player shows all users)
9. POST inserts into MySQL via parameterized query → conn.commit() → redirect to list page

10. On logout → session.clear() → back to login
```

---

## What I Need to Know for Viva

### Architecture
- Flask (Python) web app with MySQL backend
- Single-file backend: `app.py` (389 lines) — no MVC framework
- Jinja2 templates for server-side rendering
- No ORM — raw SQL queries with `mysql.connector`
- Session-based authentication using Flask sessions

### Database
- 8 tables: users, games, players, teams, tournaments, registrations, matches, results
- Two roles stored in `users.role` ENUM: 'admin' and 'user'
- Passwords stored as bcrypt hashes
- Foreign keys with CASCADE and SET NULL for referential integrity
- CHECK constraints on tournament dates and match scores
- Composite unique key on registrations (tournament_id, team_id)

### Authentication
- Login validates credentials against MySQL using bcrypt
- Role stored in Flask session (`session['role']`)
- Two decorators: `@login_required` and `@admin_required`
- `@admin_required` checks `session.get('role') != 'admin'`

### Authorization
- Admin: full CRUD on all entities (except no UPDATE for anyone)
- User: can only VIEW all entities + can ADD/DELETE registrations
- Failed admin access → flash message + redirect to dashboard

### Security (What We Use)
- Parameterized SQL queries (prevents SQL injection)
- Bcrypt password hashing
- Session-based auth

### Security (What's Missing — bonus points in viva)
- No CSRF protection, no rate limiting, hardcoded secrets, debug mode on

### CRUD Coverage
- C + R + D implemented for all 6 entities (Players, Teams, Games, Tournaments, Matches, Results) + Registrations
- **UPDATE not implemented for any entity**

---

## Quick Revision

```
Project:       Gaming Tournament Management System (DBMS Project)
Stack:         Flask + MySQL + Jinja2 + Bcrypt + HTML/CSS
Backend:       app.py (single file, all routes)
Database:      tournament_db (8 tables)
Roles:         admin, user (ENUM in users table)

User can:      Login, View all entities (Players, Teams, Games,
               Tournaments, Registrations, Matches, Results),
               Add + Delete Registrations
Admin can:     Everything User can + Add/Delete Players, Teams,
               Games, Tournaments, Matches, Results

Main tables:   users → players → teams → tournaments → matches → results
                            ↘ registrations ↗
               games → tournaments

Key FKs:       players.user_id → users
               players.team_id → teams
               teams.captain_id → players
               tournaments.game_id → games
               registrations → tournaments + teams
               matches → tournaments + 2 teams
               results → match + winner team

Authentication: Login → bcrypt check → Flask session (user_id + role)
Authorization:  @login_required (checks session exists)
                @admin_required (checks session + role == 'admin')

Main CRUD:     CREATE + READ + DELETE for all entities
               ❌ UPDATE not implemented anywhere

Important SQL:  All parameterized with %s (SQL injection safe)
                conn.commit() after every write operation
                cursor(dictionary=True) for SELECT (returns dicts)
                cursor() for INSERT/DELETE

Key files:      app.py        — backend logic + all routes
                schema.sql    — database schema + sample data
                style.css     — dark gaming theme UI
                templates/    — 16 Jinja2 HTML templates
```
