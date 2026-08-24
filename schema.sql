-- Gaming Tournament Management System Schema
CREATE DATABASE IF NOT EXISTS tournament_db;
USE tournament_db;

-- 1. Users
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- Will store hashed password
    email VARCHAR(100) NOT NULL UNIQUE,
    role ENUM('admin', 'user') DEFAULT 'user'
);

-- 2. Games
CREATE TABLE games (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    genre VARCHAR(50)
);

-- 3. Players (linked to Users)
CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 4. Teams
CREATE TABLE teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    captain_id INT,
    FOREIGN KEY (captain_id) REFERENCES players(player_id) ON DELETE SET NULL
);

-- Update players to have team_id
ALTER TABLE players ADD COLUMN team_id INT;
ALTER TABLE players ADD FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL;

-- 5. Tournaments
CREATE TABLE tournaments (
    tournament_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    game_id INT,
    FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE SET NULL,
    CONSTRAINT chk_dates CHECK (end_date >= start_date)
);

-- 6. Registrations
CREATE TABLE registrations (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT NOT NULL,
    team_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
    UNIQUE(tournament_id, team_id) -- No duplicate registration
);

-- 7. Matches
CREATE TABLE matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT NOT NULL,
    team1_id INT NOT NULL,
    team2_id INT NOT NULL,
    match_date DATETIME NOT NULL,
    status ENUM('scheduled', 'completed') DEFAULT 'scheduled',
    FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id) ON DELETE CASCADE,
    FOREIGN KEY (team1_id) REFERENCES teams(team_id),
    FOREIGN KEY (team2_id) REFERENCES teams(team_id)
);

-- 8. Results
CREATE TABLE results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL UNIQUE,
    winner_team_id INT,
    score_team1 INT NOT NULL DEFAULT 0,
    score_team2 INT NOT NULL DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    FOREIGN KEY (winner_team_id) REFERENCES teams(team_id),
    CONSTRAINT chk_scores CHECK (score_team1 >= 0 AND score_team2 >= 0)
);

-- Sample Data
-- Password for admin: 'adminpass'
-- Password for player1: 'playerpass'
INSERT INTO users (username, password, email, role) VALUES 
('admin', '$2b$12$E/sUVbvhd5eauZJp4BR1ueYcfd4/JJyaLSmC5i3dJgjNLPGgnJ1kC', 'admin@example.com', 'admin'),
('player1', '$2b$12$S9TMuv56Vf4tqwnBYeWgAOcLzpacigo7DOgwkcSvsqWZYRAdsgBXi', 'player1@example.com', 'user');

INSERT INTO games (name, genre) VALUES 
('Valorant', 'FPS'),
('Dota 2', 'MOBA');

INSERT INTO teams (name) VALUES ('Team Alpha'), ('Team Beta');

INSERT INTO players (user_id, name, email, team_id) VALUES 
(2, 'Player One', 'p1@example.com', 1);

UPDATE teams SET captain_id = 1 WHERE team_id = 1;

INSERT INTO tournaments (name, start_date, end_date, game_id) VALUES 
('Summer Valorant Cup', '2026-09-01', '2026-09-10', 1);

INSERT INTO registrations (tournament_id, team_id) VALUES (1, 1), (1, 2);
