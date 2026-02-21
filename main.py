# main.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import estoque
import pedido
import relatorio
import db


def abrir_estoque():
    root.withdraw()
    estoque.janela_estoque(root)


def abrir_pedido():
    root.withdraw()
    pedido.janela_pedido(root)


def abrir_relatorio():
    root.withdraw()
    relatorio.janela_relatorio(root)


def realizar_backup():
    sucesso, msg = db.fazer_backup()
    if sucesso:
        messagebox.showinfo("Sucesso", f"Backup realizado com sucesso!\nArquivo: {msg}")
    else:
        messagebox.showerror("Erro", f"Falha no backup: {msg}")


# --- Paleta de Cores Kaibem ---
COR_FUNDO = "#FFFFFF"
COR_TEXTO_TITULO = "#4B2C82"
COR_TEXTO_SUB = "#6A4C93"
ROXO_FORTE = "#4B2C82"
ROXO_MEDIO = "#8467B3"
ROXO_CLARO = "#9D88C8"
ROXO_SUAVE = "#C5B9DE"

root = tk.Tk()
root.title("Sistema de Gestão - Sorveteria")
root.geometry("500x650")
root.configure(bg=COR_FUNDO)

#LOGO
try:
    img_logo = Image.open("logo.png")
    photo_logo = ImageTk.PhotoImage(img_logo)

    lbl_logo_img = tk.Label(root, image=photo_logo, bg=COR_FUNDO)
    lbl_logo_img.image = photo_logo
    lbl_logo_img.pack(pady=(30, 20))
except Exception as e:
    print(f"Erro ao carregar logo: {e}")

    #Fallback caso a imagem não exista
    tk.Label(root, text="KAIBEM", font=("Segoe UI Black", 32), bg=COR_FUNDO, fg=COR_TEXTO_TITULO).pack(pady=(40, 0))

# --- Títulos ---
tk.Label(
    root,
    text="SISTEMA DE GESTÃO",
    font=("Segoe UI", 20, "bold"),
    bg=COR_FUNDO,
    fg=COR_TEXTO_TITULO
).pack()

tk.Label(
    root,
    text="Selecione uma opção",
    font=("Segoe UI", 12),
    bg=COR_FUNDO,
    fg=COR_TEXTO_SUB
).pack(pady=(0, 30))


# --- Função para criar os botões no estilo da imagem ---
def criar_botao(texto, comando, cor_bg):
    return tk.Button(
        root,
        text=texto,
        command=comando,
        font=("Segoe UI", 13, "bold"),
        bg=cor_bg,
        fg="white",
        width=40,
        height=2,
        relief="flat",
        cursor="hand2",
        activebackground=COR_TEXTO_TITULO,
        activeforeground="white"
    )


# --- Lista de Botões ---
btn_pedido = criar_botao("Fazer Pedido", abrir_pedido, ROXO_FORTE)
btn_pedido.pack(pady=7)

btn_estoque = criar_botao("Gerenciar Estoque", abrir_estoque, ROXO_MEDIO)
btn_estoque.pack(pady=7)

btn_relatorio = criar_botao("Relatórios", abrir_relatorio, ROXO_CLARO)
btn_relatorio.pack(pady=7)

btn_backup = criar_botao("Fazer Backup (JSON)", realizar_backup, ROXO_SUAVE)
btn_backup.pack(pady=7)

# --- Rodapé ---
lbl_footer = tk.Label(
    root,
    text="KAIBEM © 2026",
    font=("Segoe UI", 9, "bold"),
    bg=COR_FUNDO,
    fg=COR_TEXTO_TITULO
)
lbl_footer.pack(side="bottom", pady=20)

# Linha colorida decorativa no fundo
canvas_linha = tk.Canvas(root, height=5, bg="#F37021", highlightthickness=0)
canvas_linha.pack(side="bottom", fill="x")

root.mainloop()