/* ================== CONFIG ================== */
const API_URL = "http://127.0.0.1:5000";

/* ================== STATE ================== */
const state = {
  user: localStorage.getItem("user")
};

/* ================== LOGIN ================== */
function login() {
  const input = document.getElementById("loginUser");
  const status = document.getElementById("status");

  if (!input) {
    console.error("loginUser input missing");
    return;
  }

  const userId = input.value.trim();

  if (!/^U\d{3,6}$/.test(userId)) {
    status.innerText = "Invalid User ID format";
    status.style.color = "#f87171";
    return;
  }

  localStorage.setItem("user", userId);
  status.innerText = "Identity verified. Redirecting…";
  status.style.color = "#4ade80";

  setTimeout(() => {
    window.location.href = "simulator.html";
  }, 800);
}

/* ================== INIT ================== */
document.addEventListener("DOMContentLoaded", () => {
  const verifyBtn = document.getElementById("verifyBtn");

  if (!verifyBtn) {
    console.error("verifyBtn not found");
    return;
  }

  verifyBtn.addEventListener("click", login);
});
