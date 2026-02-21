import tkinter as tk
from tkinter import ttk, messagebox
import db

# --- Configurações de Design Kaibem ---
COR_FUNDO = "#FFFFFF"
COR_TEXTO_TITULO = "#4B2C82"
COR_TEXTO_SUB = "#6A4C93"
ROXO_MEDIO = "#8467B3"
ROXO_SUAVE = "#C5B9DE"
VERDE_KAIBEM = "#2ECC71"
VERMELHO_EXCLUIR = "#FF7675"
AZUL_EDITAR = "#74B9FF"

CATEGORIAS = ["Sorvete", "Açaí", "Caldo", "Pote"]


def janela_estoque(janela_pai):
    top = tk.Toplevel()
    top.title("Gerenciamento de Estoque - Kaibem")
    top.geometry("900x700")
    top.configure(bg=COR_FUNDO)


    #Frame de scroll estilizado
    container = tk.Frame(top, bg=COR_FUNDO)
    container.pack(fill="both", expand=True, padx=20, pady=10)

    canvas = tk.Canvas(container, bg=COR_FUNDO, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=COR_FUNDO)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=840)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def carregar_estoque():
        #Limpa o frame atual
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        conn = db.get_connection()
        cursor = conn.cursor()

        for cat in CATEGORIAS:
            #Frame para a Categoria (Estilo Card)
            frame_cat = tk.LabelFrame(
                scrollable_frame, text=f"  {cat.upper()}  ",
                font=("Segoe UI", 12, "bold"),
                bg=COR_FUNDO, fg=COR_TEXTO_TITULO,
                padx=15, pady=15, relief="solid", bd=1
            )
            frame_cat.pack(fill="x", padx=15, pady=15)

            #Buscar produtos dessa categoria
            cursor.execute("SELECT id, nome, quantidade, preco FROM produtos WHERE categoria = ?", (cat,))
            produtos = cursor.fetchall()

            if not produtos:
                tk.Label(frame_cat, text="Nenhum item nesta categoria.", bg=COR_FUNDO, fg="gray",
                         font=("Segoe UI", 10, "italic")).pack(pady=10)

            for prod in produtos:
                frame_item = tk.Frame(frame_cat, bg=COR_FUNDO)
                frame_item.pack(fill="x", pady=5)

                #Info do Produto
                info_p = f"• {prod['nome']}"
                tk.Label(frame_item, text=info_p, font=("Segoe UI", 11), bg=COR_FUNDO, fg="#2D3436", width=35,
                         anchor="w").pack(side="left")

                #Valores
                detalhes = f"Qtd: {prod['quantidade']} | R$ {prod['preco']:.2f}"
                tk.Label(frame_item, text=detalhes, font=("Segoe UI", 10, "bold"), bg=COR_FUNDO, fg=ROXO_MEDIO,
                         width=25, anchor="w").pack(side="left")

                #Botões de Ação
                btn_base = {"relief": "flat", "font": ("Segoe UI", 9, "bold"), "fg": "white", "cursor": "hand2"}

                tk.Button(frame_item, text="EDITAR", bg=AZUL_EDITAR,
                          command=lambda p=prod: editar_produto(p, carregar_estoque), **btn_base).pack(side="left",
                                                                                                       padx=5)

                tk.Button(frame_item, text="EXCLUIR", bg=VERMELHO_EXCLUIR,
                          command=lambda p=prod: excluir_produto(p, carregar_estoque), **btn_base).pack(side="left",
                                                                                                        padx=5)

            #Botão Adicionar Item na Categoria
            tk.Button(
                frame_cat, text="+ ADICIONAR ITEM",
                font=("Segoe UI", 9, "bold"), bg=ROXO_SUAVE, fg=COR_TEXTO_TITULO,
                relief="flat", cursor="hand2",
                command=lambda c=cat: adicionar_produto(c, carregar_estoque)
            ).pack(pady=(15, 0), anchor="e")

        conn.close()

    # --- Funções de Operação ---

    def adicionar_produto(categoria, callback):
        top_add = tk.Toplevel()
        top_add.title(f"Novo em {categoria}")
        top_add.geometry("350x450")
        top_add.configure(bg=COR_FUNDO)
        top_add.grab_set()

        tk.Label(top_add, text=f"ADICIONAR {categoria.upper()}",
                 font=("Segoe UI", 13, "bold"), bg=COR_FUNDO, fg=COR_TEXTO_TITULO).pack(pady=20)

        entradas = {}
        for campo in ["Nome", "Quantidade", "Preço"]:
            tk.Label(top_add, text=f"{campo}:", bg=COR_FUNDO, fg=COR_TEXTO_SUB, font=("Segoe UI", 10)).pack()
            e = tk.Entry(top_add, font=("Segoe UI", 11), relief="solid", bd=1)
            e.pack(pady=5, padx=30, fill="x")
            entradas[campo] = e

        def salvar():
            try:
                nome = entradas["Nome"].get()
                qtd = int(entradas["Quantidade"].get())
                preco = float(entradas["Preço"].get().replace(',', '.'))

                if not nome: raise ValueError

                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO produtos (categoria, nome, quantidade, preco) VALUES (?, ?, ?, ?)",
                               (categoria, nome, qtd, preco))
                conn.commit()
                conn.close()
                top_add.destroy()
                callback()
            except ValueError:
                messagebox.showerror("Erro", "Dados inválidos. Use números para Qtd e Preço.")

        tk.Button(top_add, text="SALVAR", bg=VERDE_KAIBEM, fg="white", font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2", command=salvar).pack(pady=25, padx=30, fill="x")

    def editar_produto(produto, callback):
        top_edit = tk.Toplevel()
        top_edit.title("Editar")
        top_edit.geometry("350x450")
        top_edit.configure(bg=COR_FUNDO)
        top_edit.grab_set()

        tk.Label(top_edit, text="EDITAR PRODUTO", font=("Segoe UI", 13, "bold"), bg=COR_FUNDO,
                 fg=COR_TEXTO_TITULO).pack(pady=20)

        #Campos
        tk.Label(top_edit, text="Nome:", bg=COR_FUNDO, fg=COR_TEXTO_SUB).pack()
        en_nome = tk.Entry(top_edit, font=("Segoe UI", 11), relief="solid", bd=1);
        en_nome.insert(0, produto['nome']);
        en_nome.pack(pady=5, padx=30, fill="x")

        tk.Label(top_edit, text="Quantidade:", bg=COR_FUNDO, fg=COR_TEXTO_SUB).pack()
        en_qtd = tk.Entry(top_edit, font=("Segoe UI", 11), relief="solid", bd=1);
        en_qtd.insert(0, produto['quantidade']);
        en_qtd.pack(pady=5, padx=30, fill="x")

        tk.Label(top_edit, text="Preço:", bg=COR_FUNDO, fg=COR_TEXTO_SUB).pack()
        en_pre = tk.Entry(top_edit, font=("Segoe UI", 11), relief="solid", bd=1);
        en_pre.insert(0, produto['preco']);
        en_pre.pack(pady=5, padx=30, fill="x")

        def atualizar():
            try:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE produtos SET nome = ?, quantidade = ?, preco = ? WHERE id = ?",
                               (en_nome.get(), int(en_qtd.get()), float(en_pre.get()), produto['id']))
                conn.commit()
                conn.close()
                top_edit.destroy()
                callback()
            except:
                messagebox.showerror("Erro", "Valores inválidos.")

        tk.Button(top_edit, text="ATUALIZAR", bg=AZUL_EDITAR, fg="white", font=("Segoe UI", 12, "bold"),
                  relief="flat", cursor="hand2", command=atualizar).pack(pady=25, padx=30, fill="x")

    def excluir_produto(produto, callback):
        if messagebox.askyesno("Confirmar", f"Deseja excluir '{produto['nome']}'?"):
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = ?", (produto['id'],))
            conn.commit()
            conn.close()
            callback()

    #Início do app
    carregar_estoque()

    def fechar():
        top.destroy()
        janela_pai.deiconify()

    top.protocol("WM_DELETE_WINDOW", fechar)