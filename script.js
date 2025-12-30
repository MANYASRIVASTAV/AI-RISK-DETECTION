/* ================== GLOBAL ================== */
const API_URL = "http://127.0.0.1:5000";
const COOLDOWN_HOURS = 24;
let currentUser = localStorage.getItem("user");

/* ================== AUTH ================== */
function login() {
  const u = document.getElementById("loginUser").value;
  if (!u) return alert("Enter User ID");
  localStorage.setItem("user", u);
  window.location.href = "simulator.html";
}

function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

function goSim() {
  window.location.href = "simulator.html";
}

function goDash() {
  window.location.href = "dashboard.html";
}

/* ================== UTILS ================== */
function recentlyConfirmed() {
  const last = localStorage.getItem("lastConfirmTime");
  if (!last) return false;

  const diffHrs =
    (Date.now() - Number(last)) / (1000 * 60 * 60);
  return diffHrs < COOLDOWN_HOURS;
}

function markConfirmed() {
  localStorage.setItem("lastConfirmTime", Date.now());
}

/* ================== CORE ================== */
async function submitTxn() {
  const amount = Number(document.getElementById("amount").value);
  const merchant = document.getElementById("merchant").value;
  const device = document.getElementById("device").value;

  if (!amount) return alert("Enter amount");

  const payload = {
    user_id: currentUser,
    amount,
    merchant,
    device
  };

  try {
    const res = await fetch(`${API_URL}/transaction`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    updateUI({
      amount,
      risk: data.risk_level,
      reason: data.reason
    });

    pushHistory(amount, data.risk_level, data.reason);
    updateDashboard();

  } catch (err) {
    alert("Backend not reachable");
    console.error(err);
  }
}

/* ================== UI ================== */
function updateUI(txn) {
  document.getElementById("liveRisk").innerText = txn.risk;
  document.getElementById("liveExplain").innerText = txn.reason;

  const banner = document.getElementById("systemState");
  const reasonsCount = txn.reason
    ? txn.reason.split(";").length
    : 0;

  if (
    txn.risk === "HIGH" &&
    reasonsCount >= 2 &&
    !recentlyConfirmed()
  ) {
    // 🔥 ESCALATION CASE
    banner.innerText = "🔴 Transaction Under Review";
    banner.className = "banner HIGH";

    document.getElementById("riskReason").innerText =
      "Unusual pattern detected. You may continue or secure your account.";

    document.getElementById("riskSheet").classList.remove("hidden");

  } else {
    // 🟢 SILENT MONITORING
    banner.innerText = "🟢 Normal Monitoring";
    banner.className = "banner LOW";
    document.getElementById("riskSheet").classList.add("hidden");
    if (txn.risk === "MEDIUM") {
  banner.innerText = "🟡 Unusual Activity Observed";
  banner.className = "banner MEDIUM";
}


}
}

/* ================== USER ACTION ================== */
function confirmTxn() {
  markConfirmed();
  document.getElementById("riskSheet").classList.add("hidden");
  addHistory("🛡 Transaction allowed (under monitoring)");
}

/* ================== HISTORY ================== */
function addHistory(msg) {
  const ul = document.getElementById("txnHistory");
  const li = document.createElement("li");
  li.innerText = msg;
  ul.prepend(li);
}

function pushHistory(amount, risk, reason) {
  const txns = JSON.parse(localStorage.getItem("txns") || "[]");

  txns.push({
    amount,
    risk,
    reason,
    time: new Date().toLocaleTimeString()
  });

  localStorage.setItem("txns", JSON.stringify(txns));
  addHistory(`₹${amount} → ${risk}`);
}

/* ================== DASHBOARD ================== */
function updateDashboard() {
  if (!document.getElementById("totalTxns")) return;

  const txns = JSON.parse(localStorage.getItem("txns") || "[]");

  document.getElementById("totalTxns").innerText = txns.length;
  document.getElementById("highRisk").innerText =
    txns.filter(t => t.risk === "HIGH").length;

  const last = txns.filter(t => t.risk === "HIGH").slice(-1)[0];
  document.getElementById("lastAlert").innerText =
    last ? `₹${last.amount} @ ${last.time}` : "None";
}

/* ================== CLOCK ================== */
setInterval(() => {
  const c = document.getElementById("clock");
  if (c) c.innerText = new Date().toLocaleTimeString();
}, 1000);

/* ================== INIT ================== */
window.onload = () => {
  const user = localStorage.getItem("user");

  if (document.getElementById("navUser")) {
    document.getElementById("navUser").innerText = "👤 " + user;
  }

  if (document.getElementById("liveUser")) {
    document.getElementById("liveUser").innerText = user;
  }
};
