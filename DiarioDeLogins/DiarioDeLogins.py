import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

DB_NAME = "logins.db"
MASTER_PASSWORD = "1234"

# Paleta de cores
BG_COLOR = "#1e1e1e"
FG_COLOR = "#f1faee"
BTN_COLOR = "#e63946"
BTN_ALT_COLOR = "#457b9d"
ENTRY_COLOR = "#2a2a2a"

def configurar_janela(janela, titulo):
    janela.title(titulo)
    janela.configure(bg=BG_COLOR)

def criar_botao(master, texto, comando, cor=BTN_COLOR):
    return tk.Button(master, text=texto, command=comando,
                     bg=cor, fg=FG_COLOR, font=("Arial", 10, "bold"),
                     relief="flat", width=20, pady=5)

def criar_label(master, texto, tamanho=12, bold=False):
    estilo = ("Arial", tamanho, "bold") if bold else ("Arial", tamanho)
    return tk.Label(master, text=texto, bg=BG_COLOR, fg=FG_COLOR, font=estilo)

def criar_entry(master, largura=30, senha=False):
    return tk.Entry(master, width=largura, show="*" if senha else "",
                    bg=ENTRY_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR,
                    relief="flat", font=("Arial", 10))

def criar_listbox(master):
    return tk.Listbox(master, width=50, bg=ENTRY_COLOR, fg=FG_COLOR,
                      selectbackground=BTN_ALT_COLOR, relief="flat",
                      font=("Arial", 10))

# Banco de dados
def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pastas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)
    cursor.execute("PRAGMA table_info(logins)")
    colunas = [info[1] for info in cursor.fetchall()]
    if not colunas:
        cursor.execute("""
        CREATE TABLE logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            senha TEXT NOT NULL,
            pasta_id INTEGER,
            FOREIGN KEY (pasta_id) REFERENCES pastas(id)
        )
        """)
    elif "pasta_id" not in colunas:
        cursor.execute("ALTER TABLE logins ADD COLUMN pasta_id INTEGER")
    conn.commit()
    return conn, cursor

conn, cursor = inicializar_banco()

# Funções simples para exemplo
def atualizar_pastas():
    cursor.execute("SELECT nome FROM pastas")
    pastas = [row[0] for row in cursor.fetchall()]
    combo_pasta['values'] = pastas

def listar_pastas():
    lista.delete(0, tk.END)
    cursor.execute("SELECT nome FROM pastas")
    registros = cursor.fetchall()
    if registros:
        for i, (nome,) in enumerate(registros, start=1):
            lista.insert(tk.END, f"Pasta {i}: {nome}")
    else:
        lista.insert(tk.END, "Nenhuma pasta criada.")

def voltar_para_pastas():
    combo_pasta.set("")
    listar_pastas()

def toggle_senha():
    if entry_senha.cget("show") == "":
        entry_senha.config(show="*")
        btn_toggle.config(text="👁️")
    else:
        entry_senha.config(show="")
        btn_toggle.config(text="🙈")

# Tela principal com scrollbar
def abrir_programa():
    login_window.destroy()
    global entry_pasta, combo_pasta, entry_email, entry_senha, btn_toggle, lista

    root = tk.Tk()
    configurar_janela(root, "🔐 Diário de Senhas")

    # Canvas + Scrollbar
    canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=BG_COLOR)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Conteúdo dentro do scroll_frame
    criar_label(scroll_frame, "🔐 Diário de Senhas", tamanho=16, bold=True).pack(pady=10)

    criar_label(scroll_frame, "Nova Pasta:", tamanho=12).pack()
    entry_pasta = criar_entry(scroll_frame)
    entry_pasta.pack(pady=5)
    criar_botao(scroll_frame, "Criar Pasta", lambda: None).pack(pady=5)

    criar_label(scroll_frame, "Escolha a Pasta:", tamanho=12).pack()
    combo_pasta = ttk.Combobox(scroll_frame, width=30, state="readonly")
    combo_pasta.pack(pady=5)
    atualizar_pastas()

    criar_label(scroll_frame, "Email:", tamanho=12).pack()
    entry_email = criar_entry(scroll_frame)
    entry_email.pack(pady=5)

    criar_label(scroll_frame, "Senha:", tamanho=12).pack()
    frame_senha = tk.Frame(scroll_frame, bg=BG_COLOR)
    frame_senha.pack()
    entry_senha = criar_entry(frame_senha, senha=True)
    entry_senha.pack(side=tk.LEFT, padx=5)
    btn_toggle = criar_botao(frame_senha, "👁️", toggle_senha, cor=BTN_ALT_COLOR)
    btn_toggle.pack(side=tk.LEFT)

    criar_botao(scroll_frame, "Salvar Login", lambda: None).pack(pady=5)
    criar_botao(scroll_frame, "Listar Logins", lambda: None, cor=BTN_ALT_COLOR).pack(pady=5)
    criar_botao(scroll_frame, "Listar Pastas", listar_pastas).pack(pady=5)
    criar_botao(scroll_frame, "Excluir Selecionado", lambda: None).pack(pady=5)
    criar_botao(scroll_frame, "Voltar", voltar_para_pastas, cor=BTN_ALT_COLOR).pack(pady=5)

    lista = criar_listbox(scroll_frame)
    lista.pack(pady=10)

    root.mainloop()

# Tela de login inicial
def verificar_login():
    senha = entry_master.get()
    if senha == MASTER_PASSWORD:
        abrir_programa()
    else:
        messagebox.showerror("Erro", "Senha incorreta!")

login_window = tk.Tk()
configurar_janela(login_window, "Login - Diário de Senhas")

criar_label(login_window, "Digite a senha para acessar:", tamanho=12, bold=True).pack(pady=10)
entry_master = criar_entry(login_window, senha=True)
entry_master.pack(pady=5)
criar_botao(login_window, "Entrar", verificar_login).pack(pady=10)

login_window.mainloop()