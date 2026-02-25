#!/usr/bin/env python3
# gerador_senha_profissional.py
"""
Gerador de senhas com interface aprimorada:
- usa ttkbootstrap para tema moderno e modo escuro
- layout com hierarquia visual
- barra de força com entropia e motivos de fraqueza
- microinterações: animação sutil, Copiado!, mostrar/ocultar senha
- acessibilidade: atalhos, foco visível, labels claros
Requisitos: Python 3.8+, ttkbootstrap
"""

import string
import secrets
import math
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from functools import partial
import sys
import os

def resource_path(relative_path):
    """
    Retorna o caminho absoluto para um recurso, funcionando tanto em execução
    normal quanto quando empacotado com PyInstaller (--onefile).
    Uso: resource_path('assets/logo.png')
    """
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)

# --- Configurações e constantes ---
AMBIGUOUS = "Il1O0"
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>/?"
DEFAULT_LENGTH = 16
CLIPBOARD_CLEAR_SECONDS = 12

# --- Utilitários de geração e avaliação ---

def build_charset(use_lower, use_upper, use_digits, use_symbols, exclude_ambiguous):
    parts = []
    if use_lower:
        parts.append(string.ascii_lowercase)
    if use_upper:
        parts.append(string.ascii_uppercase)
    if use_digits:
        parts.append(string.digits)
    if use_symbols:
        parts.append(SYMBOLS)
    charset = "".join(parts)
    if exclude_ambiguous:
        charset = "".join(ch for ch in charset if ch not in AMBIGUOUS)
    return charset

def generate_password(length, charset, require_each=False):
    if not charset:
        return ""
    # Se require_each, tenta garantir pelo menos um de cada tipo presente no charset_groups
    if require_each:
        groups = []
        if any(c.islower() for c in charset):
            groups.append([c for c in charset if c.islower()])
        if any(c.isupper() for c in charset):
            groups.append([c for c in charset if c.isupper()])
        if any(c.isdigit() for c in charset):
            groups.append([c for c in charset if c.isdigit()])
        if any(c in SYMBOLS for c in charset):
            groups.append([c for c in charset if c in SYMBOLS])
        if len(groups) <= length:
            pwd_chars = [secrets.choice(g) for g in groups]
            remaining = length - len(pwd_chars)
            pwd_chars += [secrets.choice(charset) for _ in range(remaining)]
            secrets.SystemRandom().shuffle(pwd_chars)
            return "".join(pwd_chars)
    return "".join(secrets.choice(charset) for _ in range(length))

def estimate_entropy(length, charset_size):
    if charset_size <= 1:
        return 0.0
    return length * math.log2(charset_size)

def strength_label(entropy_bits):
    if entropy_bits < 28:
        return "Muito fraca"
    if entropy_bits < 36:
        return "Fraca"
    if entropy_bits < 60:
        return "Moderada"
    if entropy_bits < 80:
        return "Forte"
    return "Muito forte"

def strength_color(entropy_bits):
    # retorna estilo de cor para progressbar
    if entropy_bits < 28:
        return "danger"
    if entropy_bits < 36:
        return "warning"
    if entropy_bits < 60:
        return "info"
    return "success"

# --- Aplicação Tkinter com ttkbootstrap ---

