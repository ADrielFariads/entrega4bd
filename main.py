import psycopg2

from cliente import *
from admin import * 

def conectar():
    return psycopg2.connect(
       host="10.61.49.127",      
        port=5432,             # a porta local do túnel
        database="ifood_db",   # seu nome do banco
        user="ifood_user",         # seu usuário do banco
        password="user_ifood"  # sua senha
   )

conn = conectar()

with conn.cursor() as cur:
    cur.execute("set search_path to ifood;")


def menu_principal():
    while True:
        print("---------------------------")
        print("\nMenu Principal:")
        print("1. Menu Cliente")
        print("2. Área Administrativa")
        print("0. Sair")

        opcao = input("Escolha: ")

        if opcao == '1':
            menu_cliente(conn)

        elif opcao == '2':
            menu_administrativo(conn)

        elif opcao == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida.")





if __name__ == "__main__":
    menu_principal()