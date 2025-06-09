from cliente import mostrar_ultimos_pedidos

def menu_administrativo(conn):
    while True:
        print("\n--- Área Administrativa ---")
        print("1 - Menu Clientes")
        print("2 - Menu Estabelecimentos")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            menu_clientes(conn)
        elif opcao == "2":
            menu_estabelecimentos(conn)
        elif opcao == "0":
            print("Saindo da área administrativa.")
            break
        else:
            print("Opção inválida, tente novamente.")

def menu_clientes(conn):
    while True:
        print("\n--- Menu Clientes ---")
        print("1 - Buscar cliente por CPF")
        print("2 - Buscar cliente por ID")
        print("3 - Deletar cliente por CPF")
        print("0 - Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cpf = input("Informe o CPF do cliente: ")
            buscar_cliente_por_cpf(conn, cpf)
        elif opcao == "2":
            idcli = input("Informe o ID do cliente: ")
            buscar_cliente_por_id(conn, idcli)
        elif opcao == "3":
            cpf = input("Informe o CPF do cliente para deletar: ")
            deletar_cliente_por_cpf(conn, cpf)
        elif opcao == "0":
            break
        else:
            print("Opção inválida, tente novamente.")

def menu_estabelecimentos(conn):
    while True:
        print("\n--- Menu Estabelecimentos ---")
        print("1 - Buscar estabelecimento por ID")
        print("2 - Deletar estabelecimento por ID")
        print("0 - Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            idest = input("Informe o ID do estabelecimento: ")
            buscar_estabelecimento_por_id(conn, idest)
        elif opcao == "2":
            idest = input("Informe o ID do estabelecimento para deletar: ")
            deletar_estabelecimento_por_id(conn, idest)
        elif opcao == "0":
            break
        else:
            print("Opção inválida, tente novamente.")

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

def deletar_cliente_por_cpf(conn, cpf):
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM cliente WHERE cpf = %s RETURNING idcli", (cpf,))
        result = cur.fetchone()
        if result:
            conn.commit()
            print(f"Cliente com ID {result[0]} deletado com sucesso.")
        else:
            print("Cliente não encontrado.")
    except Exception as e:
        print("Erro ao deletar cliente:", e)
        conn.rollback()
    finally:
        cur.close()

def buscar_estabelecimento_por_id(conn, idest):
    cur = conn.cursor()
    try:
        cur.execute("SELECT idest, nomeest FROM estabelecimento WHERE idest = %s", (idest,))
        est = cur.fetchone()
        if est:
            print(f"ID: {est[0]} - Nome: {est[1]}")
        else:
            print("Estabelecimento não encontrado.")
    except Exception as e:
        print("Erro ao buscar estabelecimento:", e)
    finally:
        cur.close()

def deletar_estabelecimento_por_id(conn, idest):
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM estabelecimento WHERE idest = %s RETURNING idest", (idest,))
        result = cur.fetchone()
        if result:
            conn.commit()
            print(f"Estabelecimento com ID {result[0]} deletado com sucesso.")
        else:
            print("Estabelecimento não encontrado.")
    except Exception as e:
        print("Erro ao deletar estabelecimento:", e)
        conn.rollback()
    finally:
        cur.close()
