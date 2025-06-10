from cliente import *

def menu_estabelecimento(conn):
    while True:
        print("\nMenu Estabelecimento:")
        print("1. Logar com CNPJ")
        print("0. Voltar")
        print("q. Sair do sistema")

        opcao = input("Escolha: ").strip().lower()
        if opcao == '1':
            cnpj = input("CNPJ do estabelecimento: ").strip()
            with conn.cursor() as cur:
                cur.execute("SELECT idest, nomeest FROM ifood.estabelecimento WHERE cnpj = %s", (cnpj,))
                row = cur.fetchone()
                if row:
                    idest, nome = row
                    print(f"Bem-vindo, {nome}!")
                    menu_estabelecimento_logado(conn, idest)
                else:
                    print("Estabelecimento não encontrado com esse CNPJ.")
        elif opcao == '0':
            print("Voltando ao menu anterior.")
            break
        elif opcao == 'q':
            print("Encerrando sistema.")
            exit(0)
        else:
            print("Opção inválida.")


def menu_estabelecimento_logado(conn, idest):
    while True:
        print("\nMenu Restaurante Logado:")
        print("1. Ver produtos")
        print("2. Adicionar produto")
        print("3. Atualizar produto")
        print("4. Deletar produto")
        print("5. Ver últimos pedidos recebidos")
        print("0. Voltar")
        print("q. Sair do sistema")

        opcao = input("Escolha: ").strip().lower()

        if opcao == '1':
            produtos = buscar_produtos_por_restaurante(conn, idest)
            if not produtos:
                print("Nenhum produto encontrado.")
            else:
                print("\nProdutos:")
                for idprod, nome, valor in produtos:
                    print(f"{idprod} - {nome} - R$ {valor:.2f}")
            aguardar_acao_usuario()

        elif opcao == '2':
            nome = input("Nome do produto: ").strip()
            valor = input("Preço (ex: 19.90): ").strip()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO ifood.produto (nomeprod, valorunitario, idest)
                        VALUES (%s, %s, %s)
                    """, (nome, float(valor), idest))
                    conn.commit()
                    print("Produto adicionado.")
            except Exception as e:
                conn.rollback()
                print("Erro ao adicionar produto:", e)
            aguardar_acao_usuario()

        elif opcao == '3':
            idprod = input("ID do produto a atualizar: ").strip()
            nome = input("Novo nome (deixe em branco para manter): ").strip()
            valor = input("Novo valor (deixe em branco para manter): ").strip()

            campos, valores = [], []
            if nome:
                campos.append("nomeprod = %s")
                valores.append(nome)
            if valor:
                campos.append("valorunitario = %s")
                valores.append(float(valor))

            if campos:
                valores.append(idprod)
                valores.append(idest)
                query = f"UPDATE ifood.produto SET {', '.join(campos)} WHERE idprod = %s AND idest = %s"
                try:
                    with conn.cursor() as cur:
                        cur.execute(query, tuple(valores))
                        conn.commit()
                        print("Produto atualizado.")
                except Exception as e:
                    conn.rollback()
                    print("Erro ao atualizar:", e)
            else:
                print("Nada para atualizar.")
            aguardar_acao_usuario()

        elif opcao == '4':
            idprod = input("ID do produto a deletar: ").strip()
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM ifood.produtopedido WHERE idprod = %s", (idprod,))
                    cur.execute("DELETE FROM ifood.produto WHERE idprod = %s AND idest = %s", (idprod, idest))
                    if cur.rowcount:
                        conn.commit()
                        print("Produto deletado junto com suas referências.")
                    else:
                        conn.rollback()
                        print("Produto não encontrado ou não pertence a este estabelecimento.")
            except Exception as e:
                conn.rollback()
                print("Erro ao deletar produto:", e)
            aguardar_acao_usuario()

        elif opcao == '5':
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.idped, p.dataped, p.valor_total, c.nomecli
                        FROM ifood.pedido p
                        JOIN ifood.cliente c ON p.idcli = c.idcli
                        WHERE p.idest = %s
                        ORDER BY p.dataped DESC
                        LIMIT 5;
                    """, (idest,))
                    pedidos = cur.fetchall()
                    if not pedidos:
                        print("Nenhum pedido encontrado.")
                    else:
                        for pid, data, total, nomecli in pedidos:
                            print("----------------------------------------------------------------")
                            print(f"Pedido {pid} - {data.strftime('%d/%m %H:%M')} - Cliente: {nomecli} - Total: R$ {total:.2f}")
                            cur.execute("""
                                SELECT pr.nomeprod, pp.quantprod, pr.valorunitario
                                FROM ifood.produtopedido pp
                                JOIN ifood.produto pr ON pp.idprod = pr.idprod
                                WHERE pp.idped = %s
                            """, (pid,))
                            itens = cur.fetchall()
                            if itens:
                                print("  Itens:")
                                for nomeprod, qtd, valorunit in itens:
                                    print(f"    {nomeprod} - Quantidade: {qtd} - Unitário: R$ {valorunit:.2f}")
                            else:
                                print("  Nenhum item encontrado para este pedido.")
            except Exception as e:
                print("Erro ao buscar pedidos:", e)
            aguardar_acao_usuario()

        elif opcao == '0':
            print("Voltando ao menu do estabelecimento.")
            break
        elif opcao == 'q':
            print("Encerrando sistema.")
            exit(0)
        else:
            print("Opção inválida.")


def aguardar_acao_usuario():
    while True:
        print("\n0. Voltar")
        print("q. Sair do sistema")
        acao = input("Escolha: ").strip().lower()
        if acao == '0':
            break
        elif acao == 'q':
            print("Encerrando sistema.")
            exit(0)
        else:
            print("Opção inválida.")
