import psycopg2
import random
import datetime
from faker import Faker

fake = Faker('pt_BR')

# Configuração da conexão
conn = psycopg2.connect(
    host="localhost",      # localhost no seu PC
    port=5432,             # a porta local do túnel
    database="ifood_db",   # seu nome do banco
    user="ifood_user",         # seu usuário do banco
    password="user_ifood"  # sua senha
   )
cursor = conn.cursor()

# Buscar dados existentes
cursor.execute("Set search_path to ifood;")

# Buscar clientes e endereços
cursor.execute("SELECT idcli FROM cliente;") #, endereco;
clientes = cursor.fetchall()

# Buscar estabelecimentos e endereços
cursor.execute("SELECT idest from estabelecimento;") #, enderecoest;
estabelecimentos = cursor.fetchall()

# Buscar entregadores
cursor.execute("SELECT ident FROM entregador;")
entregadores = [row[0] for row in cursor.fetchall()]

# Buscar produtos por estabelecimento
cursor.execute("SELECT idprod, idest FROM produto;")
produtos = cursor.fetchall()

print(f"{len(clientes)} clientes, {len(estabelecimentos)} estabelecimentos, {len(entregadores)} entregadores carregados.")

# Agora você pode usar esses IDs para gerar pedidos

id_cliente = random.choice(clientes)
id_entregador = random.choice(entregadores)
id_estabelecimento = random.choice(estabelecimentos)

