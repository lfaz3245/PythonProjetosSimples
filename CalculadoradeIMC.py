import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import winreg

resultados = []

# Detectar tema automático (Windows)
def detectar_tema():
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(reg, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return "flatly" if value == 1 else "darkly"
    except Exception:
        return "flatly"

# Função para mudar tema manualmente
def mudar_tema():
    tema = combo_tema.get()
    if tema == "Claro":
        app.style.theme_use("flatly")
    else:
        app.style.theme_use("darkly")

# Função principal de cálculo
def calcular_imc():
    for campo in [entry_nome, entry_idade, entry_peso, entry_altura]:
        campo.config(bootstyle="")

    nome = entry_nome.get().strip()
    idade = entry_idade.get().strip()
    peso = entry_peso.get().strip()
    altura = entry_altura.get().strip()

    campos_vazios = []
    if not nome: campos_vazios.append(entry_nome)
    if not idade: campos_vazios.append(entry_idade)
    if not peso: campos_vazios.append(entry_peso)
    if not altura: campos_vazios.append(entry_altura)

    if campos_vazios:
        for campo in campos_vazios:
            campo.config(bootstyle="danger")
        label_resultado.config(text="Por favor, preencha todos os campos!", bootstyle="danger")
        return

    try:
        idade = int(idade)
        peso = float(peso)
        altura = float(altura)
        imc = peso / (altura ** 2)

        if imc < 18.5:
            mensagem = "Abaixo do peso (negativo)"
            estilo = "warning"
            progresso = 25
        elif 18.5 <= imc < 24.9:
            mensagem = "Peso normal (positivo)"
            estilo = "success"
            progresso = 50
        elif 25 <= imc < 29.9:
            mensagem = "Sobrepeso (negativo)"
            estilo = "warning"
            progresso = 75
        else:
            mensagem = "Obesidade (negativo)"
            estilo = "danger"
            progresso = 100

        resultado_texto = f"{nome}, {idade} anos\nIMC: {imc:.2f} - {mensagem}"
        label_resultado.config(text=resultado_texto, bootstyle=estilo)

        barra_progresso['value'] = progresso
        barra_progresso.config(bootstyle=estilo)

        if len(resultados) < 5:
            resultados.append((nome, idade, peso, f"{imc:.2f}", mensagem))
            atualizar_tabela()
        else:
            label_resultado.config(text="Limite de 5 resultados atingido! Limpe a tabela para continuar.", bootstyle="danger")

    except ValueError:
        label_resultado.config(text="Erro: insira valores numéricos válidos!", bootstyle="danger")

def atualizar_tabela():
    for item in tabela.get_children():
        tabela.delete(item)
    for i, (nome, idade, peso, imc, mensagem) in enumerate(resultados, start=1):
        tag = "oddrow" if i % 2 else "evenrow"
        tabela.insert("", "end", values=(nome, idade, peso, imc, mensagem), tags=(tag,))

def limpar_tabela():
    resultados.clear()
    atualizar_tabela()
    label_resultado.config(text="Resultados limpos!", bootstyle="secondary")

def novo_calculo():
    entry_nome.delete(0, tk.END)
    entry_idade.delete(0, tk.END)
    entry_peso.delete(0, tk.END)
    entry_altura.delete(0, tk.END)
    label_resultado.config(text="", bootstyle="")
    barra_progresso['value'] = 0

def exportar_csv():
    if resultados:
        with open("resultados_imc.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Nome", "Idade", "Peso", "IMC", "Mensagem"])
            writer.writerows(resultados)
        label_resultado.config(text="Resultados exportados para resultados_imc.csv", bootstyle="success")
    else:
        label_resultado.config(text="Nenhum resultado para exportar!", bootstyle="danger")

