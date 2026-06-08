import asyncio
import threading
import aiohttp
from bs4 import BeautifulSoup
import websockets
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock

# ----------------- 1. Mobile Bridge Worker -----------------
class MobileBridgeWorker:
    def __init__(self, token, ui_callback):
        self.token = token
        self.ui_callback = ui_callback
        self.loop = None
        self.is_running = True

    def start(self):
        threading.Thread(target=self._run_loop, daemon=True).start()

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect())

    async def _connect(self):
        self.ui_callback("📡 Connecting to Space Station...")
        try:
            async with websockets.connect(self.token, ping_interval=20, ping_timeout=20) as websocket:
                self.ui_callback("🟢 ● CONNECTED (Radar Active)")
                while self.is_running:
                    msg = await websocket.recv()
                    await asyncio.sleep(0.1)
        except Exception as e:
            self.ui_callback(f"❌ Disconnected: {str(e)[:20]}")

    def stop(self):
        self.is_running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)

# ----------------- 2. Kivy UI (International Version) -----------------
class LittleBearRadarApp(App):
    def build(self):
        self.title = "Bear Scout Starlink Radar"
        self.worker = None
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=30)
        
        # Status Monitor (Red / Amber / Green)
        self.status_label = Label(
            text="🔴 ● DISCONNECTED (Radar Offline)", 
            font_size='18sp', 
            color=(1, 0, 0, 1),
            bold=True
        )
        layout.add_widget(self.status_label)
        
        # User Instruction
        instruction = Label(
            text="Please paste your Bear Activation Token below:", 
            font_size='14sp', 
            size_hint_y=None, 
            height=40
        )
        layout.add_widget(instruction)
        
        # Token Input Field
        self.token_input = TextInput(
            hint_text="wss://api.xiaozhi.me/mcp/?token=...", 
            multiline=False, 
            font_size='12sp', 
            size_hint_y=None, 
            height=120
        )
        layout.add_widget(self.token_input)
        
        # Ignition Big Button
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
            self.status_label.color = (0, 1, 0, 1)      # Green Light
        elif "📡" in text:
            self.status_label.color = (1, 0.7, 0, 1)    # Amber Light
        else:
            self.status_label.color = (1, 0, 0, 1)      # Red Light

    def toggle_radar(self, instance):
        if self.worker is None:
            token = self.token_input.text.strip()
            if not token or not token.startswith("ws"):
                self.update_status("❌ ERROR: Invalid Token URL!")
                return
            
            self.worker = MobileBridgeWorker(token, self.update_status)
            self.worker.start()
            self.btn.text = "DEACTIVATE RADAR"
            self.btn.background_color = (1, 0.2, 0.2, 1) # Turn Red
        else:
            self.worker.stop()
            self.worker = None
            self.btn.text = "ACTIVATE RADAR"
            self.btn.background_color = (0, 0.7, 1, 1)   # Turn Blue
            self.update_status("🔴 ● DISCONNECTED (Radar Offline)")

if __name__ == '__main__':
    LittleBearRadarApp().run()
