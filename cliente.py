from datetime import datetime, date

def criar_cliente(conn, nomecli, clube, cpf, endereco):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO ifood.cliente (nomecli, clube, cpf, endereco)
                VALUES (%s, %s, %s, %s)
                RETURNING idcli;
            """, (nomecli, clube, cpf, endereco))
            idcli = cur.fetchone()[0]
            conn.commit()
            return idcli
        except Exception as e:
            conn.rollback()
            print("Erro ao criar cliente:", e)
            return None
        
def listar_clientes(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT idcli, nomecli, clube, cpf, endereco FROM ifood.cliente;")
        return cur.fetchall()
    
def atualizar_cliente(conn, idcli, nomecli=None, clube=None, endereco=None, telefone=None):
    campos = []
    valores = []

    if nomecli is not None:
        campos.append("nomecli = %s")
        valores.append(nomecli)
    if clube is not None:
        campos.append("clube = %s")
        valores.append(clube)
    if endereco is not None:
        campos.append("endereco = %s")
        valores.append(endereco)
    if telefone is not None:
        campos.append("telefone = %s")
        valores.append(telefone)

    if not campos:
        return False  # Nenhum campo para atualizar

    valores.append(idcli)
    query = f"UPDATE cliente SET {', '.join(campos)} WHERE idcli = %s"

    try:
        with conn.cursor() as cur:
            cur.execute(query, tuple(valores))
            conn.commit()
            return True
    except Exception as e:
        print(f"[ERRO] Falha ao atualizar cliente: {e}")
        conn.rollback()
        return False

def deletar_cliente(conn, idcli):
    with conn.cursor() as cur:
        try:
            cur.execute("DELETE FROM ifood.cliente WHERE idcli = %s;", (idcli,))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            conn.rollback()
            print("Erro ao deletar cliente:", e)
            return False

def buscar_cliente_por_cpf(conn, cpf):
    with conn.cursor() as cur:
        cur.execute("SELECT idcli, nomecli, clube, cpf, endereco FROM ifood.cliente WHERE cpf = %s;", (cpf,))
        return cur.fetchone()
    

def extrair_uf(endereco):
    # Supondo que a UF seja as últimas 2 letras do endereço (ex: "Rua X, 123 - SP")
    # Vamos buscar as duas últimas letras maiúsculas do endereço
    if not endereco:
        return None
    endereco = endereco.strip()
    # Pega a última palavra, que deve ser a UF
    partes = endereco.split()
    uf = partes[-1].upper()
    if len(uf) == 2 and uf.isalpha():
        return uf
    return None

#buscando restaurantes
def buscar_restaurantes_por_uf(conn, uf):
    with conn.cursor() as cur:
        query = """
            SELECT idest, nomeest, enderecoest, pedido_minimo 
            FROM ifood.estabelecimento
            WHERE enderecoest LIKE %s
            LIMIT 10
        """
        cur.execute(query, ('%' + uf,))
        return cur.fetchall()

def buscar_produtos_por_restaurante(conn, idest):
    with conn.cursor() as cur:
        cur.execute("SELECT idprod, nomeprod, valorunitario FROM ifood.produto WHERE idest = %s", (idest,))
        return cur.fetchall()
    
def mostrar_produtos_restaurante(conn, idcli, idest):
    produtos = buscar_produtos_por_restaurante(conn, idest)
    if not produtos:
        print("Nenhum produto encontrado.")
        return

    # Chama a função fazer_pedido para lidar com o pedido completo
    fazer_pedido(conn, idcli, idest, produtos)


#colocando pedido
def criar_pedido(conn, idcli, idest, produtos, metodo_pagamento):
    try:
        with conn.cursor() as cur:
            # calcular valor total
            ids_produtos = [p[0] for p in produtos]
            cur.execute(
                "SELECT idprod, valorunitario FROM ifood.produto WHERE idprod = ANY(%s)",
                (ids_produtos,)
            )
            precos_db = {row[0]: row[1] for row in cur.fetchall()}
            valor_total = sum(precos_db[idprod] * quant for idprod, quant in produtos)
            print(f"Valor total calculado: R${valor_total:.2f}")

            # pegar valor mínimo do restaurante
            cur.execute("SELECT pedido_minimo FROM ifood.estabelecimento WHERE idest = %s", (idest,))
            row = cur.fetchone()
            if row is None:
                print("Restaurante não encontrado.")
                return None

            valor_minimo = row[0]

            if valor_total < valor_minimo:
                print(f"Valor do pedido R${valor_total:.2f} é menor que o mínimo do restaurante R${valor_minimo:.2f}. Pedido não criado.")
                return None

            # inserir pedido
            cur.execute("""
                INSERT INTO ifood.pedido (dataped, statusped, idcli, idest, valor_total)
                VALUES (NOW(), 'pendente', %s, %s, %s)
                RETURNING idped;
            """, (idcli, idest, valor_total))
            idped = cur.fetchone()[0]

            # inserir produtopedido
            for idprod, quant in produtos:
                cur.execute("""
                    INSERT INTO ifood.produtopedido (idprod, idped, quantprod)
                    VALUES (%s, %s, %s);
                """, (idprod, idped, quant))

            # inserir pagamento
            cur.execute("""
                INSERT INTO ifood.pagamento (metodo_pagamento, status_pagamento, idcli, idped)
                VALUES (%s, 'concluído', %s, %s)
                RETURNING idpag;
            """, (metodo_pagamento, idcli, idped))
            idpag = cur.fetchone()[0]

            # inserir entrega (15 minutos depois do pedido)
            cur.execute("""
                INSERT INTO ifood.entrega (idped, horario_entrega)
                VALUES (%s, NOW() + INTERVAL '15 minutes');
            """, (idped,))

            conn.commit()

            # Perguntar avaliação
            avaliar = input("Deseja avaliar seu pedido? (s/n): ").strip().lower()
            if avaliar == 's':
                while True:
                    try:
                        nota = int(input("Informe uma nota de 1 a 5: "))
                        if 1 <= nota <= 5:
                            break
                        else:
                            print("Nota deve ser entre 1 e 5.")
                    except ValueError:
                        print("Entrada inválida. Digite um número entre 1 e 5.")
                mensagem = input("Deixe uma mensagem (opcional): ").strip()
                try:
                    cur.execute("""
                        INSERT INTO ifood.avaliacao (idped, nota, mensagem)
                        VALUES (%s, %s, %s);
                    """, (idped, nota, mensagem if mensagem else None))
                    conn.commit()
                    print("Avaliação registrada com sucesso.")
                except Exception as e:
                    conn.rollback()
                    print("Erro ao registrar avaliação:", e)

            return idped

    except Exception as e:
        conn.rollback()
        print("Erro ao criar pedido completo:", e)
        return None
            

    except Exception as e:
        conn.rollback()
        print("Erro ao criar pedido completo:", e)
        return None


def adicionar_produtos_ao_pedido(conn, idped, produtos):  # produtos = [(idprod, quantidade)]
    with conn.cursor() as cur:
        try:
            for idprod, quant in produtos:
                cur.execute("""
                    INSERT INTO ifood.produtopedido (idprod, idped, quantprod)
                    VALUES (%s, %s, %s);
                """, (idprod, idped, quant))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("Erro ao adicionar produtos:", e)

def mostrar_restaurantes_proximos(conn, idcli):
    with conn.cursor() as cur:
        cur.execute("SELECT endereco FROM ifood.cliente WHERE idcli = %s", (idcli,))
        endereco_cliente = cur.fetchone()
        if not endereco_cliente:
            print("Endereço do cliente não encontrado.")
            return
        uf_cliente = extrair_uf(endereco_cliente[0])
        if not uf_cliente:
            print("Não foi possível extrair UF do endereço.")
            return

    restaurantes = buscar_restaurantes_por_uf(conn, uf_cliente)
    if not restaurantes:
        print("Nenhum restaurante encontrado na sua região.")
        return

    print("Restaurantes próximos:")
    for i, (idest, nomeest, _, pedido_minimo) in enumerate(restaurantes, 1):
        print(f"{i}. {nomeest} - Pedido mínimo: {pedido_minimo}")

    escolha = input("Escolha um restaurante pelo número (ou 0 para voltar): ")
    if escolha == '0':
        return
    try:
        escolha_int = int(escolha)
        if 1 <= escolha_int <= len(restaurantes):
            idest = restaurantes[escolha_int - 1][0]
            mostrar_produtos_restaurante(conn, idcli, idest)
        else:
            print("Escolha inválida.")
    except ValueError:
        print("Entrada inválida.")

def mostrar_cupons(conn, idcli):
    with conn.cursor() as cur:
        # Busca cupons com validade hoje ou maior (ativos)
        cur.execute("""
            SELECT idcup, tipo_cupom, valor_cupom, validade
            FROM ifood.cupom
            WHERE idcli = %s AND validade >= %s
            ORDER BY validade
        """, (idcli, date.today()))
        
        cupons = cur.fetchall()
        
        if not cupons:
            print("Nenhum cupom ativo encontrado.")
            return
        
        for idcup, tipo, valor, validade in cupons:
            print(f"Cupom {idcup} - Tipo: {tipo} - Valor: R$ {valor:.2f} - Validade: {validade.strftime('%d/%m/%Y')}")

def fazer_pedido(conn, idcli, idest, produtos_disponiveis):
    carrinho = []
    while True:
        print("\nProdutos disponíveis:")
        for i, (idprod, nome, preco) in enumerate(produtos_disponiveis, 1):
            print(f"{i}. {nome} - R${preco:.2f}")
        print("0. Finalizar pedido")

        opcao = input("Escolha um produto para adicionar ou 0 para finalizar: ")
        if opcao == '0':
            break
        try:
            index = int(opcao) - 1
            if 0 <= index < len(produtos_disponiveis):
                quant = int(input("Quantidade: "))
                if quant > 0:
                    carrinho.append((produtos_disponiveis[index][0], quant))
                else:
                    print("Quantidade deve ser maior que zero.")
            else:
                print("Opção inválida.")
        except ValueError:
            print("Entrada inválida.")

    if not carrinho:
        print("Carrinho vazio. Pedido cancelado.")
        return

    metodo = input("Forma de pagamento (crédito, débito, pix, boleto): ").strip().lower()

    idped = criar_pedido(conn, idcli, idest, carrinho, metodo)
    if idped:
        print(f"Pedido {idped} criado com sucesso!")
    else:
        print("Falha ao criar pedido.")


def criar_pagamento(conn, idcli, idped, metodo):
    with conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO ifood.pagamento (metodo_pagamento, status_pagamento, idcli, idped) VALUES (%s, %s, %s, %s) RETURNING idpag",
                (metodo, 'concluído', idcli, idped)
            )
            idpag = cur.fetchone()[0]
            conn.commit()
            return idpag
        except Exception as e:
            conn.rollback()
            print("Erro ao criar pagamento:", e)
            return None

def ultimos_pedidos(conn, id_cliente, limite=5):
    query = """
    SELECT
        p.idped,
        p.dataped,
        p.statusped,
        p.valor_total,
        STRING_AGG(pr.nomeprod || ' (x' || pp.quantprod || ')', ', ') AS produtos
    FROM ifood.pedido p
    JOIN ifood.produtopedido pp ON p.idped = pp.idped
    JOIN ifood.produto pr ON pp.idprod = pr.idprod
    WHERE p.idcli = %s
    GROUP BY p.idped, p.dataped, p.statusped, p.valor_total
    ORDER BY p.dataped DESC
    LIMIT %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (id_cliente, limite))
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
    
    return [dict(zip(colnames, row)) for row in rows]


