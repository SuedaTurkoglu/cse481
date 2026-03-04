// Populate dropdowns on load, handle mode toggle, and start trading with WebSocket updates.
window.addEventListener("load", async () => {
  await loadConfig();
  setupModeToggle();
  wireStartButton();
});

async function loadConfig() {
  const symbolSelect = document.getElementById("symbol");
  const intervalSelect = document.getElementById("candle_interval");
  const dateSelect = document.getElementById("check_date");

  if (!symbolSelect || !intervalSelect || !dateSelect) return;

  try {
    const res = await fetch("http://localhost:8000/api/config");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    fillSelect(symbolSelect, data.available_symbols);
    fillSelect(intervalSelect, data.available_intervals);
    fillSelect(dateSelect, data.available_date_ranges);
  } catch (err) {
    console.error("Configuration failed to load:", err);
  }
}

function fillSelect(selectEl, options) {
  if (!Array.isArray(options)) return;
  selectEl.innerHTML = options.map((opt) => `<option value="${opt}">${opt}</option>`).join("");
}

function setupModeToggle() {
  const backtestSettings = document.getElementById("backtest-settings");
  const liveSettings = document.getElementById("live-settings");
  const modeRadios = document.querySelectorAll('input[name="mode"]');

  if (!backtestSettings || !liveSettings || modeRadios.length === 0) return;

  const applyVisibility = (modeValue) => {
    const isBacktest = modeValue === "2";
    backtestSettings.classList.toggle("d-none", !isBacktest);
    liveSettings.classList.toggle("d-none", isBacktest);
  };

  modeRadios.forEach((radio) => {
    radio.addEventListener("change", (e) => applyVisibility(e.target.value));
  });

  const checked = document.querySelector('input[name="mode"]:checked');
  applyVisibility(checked ? checked.value : "2");
}

function wireStartButton() {
  const startBtn = document.getElementById("start-btn");
  if (!startBtn) return;
  startBtn.addEventListener("click", (e) => {
    e.preventDefault();
    startTrade();
  });
}

async function startTrade() {
  const logWindow = document.getElementById("log-window");
  if (logWindow) logWindow.innerHTML = "";

  const finalEl = document.getElementById("final-balance");
  if (finalEl) finalEl.textContent = "$0.00";

  const profitEl = document.getElementById("profit-loss");
  if (profitEl) {
    profitEl.textContent = "$0.00";
    profitEl.classList.remove("text-success", "text-danger");
  }

  const modeInput = document.querySelector('input[name="mode"]:checked');
  const mode = modeInput ? modeInput.value : "2";
  const payload = {
    symbol: document.getElementById("symbol")?.value || "BTCUSDT",
    mode,
    initial_balance: Number(document.getElementById("initial_balance")?.value || 10000),
    stop_loss_pct: Number(document.getElementById("stop_loss_pct")?.value || 2),
    position_size_pct: 50, // default placeholder: 50% position size
  };

  if (mode === "1") {
    payload.interval_mins = Number(document.getElementById("interval_mins")?.value || 5);
  } else {
    payload.candle_interval = document.getElementById("candle_interval")?.value || "1m";
    payload.check_date = document.getElementById("check_date")?.value || "1 hour ago UTC";
  }

  try {
    const res = await fetch("http://localhost:8000/api/trade/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    const sessionId = data.session_id;
    if (!sessionId) throw new Error("Session ID alinamadi.");

    appendLog("Trade started. Session ID: " + sessionId);
    openWebSocket(sessionId);
  } catch (err) {
    appendLog("Error: " + err.message, true);
    console.error("Request error:", err);
  }
}

function openWebSocket(sessionId) {
  const ws = new WebSocket(`ws://localhost:8000/ws/updates/${sessionId}`);

  ws.onopen = () => {
    appendLog("Connection established...");
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === "log" && msg.message) {
        appendLog(msg.message);
      } else if (msg.type === "result") {
        updateSummary(msg.final_balance, msg.profit_loss);
        appendLog("Trade completed.");
      }
    } catch (err) {
      console.error("WebSocket message error:", err);
    }
  };

  ws.onerror = (event) => {
    console.error("WebSocket error:", event);
    appendLog("WebSocket error occurred.", true);
  };
}

function appendLog(message, isError = false) {
  const logWindow = document.getElementById("log-window");
  if (!logWindow) return;
  const line = document.createElement("div");
  line.textContent = message;
  if (isError) line.classList.add("text-danger");
  logWindow.appendChild(line);
  logWindow.scrollTop = logWindow.scrollHeight;
}

function updateSummary(finalBalance, profitLoss) {
  const finalEl = document.getElementById("final-balance");
  const profitEl = document.getElementById("profit-loss");
  const profit = Number(profitLoss || 0);
  if (finalEl) finalEl.textContent = `$${Number(finalBalance || 0).toFixed(2)}`;
  if (profitEl) {
    profitEl.textContent = `$${profit.toFixed(2)}`;
    profitEl.classList.toggle("text-success", profit >= 0);
    profitEl.classList.toggle("text-danger", profit < 0);
  }
}
