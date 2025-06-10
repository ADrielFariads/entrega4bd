from cliente import mostrar_ultimos_pedidos
from entregador import menu_entregador
import sys

def menu_administrativo(conn):
    while True:
        print("\n--- Área Administrativa ---")
        print("1 - Menu Clientes")
        print("2 - Menu Estabelecimentos")
        print("3 - Menu Entregador")
        print("0 - Voltar")
        print("q - Sair do sistema")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            menu_clientes(conn)
        elif opcao == "2":
            menu_estabelecimentos(conn)
        elif opcao == '3':
            menu_entregador(conn)
        
        elif opcao == "0":
            print("Voltando ao menu principal...")
            break
        elif opcao == "q":
            print("Encerrando o sistema...")
            sys.exit(0)
        else:
            print("Opção inválida, tente novamente.")

def menu_clientes(conn):
    while True:
        print("\n--- Menu Clientes ---")
        print("1 - Buscar cliente por CPF")
        print("2 - Buscar cliente por ID")
        print("0 - Voltar")
        print("q - Sair do sistema")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cpf = input("Informe o CPF do cliente: ")
            buscar_cliente_por_cpf(conn, cpf)
        elif opcao == "2":
            idcli = input("Informe o ID do cliente: ")
            buscar_cliente_por_id(conn, idcli)
        elif opcao == "0":
            break
        elif opcao == "q":
            print("Encerrando o sistema...")
            sys.exit(0)
        else:
            print("Opção inválida, tente novamente.")
            continue

        if not menu_voltar_ou_sair():
            sys.exit(0)

def menu_estabelecimentos(conn):
    while True:
        print("\n--- Menu Estabelecimentos ---")
        print("1 - Buscar estabelecimento por ID")

        print("2 - Buscar estabelecimento por CNPJ")

        print("0 - Voltar")
        print("q - Sair do sistema")


        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            idest = input("Informe o ID do estabelecimento: ")
            buscar_estabelecimento_por_id(conn, idest)
        elif opcao == "2":
            cnpj = input("Informe o CNPJ do estabelecimento: ")
            buscar_estabelecimento_por_cnpj(conn, cnpj)

        elif opcao == "0":
            break
        elif opcao == "q":
            print("Encerrando o sistema...")
            sys.exit(0)
        else:
            print("Opção inválida, tente novamente.")
            continue

        if not menu_voltar_ou_sair():
            sys.exit(0)

# Função comum para escolha após ação
def menu_voltar_ou_sair():
    while True:
        print("\n0 - Voltar")
        print("q - Sair do sistema")
        escolha = input("Escolha: ").strip()
        if escolha == "0":
            return True
        elif escolha == "q":
            print("Encerrando o sistema...")
            return False
        else:
            print("Opção inválida.")

def buscar_cliente_por_cpf(conn, cpf):
    cur = conn.cursor()
    try:
        sql = """
            SELECT idcli, nomecli, telefone, cpf
            FROM cliente
            WHERE cpf = %s
        """
        cur.execute(sql, (cpf,))
        cliente = cur.fetchone()
        if cliente:
            idcli, nome, telefone, cpf = cliente
            cpf_mascarado = cpf[:4] + '*' * (len(cpf) - 4)
            print(f"ID: {idcli} - Nome: {nome} - Telefone: {telefone} - CPF: {cpf_mascarado}")
            mostrar_ultimos_pedidos(conn, idcli)
        else:
            print("Cliente não encontrado.")
    except Exception as e:
        print("Erro ao buscar cliente por CPF:", e)
    finally:
        cur.close()

def buscar_cliente_por_id(conn, idcli):
    cur = conn.cursor()
    try:
        sql = """
            SELECT idcli, nomecli, telefone, cpf
            FROM cliente
            WHERE idcli = %s
        """
        cur.execute(sql, (idcli,))
        cliente = cur.fetchone()
        if cliente:
            idcli, nome, telefone, cpf = cliente
            cpf_mascarado = cpf[:4] + '*' * (len(cpf) - 4)
            print(f"ID: {idcli} - Nome: {nome} - Telefone: {telefone} - CPF: {cpf_mascarado}")
            mostrar_ultimos_pedidos(conn, idcli)
        else:
            print("Cliente não encontrado.")
    except Exception as e:
        print("Erro ao buscar cliente por ID:", e)
    finally:
        cur.close()