def mostrar_ultimos_pedidos(conn, idcli):
    pedidos = ultimos_pedidos(conn, idcli)
    if not pedidos:
        print("Nenhum pedido encontrado.")
        return
    else:
        print("------------------------Últimos pedidos------------------------ \n")
        for ped in pedidos:
            data_formatada = ped['dataped'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"Pedido {ped['idped']} - Data: {data_formatada} - Status: {ped['statusped']} - Total: R$ {ped['valor_total']:.2f}")
            print(f"Produtos: {ped['produtos']}\n")

def buscar_cliente_por_idcli(conn, idcli):
    with conn.cursor() as cur:
        query = """
            SELECT idcli, nomecli, clube, cpf, endereco, telefone
            FROM ifood.cliente
            WHERE idcli = %s
        """
        cur.execute(query, (idcli,))
        row = cur.fetchone()
        if row:
            return {
                "idcli": row[0],
                "nomecli": row[1],
                "clube": row[2],
                "cpf": row[3],
                "endereco": row[4],
                "telefone": row[5] if len(row) > 5 else None
            }
        return None


def alterar_dados_cliente(conn, idcli):
    cliente = buscar_cliente_por_idcli(conn, idcli)
    if not cliente:
        print("Cliente não encontrado.")
        return

    print("\nDados atuais do cliente:")
    print(f"Nome: {cliente['nomecli']}")
    print(f"É do clube? {'Sim' if cliente['clube'] else 'Não'}")
    print(f"CPF: {cliente['cpf']}")
    print(f"Endereço: {cliente['endereco']}")
    print(f"Telefone: {cliente.get('telefone', '(não informado)')}")

    print("\nAlterar dados do cliente (deixe em branco para não alterar)")

    nomecli = input("Novo nome: ").strip()
    clube_input = input("É do clube? (s/n): ").strip().lower()
    endereco = input("Novo endereço: ").strip()
    telefone = input("Novo telefone: ").strip()

    if clube_input == 's':
        clube = True
    elif clube_input == 'n':
        clube = False
    else:
        clube = None  # não alterar

    sucesso = atualizar_cliente(
        conn,
        idcli,
        nomecli=nomecli if nomecli else None,
        clube=clube,
        endereco=endereco if endereco else None,
        telefone=telefone if telefone else None
    )

    if sucesso:
        print("Dados atualizados com sucesso.")
    else:
        print("Nenhum dado foi alterado ou ocorreu um erro.")

