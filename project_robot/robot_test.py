import pydobot
import socket, threading
from torch.xpu import device

x1 = 235
y1 = 0
z1 = 118


def MachineSetting():
    global device
    port = 'COM4'
    device = pydobot.Dobot(port=port, verbose=True)
    device.move_to(x1, y1, z1, 0)


def moveTest():
    x1 = 235
    y1 = 0
    z1 = -5

    device.move_to(x1, y1, z1, 0)
    device.wait(2000)
    device.suck(True)
    # x1 += 0
    # y1 += 20
    z1 += 20
    device.move_to(x1, y1, z1, 0)
    device.suck(False)

# 클라이언트와 메세지 송수신
def HandleClient(client_socket, addr):

    try:
        while True:
            data = client_socket.recv(4)
            length = int.from_bytes(data, "big")
            data = client_socket.recv(length)
            msg = data.decode()
            print('받은 메세지 :', msg)

            msg = "echo : " + msg
            data = msg.encode()
            length = len(data)
            client_socket.sendall(length.to_bytes(4, byteorder='big'))
            client_socket.sendall(data)
    except:
        print("except : ", addr)
    finally:
        client_socket.close()


def connectToClnt():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('10.10.20.116', 12345))
    server_socket.listen()
    print('클라이언트 연결성공')

    try:
        while True:
            client_socket, addr = server_socket.accept()
            th = threading.Thread(target=HandleClient, args=(client_socket, addr))
            th.start()
    except:
        print("server")
    finally:
        server_socket.close()

if __name__ == "__main__":
    connectToClnt()
    HandleClient()
    # MachineSetting()
    # moveTest()
