import sys
import os
import tkinter as tk
import time
import threading
from tkinter import PhotoImage
from pynput import keyboard
from screeninfo import get_monitors

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class StroboProFinal:
    def __init__(self):
        self.monitores = get_monitors()
        self.janelas_overlay = []
        
        # Estados
        self.bpm = 0
        self.last_tap_time = 0
        self.bpm_ativo = False
        self.intervalo = 0
        self.blackout_ativo = False
        self.current_brightness = 0
        self.pressionado_j = False
        self.max_brightness_val = 180
        self.fade_speed_val = 10
        self.current_color_rgb = (255, 255, 255)

        self.control = tk.Tk()
        self.control.title("STROBO PRO - CONSOLE")
        self.control.geometry("850x650")
        self.control.configure(bg="black")
        self.control.attributes("-topmost", True)

        try:
            self.control.iconbitmap(resource_path("strobo-pro.ico"))
        except: pass

        self.setup_ui()

        # 2. OVERLAYS (CONFIGURADOS PARA TRANSPARÊNCIA)
        for m in self.monitores:
            ov = tk.Toplevel(self.control)
            ov.overrideredirect(True)
            ov.geometry(f"{m.width}x{m.height}+{m.x}+{m.y}")
            ov.attributes("-topmost", True)
            ov.attributes("-disabled", True)
            # Define a cor de fundo da janela (será a cor do flash)
            ov.configure(bg="white")
            # Inicia totalmente transparente
            ov.attributes("-alpha", 0.0)
            
            self.janelas_overlay.append(ov)

        self.listener = keyboard.Listener(on_press=self.key_p, on_release=self.key_r)
        self.listener.start()
        threading.Thread(target=self.bpm_worker, daemon=True).start()

        self.reforcar_topo()
        self.control.mainloop()

    def setup_ui(self):
        self.top_frame = tk.Frame(self.control, bg="black")
        self.top_frame.pack(fill="x", padx=20, pady=10)

        try:
            self.logo_img = PhotoImage(file=resource_path("Aplicação#11.png")).subsample(5, 5)
            tk.Label(self.top_frame, image=self.logo_img, bg="black").pack(side="right")
        except: pass

        self.lbl_bpm = tk.Label(self.top_frame, text="BPM: 000", fg="yellow", bg="black", font=("Consolas", 18, "bold"))
        self.lbl_bpm.pack(side="left")

        self.config_area = tk.Frame(self.control, bg="#111111", padx=10, pady=10)
        self.config_area.pack(fill="x", padx=20, pady=5)
        self.config_area.columnconfigure(1, weight=1)

        self.sld_brilho = tk.Scale(self.config_area, from_=0, to=255, orient="horizontal", bg="#111111", fg="yellow", label="OPACIDADE MÁXIMA", command=self.upd_val)
        self.sld_brilho.set(self.max_brightness_val)
        self.sld_brilho.grid(row=0, column=1, sticky="ew")

        self.sld_fade = tk.Scale(self.config_area, from_=1, to=50, orient="horizontal", bg="#111111", fg="yellow", label="VELOCIDADE DO FADE", command=self.upd_val)
        self.sld_fade.set(self.fade_speed_val)
        self.sld_fade.grid(row=1, column=1, sticky="ew")

        self.color_p = tk.Frame(self.config_area, bg="#111111")
        self.color_p.grid(row=2, column=0, columnspan=2, pady=10)
        cores = [("#FFFFFF", (255,255,255)), ("#FFBF00", (255,191,0)), ("#007FFF", (0,127,255)), ("#FF0000", (255,0,0))]
        for hex_c, rgb_c in cores:
            tk.Button(self.color_p, bg=hex_c, width=6, command=lambda c=rgb_c, h=hex_c: self.set_c(rgb_c, h)).pack(side="left", padx=5)

        self.btn_grid = tk.Frame(self.control, bg="black")
        self.btn_grid.pack(expand=True)
        btns = [("INSTANT [I]", "I", 0, 0), ("FADE [J]", "J", 0, 1), ("TAP [T]", "T", 0, 2),
                ("BLACKOUT [B]", "B", 1, 0), ("RESET [R]", "R", 1, 1), ("STOP [S]", "S", 1, 2)]
        for t, k, r, c in btns:
            b = tk.Button(self.btn_grid, text=t, bg="yellow", fg="black", width=15, height=4, font=("Arial", 10, "bold"))
            b.grid(row=r, column=c, padx=8, pady=8)
            self.bind_b(b, k)

    def set_c(self, rgb, hex_c):
        self.current_color_rgb = rgb
        for ov in self.janelas_overlay:
            ov.configure(bg=hex_c)

    def upd_val(self, e): 
        self.max_brightness_val = self.sld_brilho.get()
        self.fade_speed_val = self.sld_fade.get()

    def update_br(self, val, force_black=False):
        """Agora controla a opacidade (-alpha) em vez da cor do retângulo"""
        if self.blackout_ativo and not force_black: return
        
        # Converte o valor 0-255 para 0.0-1.0 (Alpha do Windows)
        # Multiplicamos pelo limite do slider de opacidade máxima
        alpha_final = (val / 255.0) * (self.max_brightness_val / 255.0)
        
        if force_black:
            alpha_final = 1.0
            for ov in self.janelas_overlay:
                ov.configure(bg="black")
        else:
            # Garante que a cor volte ao selecionado se sair do blackout
            # (Poderia ser otimizado, mas para esse uso é seguro)
            pass

        for ov in self.janelas_overlay:
            ov.attributes("-alpha", alpha_final)

    def fade_loop(self):
        if not self.pressionado_j and self.current_brightness > 0:
            self.current_brightness -= self.fade_speed_val
            self.update_br(max(0, self.current_brightness))
            self.control.after(16, self.fade_loop)

    def instant_press(self): self.update_br(255)
    def instant_release(self): self.update_br(0)
    def fade_press(self): self.pressionado_j = True; self.current_brightness = 255; self.update_br(255)
    def fade_release(self): self.pressionado_j = False; self.fade_loop()

    def tap_tempo(self):
        t = time.time()
        if self.last_tap_time > 0:
            diff = t - self.last_tap_time
            if 0.25 < diff < 2.0:
                self.intervalo = diff
                self.bpm = int(60/diff)
                self.bpm_ativo = True
                self.lbl_bpm.config(text=f"BPM: {self.bpm:03}")
        self.last_tap_time = t

    def bpm_worker(self):
        while True:
            if self.bpm_ativo and not self.blackout_ativo:
                self.control.after(0, self.bpm_flash)
                time.sleep(self.intervalo)
            else: time.sleep(0.1)

    def bpm_flash(self):
        self.current_brightness = 255
        self.pressionado_j = False
        self.fade_loop()

    def reset_bpm(self):
        self.bpm = 0; self.intervalo = 0; self.last_tap_time = 0; self.bpm_ativo = False
        self.lbl_bpm.config(text="BPM: 000"); self.update_br(0)

    def bind_b(self, b, k):
        if k == "I":
            b.bind("<ButtonPress-1>", lambda e: self.instant_press())
            b.bind("<ButtonRelease-1>", lambda e: self.instant_release())
        elif k == "J":
            b.bind("<ButtonPress-1>", lambda e: self.fade_press())
            b.bind("<ButtonRelease-1>", lambda e: self.fade_release())
        elif k == "T": b.config(command=self.tap_tempo)
        elif k == "B": b.config(command=self.toggle_blackout)
        elif k == "R": b.config(command=self.reset_bpm)
        elif k == "S": b.config(command=self.stop_all)

    def stop_all(self):
        self.bpm_ativo = False; self.blackout_ativo = False
        self.update_br(0)

    def toggle_blackout(self):
        self.blackout_ativo = not self.blackout_ativo
        if self.blackout_ativo:
            for ov in self.janelas_overlay: ov.configure(bg="black")
            self.update_br(255, force_black=True)
        else:
            # Volta para a cor que estava antes do blackout
            hex_atual = "#%02x%02x%02x" % self.current_color_rgb
            for ov in self.janelas_overlay: ov.configure(bg=hex_atual)
            self.update_br(0)

    def key_p(self, key):
        try:
            k = key.char.lower()
            if k == 'i': self.control.after(0, self.instant_press)
            if k == 'j' and not self.pressionado_j: self.control.after(0, self.fade_press)
            if k == 't': self.control.after(0, self.tap_tempo)
            if k == 'b': self.control.after(0, self.toggle_blackout)
            if k == 'r': self.control.after(0, self.reset_bpm)
            if k == 's': self.control.after(0, self.stop_all)
        except:
            if key == keyboard.Key.esc: self.control.after(0, self.control.destroy)

    def key_r(self, key):
        try:
            k = key.char.lower()
            if k == 'i': self.control.after(0, self.instant_release)
            if k == 'j': self.control.after(0, self.fade_release)
        except: pass

    def reforcar_topo(self):
        for o in self.janelas_overlay: o.attributes("-topmost", True); o.lift()
        self.control.after(500, self.reforcar_topo)

if __name__ == "__main__":
    StroboProFinal()
