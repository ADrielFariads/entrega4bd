import psycopg2

def menu_entregador(conn):
    while True:
        print("\n--- MENU ENTREGADOR ---")
        print("1 - Cadastrar entregador")
        print("2 - Buscar entregador por CPF")
        print("0 - Voltar")
        print("q - Sair do sistema")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            cadastrar_entregador(conn)
        elif opcao == '2':
            buscar_entregador_por_cpf(conn)

        elif opcao == '0':
            break
        elif opcao == 'q':
            print("Encerrando o sistema.")
            exit()
        else:
            print("Opção inválida. Tente novamente.")

def cadastrar_entregador(conn):
    try:
        print("\n--- Cadastro de Entregador ---")
        nome = input("Nome do entregador: ").strip()
        cpf = input("CPF (somente números): ").strip()
        veiculo = input("Veículo (Moto/Bicicleta): ").strip().capitalize()
        status = "Disponível"
        endereco = input("Endereço completo: ").strip()

        if not nome or not cpf or not veiculo or not status or not endereco:
            print("⚠️ Todos os campos são obrigatórios.")
            return
        if veiculo not in ['Moto', 'Bicicleta']:
            print("⚠️ Veículo deve ser 'Moto' ou 'Bicicleta'.")
            return

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entregador (nomeent, cpf_entregador, veiculo, statusent, endereco)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, cpf, veiculo, status, endereco))

        conn.commit()
        print("✅ Entregador cadastrado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao cadastrar entregador: {e}")
        conn.rollback()

    menu_retorno()

def buscar_entregador_por_cpf(conn):
    cpf = input("Digite o CPF do entregador: ").strip()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ident, nomeent, cpf_entregador, veiculo, statusent, endereco
                FROM entregador
                WHERE cpf_entregador = %s
            """, (cpf,))
            entregador = cur.fetchone()

            if entregador:
                print("\n--- Entregador encontrado ---")
                print(f"ID: {entregador[0]}")
                print(f"Nome: {entregador[1]}")
                print(f"CPF: {entregador[2]}")
                print(f"Veículo: {entregador[3]}")
                print(f"Status: {entregador[4]}")
                print(f"Endereço: {entregador[5]}")
            else:
                print("⚠️ Nenhum entregador encontrado com esse CPF.")
    except Exception as e:
        print(f"❌ Erro ao buscar entregador: {e}")

    menu_retorno()

def deletar_entregador_por_cpf(conn):
    cpf = input("Digite o CPF do entregador a ser deletado: ").strip()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM entregador WHERE cpf_entregador = %s", (cpf,))
            if cur.fetchone() is None:
                print("⚠️ Entregador não encontrado.")
                return

            confirmacao = input("Tem certeza que deseja excluir este entregador? (s/n): ").strip().lower()
            if confirmacao == 's':
                cur.execute("DELETE FROM entregador WHERE cpf_entregador = %s", (cpf,))
                conn.commit()
                print("✅ Entregador excluído com sucesso.")
            else:
                print("❌ Operação cancelada.")
    except Exception as e:
        print(f"❌ Erro ao excluir entregador: {e}")
        conn.rollback()

    menu_retorno()

def menu_retorno():
    while True:
        print("\n0 - Voltar")
        print("q - Sair do sistema")
        escolha = input("Escolha: ").strip()
        if escolha == '0':
            break
        elif escolha == 'q':
            print("Encerrando o sistema.")
            exit()
        else:
            print("Opção inválida. Tente novamente.")
