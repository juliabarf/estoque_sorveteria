import tkinter as tk
from tkinter import ttk, messagebox
import db
from datetime import datetime

CATEGORIAS = ["Sorvete", "Açaí", "Caldo", "Pote"]


def janela_pedido(janela_pai):
    top = tk.Toplevel()
    top.title("Fazer Pedido - Kaibem")
    top.geometry("850x600")

    COR_FUNDO = "#FFFFFF"
    COR_TEXTO_TITULO = "#4B2C82"
    COR_TEXTO_SUB = "#6A4C93"
    ROXO_MEDIO = "#8467B3"
    VERDE_CONFIRMAR = "#2ECC71"
    CINZA_VOLTAR = "#95A5A6"
    AZUL_CARRINHO = "#74B9FF"

    top.configure(bg=COR_FUNDO)

    #Variáveis de controle
    categoria_var = tk.StringVar()
    produto_var = tk.StringVar()
    quantidade_var = tk.IntVar(value=1)
    carrinho_itens = []  # Lista temporária

    # --- FUNÇÕES LÓGICAS ---
    def atualizar_info(event=None):
        cat, nome_prod = categoria_var.get(), produto_var.get()
        if not cat or not nome_prod: return
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT quantidade, preco FROM produtos WHERE categoria = ? AND nome = ?", (cat, nome_prod))
            prod = cursor.fetchone()
            conn.close()
            if prod:
                info_label.config(text=f"Preço: R$ {prod['preco']:.2f} | Estoque: {prod['quantidade']}", fg=ROXO_MEDIO)
        except Exception as e:
            print(f"Erro ao buscar info: {e}")

    def carregar_produtos(event=None):
        cat = categoria_var.get()
        if not cat: return
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nome FROM produtos WHERE categoria = ?", (cat,))
            produtos = cursor.fetchall()
            conn.close()
            nomes = [p['nome'] for p in produtos]
            combo_produto['values'] = nomes
            if nomes:
                combo_produto.current(0)
                atualizar_info()
            else:
                produto_var.set("")
                info_label.config(text="Nenhum produto nesta categoria", fg="red")
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")

    def adicionar_ao_carrinho():
        cat, nome_prod, qtd = categoria_var.get(), produto_var.get(), quantidade_var.get()

        if not nome_prod or qtd <= 0:
            messagebox.showwarning("Aviso", "Selecione um produto e quantidade válida.")
            return

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT preco, quantidade FROM produtos WHERE categoria = ? AND nome = ?", (cat, nome_prod))
        prod = cursor.fetchone()
        conn.close()

        if prod and prod['quantidade'] >= qtd:
            total_item = prod['preco'] * qtd
            item = {
                'cat': cat, 'nome': nome_prod, 'qtd': qtd,
                'preco_un': prod['preco'], 'total': total_item
            }
            carrinho_itens.append(item)
            listbox_carrinho.insert(tk.END, f" {qtd}x {nome_prod} ({cat}) - R$ {total_item:.2f}")
            atualizar_total_visual()

            #Limpar campos para o próximo item
            produto_var.set("")
            quantidade_var.set(1)
            info_label.config(text="Item adicionado!", fg=VERDE_CONFIRMAR)
        else:
            messagebox.showerror("Erro", "Estoque insuficiente!")

    def atualizar_total_visual():
        total_geral = sum(item['total'] for item in carrinho_itens)
        lbl_total_carrinho.config(text=f"Total: R$ {total_geral:.2f}")

    def finalizar_pedido_completo():
        if not carrinho_itens:
            messagebox.showwarning("Aviso", "O carrinho está vazio!")
            return

        if not messagebox.askyesno("Confirmar", "Deseja finalizar o pedido?"):
            return

        conn = db.get_connection()
        cursor = conn.cursor()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            for item in carrinho_itens:
                # 1. Baixar estoque
                cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE nome = ? AND categoria = ?",
                               (item['qtd'], item['nome'], item['cat']))
                # 2. Inserir no histórico
                cursor.execute(
                    "INSERT INTO pedidos (categoria, nome_produto, quantidade, preco_unitario, total, data_hora) VALUES (?, ?, ?, ?, ?, ?)",
                    (item['cat'], item['nome'], item['qtd'], item['preco_un'], item['total'], data_hora))

            conn.commit()
            messagebox.showinfo("Sucesso", "Venda realizada com sucesso!")

            # Resetar interface
            carrinho_itens.clear()
            listbox_carrinho.delete(0, tk.END)
            atualizar_total_visual()
            categoria_var.set("")
            produto_var.set("")
            info_label.config(text="Aguardando novo pedido...", fg="gray")

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Erro ao processar: {e}")
        finally:
            conn.close()

    # --- INTERFACE ---
    tk.Label(top, text="🛒 NOVO PEDIDO", font=("Segoe UI", 18, "bold"),
             bg=COR_FUNDO, fg=COR_TEXTO_TITULO).pack(pady=(20, 5), anchor="w", padx=40)

    container_split = tk.Frame(top, bg=COR_FUNDO)
    container_split.pack(fill="both", expand=True, padx=40)

    # LADO ESQUERDO: FORMULÁRIO
    frame_form = tk.Frame(container_split, bg=COR_FUNDO)
    frame_form.pack(side="left", anchor="n", pady=10)

    def criar_label(texto, row):
        tk.Label(frame_form, text=texto, font=("Segoe UI", 10, "bold"),
                 bg=COR_FUNDO, fg=COR_TEXTO_TITULO).grid(row=row, column=0, sticky="w", pady=(10, 2))

    criar_label("Categoria:", 0)
    combo_categoria = ttk.Combobox(frame_form, values=CATEGORIAS, textvariable=categoria_var,
                                   state="readonly", width=35)
    combo_categoria.grid(row=1, column=0, sticky="w")
    combo_categoria.bind("<<ComboboxSelected>>", carregar_produtos)

    criar_label("Produto:", 2)
    combo_produto = ttk.Combobox(frame_form, values=[], textvariable=produto_var,
                                 state="readonly", width=35)
    combo_produto.grid(row=3, column=0, sticky="w")
    combo_produto.bind("<<ComboboxSelected>>", atualizar_info)

    criar_label("Quantidade:", 4)
    spin_qtd = tk.Spinbox(frame_form, from_=1, to=100, textvariable=quantidade_var,
                          font=("Segoe UI", 11), relief="solid", bd=1, width=33)
    spin_qtd.grid(row=5, column=0, sticky="w")

    info_label = tk.Label(frame_form, text="Selecione um item", fg="gray",
                          font=("Segoe UI", 9, "italic"), bg=COR_FUNDO)
    info_label.grid(row=6, column=0, sticky="w", pady=10)

    btn_add_car = tk.Button(frame_form, text="+ Adicionar ao Carrinho", bg=AZUL_CARRINHO, fg="white",
                            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                            command=adicionar_ao_carrinho, width=25)
    btn_add_car.grid(row=7, column=0, sticky="w", pady=10)

    # LADO DIREITO: CARRINHO
    frame_carrinho = tk.LabelFrame(container_split, text=" Resumo do Pedido ", font=("Segoe UI", 10, "bold"),
                                   bg=COR_FUNDO, fg=COR_TEXTO_TITULO, padx=10, pady=10)
    frame_carrinho.pack(side="right", fill="both", expand=True, padx=(20, 0), pady=10)

    listbox_carrinho = tk.Listbox(frame_carrinho, font=("Segoe UI", 11), height=15,
                                  relief="flat", highlightthickness=1, highlightbackground="#DDDDDD")
    listbox_carrinho.pack(fill="both", expand=True)

    lbl_total_carrinho = tk.Label(frame_carrinho, text="Total: R$ 0.00", font=("Segoe UI", 14, "bold"),
                                  bg=COR_FUNDO, fg=COR_TEXTO_TITULO)
    lbl_total_carrinho.pack(pady=10)

    # BOTÕES FINAIS
    frame_btns_final = tk.Frame(frame_form, bg=COR_FUNDO, pady=20)
    frame_btns_final.grid(row=8, column=0, sticky="w")

    tk.Button(frame_btns_final, text="FINALIZAR PEDIDO", bg=VERDE_CONFIRMAR, fg="white",
              font=("Segoe UI", 12, "bold"), width=22, height=2, relief="flat",
              cursor="hand2", command=finalizar_pedido_completo).pack(anchor="w")

    tk.Button(frame_btns_final, text="Voltar", bg=CINZA_VOLTAR, fg="white",
              font=("Segoe UI", 9, "bold"), width=12, relief="flat", cursor="hand2",
              command=lambda: (top.destroy(), janela_pai.deiconify())).pack(anchor="w", pady=15)

    top.protocol("WM_DELETE_WINDOW", lambda: (top.destroy(), janela_pai.deiconify()))