const cells = document.querySelectorAll(".cell");
const statusText = document.getElementById("status");

async function fetchGameState() {
    const response = await fetch("/game_state");
    const data = await response.json();

    updateBoard(data);
}

function updateBoard(data) {
    cells.forEach((cell, index) => {
        cell.textContent = data.board[index];
    });

    if (data.game_over) {
        if (data.winner === "Draw") {
            statusText.textContent = "Game Draw!";
        } else {
            statusText.textContent = `Winner: ${data.winner}`;
        }
    } else {
        statusText.textContent = `Current Player: ${data.current_player}`;
    }
}

cells.forEach(cell => {
    cell.addEventListener("click", async () => {
        const index = parseInt(cell.dataset.index);

        const response = await fetch("/make_move", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                cell_index: index
            })
        });

        const data = await response.json();

        if (!data.error) {
            updateBoard(data);
        }
    });
});

async function resetGame() {
    const response = await fetch("/reset_game", {
        method: "POST"
    });

    const data = await response.json();
    updateBoard(data);
}

async function setMode(mode) {
    const response = await fetch("/set_mode", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            mode: mode
        })
    });

    const data = await response.json();
    updateBoard(data);
}

fetchGameState();