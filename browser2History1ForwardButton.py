import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout,
    QWidget, QLineEdit, QHBoxLayout, QPushButton,
    QListWidget, QSplitter, QLabel, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon

# Enable high DPI scaling
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

class HistoryItem:
    def __init__(self, url, domain):
        self.url = url
        self.domain = domain

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle("Custom Web Browser")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        self.history_list = []
        
        # Create UI components
        self.create_navigation_bar()
        self.create_history_sidebar()
        self.create_tab_system()
        
        # Main layout setup
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navigation bar
        main_layout.addWidget(self.nav_bar)
        
        # Splitter for history and tabs
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self.history_widget)
        main_splitter.addWidget(self.tabs)
        main_splitter.setSizes([200, 800])
        main_splitter.setStretchFactor(0, 0)  # History fixed width
        main_splitter.setStretchFactor(1, 1)  # Tabs expand
        
        # Size policies for proper scaling
        main_splitter.setSizePolicy(QSizePolicy.Policy.Expanding, 
                                 QSizePolicy.Policy.Expanding)
        
        main_layout.addWidget(main_splitter)
        self.setCentralWidget(main_container)
        
        # Add initial tab
        self.add_new_tab(QUrl("https://www.google.com"), "Home")

    def create_navigation_bar(self):
        self.nav_bar = QWidget()
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(5)
        
        # Navigation buttons
        self.back_button = QPushButton("←")
        self.forward_button = QPushButton("→")
        self.refresh_button = QPushButton("⟳")
        self.new_tab_button = QPushButton("+")
        self.history_button = QPushButton("History")
        
        # Set fixed sizes for buttons
        btn_size = 30
        for button in [self.back_button, self.forward_button, 
                      self.refresh_button, self.new_tab_button]:
            button.setFixedSize(btn_size, btn_size)
        
        self.history_button.setFixedHeight(btn_size)
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL")
        self.url_input.setFixedHeight(30)
        self.url_input.setSizePolicy(QSizePolicy.Policy.Expanding, 
                                   QSizePolicy.Policy.Fixed)
        
        # Connect signals
        self.back_button.clicked.connect(self.back_history)
        self.forward_button.clicked.connect(self.forward_history)
        self.refresh_button.clicked.connect(self.refresh_page)
        self.url_input.returnPressed.connect(self.load_url)
        self.new_tab_button.clicked.connect(self.add_new_tab)
        self.history_button.clicked.connect(self.toggle_history)
        
        # Add widgets to layout
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.refresh_button)
        nav_layout.addWidget(self.url_input)
        nav_layout.addWidget(self.new_tab_button)
        nav_layout.addWidget(self.history_button)
        
        # Set fixed height for navigation bar
        self.nav_bar.setFixedHeight(40)

    def create_history_sidebar(self):
        self.history_widget = QWidget()
        layout = QVBoxLayout(self.history_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        self.history_label = QLabel("History (Double-click to visit)")
        self.history_list_widget = QListWidget()
        self.history_list_widget.setAlternatingRowColors(True)
        self.history_list_widget.setUniformItemSizes(True)
        
        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.setFixedHeight(30)
        
        layout.addWidget(self.history_label)
        layout.addWidget(self.history_list_widget)
        layout.addWidget(self.clear_history_button)
        
        # Size policies
        self.history_widget.setMinimumWidth(200)
        self.history_widget.setSizePolicy(QSizePolicy.Policy.Fixed, 
                                       QSizePolicy.Policy.Expanding)
        self.history_widget.hide()
        
        # Connect signals
        self.history_list_widget.itemDoubleClicked.connect(self.load_from_history)
        self.clear_history_button.clicked.connect(self.clear_history)

    def create_tab_system(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.TextElideMode.ElideRight)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # Size policy to ensure proper expansion
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding,
                              QSizePolicy.Policy.Expanding)

    def toggle_history(self):
        self.history_widget.setVisible(not self.history_widget.isVisible())

    def add_to_history(self, url):
        if url.toString() not in [item.url for item in self.history_list]:
            self.history_list.append(HistoryItem(url.toString(), url.host()))
            self.history_list_widget.addItem(f"{url.host()} - {url.toString()}")

    def load_from_history(self, item):
        url_str = item.text().split(" - ")[-1]
        current_tab = self.tabs.currentWidget()
        current_tab.setUrl(QUrl(url_str))

    def clear_history(self):
        self.history_list.clear()
        self.history_list_widget.clear()

    def add_new_tab(self, url=QUrl(""), title="New Tab"):
        web_view = QWebEngineView()
        web_view.setUrl(url if url else QUrl("about:blank"))
        
        # Set size policy to expand in both directions
        web_view.setSizePolicy(QSizePolicy.Policy.Expanding, 
                             QSizePolicy.Policy.Expanding)
        
        # Connect signals - FIXED SECTION
        web_view.urlChanged.connect(lambda q: self.update_urlbar(q, web_view))
        web_view.titleChanged.connect(lambda t: self.update_tab_title(t, web_view))
        web_view.loadFinished.connect(lambda: self.update_navigation_buttons(web_view))
        web_view.urlChanged.connect(lambda q: self.add_to_history(q))
        
        tab_index = self.tabs.addTab(web_view, title)
        self.tabs.setCurrentIndex(tab_index)
        
        # Update buttons immediately
        self.update_navigation_buttons(web_view)

    def back_history(self):
        current_tab = self.tabs.currentWidget()
        if current_tab and current_tab.history().canGoBack():
            current_tab.back()
            self.update_navigation_buttons(current_tab)

    def forward_history(self):
        current_tab = self.tabs.currentWidget()
        if current_tab and current_tab.history().canGoForward():
            current_tab.forward()
            self.update_navigation_buttons(current_tab)

    def refresh_page(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.reload()

    def load_url(self):
        url_text = self.url_input.text()
        try:
            if not url_text.startswith(("http://", "https://")):
                url_text = "http://" + url_text
            qurl = QUrl(url_text)
            if qurl.isValid():
                self.tabs.currentWidget().setUrl(qurl)
        except Exception as e:
            print(f"URL Error: {e}")

    def update_urlbar(self, qurl, web_view):
        if self.tabs.currentWidget() == web_view:
            self.url_input.setText(qurl.toString())

    def update_tab_title(self, title, web_view):
        index = self.tabs.indexOf(web_view)
        if index != -1:
            self.tabs.setTabText(index, title[:20] + "..." if len(title) > 20 else title)

    def update_navigation_buttons(self, web_view=None):
        current_tab = web_view if web_view else self.tabs.currentWidget()
        if current_tab:
            self.back_button.setEnabled(current_tab.history().canGoBack())
            self.forward_button.setEnabled(current_tab.history().canGoForward())

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.add_new_tab()
            self.tabs.removeTab(index)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        browser = BrowserWindow()
        browser.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)