class PasswordGeneratorApp(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Gerador de Senhas Profissional")
        self.minsize(560, 300)
        # não atribuir self.style = self.style (causava AttributeError)
        self.create_variables()
        self.create_widgets()
        self.bind_shortcuts()
        self.after(100, self.initial_focus)
        self.center_window()

    def create_variables(self):
        self.length_var = tk.IntVar(value=DEFAULT_LENGTH)
        self.lower_var = tk.BooleanVar(value=True)
        self.upper_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.ambig_var = tk.BooleanVar(value=True)
        self.require_each_var = tk.BooleanVar(value=False)
        self.auto_clear_clipboard_var = tk.BooleanVar(value=True)
        self.password_var = tk.StringVar()
        self.entropy_var = tk.StringVar(value="")
        self.strength_text_var = tk.StringVar(value="")
        self.show_password = tk.BooleanVar(value=False)
        self.theme_mode = tk.StringVar(value="light")

    def create_widgets(self):
        pad = {"padx": 12, "pady": 8}

        # Top frame: título e tema
        top = ttk.Frame(self)
        top.pack(fill="x", **pad)
        ttk.Label(top, text="Gerador de Senhas Seguras", font=("Segoe UI", 14, "bold")).pack(side="left")
        theme_frame = ttk.Frame(top)
        theme_frame.pack(side="right")
        ttk.Label(theme_frame, text="Tema").pack(side="left", padx=(0,6))
        self.theme_btn = tb.Checkbutton(theme_frame, text="Modo escuro", bootstyle="secondary", variable=self.theme_mode, onvalue="dark", offvalue="light", command=self.toggle_theme)
        self.theme_btn.pack(side="right")

        # Main content frame with two columns
        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, **pad)

        # Left: opções
        options = ttk.LabelFrame(content, text="Opções", padding=(12,10))
        options.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        options.columnconfigure(1, weight=1)

        ttk.Label(options, text="Tamanho").grid(row=0, column=0, sticky="w")
        self.length_spin = ttk.Spinbox(options, from_=4, to=128, textvariable=self.length_var, width=6)
        self.length_spin.grid(row=0, column=1, sticky="w")
        self.length_scale = ttk.Scale(options, from_=4, to=128, orient="horizontal", command=self.on_scale_move)
        self.length_scale.set(self.length_var.get())
        self.length_scale.grid(row=1, column=0, columnspan=2, sticky="we", pady=(6,0))

        # Checkbuttons agrupados
        cb_frame = ttk.Frame(options)
        cb_frame.grid(row=2, column=0, columnspan=2, pady=(10,0), sticky="w")
        ttk.Checkbutton(cb_frame, text="Letras minúsculas", variable=self.lower_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(cb_frame, text="Letras maiúsculas", variable=self.upper_var).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(cb_frame, text="Dígitos", variable=self.digits_var).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(cb_frame, text="Símbolos", variable=self.symbols_var).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(cb_frame, text="Excluir ambíguos Il1O0", variable=self.ambig_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=(6,0))
        ttk.Checkbutton(cb_frame, text="Garantir pelo menos 1 de cada tipo selecionado", variable=self.require_each_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=(6,0))

        ttk.Separator(options, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="we", pady=(10,6))
        ttk.Checkbutton(options, text="Limpar clipboard automaticamente", variable=self.auto_clear_clipboard_var).grid(row=5, column=0, columnspan=2, sticky="w")

        # Right: resultado e ações
        result = ttk.LabelFrame(content, text="Senha gerada", padding=(12,10))
        result.grid(row=0, column=1, sticky="nsew")
        result.columnconfigure(0, weight=1)

        # Entry com fonte monoespaçada e botão olho
        entry_frame = ttk.Frame(result)
        entry_frame.grid(row=0, column=0, sticky="we")
        self.password_entry = ttk.Entry(entry_frame, textvariable=self.password_var, font=("Consolas", 12), state="readonly")
        self.password_entry.pack(side="left", fill="x", expand=True)
        self.eye_btn = ttk.Button(entry_frame, text="👁️", width=3, command=self.toggle_show_password)
        self.eye_btn.pack(side="left", padx=(6,0))
        self.eye_btn.bind("<Return>", lambda e: self.toggle_show_password())

        # Barra de força e rótulos
        info_frame = ttk.Frame(result)
        info_frame.grid(row=1, column=0, sticky="we", pady=(10,0))
        self.progress = tb.Progressbar(info_frame, length=320, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True)
        self.entropy_label = ttk.Label(info_frame, textvariable=self.entropy_var, width=14, anchor="e")
        self.entropy_label.pack(side="right", padx=(8,0))

        self.strength_label = ttk.Label(result, textvariable=self.strength_text_var, foreground="#0b5", anchor="w")
        self.strength_label.grid(row=2, column=0, sticky="w", pady=(6,0))

        # Motivos de fraqueza
        self.reason_label = ttk.Label(result, text="", foreground="#b33", wraplength=360, anchor="w")
        self.reason_label.grid(row=3, column=0, sticky="we", pady=(6,0))

        # Botões de ação
        actions = ttk.Frame(result)
        actions.grid(row=4, column=0, sticky="e", pady=(12,0))
        self.generate_btn = tb.Button(actions, text="Gerar (Ctrl+G)", bootstyle="success", command=self.on_generate)
        self.generate_btn.pack(side="left", padx=(0,8))
        self.copy_btn = tb.Button(actions, text="Copiar (Ctrl+C)", bootstyle="secondary", command=self.on_copy)
        self.copy_btn.pack(side="left")
        self.copy_btn.bind("<Enter>", lambda e: self.status_set("Copiar senha para a área de transferência"))
        self.copy_btn.bind("<Leave>", lambda e: self.status_set(""))

        # Status bar
        self.status_var = tk.StringVar(value="")
        status = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        status.pack(fill="x", side="bottom")

        # Ajustes de grid para responsividade
        content.columnconfigure(0, weight=0)
        content.columnconfigure(1, weight=1)

        # Gera senha inicial com animação sutil
        self.animate_generate()

    # --- Acessibilidade e atalhos ---
    def bind_shortcuts(self):
        self.bind_all("<Control-g>", lambda e: self.on_generate())
        self.bind_all("<Control-G>", lambda e: self.on_generate())
        self.bind_all("<Control-c>", lambda e: self.on_copy())
        self.bind_all("<Control-C>", lambda e: self.on_copy())
        self.bind_all("<Control-s>", lambda e: self.toggle_theme())

    def initial_focus(self):
        self.length_spin.focus_set()

    def status_set(self, text, timeout=None):
        self.status_var.set(text)
        if timeout:
            self.after(timeout, lambda: self.status_var.set(""))

    # --- Tema ---
    def toggle_theme(self):
        # alterna entre light e dark
        if self.theme_mode.get() == "dark":
            self.style.theme_use("darkly")
        else:
            self.style.theme_use("flatly")

    # --- Interações ---
    def on_scale_move(self, val):
        v = int(float(val))
        self.length_var.set(v)

    def toggle_show_password(self):
        if self.show_password.get():
            # ocultar
            self.password_entry.configure(state="normal")
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, "•" * len(self.password_var.get()))
            self.password_entry.configure(state="readonly")
            self.show_password.set(False)
            self.eye_btn.config(text="👁️")
        else:
            # mostrar
            self.password_entry.configure(state="normal")
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, self.password_var.get())
            self.password_entry.configure(state="readonly")
            self.show_password.set(True)
            self.eye_btn.config(text="🙈")

    def on_generate(self):
        # animação sutil: botão muda de texto e volta
        old_text = self.generate_btn.cget("text")
        self.generate_btn.config(text="Gerando...")
        self.update_idletasks()
        self.after(120, self._do_generate)
        self.after(700, lambda: self.generate_btn.config(text=old_text))

    def animate_generate(self):
        # chamada inicial para gerar com efeito
        self.on_generate()

    def _do_generate(self):
        length = int(self.length_var.get())
        charset = build_charset(
            use_lower=self.lower_var.get(),
            use_upper=self.upper_var.get(),
            use_digits=self.digits_var.get(),
            use_symbols=self.symbols_var.get(),
            exclude_ambiguous=self.ambig_var.get()
        )
        if not charset:
            self.password_var.set("")
            self.strength_text_var.set("Escolha pelo menos um tipo de caractere.")
            self.entropy_var.set("")
            self.reason_label.config(text="Nenhum conjunto de caracteres selecionado.")
            self.update_progress(0, "danger")
            return

        pwd = generate_password(length, charset, require_each=self.require_each_var.get())
        self.password_var.set(pwd)
        # Exibir conforme estado show_password
        if self.show_password.get():
            self.password_entry.configure(state="normal")
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, pwd)
            self.password_entry.configure(state="readonly")
        else:
            self.password_entry.configure(state="normal")
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, "•" * len(pwd))
            self.password_entry.configure(state="readonly")

        # Entropia e força
        ent = estimate_entropy(length, len(set(charset)))
        self.entropy_var.set(f"{ent:.1f} bits")
        label = strength_label(ent)
        self.strength_text_var.set(f"{label}")
        self.update_progress(ent, strength_color(ent))

        # Motivos de fraqueza
        reasons = []
        if length < 8:
            reasons.append("Comprimento muito curto")
        if not self.lower_var.get() and not self.upper_var.get():
            reasons.append("Sem letras")
        if not self.digits_var.get():
            reasons.append("Sem dígitos")
        if not self.symbols_var.get():
            reasons.append("Sem símbolos")
        if self.require_each_var.get():
            # checar se a senha realmente contém cada tipo
            if self.lower_var.get() and not any(c.islower() for c in pwd):
                reasons.append("Não contém letra minúscula")
            if self.upper_var.get() and not any(c.isupper() for c in pwd):
                reasons.append("Não contém letra maiúscula")
            if self.digits_var.get() and not any(c.isdigit() for c in pwd):
                reasons.append("Não contém dígito")
            if self.symbols_var.get() and not any(c in SYMBOLS for c in pwd):
                reasons.append("Não contém símbolo")
        # Mensagem clara
        if reasons:
            self.reason_label.config(text="Motivos: " + "; ".join(reasons))
        else:
            self.reason_label.config(text="")

    def update_progress(self, entropy_bits, color_key):
        # normaliza entropia para 0..100 (assume 100 bits como máximo prático)
        val = min(max(entropy_bits / 100 * 100, 0), 100)
        # usa bootstyle para colorir
        style = f"{color_key}-striped"
        try:
            self.progress.configure(bootstyle=style)
        except Exception:
            pass
        self.progress['value'] = val

    def on_copy(self):
        pwd = self.password_var.get()
        if not pwd:
            self.status_set("Nada para copiar", 2000)
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(pwd)
            self.status_set("Senha copiada para a área de transferência", 3000)
            old = self.copy_btn.cget("text")
            self.copy_btn.config(text="Copiado!")
            self.after(1200, lambda: self.copy_btn.config(text=old))
            if self.auto_clear_clipboard_var.get():
                # limpar clipboard após X segundos
                self.after(CLIPBOARD_CLEAR_SECONDS * 1000, self.clear_clipboard_if_matches, pwd)
        except Exception:
            self.status_set("Falha ao copiar", 3000)

    def clear_clipboard_if_matches(self, value):
        try:
            current = self.clipboard_get()
            if current == value:
                self.clipboard_clear()
                self.status_set("Área de transferência limpa", 3000)
        except Exception:
            pass

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()