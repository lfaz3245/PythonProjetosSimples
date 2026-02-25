import tkinter as tk
from tkinter import messagebox, filedialog
import schedule
import time
import threading
import json
import os
import datetime

MAX_TASKS = 15
tasks = []
running = False
history = []

SAVE_FILE = "tarefas.json"

# Função para mostrar notificação em posição escolhida
def mostrar_notificacao(titulo, mensagem):
    notif = tk.Toplevel()
    notif.title("")
    notif.overrideredirect(True)

    largura_tela = notif.winfo_screenwidth()
    altura_tela = notif.winfo_screenheight()

    largura = 320
    altura = 120

    posicao = posicao_var.get()
    if posicao == "Inferior Direito":
        x = largura_tela - largura - 15
        y = altura_tela - altura - 60
    elif posicao == "Superior Direito":
        x = largura_tela - largura - 15
        y = 15
    else:
        x = largura_tela - largura - 15
        y = altura_tela - altura - 60

    notif.geometry(f"{largura}x{altura}+{x}+{y}")

    frame = tk.Frame(notif, bg="#fef9e7", bd=2, relief="solid")
    frame.pack(expand=True, fill="both")

    tk.Label(frame, text=titulo, font=("Segoe UI", 12, "bold"), bg="#fef9e7", fg="#2c3e50").pack(pady=(10,0))
    tk.Label(frame, text=mensagem, font=("Segoe UI", 10), bg="#fef9e7", fg="#34495e").pack(pady=(5,10))

    notif.after(7000, notif.destroy)

    # Adiciona ao histórico
    history.append(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {titulo}: {mensagem}")
    update_history()

def enviar_notificacao(titulo, mensagem):
    threading.Thread(target=lambda: mostrar_notificacao(titulo, mensagem)).start()

def run_scheduler():
    while running:
        schedule.run_pending()
        time.sleep(1)

def update_task_list():
    listbox.delete(0, tk.END)
    for i, task in enumerate(tasks, start=1):
        nome = task["nome"].get() if task["nome"].get() else f"Tarefa {i}"
        msg = task["msg"].get()
        time_str = task["time"].get()
        repeat_str = task["repeat"].get()
        if msg:
            if time_str:
                listbox.insert(tk.END, f"{nome}: '{msg}' às {time_str}")
            elif repeat_str.isdigit():
                listbox.insert(tk.END, f"{nome}: '{msg}' a cada {repeat_str} min")

def update_history():
    history_list.delete(0, tk.END)
    for item in history[-20:]:
        history_list.insert(tk.END, item)

def start_bot():
    global running
    running = True
    schedule.clear()

    for i, task in enumerate(tasks, start=1):
        nome = task["nome"].get() if task["nome"].get() else f"Tarefa {i}"
        msg = task["msg"].get()
        time_str = task["time"].get()
        repeat_str = task["repeat"].get()

        if msg:
            if time_str:
                try:
                    datetime.datetime.strptime(time_str, "%H:%M")
                    schedule.every().day.at(time_str).do(
                        lambda m=msg, n=nome: enviar_notificacao(n, m)
                    )
                except Exception:
                    messagebox.showerror("Erro", f"{nome}: horário inválido (use HH:MM).")
            elif repeat_str.isdigit():
                schedule.every(int(repeat_str)).minutes.do(
                    lambda m=msg, n=nome: enviar_notificacao(n, m)
                )

    if not schedule.jobs:
        messagebox.showwarning("Aviso", "Por favor, defina uma tarefa e horário.")
        running = False
        return

    update_task_list()
    threading.Thread(target=run_scheduler, daemon=True).start()
    status_var.set("Ativo")
    messagebox.showinfo("Bot", "Automatização iniciada!")

def stop_bot():
    global running
    running = False
    schedule.clear()
    listbox.delete(0, tk.END)
    status_var.set("Desligado")
    messagebox.showinfo("Bot", "Automatização desligada!")

def add_task():
    if len(tasks) >= MAX_TASKS:
        messagebox.showwarning("Aviso", f"Limite máximo de {MAX_TASKS} tarefas atingido.")
        return

    frame = tk.Frame(task_frame, bd=2, relief="groove", bg="#ecf0f1")
    frame.pack(pady=5, fill="x")

    tk.Label(frame, text=f"Nome da Tarefa {len(tasks)+1} (opcional):", bg="#ecf0f1", fg="#2c3e50").pack()
    entry_nome = tk.Entry(frame, width=40)
    entry_nome.pack()

    tk.Label(frame, text="Mensagem da Tarefa:", bg="#ecf0f1", fg="#2c3e50").pack()
    entry_msg = tk.Entry(frame, width=40)
    entry_msg.pack()

    tk.Label(frame, text="Horário (HH:MM) ou deixe vazio:", bg="#ecf0f1", fg="#2c3e50").pack()
    entry_time = tk.Entry(frame, width=10)
    entry_time.pack()

    tk.Label(frame, text="Repetir a cada X minutos (opcional):", bg="#ecf0f1", fg="#2c3e50").pack()
    entry_repeat = tk.Entry(frame, width=10)
    entry_repeat.pack()

    tasks.append({"frame": frame, "nome": entry_nome, "msg": entry_msg, "time": entry_time, "repeat": entry_repeat})

def remove_task():
    if tasks:
        task = tasks.pop()
        task["frame"].destroy()
        update_task_list()
    else:
        messagebox.showwarning("Aviso", "Nenhuma tarefa para remover.")

# Interface gráfica
root = tk.Tk()
root.title("Bot de Notificações")
root.configure(bg="#f4f6f7")
root.geometry("400x400")

# Container principal com scrollbar
main_container = tk.Frame(root, bg="#f4f6f7")
main_container.pack(fill="both", expand=True)

canvas_main = tk.Canvas(main_container, bg="#f4f6f7", highlightthickness=0)
scrollbar_main = tk.Scrollbar(main_container, orient="vertical", command=canvas_main.yview)
canvas_main.configure(yscrollcommand=scrollbar_main.set)

scrollbar_main.pack(side="right", fill="y")
canvas_main.pack(side="left", fill="both", expand=True)

# Frame interno que conterá todo o conteúdo
content_frame = tk.Frame(canvas_main, bg="#f4f6f7")
canvas_main.create_window((0, 0), window=content_frame, anchor="nw")

def on_content_configure(event):
    canvas_main.configure(scrollregion=canvas_main.bbox("all"))

content_frame.bind("<Configure>", on_content_configure)

# Cabeçalho
header = tk.Label(content_frame, text="🔔 Bot de Notificações", font=("Segoe UI", 16, "bold"), bg="#f4f6f7", fg="#2c3e50")
header.pack(pady=10)

# Configurações
config_frame = tk.Frame(content_frame, bg="#f4f6f7")
config_frame.pack(pady=10)

tk.Label(config_frame, text="Posição da Notificação:", bg="#f4f6f7", fg="#2c3e50").pack()
posicao_var = tk.StringVar(value="Inferior Direito")
posicao_menu = tk.OptionMenu(config_frame, posicao_var, "Inferior Direito", "Superior Direito")
posicao_menu.pack(pady=5)

# Área de tarefas
task_frame = tk.Frame(content_frame, bg="#f4f6f7")
task_frame.pack(pady=10, fill="both", expand=True)

btn_add = tk.Button(content_frame, text="+ Adicionar Tarefa", command=add_task, bg="#3498db", fg="white", font=("Segoe UI", 10, "bold"))
btn_add.pack(pady=5)

btn_remove = tk.Button(content_frame, text="- Remover Tarefa", command=remove_task, bg="#e67e22", fg="white", font=("Segoe UI", 10, "bold"))
btn_remove.pack(pady=5)

# Lista de tarefas com scrollbar
tk.Label(content_frame, text="Tarefas Ativas:", bg="#f4f6f7", fg="#2c3e50").pack()

list_frame = tk.Frame(content_frame)
list_frame.pack(pady=5)

scrollbar_list = tk.Scrollbar(list_frame, orient="vertical")
listbox = tk.Listbox(list_frame, width=60, height=10, font=("Segoe UI", 9), yscrollcommand=scrollbar_list.set)

scrollbar_list.config(command=listbox.yview)
scrollbar_list.pack(side="right", fill="y")
listbox.pack(side="left", fill="both", expand=True)

btn_update = tk.Button(content_frame, text="Atualizar Lista", command=update_task_list,
                       bg="#8e44ad", fg="white", font=("Segoe UI", 10, "bold"))
btn_update.pack(pady=5)

# Histórico
history_frame = tk.Frame(content_frame, bg="#f4f6f7")
history_frame.pack(pady=10)
tk.Label(history_frame, text="Histórico de Notificações:", bg="#f4f6f7", fg="#2c3e50").pack()
history_list = tk.Listbox(history_frame, width=60, height=10, font=("Segoe UI", 9))
history_list.pack(pady=5)

# Status
status_var = tk.StringVar(value="Desligado")
status_label = tk.Label(content_frame, textvariable=status_var, bg="#f4f6f7",
                        fg="#2c3e50", font=("Segoe UI", 10, "bold"))
status_label.pack(pady=5)

# Controle
control_frame = tk.Frame(content_frame, bg="#f4f6f7")
control_frame.pack(pady=10)

btn_start = tk.Button(control_frame, text="▶ Ligar Bot", command=start_bot,
                      bg="#27ae60", fg="white", font=("Segoe UI", 11, "bold"))
btn_start.pack(side="left", padx=10)

btn_stop = tk.Button(control_frame, text="■ Desligar Bot", command=stop_bot,
                     bg="#c0392b", fg="white", font=("Segoe UI", 11, "bold"))
btn_stop.pack(side="left", padx=10)

# Inicialmente adiciona 1 tarefa
add_task()

root.mainloop()