def menu_cliente(conn):
    while True:
        print("\nMenu Cliente:")
        print("1. Logar")
        print("2. Criar conta")
        print("0. Voltar para o menu principal")

        opcao = input("Escolha: ")

        if opcao == '1':
            cpf = input("CPF: ")
            cliente = buscar_cliente_por_cpf(conn, cpf)
            if cliente:
                primeiro_nome = cliente[1].split()[0]
                print(f"Logado como {primeiro_nome}")
                menu_cliente_logado(conn, cliente[0])  # Passa idcli
            else:
                print("Cliente não encontrado.")
        elif opcao == '2':
            nome = input("Nome: ").strip()
            clube_input = input("É do clube? (s/n): ").strip().lower()
            clube = True if clube_input == 's' else False
            cpf = input("CPF: ").strip()
            endereco = input("Endereço: ").strip()

            idcli = criar_cliente(conn, nome, clube, cpf, endereco)
            if idcli:
                print(f"Conta criada com sucesso! Seu ID é {idcli}")
            else:
                print("Falha ao criar conta.")
        elif opcao == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")

def menu_cliente_logado(conn, idcli):
    while True:
        print("\nMenu Cliente Logado:")
        print("1. Mostrar últimos pedidos")
        print("2. Mostrar cupons")
        print("3. Mostrar restaurantes próximos")
        print("4. Alterar dados cadastrais")
        print("0. Logout")

        opcao = input("Escolha: ")

        if opcao == '1':
            mostrar_ultimos_pedidos(conn, idcli)
        elif opcao == '2':
            mostrar_cupons(conn, idcli)
        elif opcao == '3':
            mostrar_restaurantes_proximos(conn, idcli)
        elif opcao == '4':
            alterar_dados_cliente(conn, idcli)
        elif opcao == '0':
            print("Logout realizado.")
            break
        else:
            print("Opção inválida. Tente novamente.")
            