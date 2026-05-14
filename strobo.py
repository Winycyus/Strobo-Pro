import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import time
import threading
import colorsys
from pynput import keyboard
from screeninfo import get_monitors
from PIL import Image, ImageTk
import csv
import urllib.request
import io

# URL da sua planilha publicada como CSV
URL_PLANILHA_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTJlMWQb9tXWsj1uYXNnNVvkXSlIb3QYH_TH1COs-DYIL0Hzo6V9__lPNnGRhkjhEdcosfpdjqALQlc/pub?output=csv"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SplashScreen:
    def __init__(self):
        self.splash = tk.Tk()
        self.splash.configure(bg="black")
        self.splash.overrideredirect(True)
        sw = self.splash.winfo_screenwidth()
        sh = self.splash.winfo_screenheight()
        self.splash.geometry(f"{sw}x{sh}+0+0")
        
        try:
            icon_path = resource_path("strobo-pro.ico")
            img_open = Image.open(icon_path)
            img_res = img_open.resize((300, 300), Image.Resampling.LANCZOS)
            self.img_icon = ImageTk.PhotoImage(img_res)
            lbl_icon = tk.Label(self.splash, image=self.img_icon, bg="black")
            lbl_icon.pack(expand=True)
        except:
            tk.Label(self.splash, text="STROBO PRO", fg="#CCFF00", bg="black", font=("Arial Black", 50)).pack(expand=True)

        self.splash.after(1500, self.finish_splash)
        self.splash.mainloop()

    def finish_splash(self):
        self.splash.destroy()
        LoginScreen()

class LoginScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Acesso - STROBO PRO")
        self.root.state('zoomed') 
        self.root.configure(bg="#121212")

        try:
            self.root.iconbitmap(resource_path("strobo-pro.ico"))
        except: pass

        self.monitores = get_monitors()
        self.setup_login_ui()
        self.root.mainloop()

    def setup_login_ui(self):
        header = tk.Frame(self.root, bg="#CCFF00", height=80)
        header.pack(fill="x", side="top")
        tk.Label(header, text="PAINEL DE ACESSO", bg="#CCFF00", fg="black", font=("Arial Black", 18)).pack(expand=True)

        content_wrapper = tk.Frame(self.root, bg="#121212")
        content_wrapper.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(content_wrapper, text="USUÁRIO", fg="#CCFF00", bg="#121212", font=("Arial", 10, "bold")).pack()
        self.ent_user = tk.Entry(content_wrapper, bg="#2b2b2b", fg="white", relief="flat", justify="center", width=30, font=("Arial", 12))
        self.ent_user.pack(ipady=8, pady=5)
        self.ent_user.insert(0, "admin")

        tk.Label(content_wrapper, text="SENHA", fg="#CCFF00", bg="#121212", font=("Arial", 10, "bold")).pack(pady=(15, 0))
        self.ent_pass = tk.Entry(content_wrapper, bg="#2b2b2b", fg="white", relief="flat", justify="center", width=30, font=("Arial", 12), show="*")
        self.ent_pass.pack(ipady=8, pady=5)

        tk.Label(content_wrapper, text="SELECIONE O MONITOR DO TELÃO", fg="#CCFF00", bg="#121212", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        monitor_names = [f"Monitor {i+1}: {m.width}x{m.height}" for i, m in enumerate(self.monitores)]
        self.combo_monitor = ttk.Combobox(content_wrapper, values=monitor_names, state="readonly", width=30, font=("Arial", 11))
        if monitor_names: self.combo_monitor.current(0)
        self.combo_monitor.pack(pady=5)

        btn_login = tk.Button(content_wrapper, text="ENTRAR NO SISTEMA", bg="#CCFF00", fg="black", relief="flat", font=("Arial", 12, "bold"), width=20, command=self.check_login)
        btn_login.pack(pady=30, ipady=12)
        self.root.bind('<Return>', lambda e: self.check_login())

    def check_login(self):
        username_digitado = self.ent_user.get()
        password_digitada = self.ent_pass.get()
        idx = self.combo_monitor.current()
        monitor_escolhido = self.monitores[idx]
        self.root.config(cursor="watch")
        self.root.update()

        try:
            with urllib.request.urlopen(URL_PLANILHA_CSV) as response:
                dados_csv = response.read().decode('utf-8')
                leitor = csv.DictReader(io.StringIO(dados_csv))
                login_sucesso = False
                for linha in leitor:
                    if (linha['usuario'].strip() == username_digitado and 
                        linha['senha'].strip() == password_digitada):
                        login_sucesso = True
                        break
                if login_sucesso:
                    self.root.destroy()
                    StroboProFinal(monitor_escolhido)
                else:
                    messagebox.showerror("Erro de Acesso", "Usuário ou Senha incorretos.")
                    self.root.config(cursor="")
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Falha ao acessar planilha online: {e}")
            self.root.config(cursor="")

class StroboProFinal:
    def __init__(self, monitor):
        self.monitor_alvo = monitor
        self.janela_overlay = None
        
        # Mapeamento de Atalhos Personalizáveis
        self.atalhos = {
            "I": "i",
            "J": "j",
            "T": "t",
            "B": "b",
            "S": "s",
            "R": "r"
        }
        self.buttons_refs = {}

        self.current_hue = 0.0
        self.last_s, self.last_v = 1.0, 1.0
        self.current_color_rgb = (255, 255, 255)
        self.hex_value = "#FFFFFF"
        self.bpm = 0
        self.last_tap_time = 0
        self.bpm_ativo = False
        self.intervalo = 0
        self.blackout_ativo = False
        self.current_brightness = 0
        self.pressionado_j = False
        self.max_brightness_val = 180
        self.fade_speed_val = 10

        self.control = tk.Tk()
        self.control.title("STROBO PRO - CONSOLE")
        self.control.state('zoomed')
        self.control.configure(bg="#121212")
        
        try:
            self.control.iconbitmap(resource_path("strobo-pro.ico"))
        except: pass

        self.setup_ui()
        self.setup_overlay()

        self.listener = keyboard.Listener(on_press=self.key_p, on_release=self.key_r)
        self.listener.start()
        threading.Thread(target=self.bpm_worker, daemon=True).start()

        self.reforcar_topo()
        self.control.mainloop()

    def setup_overlay(self):
        m = self.monitor_alvo
        ov = tk.Toplevel(self.control)
        ov.overrideredirect(True)
        ov.geometry(f"{m.width}x{m.height}+{m.x}+{m.y}")
        ov.attributes("-topmost", True)
        ov.attributes("-disabled", True)
        ov.configure(bg="white")
        ov.attributes("-alpha", 0.0)
        self.janela_overlay = ov

    def change_shortcut(self, key_id):
        """Abre um diálogo para capturar a nova tecla de atalho"""
        nova_tecla = simpledialog.askstring("Personalizar", f"Digite a nova tecla para {key_id}:")
        if nova_tecla and len(nova_tecla) == 1:
            self.atalhos[key_id] = nova_tecla.lower()
            # Atualiza o texto do botão visualmente
            btn = self.buttons_refs[key_id]
            current_text = btn.cget("text").split("[")[0]
            btn.config(text=f"{current_text}[{nova_tecla.upper()}]")

    def setup_ui(self):
        header = tk.Frame(self.control, bg="#CCFF00", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="STROBO PRO", bg="#CCFF00", fg="black", font=("Arial Black", 20)).pack(side="left", padx=20)
        
        info_monitor = f"TELÃO: {self.monitor_alvo.width}x{self.monitor_alvo.height}"
        tk.Label(header, text=info_monitor, bg="#CCFF00", fg="#555", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        self.lbl_bpm = tk.Label(header, text="BPM: 000", bg="#CCFF00", fg="black", font=("Consolas", 14, "bold"))
        self.lbl_bpm.pack(side="right", padx=60)

        body = tk.Frame(self.control, bg="#121212")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        # PAINEL ESQUERDO
        self.left_panel = tk.Frame(body, bg="#1e1e1e", width=380)
        self.left_panel.pack(side="left", fill="both")
        self.left_panel.pack_propagate(False)

        self.sat_val_canvas = tk.Canvas(self.left_panel, width=300, height=250, bg="black", highlightthickness=0)
        self.sat_val_canvas.pack(pady=(20, 10), padx=40)
        self.draw_sat_val_gradient()
        self.sat_val_canvas.bind("<B1-Motion>", self.pick_color)
        self.sat_val_canvas.bind("<Button-1>", self.pick_color)

        self.hue_canvas = tk.Canvas(self.left_panel, width=300, height=20, highlightthickness=0)
        self.hue_canvas.pack(pady=10)
        self.draw_hue_gradient()
        self.hue_canvas.bind("<B1-Motion>", self.pick_hue)
        self.hue_canvas.bind("<Button-1>", self.pick_hue)

        self.hex_label = tk.Label(self.left_panel, text="#FFFFFF", fg="#CCFF00", bg="#2b2b2b", width=12, font=("Consolas", 12))
        self.hex_label.pack(pady=10)

        # PAINEL DIREITO
        self.right_panel = tk.Frame(body, bg="#2b2b2b")
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(20, 0))

        # GRID DE BOTÕES (Clique direito para personalizar atalho)
        self.sec_main = tk.Frame(self.right_panel, bg="#3d3d3d", pady=20)
        self.sec_main.pack(fill="x", padx=20, pady=15)
        
        btns_config = [("Strobo Instant", "I"), ("STROBO FADE", "J"), ("Strobo TAP", "T")]
        for txt, k in btns_config:
            btn = tk.Button(self.sec_main, text=f"{txt} [{self.atalhos[k].upper()}]", bg="#D9D9D9", relief="flat", width=15, height=2)
            btn.pack(side="left", expand=True, padx=5)
            self.buttons_refs[k] = btn
            if k == "T": btn.config(command=self.tap_tempo)
            else: self.bind_b(btn, k)
            btn.bind("<Button-3>", lambda e, ki=k: self.change_shortcut(ki)) # Botão DIREITO para personalizar

        self.sec_sld = tk.Frame(self.right_panel, bg="#3d3d3d", pady=20)
        self.sec_sld.pack(fill="x", padx=20, pady=10)
        self.sld_brilho = self.create_styled_slider(self.sec_sld, "OPACIDADE MÁXIMA", self.max_brightness_val, 255)
        self.sld_fade = self.create_styled_slider(self.sec_sld, "VELOCIDADE FADE", self.fade_speed_val, 50)

        self.sec_extra = tk.Frame(self.right_panel, bg="#3d3d3d", pady=20)
        self.sec_extra.pack(fill="x", padx=20, pady=15)
        extra_config = [("BLACKOUT", "B"), ("STOP", "S"), ("RESET", "R")]
        for txt, k in extra_config:
            btn = tk.Button(self.sec_extra, text=f"{txt} [{self.atalhos[k].upper()}]", bg="#D9D9D9", relief="flat", width=15, height=2)
            btn.pack(side="left", expand=True, padx=5)
            self.buttons_refs[k] = btn
            self.bind_extra(btn, k)
            btn.bind("<Button-3>", lambda e, ki=k: self.change_shortcut(ki)) # Botão DIREITO para personalizar

    # --- MÉTODOS DE COR ---
    def draw_hue_gradient(self):
        for i in range(300):
            hue = i / 300
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = "#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255))
            self.hue_canvas.create_line(i, 0, i, 20, fill=color)

    def draw_sat_val_gradient(self):
        self.sat_val_canvas.delete("grad")
        for x in range(0, 300, 10):
            for y in range(0, 250, 10):
                s, v = x/300, 1.0-(y/250)
                r, g, b = colorsys.hsv_to_rgb(self.current_hue, s, v)
                color = "#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255))
                self.sat_val_canvas.create_rectangle(x, y, x+10, y+10, fill=color, outline="", tags="grad")

    def pick_hue(self, event):
        self.current_hue = max(0, min(event.x, 300)) / 300
        self.draw_sat_val_gradient()
        self.update_final_color(self.last_s, self.last_v)

    def pick_color(self, event):
        self.last_s, self.last_v = max(0, min(event.x, 300))/300, 1.0-(max(0, min(event.y, 250))/250)
        self.update_final_color(self.last_s, self.last_v)

    def update_final_color(self, s, v):
        r, g, b = colorsys.hsv_to_rgb(self.current_hue, s, v)
        self.hex_value = "#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255))
        self.hex_label.config(text=self.hex_value.upper())
        if self.janela_overlay: self.janela_overlay.configure(bg=self.hex_value)

    # --- LÓGICA ---
    def panic_reset(self):
        self.stop_all(); self.reset_bpm(); self.blackout_ativo = False
        if self.janela_overlay: self.janela_overlay.configure(bg=self.hex_value); self.janela_overlay.attributes("-alpha", 0.0)
        self.current_brightness = 0

    def update_br(self, val, force_black=False):
        if self.blackout_ativo and not force_black: return
        alpha = (val / 255.0) * (self.max_brightness_val / 255.0)
        if force_black:
            alpha = 1.0
            if self.janela_overlay: self.janela_overlay.configure(bg="black")
        if self.janela_overlay: self.janela_overlay.attributes("-alpha", alpha)

    def create_styled_slider(self, parent, label, start, to):
        tk.Label(parent, text=label, bg="#3d3d3d", fg="white", font=("Arial", 8, "bold")).pack(anchor="w", padx=40)
        s = tk.Scale(parent, from_=0, to=to, orient="horizontal", bg="#D9D9D9", highlightthickness=0, relief="flat", command=lambda e: self.upd_val())
        s.set(start); s.pack(fill="x", padx=40, pady=(0, 10))
        return s

    def upd_val(self):
        self.max_brightness_val, self.fade_speed_val = self.sld_brilho.get(), self.sld_fade.get()

    def fade_loop(self):
        if not self.pressionado_j and self.current_brightness > 0:
            self.current_brightness -= self.fade_speed_val
            self.update_br(max(0, self.current_brightness))
            self.control.after(16, self.fade_loop)

    def instant_press(self): self.update_br(255)
    def instant_release(self): self.update_br(0)
    def fade_press(self): self.pressionado_j, self.current_brightness = True, 255; self.update_br(255)
    def fade_release(self): self.pressionado_j = False; self.fade_loop()

    def tap_tempo(self):
        t = time.time()
        if self.last_tap_time > 0:
            diff = t - self.last_tap_time
            if 0.25 < diff < 2.0:
                self.intervalo, self.bpm, self.bpm_ativo = diff, int(60/diff), True
                self.lbl_bpm.config(text=f"BPM: {self.bpm:03}")
        self.last_tap_time = t

    def bpm_worker(self):
        while True:
            if self.bpm_ativo and not self.blackout_ativo:
                self.control.after(0, self.bpm_flash); time.sleep(self.intervalo)
            else: time.sleep(0.1)

    def bpm_flash(self):
        self.current_brightness, self.pressionado_j = 255, False; self.fade_loop()

    def reset_bpm(self):
        self.bpm, self.bpm_ativo = 0, False; self.lbl_bpm.config(text="BPM: 000"); self.update_br(0)

    def stop_all(self): self.bpm_ativo = False; self.update_br(0)

    def toggle_blackout(self):
        self.blackout_ativo = not self.blackout_ativo
        if self.blackout_ativo: self.update_br(255, True)
        else:
            if self.janela_overlay: self.janela_overlay.configure(bg=self.hex_value)
            self.update_br(0)

    def bind_b(self, b, k):
        if k == "I":
            b.bind("<ButtonPress-1>", lambda e: self.instant_press())
            b.bind("<ButtonRelease-1>", lambda e: self.instant_release())
        elif k == "J":
            b.bind("<ButtonPress-1>", lambda e: self.fade_press())
            b.bind("<ButtonRelease-1>", lambda e: self.fade_release())

    def bind_extra(self, b, k):
        if k == "B": b.config(command=self.toggle_blackout)
        elif k == "S": b.config(command=self.stop_all)
        elif k == "R": b.config(command=self.reset_bpm)

    def key_p(self, key):
        try:
            k = key.char.lower()
            # Verifica contra o dicionário de atalhos configurados
            if k == self.atalhos["I"]: self.control.after(0, self.instant_press)
            if k == self.atalhos["J"] and not self.pressionado_j: self.control.after(0, self.fade_press)
            if k == self.atalhos["T"]: self.control.after(0, self.tap_tempo)
            if k == self.atalhos["B"]: self.control.after(0, self.toggle_blackout)
            if k == self.atalhos["R"]: self.control.after(0, self.reset_bpm)
            if k == self.atalhos["S"]: self.control.after(0, self.stop_all)
        except:
            if key == keyboard.Key.esc: self.control.after(0, self.panic_reset)

    def key_r(self, key):
        try:
            k = key.char.lower()
            if k == self.atalhos["I"]: self.control.after(0, self.instant_release)
            if k == self.atalhos["J"]: self.control.after(0, self.fade_release)
        except: pass

    def reforcar_topo(self):
        if self.janela_overlay: self.janela_overlay.attributes("-topmost", True); self.janela_overlay.lift()
        self.control.after(500, self.reforcar_topo)

if __name__ == "__main__":
    SplashScreen()