def mostrar_grafico():
    if not resultados:
        label_resultado.config(text="Nenhum resultado para gerar gráfico!", bootstyle="danger")
        return

    categorias = ["Abaixo do peso", "Normal", "Sobrepeso", "Obesidade"]
    contagem = [0, 0, 0, 0]

    for _, _, _, _, msg in resultados:
        if "Abaixo" in msg: contagem[0] += 1
        elif "normal" in msg: contagem[1] += 1
        elif "Sobrepeso" in msg: contagem[2] += 1
        else: contagem[3] += 1

    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(categorias, contagem, color=["orange","green","yellow","red"])
    ax.set_title("Distribuição dos Resultados IMC")

    grafico_frame = ttk.Frame(frame_main)
    grafico_frame.grid(row=12, column=0, columnspan=3, pady=10)
    canvas = FigureCanvasTkAgg(fig, master=grafico_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Tooltip simples
def criar_tooltip(widget, texto):
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
        label = tk.Label(tooltip, text=texto, background="yellow", relief="solid", borderwidth=1)
        label.pack()
        widget.tooltip = tooltip
    def on_leave(event):
        if hasattr(widget, "tooltip"):
            widget.tooltip.destroy()
            widget.tooltip = None
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


# Janela principal
app = ttk.Window(themename=detectar_tema())
app.title("🏥 Calculadora de IMC")

largura, altura = 1055, 840
pos_x = app.winfo_screenwidth()//2 - largura//2
pos_y = app.winfo_screenheight()//2 - altura//2
app.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

# Configurar expansão da janela
app.rowconfigure(0, weight=1)
app.columnconfigure(0, weight=1)


# Definir ícone da janela (coloque um arquivo .ico na pasta do projeto)
try:
    app.iconbitmap("icone_imc.ico")
except Exception:
    pass  # se não encontrar o ícone, ignora

# Fonte padrão
fonte_padrao = ("Helvetica", 12)

# Frame principal sem fundo pesado
frame_main = ttk.Frame(app, padding=5)  # padding reduzido
frame_main.pack(fill="both", expand=True)

# Título estilizado avançado
label_titulo = ttk.Label(
    frame_main,
    text="🏥 Calculadora de IMC",
    font=("Helvetica", 28, "bold"),
    bootstyle="primary"
)
label_titulo.pack(pady=(10,5))

# Linha decorativa abaixo do título
linha = ttk.Separator(frame_main, orient="horizontal")
linha.pack(fill="x", padx=30, pady=(0,15))

# Animação suave no título (pulsar entre estilos)
def animar_titulo():
    atual = getattr(animar_titulo, "estado", True)
    if atual:
        label_titulo.config(bootstyle="info")   # azul claro
    else:
        label_titulo.config(bootstyle="primary") # azul escuro
    animar_titulo.estado = not atual
    app.after(1000, animar_titulo)

animar_titulo()


# Criar Canvas com Scrollbar
main_canvas = tk.Canvas(app)
scrollbar = ttk.Scrollbar(app, orient="vertical", command=main_canvas.yview)
scrollbar.pack(side="right", fill="y")
main_canvas.pack(side="left", fill="both", expand=True)

main_canvas.configure(yscrollcommand=scrollbar.set)
main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

# Frame dentro do Canvas
frame_main = ttk.Frame(main_canvas, padding=20)
main_canvas.create_window((0,0), window=frame_main, anchor="nw")

# Campos com tooltips
ttk.Label(frame_main, text="Nome:", font=fonte_padrao).grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_nome = ttk.Entry(frame_main, width=25)
entry_nome.grid(row=0, column=1, padx=10, pady=5)
criar_tooltip(entry_nome, "Digite seu nome completo")

ttk.Label(frame_main, text="Idade:", font=fonte_padrao).grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_idade = ttk.Entry(frame_main, width=10)
entry_idade.grid(row=1, column=1, padx=10, pady=5)
criar_tooltip(entry_idade, "Digite sua idade em anos")

ttk.Label(frame_main, text="Peso (kg):", font=fonte_padrao).grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_peso = ttk.Entry(frame_main, width=10)
entry_peso.grid(row=2, column=1, padx=10, pady=5)
criar_tooltip(entry_peso, "Digite seu peso em quilogramas, ex: 70")

ttk.Label(frame_main, text="Altura (m):", font=fonte_padrao).grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_altura = ttk.Entry(frame_main, width=10)
entry_altura.grid(row=3, column=1, padx=10, pady=5)
criar_tooltip(entry_altura, "Digite sua altura em metros, ex: 1.75")

# Tema manual
ttk.Label(frame_main, text="Tema:", font=fonte_padrao).grid(row=4, column=0, padx=10, pady=5, sticky="w")
combo_tema = ttk.Combobox(frame_main, values=["Claro", "Escuro"], state="readonly")
combo_tema.current(0)
combo_tema.grid(row=4, column=1, padx=10, pady=5)
btn_tema = ttk.Button(frame_main, text="Aplicar Tema", bootstyle=SECONDARY, command=mudar_tema)
btn_tema.grid(row=4, column=2, padx=10, pady=5)

# Botão calcular
btn_calcular = ttk.Button(frame_main, text="Calcular IMC", bootstyle=PRIMARY, command=calcular_imc)
btn_calcular.grid(row=5, column=0, columnspan=3, pady=15)

# Função de animação para o botão
def animar_botao():
    # alterna entre estilos para criar efeito de pulsar
    atual = getattr(animar_botao, "estado", True)
    if atual:
        btn_calcular.config(bootstyle="success")   # verde
    else:
        btn_calcular.config(bootstyle="primary")   # azul padrão
    animar_botao.estado = not atual
    # chama novamente após 600ms
    app.after(600, animar_botao)

# Iniciar animação
animar_botao()

# Botão novo cálculo
btn_novo = ttk.Button(frame_main, text="Novo Cálculo", bootstyle=INFO, command=novo_calculo)
btn_novo.grid(row=6, column=0, columnspan=3, pady=5)

# Caixa de resultado
frame_resultado = ttk.Frame(frame_main, padding=15, bootstyle="secondary")
frame_resultado.grid(row=7, column=0, columnspan=3, pady=10, sticky="ew")

label_resultado = ttk.Label(frame_resultado, text="", font=("Helvetica", 14), anchor=CENTER)
label_resultado.pack(fill=X)

# Barra de progresso IMC
barra_progresso = ttk.Progressbar(frame_resultado, orient="horizontal", mode="determinate", length=400)
barra_progresso.pack(pady=10)

# Tabela de resultados
tabela = ttk.Treeview(frame_main, columns=("Nome", "Idade", "Peso", "IMC", "Mensagem"), show="headings", height=5)
tabela.grid(row=8, column=0, columnspan=3, pady=10, sticky="ew")

tabela.heading("Nome", text="Nome")
tabela.heading("Idade", text="Idade")
tabela.heading("Peso", text="Peso (kg)")
tabela.heading("IMC", text="IMC")
tabela.heading("Mensagem", text="Mensagem")

tabela.tag_configure("oddrow", background="#f0f0f0")
tabela.tag_configure("evenrow", background="#ffffff")

# Botões extras
btn_limpar = ttk.Button(frame_main, text="Limpar Resultados", bootstyle=DANGER, command=limpar_tabela)
btn_limpar.grid(row=9, column=0, columnspan=3, pady=5)

btn_exportar = ttk.Button(frame_main, text="Exportar CSV", bootstyle=SUCCESS, command=exportar_csv)
btn_exportar.grid(row=10, column=0, columnspan=3, pady=5)

btn_grafico = ttk.Button(frame_main, text="Mostrar Gráfico", bootstyle=INFO, command=mostrar_grafico)
btn_grafico.grid(row=11, column=0, columnspan=3, pady=5)

app.mainloop()