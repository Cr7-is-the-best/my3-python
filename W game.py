#install
pip install PyQt6 PyQt6-WebEngine
pip install speechrecognition pyaudio
pip install pygame

#Code
import sys
import os
import json
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar,
    QLineEdit, QPushButton, QDockWidget, QListWidget,
    QTextEdit, QWidget, QVBoxLayout, QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


# ---------------- FILE STORAGE ----------------
BOOKMARK_FILE = "bookmarks.json"
HISTORY_FILE = "history.json"
SESSION_FILE = "session.json"


def load(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []


def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f)


# ---------------- BROWSER TAB ----------------
class Tab(QWebEngineView):
    def __init__(self, incognito=False):
        super().__init__()
        self.incognito = incognito
        self.setUrl(QUrl("https://www.google.com"))


# ---------------- AI PANEL ----------------
class AIPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask AI...")

        btn = QPushButton("Send")
        btn.clicked.connect(self.ask)

        layout.addWidget(QLabel("🧠 AI Assistant (API-ready slot)"))
        layout.addWidget(self.chat)
        layout.addWidget(self.input)
        layout.addWidget(btn)

        self.setLayout(layout)

    def ask(self):
        msg = self.input.text()
        if not msg:
            return
        self.chat.append(f"You: {msg}")

        # 🔥 Replace this with OpenAI API later
        self.chat.append(f"AI: (demo response) You said '{msg}'\n")
        self.input.clear()


# ---------------- DOWNLOAD PANEL ----------------
class DownloadPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.list = QListWidget()
        layout.addWidget(QLabel("⬇ Downloads"))
        layout.addWidget(self.list)
        self.setLayout(layout)

    def add(self, file):
        self.list.addItem(file)


# ---------------- MAIN BROWSER ----------------
class UltraBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🚀 ULTRA Python Browser")
        self.resize(1400, 900)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Data
        self.bookmarks = load(BOOKMARK_FILE)
        self.history = load(HISTORY_FILE)

        # UI
        self.dark = False
        self.incognito = False

        self.add_tab("https://www.google.com")

        self.setup_toolbar()
        self.setup_docks()

    # ---------------- TOOLBAR ----------------
    def setup_toolbar(self):
        bar = QToolBar()
        self.addToolBar(bar)

        bar.addWidget(self.btn("⬅", lambda: self.current().back()))
        bar.addWidget(self.btn("➡", lambda: self.current().forward()))
        bar.addWidget(self.btn("⟳", lambda: self.current().reload()))
        bar.addWidget(self.btn("🏠", lambda: self.current().setUrl(QUrl("https://www.google.com"))))

        bar.addWidget(self.btn("🕶 Incognito", self.toggle_incognito))
        bar.addWidget(self.btn("🧠 AI", self.toggle_ai))
        bar.addWidget(self.btn("⬇ Downloads", self.toggle_downloads))
        bar.addWidget(self.btn("🌙 Theme", self.toggle_theme))
        bar.addWidget(self.btn("⛶ Full", self.fullscreen))

        # URL BAR
        self.url = QLineEdit()
        self.url.returnPressed.connect(self.go)
        bar.addWidget(self.url)

        bar.addWidget(self.btn("⭐", self.add_bookmark))
        bar.addWidget(self.btn("🎤", self.voice_search))

    # ---------------- DOCKS ----------------
    def setup_docks(self):
        # Bookmarks
        self.book_list = QListWidget()
        self.book_list.itemClicked.connect(self.open_bookmark)

        self.book_dock = QDockWidget("⭐ Bookmarks", self)
        self.book_dock.setWidget(self.book_list)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.book_dock)

        for b in self.bookmarks:
            self.book_list.addItem(b)

        # AI
        self.ai = AIPanel()
        self.ai_dock = QDockWidget("🧠 AI", self)
        self.ai_dock.setWidget(self.ai)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_dock)
        self.ai_dock.hide()

        # Downloads
        self.downloads = DownloadPanel()
        self.dl_dock = QDockWidget("⬇ Downloads", self)
        self.dl_dock.setWidget(self.downloads)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dl_dock)
        self.dl_dock.hide()

    # ---------------- TABS ----------------
    def add_tab(self, url):
        tab = Tab(self.incognito)
        tab.setUrl(QUrl(url))

        i = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(i)

        tab.urlChanged.connect(lambda q, t=tab: self.sync_url(q, t))
        tab.loadFinished.connect(lambda _, t=tab: self.tabs.setTabText(i, t.page().title()))

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def current(self):
        return self.tabs.currentWidget()

    # ---------------- NAVIGATION ----------------
    def go(self):
        text = self.url.text()

        if "." not in text:
            text = "https://www.google.com/search?q=" + text

        self.current().setUrl(QUrl(text))

    def sync_url(self, url, tab):
        if tab == self.current():
            self.url.setText(url.toString())
            self.history.append(url.toString())
            save(HISTORY_FILE, self.history)

    # ---------------- BOOKMARKS ----------------
    def add_bookmark(self):
        url = self.url.text()
        self.bookmarks.append(url)
        self.book_list.addItem(url)
        save(BOOKMARK_FILE, self.bookmarks)

    def open_bookmark(self, item):
        self.current().setUrl(QUrl(item.text()))

    # ---------------- FEATURES ----------------
    def toggle_ai(self):
        self.ai_dock.setVisible(not self.ai_dock.isVisible())

    def toggle_downloads(self):
        self.dl_dock.setVisible(not self.dl_dock.isVisible())

    def toggle_theme(self):
        self.dark = not self.dark

        if self.dark:
            self.setStyleSheet("""
                QMainWindow { background: #121212; color: white; }
                QLineEdit { background: #2a2a2a; color: white; }
                QPushButton { background: #333; color: white; }
            """)
        else:
            self.setStyleSheet("")

    def toggle_incognito(self):
        self.incognito = not self.incognito
        self.add_tab("https://www.google.com")

    def fullscreen(self):
        self.showFullScreen() if not self.isFullScreen() else self.showNormal()

    # ---------------- VOICE SEARCH ----------------
    def voice_search(self):
        try:
            import speech_recognition as sr

            r = sr.Recognizer()
            with sr.Microphone() as source:
                self.url.setText("Listening...")
                audio = r.listen(source)

            text = r.recognize_google(audio)
            self.url.setText(text)
            self.go()

        except:
            self.url.setText("Voice not available")

    # ---------------- BUTTON HELPER ----------------
    def btn(self, text, func):
        b = QPushButton(text)
        b.clicked.connect(func)
        return b

    # ---------------- CLOSE ----------------
    def closeEvent(self, event):
        save(BOOKMARK_FILE, self.bookmarks)
        save(HISTORY_FILE, self.history)
        event.accept()


# ---------------- RUN ----------------
app = QApplication(sys.argv)
window = UltraBrowser()
window.show()
sys.exit(app.exec())