# Dicionário com categorias e produtos (usando seu exemplo)
pedidos_por_categoria = {
    'Pizzaria': ['Pizza Margherita Clássica',
        'Pizza Calabresa Defumada com Cebola Roxa',
        'Pizza Portuguesa Gourmet',
        'Pizza Quatro Queijos Trufada',
        'Pizza Vegana de Grão-de-Bico com Rúcula',
        'Pizza de Cogumelos Selvagens',
        'Pizza de Presunto de Parma com Rúcula e Parmesão',
        'Pizza de Pepperoni Picante',
        'Pizza de Frango com Catupiry',
        'Pizza Napolitana com Manjericão Fresco',
        'Pizza de Abobrinha com Queijo de Cabra',
        'Pizza de Atum com Azeitonas Pretas',
        'Pizza Carbonara Cremosa',
        'Pizza de Cordeiro com Hortelã',
        'Pizza de Palmito com Alho-Poró',
        'Pizza de Tomate Seco com Rúcula',
        'Pizza Havaiana com Abacaxi Caramelizado',
        'Pizza de Bacalhau com Azeitonas',
        'Pizza de Linguiça Artesanal com Cebola',
        'Pizza de Ricota com Espinafre e Nozes'],

    'Cafeteria': [
        'Cappuccino Italiano com Canela',
        'Espresso Intenso Duplo',
        'Latte Macchiato com Baunilha',
        'Mocha Cremoso com Chocolate Belga',
        'Café Turco Aromático',
        'Chá Masala Chai',
        'Affogato com Gelato de Baunilha',
        'Café com Leite Vaporizado',
        'Flat White Cremoso',
        'Macchiato Caramelizado',
        'Chá Verde com Jasmim',
        'Chá Preto Defumado Lapsang',
        'Café Gelado com Creme',
        'Chocolate Quente com Marshmallow',
        'Café com Cardamomo',
        'Matcha Latte Cremoso',
        'Café Irish com Whisky',
        'Chá de Hortelã Refrescante',
        'Café com Especiarias Indianas',
        'Café Vienense com Chantilly'],

    'Comida Brasileira': ['Feijoada Tradicional com Couve e Laranja',
        'Churrasco Misto com Farofa Crocante',
        'Moqueca de Camarão Baiana',
        'Bobó de Camarão',
        'Escondidinho de Carne Seca com Mandioca',
        'Arroz Carreteiro Gaúcho',
        'Vatapá com Pimenta-de-Cheiro',
        'Galinhada Caipira com Pequi',
        'Rabada com Agrião',
        'Dobradinha com Feijão Branco',
        'Tutu de Feijão com Torresmo',
        'Pirão de Peixe com Dendê',
        'Baião de Dois com Queijo Coalho',
        'Pirão de Mandioca com Carne de Sol',
        'Moqueca Capixaba com Pirão',
        'Feijão Tropeiro com Couve Mineira',
        'Caldinho de Feijão com Bacon',
        'Frango com Quiabo e Polenta',
        'Escondidinho de Camarão com Catupiry',
        'Pão de Queijo Recheado com Linguiça'],


    'Lanchonete': ['X-Salada Artesanal',
        'Cachorro-Quente com Molho Especial',
        'Sanduíche Natural de Frango com Cenoura',
        'Wrap de Frango Grelhado com Guacamole',
        'Beirute de Rosbife',
        'Tostex de Queijo Meia Cura',
        'Pão com Linguiça Defumada',
        'Hambúrguer de Costela com Queijo Brie',
        'Sanduíche de Pernil com Abacaxi',
        'Croque Monsieur Clássico',
        'Sanduíche de Pastrami com Mostarda',
        'Bauru Tradicional com Muita Queijo',
        'Pão Sírio com Hommus e Vegetais',
        'Sanduíche de Falafel com Tahine',
        'Wrap Vegetariano com Molho de Iogurte',
        'Sanduíche de Atum com Maionese de Ervas',
        'X-Bacon com Ovo e Maionese Caseira',
        'Sanduíche de Carne Louca com Vinagrete',
        'Sanduíche de Frango ao Curry',
        'Pão Italiano com Presunto Cru e Rúcula'],

    'Churrascaria': ['Picanha na Brasa com Sal Grosso',
        'Costela Bovina Assada por 8h',
        'Linguiça Artesanal Apimentada',
        'Fraldinha Grelhada com Chimichurri',
        'Espetinho de Coração de Frango',
        'Alcatra Maturada com Alho Confitado',
        'Cupim Assado no Bafo',
        'Maminha com Molho Barbecue',
        'Contrafilé com Ervas Finas',
        'Cordeiro ao Forno com Alecrim',
        'Tiras de Frango ao Limão Siciliano',
        'Costela Suína ao Molho de Mostarda',
        'Kafta de Cordeiro na Brasa',
        'Espeto de Camarão com Limão',
        'Picanha Suína com Molho de Maracujá',
        'Chorizo Argentino com Chimichurri',
        'Linguiça Blumenau com Cebola Caramelizada',
        'Espetinho de Vegetais Grelhados',
        'Medalhão de Filé Mignon com Bacon',
        'Frango Caipira Assado com Ervas'],

    'Comida Japonesa': ['Sashimi de Salmão Premium',
        'Temaki de Atum com Cream Cheese',
        'Hot Roll Crocante com Molho Tarê',
        'Uramaki de Camarão Empanado',
        'Nigiri de Polvo com Wasabi',
        'Gunkan de Ovas Tobiko',
        'Sushi de Enguia com Molho Teriyaki',
        'Temaki de Salmão com Abacate',
        'Uramaki Spicy Tuna',
        'Sashimi de Robalo com Limão',
        'Nigiri de Camarão com Gengibre',
        'Hot Roll de Salmão com Cream Cheese',
        'Sushi de Pepino com Cream Cheese',
        'Temaki Vegetariano com Tofu',
        'Uramaki de Salmão Skin',
        'Sashimi de Atum Bluefin',
        'Nigiri de Lula com Molho Ponzu',
        'Gunkan de Ovas de Salmão',
        'Temaki de Polvo com Maionese Apimentada',
        'Sushi California Roll'],

    'Padaria': ['Brigadeiro Gourmet de Pistache',
        'Torta de Limão com Merengue Italiano',
        'Macaron de Framboesa com Ganache',
        'Cheesecake de Frutas Vermelhas',
        'Pavê de Chocolate com Nozes',
        'Brownie de Chocolate Meio Amargo',
        'Sorvete Artesanal de Doce de Leite',
        'Mousse de Maracujá com Chantilly',
        'Pudim de Leite Condensado Cremoso',
        'Tiramisu Clássico Italiano',
        'Bolo Red Velvet com Cream Cheese',
        'Creme Brûlée com Baunilha Bourbon',
        'Quindim de Coco Tradicional',
        'Churros com Doce de Leite',
        'Panna Cotta com Calda de Frutas Vermelhas',
        'Tarte Tatin de Maçã',
        'Cookies de Chocolate com Nozes',
        'Gelatina Colorida de Frutas Tropicais',
        'Bombom de Chocolate Amargo com Flor de Sal',
        'Petit Gateau com Sorvete de Baunilha'],

    'Fast Food': ['Hambúrguer Artesanal com Bacon Caramelizado',
        'Batata Frita Rústica com Páprica',
        'Kebab de Cordeiro com Molho de Hortelã',
        'Nuggets Crocantes com Mostarda e Mel',
        'Taco Mexicano com Guacamole',
        'Frango Frito Estilo Sulista Americano',
        'Pizza Burger com Queijo Cheddar',
        'Wrap Tex-Mex com Molho Picante',
        'Hot Dog Chicago Style',
        'Sanduíche Cubano com Presunto e Picles',
        'Frango Empanado com Molho Barbecue',
        'Batata Chips Temperada com Alecrim',
        'Burger Vegano de Grão-de-Bico',
        'Burrito de Carne com Feijão Preto',
        'Onion Rings Crocantes',
        'Taco de Peixe com Molho de Iogurte',
        'Pizza de Pepperoni com Molho Especial',
        'Quesadilla de Frango com Queijo',
        'Sanduíche Philly Cheese Steak',
        'Cachorro-Quente Alemão com Mostarda']
}

