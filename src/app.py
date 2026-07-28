import flet as ft
import database as db
from datetime import *
from flet_charts import PieChart, PieChartSection, BarChart, BarChartGroup, BarChartRod
import exportar

def main(page: ft.Page):
    page.title = "KauanKoenigkan App"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    db.criar_tabela()
    db.criar_tabela_renda()
    db.criar_tabela_lancamentos()

    if db.usuarios() is not None:
        modo = {"atual": "login"}
    else:
        modo = {"atual": "cadastro"}

    titulo = ft.Text("", size=24, weight="bold")
    username = ft.TextField(label="Nome", width=500, autofocus=True)
    password = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=500)
    usuario_logado = {"id": None, "nome": None}

    def entrar_click(e):
        if not username.value.strip() or not password.value.strip():
            titulo.value = "⚠️ Por favor, preencha o Usuário e a Senha."
            page.update()
            return

        if modo["atual"] == "cadastro":
            if db.buscar_usuario(username.value) is not None:
                titulo.value = "Já existe um usuário cadastrado. Faça login."
                modo["atual"] = "login"
                atualizar_tela()
            else:
                page.controls.clear()
                db.cadastrar_usuario(username.value, password.value)
                result = db.verificar_login(username.value, password.value)
                usuario_logado["id"], usuario_logado["nome"] = result
                menu()

        elif modo["atual"] == "login":
            result = db.verificar_login(username.value, password.value)
            if result is None:
                titulo.value = "Usuário ou senha não encontrados"
                page.update()
            else:
                page.controls.clear()
                usuario_logado["id"], usuario_logado["nome"] = result
                menu()

    botao_acao = ft.Button("Entrar", on_click = entrar_click)
    botao_alternar = ft.Button("Ainda não tenho conta")

    def atualizar_tela():
        if modo["atual"] == "login":
            titulo.value = "Login"
            botao_acao.content = "Entrar"
            botao_alternar.content = "Ainda não tenho conta"
        else:
            titulo.value = "Cadastro"
            botao_acao.content = "Cadastrar"
            botao_alternar.content = "Já tenho conta"
        page.update()

    def alternar_click(e):
        if modo["atual"] == "login":
            modo["atual"] = "cadastro"
        else:
            modo["atual"] = "login"
        atualizar_tela()

    botao_alternar.on_click = alternar_click

    atualizar_tela() 

    async def sair(e):
        print('Fechando')
        await page.window.close()

    botao_exit = ft.Button("Sair", width=300, color="red", on_click=sair)

    page.add(
        ft.Column(
            [titulo, username, password, botao_acao],
            horizontal_alignment="center",
            spacing=30,
        )
    )

    page.add(
        ft.Column(
            [botao_alternar, botao_exit],
            horizontal_alignment="center",
            spacing=50,
        )
    )

    # ================================================================================= APLICAÇÃO DOS DADOS ============================================================================================

    def menu():
        page.controls.clear()
        user_text = ft.Text(f"Bem vindo(a), {username.value}", size=34, weight="bold")



        def lancar(e=None):
            page.controls.clear()

            periodo = db.periodo_atual()
            renda_salva = db.buscar_renda_mes(usuario_logado["id"], periodo)

            if renda_salva is None:
                periodo_ant = db.periodo_anterior(periodo)
                saldo_anterior = db.calcular_saldo_periodo(usuario_logado["id"], periodo_ant)

                campo_salario = ft.TextField(label="Salário fixo (R$)", keyboard_type=ft.KeyboardType.NUMBER)
                campo_extra = ft.TextField(label="Renda extra (freelance, bônus, etc.)", keyboard_type=ft.KeyboardType.NUMBER)
                mensagem = ft.Text("", color="red")

                texto_saldo = ft.Text("", size=14, color="green")
                if saldo_anterior > 0:
                    texto_saldo.value = f"💰 Sobrou R$ {saldo_anterior:.2f} do período anterior. Esse valor será somado à sua renda."
                elif saldo_anterior < 0:
                    texto_saldo.value = f"⚠️ Você gastou R$ {abs(saldo_anterior):.2f} a mais do que ganhou no período anterior."
                    texto_saldo.color = "red"

                def salvar_renda_click(e):
                    try:
                        fixo = float(campo_salario.value.replace(",", "."))
                        extra = float(campo_extra.value.replace(",", "."))
                    except (ValueError, AttributeError):
                        mensagem.value = "Preencha os dois valores corretamente."
                        page.update()
                        return

                    extra_total = extra + saldo_anterior
                    db.salvar_renda_mes(usuario_logado["id"], periodo, fixo, extra_total)
                    lancar()

                page.add(
                    ft.Column(
                        [
                            ft.Column(
                                [
                                    ft.Text(f"Informe sua renda de {periodo}", size=20, weight="bold"),
                                    texto_saldo,
                                    campo_salario,
                                    campo_extra,
                                    ft.Button("Salvar renda", on_click=salvar_renda_click),
                                    mensagem,
                                ],
                                horizontal_alignment="center",
                                alignment="center",
                                spacing=15,
                                expand=True,
                            ),
                            ft.Row([botao_home, botao_exit], alignment="center"),
                        ],
                        horizontal_alignment="center",
                        expand=True,
                    )
                )
            else:
                salario_fixo, renda_extra = renda_salva

                campo_tipo = ft.Dropdown(
                    label="Tipo",
                    options=[ft.dropdown.Option("Gasto"), ft.dropdown.Option("Entrada")],
                    value="Gasto",
                    width=300,
                )
                campo_descricao = ft.TextField(label="Descrição (opcional)", width=300)
                campo_valor = ft.TextField(label="Valor (R$)", keyboard_type=ft.KeyboardType.NUMBER, width=300)
                mensagem_lancamento = ft.Text("", color="red")

                campo_bloco = ft.Dropdown(
                    label="Categoria",
                    options=[
                            ft.dropdown.Option("Moradia"),
                            ft.dropdown.Option("Alimentação"),
                            ft.dropdown.Option("Obrigações"),
                            ft.dropdown.Option("Investimento"),
                            ft.dropdown.Option("Lazer"),
                            ft.dropdown.Option("Entrada"),
                    ],
                    width=300,
                )

                def salvar_lancamento_click(e):
                    try:
                        valor = float(campo_valor.value.replace(",", "."))
                    except (ValueError, AttributeError):
                        mensagem_lancamento.value = "Valor inválido."
                        page.update()
                        return

                    if not campo_bloco.value:
                        mensagem_lancamento.value = "Escolha uma categoria"
                        page.update()
                        return


                    db.adicionar_lancamento(
                        usuario_logado["id"], 
                        periodo,
                        campo_tipo.value,
                        campo_bloco.value, 
                        campo_descricao.value, 
                        valor,
                        campo_bloco.value,
                    )
                    campo_descricao.value = ""
                    campo_valor.value = ""
                    campo_bloco.value = None
                    mensagem_lancamento.value = "Lançamento salvo!"
                    mensagem_lancamento.color = "green"
                    page.update()

                page.add(
                    ft.Column(
                        [
                            ft.Column(
                                [
                                    ft.Text(f"Renda de {periodo}: R$ {salario_fixo + renda_extra:.2f}", size=16, weight="bold"),
                                    ft.Divider(),
                                    campo_tipo,
                                    campo_bloco,
                                    campo_descricao,
                                    campo_valor,
                                    ft.Button("Salvar lançamento", on_click=salvar_lancamento_click),
                                    mensagem_lancamento,
                                    ft.Divider(),
                                ],
                                horizontal_alignment="center",
                                spacing=25,
                                scroll="auto",
                                expand=True,
                            ),
                            ft.Row([botao_home, botao_exit], alignment="center"),
                        ],
                        horizontal_alignment="center",
                        expand=True,
                    )
                )
                page.update()

        def resumo(e=None):
                page.controls.clear()

                mes = db.periodo_atual()
                renda_salva = db.buscar_renda_mes(usuario_logado["id"], mes)

                if renda_salva is None:
                    page.add(
                        ft.Column(
                            [
                                ft.Text("Você ainda não informou a renda deste mês.", size=20),
                                ft.Text("Vá em Lançar para começar.", size=20, color="gray"),
                                ft.Row([botao_home, botao_exit], alignment="center"),
                            ],
                            horizontal_alignment="center",
                            alignment="center",
                            expand=True,
                            spacing=15,
                        )
                    )
                    page.update()
                    return

                salario_fixo, renda_extra = renda_salva
                renda_total = salario_fixo + renda_extra

                gastos_por_bloco = db.somar_gastos_por_bloco(usuario_logado["id"], mes)

                gasto_casa = 0
                gasto_lazer = 0
                gasto_investimento = 0
                total_entradas = 0

                for bloco, subtipo, total in gastos_por_bloco:
                    if bloco == "Moradia":
                        gasto_casa += total
                    elif bloco == "Lazer":
                        gasto_lazer += total
                    elif bloco == "Alimentação":
                        gasto_casa += total
                    elif bloco == "Obrigações":
                        gasto_casa += total
                    elif bloco == "Investimento":
                        gasto_investimento = total
                    elif bloco == "Entrada" or bloco == "Entradas":
                        total_entradas += total

                salario_fixo, renda_extra = renda_salva
                entradas_do_periodo = db.somar_entradas_extras(usuario_logado["id"], mes)
                renda_total = salario_fixo + renda_extra + entradas_do_periodo

                pct_obrigacoes, pct_investimento, pct_lazer = db.buscar_porcentagens(usuario_logado["id"], mes)

                input_obrigacoes = ft.TextField(value=str(int(pct_obrigacoes)), label="% Obrigações", width=110, keyboard_type=ft.KeyboardType.NUMBER)
                input_investimento = ft.TextField(value=str(int(pct_investimento)), label="% Investimento", width=110, keyboard_type=ft.KeyboardType.NUMBER)
                input_lazer = ft.TextField(value=str(int(pct_lazer)), label="% Lazer", width=110, keyboard_type=ft.KeyboardType.NUMBER)
                msg_porcentagem = ft.Text("", size=12)

                def salvar_porcentagens(e):
                    try:
                        p_ob = float(input_obrigacoes.value.replace(",", "."))
                        p_in = float(input_investimento.value.replace(",", "."))
                        p_lz = float(input_lazer.value.replace(",", "."))
                    except ValueError:
                        msg_porcentagem.value = "⚠️ Digite valores válidos."
                        msg_porcentagem.color = "red"
                        page.update()
                        return

                    if round(p_ob + p_in + p_lz, 2) != 100.0:
                        msg_porcentagem.value = f"⚠️ A soma deve ser 100% (atual: {p_ob + p_in + p_lz:.1f}%)"
                        msg_porcentagem.color = "red"
                        page.update()
                        return

                    db.salvar_porcentagens(usuario_logado["id"], mes, p_ob, p_in, p_lz)
                    resumo()

                painel_porcentagens = ft.ExpansionTile(
                    title=ft.Text("⚙️ Personalizar Regra de Distribuição (%)", size=14, weight="medium"),
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row([input_obrigacoes, input_investimento, input_lazer], alignment="center", spacing=10),
                                    ft.Button("Salvar Porcentagens", on_click=salvar_porcentagens),
                                    msg_porcentagem,
                                ],
                                horizontal_alignment="center",
                                spacing=10,
                            ),
                            padding=10,
                        )
                    ],
                )

                limite_casa = renda_total * (pct_obrigacoes / 100.0)
                limite_investimento = renda_total * (pct_investimento / 100.0)
                limite_lazer = renda_total * (pct_lazer / 100.0)

                page.update()

                def grafico_barra(gasto, limite):
                    estourou = gasto > limite
                    cor_gasto = "red" if estourou else "blue"

                    maior_valor = max(gasto, limite)

                    return BarChart(
                        groups=[
                            BarChartGroup(
                                x=0,
                                rods=[BarChartRod(to_y=gasto, width=30, color=cor_gasto, tooltip=f"Gasto: R$ {gasto:.2f}")],
                            ),
                            BarChartGroup(
                                x=1,
                                rods=[BarChartRod(to_y=limite, width=30, color="#e0e0e0", tooltip=f"Limite: R$ {limite:.2f}")],
                            ),
                        ],
                        max_y=maior_valor * 1.2 if maior_valor > 0 else 100,
                        height=180,
                        width=180,
                        interactive=True,
                    )

                def bloco_com_grafico(nome, gasto, limite):
                    estourou = gasto > limite
                    widgets = [
                        ft.Text(nome, size=15, weight="bold"),
                        grafico_barra(gasto, limite),
                        ft.Text(f"R$ {gasto:.2f} / R$ {limite:.2f}", size=13),
                    ]
                    if estourou:
                        excesso = gasto - limite
                        widgets.append(ft.Text(f"⚠️ Ultrapassou em R$ {excesso:.2f}", color="red", size=12))
                    return ft.Column(widgets, horizontal_alignment="center", spacing=6)

                page.add(
                    ft.Column(
                        [
                            ft.Column(
                                [
                                    ft.Text(f"Resumo de {mes}", size=22, weight="bold"),
                                    ft.Text(f"Renda total: R$ {renda_total:.2f}", size=16),
                                    ft.Divider(),
                                    ft.Row(
                                        [
                                            bloco_com_grafico("🏠 Obrigações (70%)", gasto_casa, limite_casa),
                                            bloco_com_grafico("📈 Investimento (20%)", gasto_investimento, limite_investimento),
                                            bloco_com_grafico("🎉 Lazer (10%)", gasto_lazer, limite_lazer),
                                        ],
                                        alignment="center",
                                        spacing=20,
                                        wrap=True,
                                    ),
                                ],
                                horizontal_alignment="center",
                                spacing=15,
                                scroll="auto",
                                expand=True,
                            ),
                            ft.Row([botao_home, botao_exit], alignment="center"),
                        ],
                        horizontal_alignment="center",
                        expand=True,
                    )
                )
                page.update()

        def historico(e=None):
            page.controls.clear()
            data_atual = datetime.now()

            drp_mes = ft.Dropdown(
                label="Mês",
                options=[ft.dropdown.Option(f"{i:02d}") for i in range(1, 13)],
                value=f"{data_atual.month:02d}",
                width=100,
            )
            drp_ano = ft.Dropdown(
                label="Ano",
                options=[ft.dropdown.Option(str(a)) for a in range(data_atual.year - 2, data_atual.year + 3)],
                value=str(data_atual.year),
                width=120,
            )

            lista_todos = ft.Column(spacing=8, scroll="auto", expand=True)
            msg_exportar = ft.Text("", size=12)

            def carregar_filtrado(e=None):
                lista_todos.controls.clear()
                msg_exportar.value = ""
                filtro = f"{drp_ano.value}-{drp_mes.value}"
                
                todos_lancamentos = db.listar_lancamentos_por_mes_ano(
                    usuario_logado["id"], filtro
                )

                if not todos_lancamentos:
                    lista_todos.controls.append(
                        ft.Text("Nenhum lançamento encontrado para este período.", color="gray", italic=True)
                    )
                else:
                    for id_lanc, tipo, categoria, descricao, valor, data_lanc in todos_lancamentos:
                        sinal = "+" if tipo == "Entrada" else "-"
                        cor = "green" if tipo == "Entrada" else "red"

                        texto = f"{data_lanc} | {categoria}"
                        if descricao:
                            texto += f" - {descricao}"
                        texto += f" | {sinal}R$ {valor:.2f}"

                        botao_desfazer = ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color="red",
                            tooltip="Desfazer/Apagar Lançamento",
                            on_click=lambda e, id_atual=id_lanc: desfazer_lancamento(id_atual),
                        )

                        card_content = ft.Row(
                            [
                                ft.Text(texto, color=cor, size=14, weight="medium", expand=True),
                                botao_desfazer,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        )

                        lista_todos.controls.append(
                            ft.Card(
                                content=ft.Container(content=card_content, padding=10, width=480)
                            )
                        )
                page.update()

            def desfazer_lancamento(id_lanc):
                db.deletar_lancamento(id_lanc)
                carregar_filtrado()

            # Ação de Exportar Direta e Robusta
            def acao_exportar_mes(e):
                periodo_escolhido = f"{drp_ano.value}-{drp_mes.value}"
                dados_mes = db.listar_lancamentos_para_exportar(usuario_logado["id"], periodo_escolhido)
                
                sucesso, mensagem = exportar.exportar_para_csv(dados_mes, periodo_escolhido)
                msg_exportar.value = mensagem
                msg_exportar.color = "green" if sucesso else "red"
                page.update()

            btn_filtrar = ft.ElevatedButton("🔍 Filtrar", on_click=carregar_filtrado)
            btn_exportar = ft.ElevatedButton("📥 Exportar Mês Selecionado", on_click=acao_exportar_mes)

            page.add(
                ft.Column(
                    [
                        ft.Text("📋 Histórico Geral de Lançamentos", size=20, weight="bold"),
                        ft.Row([drp_mes, drp_ano, btn_filtrar], alignment="center", spacing=10),
                        ft.Row([btn_exportar], alignment="center"),
                        msg_exportar,
                        ft.Text("Clique na lixeira para desfazer um lançamento.", size=12, color="gray"),
                        ft.Divider(),
                        lista_todos,
                        ft.Divider(),
                        ft.Row([botao_home, botao_exit], alignment="center"),
                    ],
                    horizontal_alignment="center",
                    alignment="center",
                    expand=True,
                    spacing=12,
                )
            )

            carregar_filtrado()
            page.update()

        botao_resumo = ft.Button("📊 Resumo", width=300, on_click=resumo)
        botao_lancar = ft.Button("📉 Lançar", width=300, on_click=lancar)
        botao_historico = ft.Button("📋 Histórico", width=300, on_click=historico)
        botao_home = ft.Button("Início", width=250, on_click=menu)

        page.add(
            ft.Column(
            [
                ft.Column(
                    [user_text, botao_lancar, botao_resumo, botao_historico],
                    horizontal_alignment="center",
                    alignment="center",
                    spacing=15,
                    expand=True,
                    ),
                ft.Row(
                    [botao_home, botao_exit],
                    alignment="center",
                    ),
                    ],
                    horizontal_alignment="center",
                    expand=True,
                    )
                )
        page.update()

ft.run(main)