# app.py
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global variable to store game state
# In a real application, this would be stored in a database or session
game_state = {
    'board': [''] * 9,  # Represents the 3x3 board: ['', 'X', '', 'O', ...]
    'current_player': 'X',
    'game_over': False,
    'winner': None,
    'mode': 'player_vs_player' # 'player_vs_player' or 'player_vs_computer'
}

# --- Game Logic Functions ---

def check_win(board):
    """Checks if there's a winner on the given board."""
    win_conditions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
        (0, 4, 8), (2, 4, 6)              # Diagonals
    ]
    for a, b, c in win_conditions:
        if board[a] == board[b] == board[c] and board[a] != '':
            return board[a]
    return None

def check_draw(board):
    """Checks if the game is a draw."""
    return '' not in board and check_win(board) is None

def reset_game_state():
    """Resets the global game state."""
    global game_state
    game_state = {
        'board': [''] * 9,
        'current_player': 'X',
        'game_over': False,
        'winner': None,
        'mode': game_state['mode'] # Keep the current mode
    }

# --- AI Logic (Minimax Algorithm) ---

def minimax(board, depth, is_maximizing):
    """
    Minimax algorithm to determine the best move for the AI.
    'X' is the AI (maximizing player), 'O' is the human (minimizing player).
    """
    winner = check_win(board)
    if winner == 'X': # AI wins
        return 1
    if winner == 'O': # Human wins
        return -1
    if check_draw(board): # Draw
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] == '':
                board[i] = 'X'
                score = minimax(board, depth + 1, False)
                board[i] = '' # Undo move
                best_score = max(best_score, score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == '':
                board[i] = 'O'
                score = minimax(board, depth + 1, True)
                board[i] = '' # Undo move
                best_score = min(best_score, score)
        return best_score

def find_best_move(board):
    """Finds the best move for the AI using Minimax."""
    best_score = -float('inf')
    best_move = -1
    for i in range(9):
        if board[i] == '':
            board[i] = 'X' # Assume AI makes this move
            score = minimax(board, 0, False) # Now it's human's turn (minimizing)
            board[i] = '' # Undo move
            if score > best_score:
                best_score = score
                best_move = i
    return best_move

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main game page."""
    return render_template('index.html')

@app.route('/game_state', methods=['GET'])
def get_game_state():
    """Returns the current game state."""
    return jsonify(game_state)

@app.route('/make_move', methods=['POST'])
def make_move():
    """Handles a player's move."""
    global game_state
    data = request.get_json()
    cell_index = data.get('cell_index')

    # Basic validation
    if not isinstance(cell_index, int) or not (0 <= cell_index < 9):
        return jsonify({'error': 'Invalid cell index'}), 400
    if game_state['game_over']:
        return jsonify({'error': 'Game is over'}), 400
    if game_state['board'][cell_index] != '':
        return jsonify({'error': 'Cell already taken'}), 400

    # Make the player's move
    game_state['board'][cell_index] = game_state['current_player']

    # Check for win/draw after player's move
    winner = check_win(game_state['board'])
    if winner:
        game_state['winner'] = winner
        game_state['game_over'] = True
    elif check_draw(game_state['board']):
        game_state['game_over'] = True
        game_state['winner'] = 'Draw'
    else:
        # Switch player
        game_state['current_player'] = 'O' if game_state['current_player'] == 'X' else 'X'

        # If it's Player vs Computer mode and it's AI's turn
        if game_state['mode'] == 'player_vs_computer' and not game_state['game_over'] and game_state['current_player'] == 'X':
            ai_move_index = find_best_move(game_state['board'])
            if ai_move_index != -1:
                game_state['board'][ai_move_index] = 'X' # AI makes its move

                # Check for win/draw after AI's move
                winner = check_win(game_state['board'])
                if winner:
                    game_state['winner'] = winner
                    game_state['game_over'] = True
                elif check_draw(game_state['board']):
                    game_state['game_over'] = True
                    game_state['winner'] = 'Draw'
                else:
                    game_state['current_player'] = 'O' # Switch back to human player

    return jsonify(game_state)

@app.route('/reset_game', methods=['POST'])
def reset_game():
    """Resets the game."""
    reset_game_state()
    return jsonify(game_state)

@app.route('/set_mode', methods=['POST'])
def set_mode():
    """Sets the game mode."""
    global game_state
    data = request.get_json()
    mode = data.get('mode')
    if mode not in ['player_vs_player', 'player_vs_computer']:
        return jsonify({'error': 'Invalid game mode'}), 400

    game_state['mode'] = mode
    reset_game_state() # Reset game when mode changes
    return jsonify(game_state)

if __name__ == '__main__':
    # To run this Flask app:
    # 1. Save this code as 'app.py'
    # 2. Create a folder named 'templates' in the same directory
    # 3. Save the HTML code (provided next) as 'index.html' inside the 'templates' folder
    # 4. Install Flask: pip install Flask
    # 5. Run from your terminal: python app.py
    # 6. Open your browser to http://127.0.0.1:5000/
    app.run(debug=True)