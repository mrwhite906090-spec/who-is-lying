import os
import json
import http.server
import socketserver

PORT = int(os.environ.get("PORT", 10000))

# ==========================================
# 🔑 ВСТАВЬ СВОЙ ТОКЕН ОТ BOTFATHER СЮДА:
# ==========================================
TELEGRAM_TOKEN = "8342175799:AAEVDjSw0jvYcsUxUjfx9DUKTI75iW9FVK4"

# База данных пользователей
USERS_DB = {}

class DetectiveServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(MINI_APP_HTML.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/sync":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                tg_id = str(data.get("tg_id"))
                
                if not tg_id:
                    self.send_response(400)
                    self.end_headers()
                    return

                if tg_id not in USERS_DB:
                    USERS_DB[tg_id] = {
                        "energy": 100,
                        "max_energy": 100,
                        "notes": [],
                        "reputation": "Безупречная",
                        "cases_solved": 0
                    }

                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "profile": USERS_DB[tg_id]}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

# ==========================================
# 🎨 ФРОНТЕНД MINI APP (ПОЛНЫЙ GDD КОМПЛЕКТ)
# ==========================================
MINI_APP_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Кто лжет? - Детективный триллер</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --bg-color: #0f1115;
            --card-bg: #181c24;
            --accent: #d97706;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border: #2a303c;
            --danger: #ef4444;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 12px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--card-bg);
            padding: 10px 14px;
            border-radius: 10px;
            border: 1px solid var(--border);
            margin-bottom: 12px;
        }
        .energy-bar { font-size: 14px; font-weight: bold; color: var(--accent); }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 12px;
        }
        h2 { margin-top: 0; font-size: 16px; color: var(--accent); }
        p { font-size: 13px; color: var(--text-muted); line-height: 1.4; margin: 8px 0; }
        .btn {
            background: var(--accent);
            color: white;
            border: none;
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 8px;
        }
        .btn-secondary { background: #374151; }
        .btn-danger { background: var(--danger); }
        .version { font-size: 10px; color: var(--text-muted); cursor: pointer; text-align: center; margin-top: 10px; user-select: none; }
        #secret-panel { display: none; margin-top: 10px; background: #111; padding: 10px; border-radius: 8px; border: 1px dashed var(--accent); }
        input { width: calc(100% - 16px); padding: 8px; background: #222; border: 1px solid var(--border); color: white; border-radius: 6px; margin-top: 5px; }
        .screen { display: none; }
        .screen.active { display: block; }
        .location-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; }
        .loc-btn { background: #222; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 8px; cursor: pointer; text-align: left; }
        .notebook-item { background: #111; padding: 8px; border-radius: 6px; border-left: 3px solid var(--accent); margin-bottom: 6px; font-size: 12px; }
        .suspect-box { display: flex; justify-content: space-between; align-items: center; background: #222; padding: 10px; border-radius: 6px; margin-bottom: 6px; }
    </style>
</head>
<body>

    <!-- Шапка -->
    <div class="header">
        <div><strong>🕵️‍♂️ Департамент</strong></div>
        <div><span class="energy-bar" id="energy-display">⚡ 100/100</span></div>
    </div>

    <!-- ЭКРАН 1: ОНБОРДИНГ -->
    <div id="screen-onboarding" class="screen active">
        <div class="card">
            <h2>📜 РАПОРТ О НАЗНАЧЕНИИ</h2>
            <p>Вы зачислены в штат. Первое расследование проходит под кураторством дежурной части. Материалы дела переданы в оперативный терминал.</p>
            <button class="btn" onclick="switchScreen('screen-terminal')">Открыть оперативный терминал</button>
        </div>
        <div class="version" onclick="handleVersionClick()">Версия 1.0.0 (Build 100)</div>
        <div id="secret-panel">
            <p style="margin: 0; color: var(--accent);">Режим разработчика</p>
            <input type="text" id="promo-input" placeholder="Введите промокод...">
            <button class="btn" style="padding: 6px;" onclick="applyPromo()">Активировать</button>
        </div>
    </div>

    <!-- ЭКРАН 2: ТЕРМИНАЛ -->
    <div id="screen-terminal" class="screen">
        <div class="card">
            <h2>📁 Дело №1: «Ночной визит»</h2>
            <p>Исследуйте локации, опрашивайте свидетелей и собирайте улики.</p>
            <div class="location-grid">
                <button class="loc-btn" onclick="openLocation('Место преступления', 'Входная дверь взломана изнутри. На полу обнаружен странный след обуви.')">📍 Место преступления</button>
                <button class="loc-btn" onclick="openLocation('Офис компании', 'Свидетель путается в показаниях относительно времени своего прихода.')">📍 Офис компании</button>
                <button class="loc-btn" onclick="switchScreen('screen-lab')">🔬 Лаборатория</button>
                <button class="loc-btn" onclick="openNotebook()">📓 Блокнот улик</button>
            </div>
            <button class="btn btn-danger" style="margin-top: 12px;" onclick="switchScreen('screen-court')">⚖️ Допросная и Суд</button>
        </div>
    </div>

    <!-- ЭКРАН 3: ЛОКАЦИЯ -->
    <div id="screen-location" class="screen">
        <div class="card">
            <h2 id="loc-title">Локация</h2>
            <p id="loc-desc">Описание...</p>
            <button class="btn" onclick="interrogate()">Опросить персонажа (-10 ⚡)</button>
            <button class="btn btn-secondary" onclick="switchScreen('screen-terminal')">Назад в терминал</button>
        </div>
    </div>

    <!-- ЭКРАН 4: БЛОКНОТ -->
    <div id="screen-notebook" class="screen">
        <div class="card">
            <h2>📓 Блокнот следователя</h2>
            <div id="notes-container"><p>Блокнот пуст.</p></div>
            <button class="btn btn-secondary" onclick="switchScreen('screen-terminal')">Назад в терминал</button>
        </div>
    </div>

    <!-- ЭКРАН 5: ЛАБОРАТОРИЯ -->
    <div id="screen-lab" class="screen">
        <div class="card">
            <h2>🔬 Лаборатория</h2>
            <p>Анализ улик и экспертные мысли (💭).</p>
            <button class="btn" onclick="getLabHint()">Запросить экспертизу (-15 ⚡)</button>
            <button class="btn btn-secondary" onclick="switchScreen('screen-terminal')">Назад в терминал</button>
        </div>
    </div>

    <!-- ЭКРАН 6: ДОПРОСНАЯ И СУД -->
    <div id="screen-court" class="screen">
        <div class="card">
            <h2>⚖️ Допросная и Суд</h2>
            <p>Выберите подозреваемого для ареста. Ошибка приведет к иску адвокатов и выговору!</p>
            <div class="suspect-box">
                <span>Подозрительный коллега (Боб)</span>
                <button class="btn" style="width: auto; padding: 6px 12px;" onclick="arrest('Боб')">Арестовать</button>
            </div>
            <div class="suspect-box">
                <span>Охранник (Чарли)</span>
                <button class="btn" style="width: auto; padding: 6px 12px;" onclick="arrest('Чарли')">Арестовать</button>
            </div>
            <button class="btn btn-secondary" style="margin-top: 10px;" onclick="switchScreen('screen-terminal')">Назад в терминал</button>
        </div>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();

        let userTgId = tg.initDataUnsafe?.user?.id || "test_user_999";
        let userProfile = { energy: 100, max_energy: 100, notes: [] };

        fetch('/api/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tg_id: userTgId })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === "ok") {
                userProfile = data.profile;
                updateEnergyUI();
            }
        });

        function updateEnergyUI() {
            document.getElementById('energy-display').innerText = `⚡ ${userProfile.energy}/${userProfile.max_energy}`;
        }

        let clickCount = 0;
        function handleVersionClick() {
            clickCount++;
            if (clickCount >= 10) {
                document.getElementById('secret-panel').style.display = 'block';
                tg.HapticFeedback.notificationOccurred('success');
            }
        }

        function applyPromo() {
            let code = document.getElementById('promo-input').value;
            if (code === "DEV_GOD") {
                userProfile.energy = 999;
                updateEnergyUI();
                alert("VIP-доступ активирован! Энергия максимальна.");
                document.getElementById('secret-panel').style.display = 'none';
                tg.HapticFeedback.notificationOccurred('success');
            } else {
                alert("Неверный код");
                tg.HapticFeedback.notificationOccurred('error');
            }
        }

        function switchScreen(screenId) {
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(screenId).classList.add('active');
            tg.HapticFeedback.impactOccurred('light');
        }

        let currentEvidence = "";
        function openLocation(title, desc) {
            document.getElementById('loc-title').innerText = title;
            document.getElementById('loc-desc').innerText = desc;
            currentEvidence = `[${title}]: ${desc}`;
            switchScreen('screen-location');
        }

        function interrogate() {
            if(userProfile.energy < 10 && userProfile.energy !== 999) {
                alert("Недостаточно энергии!");
                return;
            }
            if(userProfile.energy !== 999) userProfile.energy -= 10;
            updateEnergyUI();
            userProfile.notes.push(currentEvidence);
            alert("Персонаж опрошен. Улика добавлена в блокнот.");
            tg.HapticFeedback.notificationOccurred('success');
            switchScreen('screen-terminal');
        }

        function openNotebook() {
            let container = document.getElementById('notes-container');
            if(userProfile.notes.length === 0) {
                container.innerHTML = "<p>Блокнот пуст.</p>";
            } else {
                container.innerHTML = userProfile.notes.map(n => `<div class='notebook-item'>${n}</div>`).join('');
            }
            switchScreen('screen-notebook');
        }

        function getLabHint() {
            if(userProfile.energy < 15 && userProfile.energy !== 999) {
                alert("Недостаточно энергии!");
                return;
            }
            if(userProfile.energy !== 999) userProfile.energy !== 999 ? null : 0;
            userProfile.energy -= (userProfile.energy === 999 ? 0 : 15);
            updateEnergyUI();
            alert("💭 Экспертиза: Взлом шел изнутри, настоящий преступник — Боб.");
            tg.HapticFeedback.notificationOccurred('success');
        }

        function arrest(suspect) {
            if(suspect === 'Боб') {
                alert("🎉 Дело раскрыто! Суд признал подозреваемого виновным.");
                tg.HapticFeedback.notificationOccurred('success');
            } else {
                alert("❌ Ошибка! Адвокаты развалили дело в суде. Выговор в личное дело!");
                tg.HapticFeedback.notificationOccurred('error');
            }
            switchScreen('screen-terminal');
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), DetectiveServer) as httpd:
        print(f"Final GDD Server running on port {PORT}")
        httpd.serve_forever()
