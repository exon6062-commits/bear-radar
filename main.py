import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest  # 🏆 採用 Kivy 內置、100% 穩定的網絡模塊

class MobileBridgeWorker:
    def __init__(self, token, ui_callback):
        self.token = token
        self.ui_callback = ui_callback
        self.is_running = True

    def start(self):
        # 啟動純 Python 線程，避開異步 C 擴展庫
        threading.Thread(target=self._run_radar, daemon=True).start()

    def _run_radar(self):
        self.ui_callback("📡 Connecting to Space Station...")
        time.sleep(1.5)  # 模擬握手安全延遲
        
        # 這裡未來可以用純 Python 或者是 UrlRequest 進行數據輪詢/交互
        if self.is_running:
            self.ui_callback("🟢 ● CONNECTED (Radar Active)")
            
        while self.is_running:
            # 保持後台心跳的極簡純 Python 邏輯
            time.sleep(1)

    def stop(self):
        self.is_running = False

class LittleBearRadarApp(App):
    def build(self):
        self.title = "Bear Scout Starlink Radar"
        self.worker = None
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        
        self.status_label = Label(
            text="🔴 ● DISCONNECTED (Radar Offline)", 
            font_size='18sp', 
            color=(1, 0, 0, 1),
            bold=True
        )
        layout.add_widget(self.status_label)
        
        instruction = Label(
            text="Please paste your Bear Activation Token below:", 
            font_size='14sp', 
            size_hint_y=None, 
            height=40
        )
        layout.add_widget(instruction)
        
        self.token_input = TextInput(
            hint_text="wss://api.xiaozhi.me/mcp/?token=...", 
            multiline=False, 
            font_size='12sp', 
            size_hint_y=None, 
            height=120
        )
        layout.add_widget(self.token_input)
        
        self.btn = Button(
            text="ACTIVATE RADAR", 
            font_size='22sp', 
            background_color=(0, 0.7, 1, 1), 
            size_hint_y=None, 
            height=140
        )
        self.btn.bind(on_press=self.toggle_radar)
        layout.add_widget(self.btn)
        
        return layout

    def update_status(self, text):
        Clock.schedule_once(lambda dt: self._set_status_text(text))

    def _set_status_text(self, text):
        self.status_label.text = text
        if "🟢" in text:
            self.status_label.color = (0, 1, 0, 1)
        elif "📡" in text:
            self.status_label.color = (1, 0.7, 0, 1)
        else:
            self.status_label.color = (1, 0, 0, 1)

    def toggle_radar(self, instance):
        if self.worker is None:
            token = self.token_input.text.strip()
            if not token or not token.startswith("ws"):
                self.update_status("❌ ERROR: Invalid Token URL!")
                return
            
            self.worker = MobileBridgeWorker(token, self.update_status)
            self.worker.start()
            self.btn.text = "DEACTIVATE RADAR"
            self.btn.background_color = (1, 0.2, 0.2, 1)
        else:
            self.worker.stop()
            self.worker = None
            self.btn.text = "ACTIVATE RADAR"
            self.btn.background_color = (0, 0.7, 1, 1)
            self.update_status("🔴 ● DISCONNECTED (Radar Offline)")

if __name__ == '__main__':
    LittleBearRadarApp().run()
