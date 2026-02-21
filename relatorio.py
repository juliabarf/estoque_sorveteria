import tkinter as tk
from tkinter import ttk, messagebox
import db
from datetime import datetime
import calendar


def janela_relatorio(janela_pai):
    top = tk.Toplevel()
    top.title("Relatórios Mensais - Kaibem")
    top.geometry("850x600")

    # --- Configurações de Cores e Estilo ---
    COR_FUNDO = "#FFFFFF"
    COR_TEXTO_TITULO = "#4B2C82"
    COR_TEXTO_SUB = "#6A4C93"
    ROXO_MEDIO = "#8467B3"
    VERDE_GERAR = "#2ECC71"
    CINZA_VOLTAR = "#95A5A6"

    top.configure(bg=COR_FUNDO)

    # --- LISTAS PARA OS SELETORES ---
    MESES = [
        ("Janeiro", "01"), ("Fevereiro", "02"), ("Março", "03"), ("Abril", "04"),
        ("Maio", "05"), ("Junho", "06"), ("Julho", "07"), ("Agosto", "08"),
        ("Setembro", "09"), ("Outubro", "10"), ("Novembro", "11"), ("Dezembro", "12")
    ]

    ano_atual = datetime.now().year
    ANOS = [str(ano) for ano in range(ano_atual, ano_atual - 6, -1)]

    # --- FUNÇÃO GERAR RELATÓRIO ---
    def gerar_relatorio():
        for item in tree.get_children():
            tree.delete(item)

        selecao_mes = combo_mes.get()
        ano = combo_ano.get()

        if not selecao_mes or not ano:
            messagebox.showwarning("Aviso", "Por favor, selecione o mês e o ano.")
            return

        mes_num = selecao_mes.split(" - ")[1]
        mes_nome = selecao_mes.split(" - ")[0]

        data_inicio = f"{ano}-{mes_num}-01 00:00:00"
        ultimo_dia = calendar.monthrange(int(ano), int(mes_num))[1]
        data_fim = f"{ano}-{mes_num}-{ultimo_dia} 23:59:59"

        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            # Busca pedidos agregados por produto e categoria
            cursor.execute("""
                           SELECT nome_produto, categoria, SUM(quantidade) as total_qtd, SUM(total) as total_valor
                           FROM pedidos
                           WHERE data_hora BETWEEN ? AND ?
                           GROUP BY nome_produto, categoria
                           ORDER BY total_qtd DESC
                           """, (data_inicio, data_fim))

            pedidos = cursor.fetchall()
            conn.close()

            if not pedidos:
                lbl_resumo.config(text=f"Nenhuma venda registrada em {mes_nome} de {ano}.", fg="red")
                return

            # Preenche a Treeview
            for p in pedidos:
                tree.insert("", "end", values=(
                    p['nome_produto'],
                    p['categoria'],
                    p['total_qtd'],
                    f"{p['total_valor']:.2f}"
                ))

            # --- DESTAQUES COM CATEGORIA ---
            mais_v = pedidos[0]
            menos_v = pedidos[-1]

            texto_resumo = (
                f"🌟 MAIS VENDIDO: {mais_v['nome_produto']} [{mais_v['categoria']}] ({mais_v['total_qtd']} un)\n"
                f"📉 MENOS VENDIDO: {menos_v['nome_produto']} [{menos_v['categoria']}] ({menos_v['total_qtd']} un)"
            )
            lbl_resumo.config(text=texto_resumo, fg=COR_TEXTO_SUB, justify="left")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar relatório: {e}")

    # --- INTERFACE VISUAL ---

    tk.Label(top, text="📊 RELATÓRIO MENSAL", font=("Segoe UI", 18, "bold"),
             bg=COR_FUNDO, fg=COR_TEXTO_TITULO).pack(pady=(20, 10), anchor="w", padx=40)

    frame_filtro = tk.Frame(top, bg=COR_FUNDO, padx=40)
    frame_filtro.pack(fill="x", anchor="w")

    f_selects = tk.Frame(frame_filtro, bg=COR_FUNDO)
    f_selects.pack(anchor="w")

    tk.Label(f_selects, text="Selecione o Mês:", bg=COR_FUNDO, font=("Segoe UI", 9, "bold")).grid(row=0, column=0,
                                                                                                  sticky="w")
    combo_mes = ttk.Combobox(f_selects, values=[f"{m[0]} - {m[1]}" for m in MESES], state="readonly", width=20)
    combo_mes.grid(row=1, column=0, padx=(0, 15), pady=(0, 10))
    combo_mes.current(datetime.now().month - 1)

    tk.Label(f_selects, text="Selecione o Ano:", bg=COR_FUNDO, font=("Segoe UI", 9, "bold")).grid(row=0, column=1,
                                                                                                  sticky="w")
    combo_ano = ttk.Combobox(f_selects, values=ANOS, state="readonly", width=10)
    combo_ano.grid(row=1, column=1, pady=(0, 10))
    combo_ano.set(str(ano_atual))

    btn_gerar = tk.Button(frame_filtro, text="GERAR RELATÓRIO", command=gerar_relatorio,
                          bg=VERDE_GERAR, fg="white", font=("Segoe UI", 10, "bold"),
                          relief="flat", padx=25, pady=8, cursor="hand2")
    btn_gerar.pack(anchor="w", pady=15)

    frame_resultados = tk.Frame(top, bg=COR_FUNDO, padx=40)
    frame_resultados.pack(fill="both", expand=True)

    colunas = ("nome", "categoria", "quantidade_vendida", "total_vendido")
    tree = ttk.Treeview(frame_resultados, columns=colunas, show="headings")

    tree.heading("nome", text="Produto")
    tree.heading("categoria", text="Categoria")
    tree.heading("quantidade_vendida", text="Qtd")
    tree.heading("total_vendido", text="Total (R$)")

    tree.column("nome", width=250)
    tree.column("categoria", width=120)
    tree.column("quantidade_vendida", width=80, anchor="center")
    tree.column("total_vendido", width=120, anchor="e")

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame_resultados, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Rodapé de Resumo (Ajustado para 2 linhas para caber a categoria melhor)
    lbl_resumo = tk.Label(top, text="Selecione o período e clique em Gerar.",
                          font=("Segoe UI", 10, "bold italic"), bg=COR_FUNDO, fg="gray",
                          anchor="w", justify="left")
    lbl_resumo.pack(pady=20, anchor="w", padx=40)

    btn_voltar = tk.Button(top, text="Voltar", command=lambda: (top.destroy(), janela_pai.deiconify()),
                           bg=CINZA_VOLTAR, fg="white", relief="flat", font=("Segoe UI", 9, "bold"), width=12)
    btn_voltar.pack(pady=(0, 20), anchor="w", padx=40)

    top.protocol("WM_DELETE_WINDOW", lambda: (top.destroy(), janela_pai.deiconify()))