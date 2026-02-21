 import tkinter as tk

from tkinter import ttk, messagebox

import db


CATEGORIAS = ["Sorvete", "Açaí", "Caldo", "Pote"]



def janela_estoque(janela_pai):

    top = tk.Toplevel()

    top.title("Gerenciamento de Estoque")

    top.geometry("800x600")


    # Frame de scroll

    canvas = tk.Canvas(top)

    scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)

    scrollable_frame = ttk.Frame(canvas)


    scrollable_frame.bind(

        "<Configure>",

        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))

    )


    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)


    canvas.pack(side="left", fill="both", expand=True)

    scrollbar.pack(side="right", fill="y")


    def carregar_estoque():

        # Limpa o frame atual

        for widget in scrollable_frame.winfo_children():

            widget.destroy()


        conn = db.get_connection()

        cursor = conn.cursor()


        for cat in CATEGORIAS:

            # Frame para a Categoria

            frame_cat = tk.LabelFrame(scrollable_frame, text=cat, font=("Arial", 12, "bold"), padx=10, pady=10)

            frame_cat.pack(fill="x", padx=10, pady=5)


            # Buscar produtos dessa categoria

            cursor.execute("SELECT id, nome, quantidade, preco FROM produtos WHERE categoria = ?", (cat,))

            produtos = cursor.fetchall()


            if not produtos:

                tk.Label(frame_cat, text="Nenhum item nesta categoria.").pack()


            for prod in produtos:

                frame_item = tk.Frame(frame_cat)

                frame_item.pack(fill="x", pady=2)


                info_text = f"{prod['nome']} | Qtd: {prod['quantidade']} | R$ {prod['preco']:.2f}"

                tk.Label(frame_item, text=info_text, width=40, anchor="w").pack(side="left")


                # Botão Editar

                tk.Button(frame_item, text="Editar", command=lambda p=prod: editar_produto(p, carregar_estoque)).pack(

                    side="left", padx=5)

                # Botão Excluir

                tk.Button(frame_item, text="Excluir", bg="#ffcccc",

                          command=lambda p=prod: excluir_produto(p, carregar_estoque)).pack(side="left", padx=5)


            # Botão Adicionar Item na Categoria

            tk.Button(frame_cat, text="+ Adicionar Item",

                      command=lambda c=cat: adicionar_produto(c, carregar_estoque)).pack(pady=5)


        conn.close()


    def adicionar_produto(categoria, callback):

        top_add = tk.Toplevel()

        top_add.title(f"Adicionar {categoria}")


        tk.Label(top_add, text="Nome:").grid(row=0, column=0)

        entry_nome = tk.Entry(top_add)

        entry_nome.grid(row=0, column=1)


        tk.Label(top_add, text="Quantidade:").grid(row=1, column=0)

        entry_qtd = tk.Entry(top_add)

        entry_qtd.grid(row=1, column=1)


        tk.Label(top_add, text="Preço:").grid(row=2, column=0)

        entry_preco = tk.Entry(top_add)

        entry_preco.grid(row=2, column=1)


        def salvar():

            try:

                nome = entry_nome.get()

                qtd = int(entry_qtd.get())

                preco = float(entry_preco.get())


                if not nome:

                    messagebox.showerror("Erro", "Nome é obrigatório")

                    return


                conn = db.get_connection()

                cursor = conn.cursor()

                cursor.execute("INSERT INTO produtos (categoria, nome, quantidade, preco) VALUES (?, ?, ?, ?)",

                               (categoria, nome, qtd, preco))

                conn.commit()

                conn.close()


                top_add.destroy()

                callback()

            except ValueError:

                messagebox.showerror("Erro", "Quantidade ou preço inválidos")


        tk.Button(top_add, text="Salvar", command=salvar).grid(row=3, columnspan=2, pady=10)


    def editar_produto(produto, callback):

        top_edit = tk.Toplevel()

        top_edit.title("Editar Produto")


        tk.Label(top_edit, text="Nome:").grid(row=0, column=0)

        entry_nome = tk.Entry(top_edit)

        entry_nome.insert(0, produto['nome'])

        entry_nome.grid(row=0, column=1)


        tk.Label(top_edit, text="Quantidade:").grid(row=1, column=0)

        entry_qtd = tk.Entry(top_edit)

        entry_qtd.insert(0, produto['quantidade'])

        entry_qtd.grid(row=1, column=1)


        tk.Label(top_edit, text="Preço:").grid(row=2, column=0)

        entry_preco = tk.Entry(top_edit)

        entry_preco.insert(0, produto['preco'])

        entry_preco.grid(row=2, column=1)


        def salvar_edicao():

            try:

                conn = db.get_connection()

                cursor = conn.cursor()

                cursor.execute("UPDATE produtos SET nome = ?, quantidade = ?, preco = ? WHERE id = ?",

                               (entry_nome.get(), int(entry_qtd.get()), float(entry_preco.get()), produto['id']))

                conn.commit()

                conn.close()


                top_edit.destroy()

                callback()

            except ValueError:

                messagebox.showerror("Erro", "Valores inválidos")


        tk.Button(top_edit, text="Salvar Alterações", command=salvar_edicao).grid(row=3, columnspan=2, pady=10)


    def excluir_produto(produto, callback):

        if messagebox.askyesno("Confirmar", f"Excluir {produto['nome']}?"):

            conn = db.get_connection()

            cursor = conn.cursor()

            cursor.execute("DELETE FROM produtos WHERE id = ?", (produto['id'],))

            conn.commit()

            conn.close()

            callback()


    # Carrega inicial

    carregar_estoque()


    # Quando fechar a janela de estoque, mostra a principal

    def on_close():

        top.destroy()

        janela_pai.deiconify()


    top.protocol("WM_DELETE_WINDOW", on_close)