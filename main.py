import os
import json
import http.server
import socketserver

PORT = int(os.environ.get("PORT", 10000))

# ==========================================
# 🔑 ВСТАВЬ СВОЙ ТОКЕН ОТ BOTFATHER СЮДА:
# ==========================================
TELEGRAM_TOKEN = "8342175799:AAEVDjSw0jvYcsUxUjfx9DUKTI75iW9FVK4"

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
# 🎨 ПОЛНЫЙ ФРОНТЕНД ИГРЫ (ROOM ESCAPE STYLE)
# ==========================================
MINI_APP_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Кто лжет? - Детективный квест</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --bg-room: #090b0e;
            --card-bg: #141820;
            --accent: #d97706;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border: #222733;
            --danger: #ef4444;
            --glow: rgba(217, 119, 6, 0.5);
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-room);
            color: var(--text-main);
            margin: 0;
            padding: 10px;
            user-select: none;
        }
        /* Верхняя панель */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--card-bg);
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 10px;
        }
        .menu-btn {
            background: #1e2430;
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: bold;
        }
        .energy-val { font-weight: bold; color: var(--accent); font-size: 13px; }

        /* Выпадающее меню шторка */
        .dropdown-menu {
            display: none;
            position: absolute;
            top: 50px;
            left: 10px;
            right: 10px;
            background: #181d28;
            border: 1px solid var(--accent);
            border-radius: 10px;
            padding: 8px;
            z-index: 100;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        }
        .dropdown-menu.open { display: block; }
        .menu-item {
            padding: 10px;
            background: #1f2533;
            border-radius: 6px;
            margin-bottom: 5px;
            cursor: pointer;
            font-size: 13px;
            border: 1px solid var(--border);
            text-align: left;
        }
        .menu-item:hover { border-color: var(--accent); }

        /* Экраны */
        .screen { display: none; }
        .screen.active { display: block; }

        /* Квестовая комната (Room Escape) */
        .room-viewport {
            position: relative;
            width: 100%;
            height: 340px;
            background: radial-gradient(circle, #1a202c 0%, #080a0f 100%);
            border: 2px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .room-title-overlay {
            position: absolute;
            top: 10px;
            font-size: 11px;
            letter-spacing: 2px;
            color: rgba(255,255,255,0.3);
            text-transform: uppercase;
        }
        /* Интерактивные точки улик */
        .hotspot {
            position: absolute;
            background: rgba(217, 119, 6, 0.25);
            border: 2px dashed var(--accent);
            border-radius: 50%;
            cursor: pointer;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 var(--glow); }
            70% { box-shadow: 0 0 0 12px rgba(217, 119, 6, 0); }
            100% { box-shadow: 0 0 0 0 rgba(217, 119, 6, 0); }
        }

        /* Панель диалогов и мыслей в стиле новелл */
        .dialogue-box {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
            min-height: 55px;
        }
        .dialogue-title { font-size: 11px; color: var(--accent); font-weight: bold; margin-bottom: 3px; text-transform: uppercase; }
        .dialogue-text { font-size: 13px; color: var(--text-muted); margin: 0; line-height: 1.35; }

        /* Общие карточки */
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
        }
        h2 { margin-top: 0; font-size: 15px; color: var(--accent); }
        .btn {
            background: var(--accent);
            color: white;
            border: none;
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 8px;
        }
        .btn-secondary { background: #374151; }
        .btn-danger { background: var(--danger); }
        
        .suspect-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #1f2533;
            padding: 8px;
            border-radius: 6px;
            margin-bottom: 6px;
            font-size: 13px;
            border: 1px solid var(--border);
        }
        .notebook-item {
            background: #191f2b;
            padding: 8px;
            border-radius: 6px;
            border-left: 3px solid var(--accent);
            margin-bottom: 6px;
            font-size: 12px;
        }
        .version { font-size: 9px; color: var(--text-muted); text-align: center; margin-top: 10px; cursor: pointer; }
    </style>
