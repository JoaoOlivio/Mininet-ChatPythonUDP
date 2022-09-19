from pydoc import cli
import socket
import _thread
import json

#from regex import E

PORT = 5000  # Porta que o Servidor esta
LISTA_USUARIO = []
DEBUG = True

def adicionar_usuario(usuario,cliente):
    novo_usuario= {}
    novo_usuario["nome"] = usuario["nome"]
    novo_usuario["conexao"] = cliente
    # novo_usuario["ip"] = cliente[0]
    # novo_usuario["porta"] = cliente[1]
    novo_usuario["id_sala"] = usuario["id_sala"]
    LISTA_USUARIO.append(novo_usuario)

def remover_usuario(usuario, cliente):
    usuario_removido = {}
    usuario_removido["nome"] = usuario["nome"]
    usuario_removido["conexao"] = cliente
    usuario_removido["id_sala"] = usuario["id_sala"]
    LISTA_USUARIO.remove(usuario_removido)



def sendto_all(udp, cliente, string_dict, msg):
    for users in LISTA_USUARIO:
        if users["id_sala"] == string_dict["id_sala"]:
            if users["conexao"] != cliente:
                msg_entrou_sala = {
                    "acao": 3,
                    "nome": string_dict["nome"],
                    "id_sala": string_dict["id_sala"],
                    #"id_msg": string_dict["id_msg"],
                    "msg": msg,
                    "status": 1
                }
                msg_json_entrou_sala = json.dumps(msg_entrou_sala)
                udp.sendto(msg_json_entrou_sala.encode("utf-8"), users["conexao"])

def chat_server(udp):
    print(f"Starting UDP Server on port {PORT}")
    #udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    orig = ("", PORT)
    udp.bind(orig)
    while True:
        msg, cliente = udp.recvfrom(1024)
        msg_decoded = msg.decode('utf-8')
        if DEBUG:
            print(f"{msg_decoded}")

        try:
            string_dict= json.loads(msg_decoded)
            if string_dict['acao'] == 1:
                if {string_dict["nome"], string_dict["id_sala"]} not in [{d['nome'],  d['id_sala']} for d in LISTA_USUARIO]:
                    adicionar_usuario(string_dict, cliente)
                    msg = {
                        "acao": 1,
                        "nome": string_dict["nome"],
                        "status": 1,
                        "id_sala": string_dict["id_sala"],
                    }
                    msg_json = json.dumps(msg)
                    if DEBUG:
                        print(f"-- ENTROU NO CHAT -- {msg_json} -> {cliente}")
                    udp.sendto(msg_json.encode("utf-8"), cliente)
                    sendto_all(
                        udp, 
                        cliente, 
                        string_dict,
                        "{} Entrou na sala!".format(string_dict["nome"])
                    )
                    
                else:
                    print("Usuario ja existente")
            elif string_dict['acao'] == 2:
                remover_usuario(string_dict, cliente)
                msg = {
                    "acao": 2,
                    "nome": string_dict["nome"],
                    "id_sala": string_dict["id_sala"],
                    "status": 1
                }
                msg_json = json.dumps(msg)
                if DEBUG:
                    print(f"-- SAIU DO CHAT --{msg_json} -> {cliente}")
                udp.sendto(msg_json.encode("utf-8"), cliente)

                sendto_all(
                    udp, 
                    cliente, 
                    string_dict,
                    "{} Saiu da sala!".format(string_dict["nome"])
                )
            elif string_dict['acao'] == 3:
                sendto_all(
                    udp, 
                    cliente, 
                    string_dict,
                    string_dict["msg"]
                )
        except Exception as ex:
            pass
    udp.close()

def main():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chat_server(udp)


if __name__ == "__main__":
    main()
