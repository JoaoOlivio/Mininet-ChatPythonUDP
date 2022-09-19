from pydoc import cli
import socket
import _thread
import json
import sys
import time

HOST = ""  # Endereco IP do Servidor
PORT = 5000  # Porta que o Servidor esta
IP_SERVIDOR = "10.0.1.10" #IP servidor
ENTROU_SALA = False
ID_SALA = None
NICKNAME = None
ID_MENSAGEM = 1

def server(udp):
    global ENTROU_SALA
    global ID_SALA

    #print(f"Starting UDP Server on port {PORT}")
    #udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    orig = ("", PORT) #Abrir Socket
    udp.bind(orig) #Bind criar uma porta 5000/ escutando a informação que vem de destino a essa porta.
    while True:
        msg, cliente = udp.recvfrom(1024) #Retorna a mensagem e a informação do cliente.
        msg_decoded = msg.decode('utf-8')
        string_dict = json.loads(msg_decoded)
        if string_dict["acao"] == 1:
            if string_dict["id_sala"] == ID_SALA:
                if string_dict["status"] == 1:
                    ENTROU_SALA = True
        elif string_dict["acao"] == 2:
            if string_dict["id_sala"] == ID_SALA:
                if string_dict["status"] == 1:
                    ENTROU_SALA = False
                    ID_SALA = None
        elif string_dict["acao"] == 3:
            if string_dict["id_sala"] == ID_SALA:
                if string_dict["status"] == 1:
                    print(f'\r{string_dict["nome"]} -> {string_dict["msg"]}', end="")
                    print("\n -> ", end="")
        #print(f"->#{cliente}# {string_dict}")
    udp.close()
    

def client():
    global ID_SALA
    global ID_MENSAGEM
    global NICKNAME

    print(f"Starting UDP Server on port {PORT}")
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _thread.start_new_thread(server, (udp,))
    #dest = (HOST, PORT)
    print("Type q to exit")
    message = None
    dest = (IP_SERVIDOR, PORT)
    nome = input("Informe o seu nickname: -> ")

    try:
        sala = int(input("Informe o ID da sala que deseja entrar: ->"))
        ID_SALA = sala
        entrar_sala = {
            "acao": 1,
            "nome": nome,
            "id_sala": sala,
        }
        string_json = json.dumps(entrar_sala) #Converter para JSON passando o dicionario
        udp.sendto(string_json.encode('utf-8'), dest)

    except Exception as ex:
        sys.exit(0)

    count = 0
    while True:
        if not ENTROU_SALA:
            print("Aguardando confirmacao...")
            NICKNAME = nome
            time.sleep(1)
            count += 1
        else:
            break

        if count == 5:
            sys.exit(0)

        time.sleep(1)

    print(f"{NICKNAME}, voce acaba de entrar na sala {ID_SALA}")
    print("Para sair, digite '!q' \n")
        
    while message != "!q":
        message = input("-> ")
        if message == "!q":
            msg = {
                "acao": 2,
                "nome": NICKNAME,
                "id_sala": ID_SALA,
            }
            
        else:
            msg = {
                "acao": 3,
                "nome": NICKNAME,
                "id_sala": ID_SALA,
                "id_msg": ID_MENSAGEM,
                "msg": message
            }
        string_json = json.dumps(msg)
        udp.sendto(string_json.encode('utf-8'), dest)
        ID_MENSAGEM += 1
    print(NICKNAME,", voce acaba de sair da sala ", ID_SALA)
    udp.close()

if __name__ == "__main__":
    client()
