from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # In a real app, use a secure random key
bcrypt = Bcrypt(app)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'jelly123',
    'database': 'tournament_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Auth Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Access Denied: Admin role required for this action.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/players')
@login_required
def list_players():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM players")
    players = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('players.html', players=players)

@app.route('/players/add', methods=['GET', 'POST'])
@admin_required
def add_player():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        user_id = request.form['user_id']

        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (name, email, user_id) VALUES (%s, %s, %s)", (name, email, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_players'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, username FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('add_player.html', users=users)

@app.route('/players/delete/<int:player_id>')
@admin_required
def delete_player(player_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE player_id = %s", (player_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('list_players'))

@app.route('/teams')
@login_required
def list_teams():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM teams")
    teams = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('teams.html', teams=teams)

@app.route('/teams/add', methods=['GET', 'POST'])
@admin_required
def add_team():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        captain_id = request.form['captain_id'] if request.form['captain_id'] else None

        cursor = conn.cursor()
        cursor.execute("INSERT INTO teams (name, captain_id) VALUES (%s, %s)", (name, captain_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_teams'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT player_id, name FROM players")
    players = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('add_team.html', players=players)

@app.route('/teams/delete/<int:team_id>')
@admin_required
def delete_team(team_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('list_teams'))

@app.route('/games')
@login_required
def list_games():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM games")
    games = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('games.html', games=games)

@app.route('/games/add', methods=['GET', 'POST'])
@admin_required
def add_game():
    if request.method == 'POST':
        name = request.form['name']
        genre = request.form['genre']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO games (name, genre) VALUES (%s, %s)", (name, genre))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_games'))

    return render_template('add_game.html')

@app.route('/games/delete/<int:game_id>')
@admin_required
def delete_game(game_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM games WHERE game_id = %s", (game_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('list_games'))

@app.route('/tournaments')
@login_required
def list_tournaments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tournaments")
    tournaments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tournaments.html', tournaments=tournaments)

@app.route('/tournaments/add', methods=['GET', 'POST'])
@admin_required
def add_tournament():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        game_id = request.form['game_id']

        cursor = conn.cursor()
        cursor.execute("INSERT INTO tournaments (name, start_date, end_date, game_id) VALUES (%s, %s, %s, %s)", (name, start_date, end_date, game_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_tournaments'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT game_id, name FROM games")
    games = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('add_tournament.html', games=games)

@app.route('/tournaments/delete/<int:tournament_id>')
@admin_required
def delete_tournament(tournament_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tournaments WHERE tournament_id = %s", (tournament_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('list_tournaments'))

@app.route('/registrations')
@login_required
def list_registrations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM registrations")
    registrations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('registrations.html', registrations=registrations)

@app.route('/registrations/add', methods=['GET', 'POST'])
@login_required
def add_registration():
    conn = get_db_connection()
    if request.method == 'POST':
        tournament_id = request.form['tournament_id']
        team_id = request.form['team_id']

        cursor = conn.cursor()
        cursor.execute("INSERT INTO registrations (tournament_id, team_id) VALUES (%s, %s)", (tournament_id, team_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_registrations'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT tournament_id, name FROM tournaments")
    tournaments = cursor.fetchall()
    cursor.execute("SELECT team_id, name FROM teams")
    teams = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('add_registration.html', tournaments=tournaments, teams=teams)

@app.route('/registrations/delete/<int:registration_id>')
@login_required
def delete_registration(registration_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registrations WHERE registration_id = %s", (registration_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('list_registrations'))

@app.route('/matches')
@login_required
def list_matches():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM matches")
    matches = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('matches.html', matches=matches)

@app.route('/matches/add', methods=['GET', 'POST'])
@admin_required
def add_match():
    conn = get_db_connection()
    if request.method == 'POST':
        tournament_id = request.form['tournament_id']
        team1_id = request.form['team1_id']
        team2_id = request.form['team2_id']
        match_date = request.form['match_date']

        cursor = conn.cursor()
        cursor.execute("INSERT INTO matches (tournament_id, team1_id, team2_id, match_date) VALUES (%s, %s, %s, %s)", (tournament_id, team1_id, team2_id, match_date))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_matches'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT tournament_id, name FROM tournaments")
    tournaments = cursor.fetchall()
    cursor.execute("SELECT team_id, name FROM teams")
    teams = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('add_match.html', tournaments=tournaments, teams=teams)

@app.route('/matches/delete/<int:match_id>')
@admin_required
def delete_match(match_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches WHERE match_id = %s", (match_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('list_matches'))

@app.route('/results')
@login_required
def list_results():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM results")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('results.html', results=results)

@app.route('/results/add', methods=['GET', 'POST'])
@admin_required
def add_result():
    conn = get_db_connection()
    if request.method == 'POST':
        match_id = request.form['match_id']
        winner_team_id = request.form['winner_team_id']
        score_team1 = request.form['score_team1']
        score_team2 = request.form['score_team2']

        cursor = conn.cursor()
        cursor.execute("INSERT INTO results (match_id, winner_team_id, score_team1, score_team2) VALUES (%s, %s, %s, %s)", (match_id, winner_team_id, score_team1, score_team2))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('list_results'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT match_id, match_date FROM matches")
    matches = cursor.fetchall()
    cursor.execute("SELECT team_id, name FROM teams")
    teams = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('add_result.html', matches=matches, teams=teams)

@app.route('/results/delete/<int:result_id>')
@admin_required
def delete_result(result_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results WHERE result_id = %s", (result_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('list_results'))

if __name__ == '__main__':
    app.run(debug=True)

