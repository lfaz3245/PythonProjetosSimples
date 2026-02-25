import tkinter as tk
from tkinter import messagebox, font, ttk
from datetime import datetime

class MuralDeNotas:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Mural de Notas 🚀")
        self.root.geometry("1100x500")

        # Temas
        self.tema_claro = {
            "bg":"#fdfdfd", "fg":"#222",
            "btn_add":"#00b894", "btn_remove":"#d63031",
            "list_bg":"#ffffff", "list_fg":"#2d3436",
            "notif_bg":"#55efc4", "notif_fg":"#222"
        }
        self.tema_escuro = {
            "bg":"#1e272e", "fg":"#f5f6fa",
            "btn_add":"#0984e3", "btn_remove":"#e17055",
            "list_bg":"#2f3640", "list_fg":"#f5f6fa",
            "notif_bg":"#74b9ff", "notif_fg":"#f5f6fa"
        }
        self.tema_atual = self.tema_claro
        self.root.configure(bg=self.tema_atual["bg"])

        # Fonte título
        titulo_font = font.Font(family="Helvetica", size=22, weight="bold")

        # Frame superior
        frame_top = tk.Frame(root, bg=self.tema_atual["bg"])
        frame_top.pack(fill="x", pady=10)

        titulo = tk.Label(frame_top, text="📌 Mural de Notas", font=titulo_font,
                          bg=self.tema_atual["bg"], fg=self.tema_atual["fg"])
        titulo.pack(side="left", padx=20)

        self.btn_tema = tk.Button(frame_top, text="🌙", font=("Arial", 14),
                                  command=self.alternar_tema, relief="flat",
                                  bg=self.tema_atual["bg"], fg=self.tema_atual["fg"])
        self.btn_tema.pack(side="right", padx=20)

        # Campos de entrada
        self.entry_titulo = tk.Entry(root, width=50, font=("Arial", 13), fg="#636e72")
        self.entry_titulo.insert(0, "Título da nota...")
        self.entry_titulo.pack(pady=5)

        self.entry_conteudo = tk.Entry(root, width=50, font=("Arial", 13), fg="#636e72")
        self.entry_conteudo.insert(0, "Digite sua nota aqui...")
        self.entry_conteudo.pack(pady=5)

        # Categorias
        categorias = ["Trabalho", "Pessoal", "Estudos"]
        self.categoria_var = tk.StringVar(value=categorias[0])
        self.combo_categoria = ttk.Combobox(root, textvariable=self.categoria_var, values=categorias, state="readonly", font=("Arial", 12))
        self.combo_categoria.pack(pady=5)

        # Botões
        self.btn_add = tk.Button(root, text="➕ Adicionar Nota", width=25,
                                 bg=self.tema_atual["btn_add"], fg="white",
                                 font=("Arial", 12, "bold"), relief="flat",
                                 command=self.adicionar_nota)
        self.btn_add.pack(pady=5)

        self.btn_remove = tk.Button(root, text="🗑️ Remover Nota", width=25,
                                    bg=self.tema_atual["btn_remove"], fg="white",
                                    font=("Arial", 12, "bold"), relief="flat",
                                    command=self.remover_nota)
        self.btn_remove.pack(pady=5)

        # Frame principal dividido
        frame_main = tk.Frame(root, bg=self.tema_atual["bg"])
        frame_main.pack(fill="both", expand=True)

        # Mural de notas
        frame_lista = tk.Frame(frame_main, bg=self.tema_atual["bg"])
        frame_lista.pack(side="left", pady=10, fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(frame_lista, width=80, height=15, font=("Arial", 12),
                                  yscrollcommand=scrollbar.set,
                                  bg=self.tema_atual["list_bg"], fg=self.tema_atual["list_fg"],
                                  selectbackground="#74b9ff", selectforeground="white")
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Histórico lateral
        frame_log = tk.Frame(frame_main, bg=self.tema_atual["bg"], bd=2, relief="groove")
        frame_log.pack(side="right", fill="y", padx=10, pady=10)

        lbl_log = tk.Label(frame_log, text="📜 Histórico de Notificações", font=("Arial", 12, "bold"),
                           bg=self.tema_atual["bg"], fg=self.tema_atual["fg"])
        lbl_log.pack(pady=5)

        self.logbox = tk.Listbox(frame_log, width=40, height=20, font=("Arial", 11),
                                 bg=self.tema_atual["list_bg"], fg=self.tema_atual["list_fg"])
        self.logbox.pack(fill="y", expand=True)

        # Lista de notas
        self.notas = []

    def adicionar_nota(self):
        titulo = self.entry_titulo.get().strip()
        conteudo = self.entry_conteudo.get().strip()
        categoria = self.categoria_var.get()
        if titulo and conteudo:
            data_criacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            numero = len(self.notas) + 1
            nota_formatada = f"{numero}. [{categoria}] {titulo} - {conteudo} (Criada em {data_criacao})"
            self.notas.append(nota_formatada)
            self.listbox.insert(tk.END, nota_formatada)
            self.entry_titulo.delete(0, tk.END)
            self.entry_conteudo.delete(0, tk.END)
            self.mostrar_notificacao("Nota criada com sucesso")
            self.logbox.insert(tk.END, f"[{data_criacao}] Nota criada: {titulo} ({categoria})")
        else:
            messagebox.showwarning("Aviso", "Digite título e conteúdo da nota!")

    def remover_nota(self):
        selecionada = self.listbox.curselection()
        if selecionada:
            index = selecionada[0]
            titulo_removido = self.notas[index]
            self.listbox.delete(index)
            del self.notas[index]
            # Atualizar numeração
            self.listbox.delete(0, tk.END)
            for i, nota in enumerate(self.notas, start=1):
                partes = nota.split(". ", 1)[1]
                self.notas[i-1] = f"{i}. {partes}"
                self.listbox.insert(tk.END, self.notas[i-1])
            self.mostrar_notificacao("Nota removida com sucesso")
            data_remocao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.logbox.insert(tk.END, f"[{data_remocao}] Nota removida: {titulo_removido}")
        else:
            messagebox.showwarning("Aviso", "Selecione uma nota para remover!")

    def mostrar_notificacao(self, mensagem="Notificação"):
        notif = tk.Frame(self.root, bg=self.tema_atual["notif_bg"], bd=2, relief="ridge")
        notif.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

        lbl = tk.Label(notif, text=mensagem, bg=self.tema_atual["notif_bg"],
                       fg=self.tema_atual["notif_fg"], font=("Arial", 11, "bold"))
        lbl.pack(side="left", padx=10, pady=5)

        btn_close = tk.Button(notif, text="✖", bg=self.tema_atual["notif_bg"],
                              fg=self.tema_atual["notif_fg"], relief="flat",
                              command=notif.destroy)
        btn_close.pack(side="right", padx=5)

        notif.after(7000, notif.destroy)

    def alternar_tema(self):
        self.tema_atual = self.tema_escuro if self.tema_atual == self.tema_claro else self.tema_claro
        self.root.configure(bg=self.tema_atual["bg"])
        self.btn_tema.config(text="☀️" if self.tema_atual == self.tema_escuro else "🌙",
                             bg=self.tema_atual["bg"], fg=self.tema_atual["fg"])
        # Atualizar cores dos botões e listas
        self.btn_add.config(bg=self.tema_atual["btn_add"])
        self.btn_remove.config(bg=self.tema_atual["btn_remove"])
        self.listbox.config(bg=self.tema_atual["list_bg"], fg=self.tema_atual["list_fg"])
        self.logbox.config(bg=self.tema_atual["list_bg"], fg=self.tema_atual["list_fg"])

# Executar aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = MuralDeNotas(root)
    root.mainloop()
