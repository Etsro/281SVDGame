const backendURL = "https://your-backend-name.onrender.com"; // Replace with your Render URL

async function loadGame() {
  const res = await fetch(backendURL + "/");
  const data = await res.json();
  updateUI(data);
}

document.getElementById("guess-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const guess = document.getElementById("guess-input").value;
  const res = await fetch(backendURL + "/guess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ guess })
  });
  const data = await res.json();
  updateUI(data);
});

function updateUI(data) {
  document.getElementById("game-image").src = backendURL + "/image/" + data.image + "?v=" + Date.now();
  document.getElementById("game-status").textContent = `Guess ${data.guess_count} of ${data.max_guesses}`;
  document.getElementById("error").textContent = data.correct ? "Correct!" :
    data.finished ? `Game Over. The correct word was '${data.answer}'.` : `You're ${data.diff} away.`;
}

function restartGame() {
  loadGame();
}

window.onload = loadGame;