# # Você também vai precisar do mapeamento do tipo de estabelecimento para categoria, caso tenha
# # Exemplo fictício, ajuste conforme sua lógica:
tipo_para_categoria = {
    'Pizzas & Forneria': 'Pizzaria',
    'Cafés & Bebidas Quentes': 'Cafeteria',
    'Gastronomia Brasileira': 'Comida Brasileira',
    'Sanduíches & Lanches Rápidos': 'Lanchonete',
    'Churrascaria': 'Churrascaria',
    'Culinária Japonesa': 'Comida Japonesa',
    'Sobremesas & Doces Finos': 'Padaria',
    'Fast Food Internacional': 'Fast Food',
    'Saladas Criativas': 'Saladas'
}


# # Como você só tem o id do estabelecimento, precisa pegar também o tipo/categoria do estabelecimento
# # Para isso, faça uma consulta que traga idest e tipo/categoria de todos os estabelecimentos, e monte um dicionário:
# # Pega idest e nome do estabelecimento (não tipo)
cursor.execute("SELECT idest, nomeest FROM estabelecimento;")
id_para_nome = {row[0]: row[1] for row in cursor.fetchall()}

def inferir_tipo_por_nome(nome_estab):
    termos = nome_estab.lower().split()

    primeiro_termo = termos[0] if len(termos) > 0 else ''
    segundo_termo = termos[1] if len(termos) > 1 else ''

    dois_termos = f"{primeiro_termo} {segundo_termo}"

    # Inferência especial para "comida japonesa"
    if dois_termos == 'comida japonesa':
        return 'Culinária Japonesa'

    # Verificações normais baseadas no primeiro termo
    if 'pizza' in primeiro_termo:
        return 'Pizzas & Forneria'
    elif 'cafe' in primeiro_termo or 'cafeteria' in primeiro_termo:
        return 'Cafés & Bebidas Quentes'
    elif 'churrascaria' in primeiro_termo or 'churrasco' in primeiro_termo:
        return 'Churrascaria'
    elif 'sushi' in primeiro_termo or 'temaki' in primeiro_termo:
        return 'Culinária Japonesa'
    elif 'doces' in primeiro_termo or 'doce' in primeiro_termo or 'confeitaria' in primeiro_termo:
        return 'Sobremesas & Doces Finos'
    elif 'fast' in primeiro_termo or 'burger' in primeiro_termo or 'hamburguer' in primeiro_termo:
        return 'Fast Food Internacional'
    elif 'salada' in primeiro_termo:
        return 'Saladas Criativas'
    elif 'brasileira' in primeiro_termo or 'brasileiro' in primeiro_termo:
        return 'Gastronomia Brasileira'

    return 'Fast Food Internacional'  # padrão