def buscar_estabelecimento_por_id(conn, idest):
    cur = conn.cursor()
    try:
        cur.execute("SELECT idest, nomeest, cnpj FROM estabelecimento WHERE idest = %s", (idest,))
        est = cur.fetchone()
        if est:
            print(f"ID: {est[0]} - Nome: {est[1]} - CNPJ: {est[2]}")
            mostrar_pedidos_estabelecimento(conn, idest)
        else:
            print("Estabelecimento não encontrado.")
    except Exception as e:
        print("Erro ao buscar estabelecimento:", e)
    finally:
        cur.close()


def buscar_estabelecimento_por_cnpj(conn, cnpj):
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT idest, nomeest, cnpj
            FROM estabelecimento
            WHERE cnpj = %s
        """, (cnpj,))
        est = cur.fetchone()
        if est:
            idest, nome, cnpj = est
            cnpj_mascarado = cnpj[:6] + '*' * (len(cnpj) - 6)
            print(f"ID: {idest} - Nome: {nome} - CNPJ: {cnpj_mascarado}")
            mostrar_pedidos_estabelecimento(conn, idest)
        else:
            print("Estabelecimento não encontrado.")
    except Exception as e:
        print("Erro ao buscar estabelecimento por CNPJ:", e)
    finally:
        cur.close()

def mostrar_pedidos_estabelecimento(conn, idest):
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
                    # Buscar produtos do pedido atual
                    cur.execute("""
                        SELECT pr.nomeprod, pp.quantprod, pr.valorunitario
                        FROM ifood.produtopedido pp
                        JOIN ifood.produto pr ON pp.idprod = pr.idprod
                        WHERE pp.idped = %s
                    """, (pid,))
                    produtos = cur.fetchall()
                    if produtos:
                        print("  Itens:")
                        for nomeprod, quantidade, valorunitario in produtos:
                            print(f"    {nomeprod} - Quantidade: {quantidade} - Unitário: R$ {valorunitario:.2f}")
                    else:
                        print("  Nenhum item encontrado para este pedido.")
    except Exception as e:
        print("Erro ao buscar pedidos do estabelecimento:", e)

def criar_indices_otimizacao(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE INDEX IF NOT EXISTS idx_cliente_cpf ON cliente (cpf);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_estabelecimento_cnpj ON estabelecimento (cnpj);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_pedido_idcli ON pedido (idcli);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_pedido_idest ON pedido (idest);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_produtopedido_idprod ON produtopedido (idprod);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_produtopedido_idped ON produtopedido (idped);")
            conn.commit()
            print("Índices criados com sucesso.")
    except Exception as e:
        print("Erro ao criar índices:", e)

    consultas = [
        {
            "descricao": "Buscar cliente por CPF",
            "query": "SELECT idcli, nomecli, telefone, cpf FROM ifood.cliente WHERE cpf = %s",
            "params": ('12345678900',),
        },
        {
            "descricao": "Buscar pedidos de um cliente por data",
            "query": "SELECT idped, dataped, valor_total FROM ifood.pedido WHERE idcli = %s ORDER BY dataped DESC LIMIT 5",
            "params": ('CLI1234',),
        },
        {
            "descricao": "Buscar pedidos de um estabelecimento por data",
            "query": "SELECT idped, dataped, valor_total FROM ifood.pedido WHERE idest = %s ORDER BY dataped DESC LIMIT 5",
            "params": ('EST1234',),
        },
        {
            "descricao": "Buscar estabelecimento por CNPJ",
            "query": "SELECT idest, nomeest, cnpj FROM ifood.estabelecimento WHERE cnpj = %s",
            "params": ('12345678000199',),
        }
    ]

    with conn.cursor() as cur:
        print("\n=== Análise comparativa com e sem índice ===\n")
        for c in consultas:
            print(f">> {c['descricao']}")

            # Desativa o uso de índice
            cur.execute("SET enable_indexscan = off;")
            cur.execute("EXPLAIN ANALYZE " + c['query'], c['params'])
            resultado_sem_indice = cur.fetchall()
            tempo_sem_indice = next((linha[0] for linha in resultado_sem_indice if "Execution Time" in linha[0]), "Tempo não encontrado")
            print(f"Tempo SEM índice: {tempo_sem_indice}")

            # Ativa o uso de índice
            cur.execute("SET enable_indexscan = on;")
            cur.execute("EXPLAIN ANALYZE " + c['query'], c['params'])
            resultado_com_indice = cur.fetchall()
            tempo_com_indice = next((linha[0] for linha in resultado_com_indice if "Execution Time" in linha[0]), "Tempo não encontrado")
            print(f"Tempo COM índice: {tempo_com_indice}")

            print("-" * 60)