</head>
<body>

    <!-- Шапка -->
    <div class="top-bar">
        <button class="menu-btn" onclick="toggleMenu()">📂 Меню дела ▾</button>
        <span class="energy-val" id="energy-display">⚡ 100/100</span>
    </div>

    <!-- Выпадающее меню (Маленькая кнопка) -->
    <div id="dropdown-menu" class="dropdown-menu">
        <div class="menu-item" onclick="switchScreen('screen-crime-scene')">📍 1. Место преступления (Осмотр)</div>
        <div class="menu-item" onclick="switchScreen('screen-station')">🏛️ 2. Участок (Доска и Допрос)</div>
        <div class="menu-item" onclick="switchScreen('screen-lab')">🔬 3. Лаборатория (Эксперт)</div>
        <div class="menu-item" onclick="switchScreen('screen-notebook')">📓 Блокнот следователя</div>
    </div>

    <!-- ЭКРАН 1: МЕСТО ПРЕСТУПЛЕНИЯ (Spotlight Style) -->
    <div id="screen-crime-scene" class="screen active">
        <div class="room-viewport">
            <div class="room-title-overlay">Дело №1 • Спальня</div>
            <!-- Интерактивные точки поиска улик -->
            <div class="hotspot" style="width: 45px; height: 45px; top: 55%; left: 25%;" onclick="inspectHotspot('Осколки вазы', 'На полу валяются осколки дорогой вазы. На них обнаружены следы крови.')"></div>
            <div class="hotspot" style="width: 40px; height: 40px; top: 30%; left: 65%;" onclick="inspectHotspot('Сейф', 'Сейф в стене открыт изнутри. Все ценности на месте, кроме компрометирующих документов.')"></div>
        </div>
        <div class="dialogue-box">
            <div class="dialogue-title">Мысли детектива</div>
            <p class="dialogue-text" id="room-thoughts">Осмотрите комнату глазами сыщика. Нажмите на светящиеся зоны, чтобы собрать улики.</p>
        </div>
    </div>

    <!-- ЭКРАН 2: УЧАСТОК (ДОСКА И ДОПРОСНАЯ) -->
    <div id="screen-station" class="screen">
        <div class="card">
            <h2>🏛️ Оперативный штаб</h2>
            <p style="font-size:12px; color:var(--text-muted);">Сопоставляйте улики на доске или вызывайте подозреваемых на допрос.</p>
            <button class="btn" onclick="alert('Криминальная доска: связи между подозреваемыми и уликами установлены.')">📌 Открыть криминальную доску</button>
            <button class="btn btn-danger" style="margin-top: 8px;" onclick="switchScreen('screen-court')">⚖️ Провести арест и суд</button>
        </div>
    </div>

    <!-- ЭКРАН 3: ЛАБОРАТОРИЯ -->
    <div id="screen-lab" class="screen">
        <div class="card">
            <h2>🔬 Лаборатория судмедэксперта</h2>
            <p style="font-size:12px; color:var(--text-muted);">Здесь эксперт анализирует улики и выдает скрытые мысли-подсказки (💭).</p>
            <button class="btn" onclick="getLabHint()">Запросить экспертизу улик (-15 ⚡)</button>
        </div>
    </div>

    <!-- ЭКРАН 4: БЛОКНОТ -->
    <div id="screen-notebook" class="screen">
        <div class="card">
            <h2>📓 Блокнот следователя</h2>
            <div id="notes-container"><p style="font-size:12px; color:var(--text-muted);">Блокнот пуст. Осмотрите место преступления.</p></div>
            <button class="btn btn-secondary" onclick="switchScreen('screen-crime-scene')">Вернуться к делу</button>
        </div>
    </div>

    <!-- ЭКРАН 5: СУД И ДОПРОСНАЯ -->
    <div id="screen-court" class="screen">
        <div class="card">
            <h2>⚖️ Допросная и Суд</h2>
            <p style="font-size:12px; color:var(--text-muted);">Выберите подозреваемого. Ошибка в суде приведет к иску адвокатов и выговору!</p>
            <div class="suspect-row">
                <span>Боб (Коллега)</span>
                <button class="btn" style="width: auto; padding: 6px 12px; margin:0;" onclick="arrest('Боб')">Арестовать</button>
            </div>
            <div class="suspect-row">
                <span>Чарли (Охранник)</span>
                <button class="btn" style="width: auto; padding: 6px 12px; margin:0;" onclick="arrest('Чарли')">Арестовать</button>
            </div>
            <button class="btn btn-secondary" style="margin-top: 10px;" onclick="switchScreen('screen-station')">Назад в штаб</button>
        </div>
    </div>

    <div class="version" onclick="handleVersionClick()">Версия 1.0.0 (Ultimate Escape Edition)</div>
    <div id="secret-panel" style="display:none; text-align:center; margin-top:5px;">
        <input type="text" id="promo" placeholder="Промокод..." style="padding:4px; width:130px; background:#111; color:#fff; border:1px solid var(--accent); border-radius:4px;">
        <button onclick="applyPromo()" style="padding:4px; background:var(--accent); color:#fff; border:none; border-radius:4px;">OK</button>
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

        function toggleMenu() {
            document.getElementById('dropdown-menu').classList.toggle('open');
            tg.HapticFeedback.impactOccurred('light');
        }

        function switchScreen(screenId) {
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById(screenId).classList.add('active');
            document.getElementById('dropdown-menu').classList.remove('open');
            tg.HapticFeedback.impactOccurred('medium');
        }

        function inspectHotspot(title, desc) {
            tg.HapticFeedback.notificationOccurred('success');
            document.getElementById('room-thoughts').innerText = `Найдено [${title}]: ${desc}`;
            let clue = `[${title}]: ${desc}`;
            if(!userProfile.notes.includes(clue)) {
                userProfile.notes.push(clue);
                updateNotesUI();
            }
        }

        function updateNotesUI() {
            let container = document.getElementById('notes-container');
            container.innerHTML = userProfile.notes.map(n => `<div class='notebook-item'>${n}</div>`).join('');
        }

        function getLabHint() {
            if(userProfile.energy < 15 && userProfile.energy !== 999) {
                alert("Недостаточно энергии!");
                return;
            }
            if(userProfile.energy !== 999) userProfile.energy -= 15;
            updateEnergyUI();
            alert("💭 Мысль судмедэксперта: Взломать сейф изнутри мог только тот, у кого был дубликат ключа Боба.");
            tg.HapticFeedback.notificationOccurred('success');
        }

        function arrest(suspect) {
            if(suspect === 'Боб') {
                alert("🎉 Дело раскрыто! Суд признал Боба виновным.");
                tg.HapticFeedback.notificationOccurred('success');
            } else {
                alert("❌ Ошибка! Адвокаты развалили дело в суде. Выговор в личное дело!");
                tg.HapticFeedback.notificationOccurred('error');
            }
            switchScreen('screen-crime-scene');
        }

        let clicks = 0;
        function handleVersionClick() {
            clicks++;
            if(clicks >= 10) {
                document.getElementById('secret-panel').style.display = 'block';
                tg.HapticFeedback.notificationOccurred('success');
            }
        }

        function applyPromo() {
            if(document.getElementById('promo').value === "DEV_GOD") {
                userProfile.energy = 999;
                updateEnergyUI();
                alert("Пасхалка активирована! Вечный безлимит энергии.");
                document.getElementById('secret-panel').style.display = 'none';
            } else {
                alert("Неверный код");
            }
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), DetectiveServer) as httpd:
        print(f"Ultimate Game Server running on port {PORT}")
        httpd.serve_forever()