def inserir_produto(nomeprod, valorunitario, idest):
    sql = """
    INSERT INTO produto (nomeprod, valorunitario, idest)
    VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (nomeprod, valorunitario, idest))
    conn.commit()

def gerar_produtos_para_estabelecimentos(min_prod=5, max_prod=15):
    for estab_id in estabelecimentos:
        nome_estab = id_para_nome.get(estab_id, '')
        tipo_estab = inferir_tipo_por_nome(nome_estab)
        categoria = tipo_para_categoria.get(tipo_estab, 'Fast Food')
        opcoes_produtos = pedidos_por_categoria.get(categoria, ['Produto Genérico'])
        nprod = random.randint(min_prod, max_prod)
        for _ in range(nprod):
            nome_produto = random.choice(opcoes_produtos)
            preco = round(random.uniform(10, 80), 2)
            inserir_produto(nome_produto, preco, estab_id)

# # Chama a função para gerar produtos
gerar_produtos_para_estabelecimentos()

# print("Produtos gerados e inseridos no banco.")

cursor.execute("SELECT idprod, idest FROM produto;")
produtos = cursor.fetchall()
produtos_por_estab = {}
for idprod, idest in produtos:
    produtos_por_estab.setdefault(idest, []).append(idprod)

def extrair_estado(endereco):
    # Assumindo formato "..., SIGLA"
    try:
        return endereco.strip().split()[-1].upper()
    except Exception:
        return None

def gerar_data_pedido():
    # Data aleatória nos últimos 30 dias
    hoje = datetime.datetime.now()
    delta = datetime.timedelta(days=random.randint(0,30), hours=random.randint(0,23), minutes=random.randint(0,59))
    return hoje - delta

def gerar_horario_entrega(data_pedido):
    # Horário entre 30 min e 2h após o pedido
    delta = datetime.timedelta(minutes=random.randint(30,120))
    return data_pedido + delta

pedidos_por_cliente = 3

# for idcli, endereco_cli in clientes:
#     estado_cli = extrair_estado(endereco_cli)
#     # Filtrar estabelecimentos do mesmo estado
#     estab_mesmo_estado = [idest for idest, end_est in estabelecimentos if extrair_estado(end_est) == estado_cli]
#     if not estab_mesmo_estado:
#         # Se não achar nenhum, ignora cliente
#         continue

#     for _ in range(random.randint(1, pedidos_por_cliente)):
#         idest = random.choice(estab_mesmo_estado)
#         ident = random.choice(entregadores)
#         dataped = gerar_data_pedido()
#         statusped = 'pendente'  # Exemplo

#         # Inserir pedido (idped gerado pela trigger)
#         cursor.execute("""
#             INSERT INTO pedido (dataped, statusped, idcli, idest, ident, valor_total)
#             VALUES (%s, %s, %s, %s, %s, %s)
#             RETURNING idped;
#         """, (dataped, statusped, idcli, idest, ident, 0.0))
#         idped = cursor.fetchone()[0]

#         # Produtos do estabelecimento
#         prods_disponiveis = produtos_por_estab.get(idest, [])
#         if not prods_disponiveis:
#             continue

#         nprodutos = random.randint(1, 5)
#         produtos_escolhidos = random.sample(prods_disponiveis, min(nprodutos, len(prods_disponiveis)))

#         valor_total = 0.0
#         for idprod in produtos_escolhidos:
#             quantprod = random.randint(1, 3)
#             # Pega preço do produto
#             cursor.execute("SELECT valorunitario FROM produto WHERE idprod = %s;", (idprod,))
#             preco = float(cursor.fetchone()[0])
#             valor_total += preco * quantprod

#             # Insere no produtopedido
#             cursor.execute("""
#                 INSERT INTO produtopedido (idprod, idped, quantprod)
#                 VALUES (%s, %s, %s);
#             """, (idprod, idped, quantprod))

#         # Atualiza valor_total do pedido
#         cursor.execute("""
#             UPDATE pedido SET valor_total = %s WHERE idped = %s;
#         """, (round(valor_total, 2), idped))

#         # Inserir entrega
#         horario_entrega = gerar_horario_entrega(dataped)
#         cursor.execute("""
#             INSERT INTO entrega (idped, horario_entrega)
#             VALUES (%s, %s);
#         """, (idped, horario_entrega))

#         conn.commit()

print("Pedidos aleatórios gerados com sucesso.")

conn.commit()
