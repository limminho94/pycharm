import pydobot
import socket
import threading
from torch.xpu import device

# 좌표 설정
x1, y1, z1 = 235, 0, 118

# 도봇 장치 초기화
def MachineSetting():
    global device
    port = 'COM4'
    device = pydobot.Dobot(port=port, verbose=True)
    device.move_to(x1, y1, z1, 0)

# 도봇 테스트 동작
def moveTest():
    x1 = 235
    y1 = 0
    z1 = -5

    device.move_to(x1, y1, z1, 0)
    device.wait(2000)
    device.suck(True)
    z1 += 20
    device.move_to(x1, y1, z1, 0)
    device.suck(False)

# 클라이언트 메시지 송신
def sendMessages(client_socket):
    try:
        while True:
            msg = input("서버에서 보낼 메시지 입력: ")
            if msg == "exit":
                break
            data = msg.encode()
            length = len(data)
            client_socket.sendall(length.to_bytes(4, byteorder='big'))  # 메시지 길이 전송
            client_socket.sendall(data)  # 실제 메시지 전송
    except Exception as e:
        print("송신 오류:", e)
    finally:
        client_socket.close()

# 클라이언트 메시지 수신
def receiveMessages(client_socket, addr):
    try:
        while True:
            # 1. 헤더 받기 (여기서는 "i"를 받는 예시)
            header = client_socket.recv(1)  # "i"는 1바이트
            if not header:
                break

            # 헤더가 예상과 다르면 오류 처리 가능
            if header != b'img':
                print(f"[{addr}] 예상하지 못한 헤더: {header}")
                break

            # 2. 길이 받기 (ushort로 보냈다면 2바이트 길이)
            length_data = client_socket.recv(2)
            if not length_data:
                break

            # 3. 길이 해석 (big-endian으로 해석)
            length = int.from_bytes(length_data, "big")

            # 4. 실제 데이터 받기 (길이에 맞춰 데이터를 받음)
            frame_data = client_socket.recv(length)
            if not frame_data:
                break

            try:
                # 5. UTF-8로 해석 시도 (문자 데이터인 경우)
                msg = frame_data.decode('utf-8')
                print(f"[{addr}] 받은 메시지(문자): {msg}")
            except UnicodeDecodeError:
                # 6. 바이너리 데이터 처리
                print(f"[{addr}] 받은 메시지(바이너리): {frame_data[:10]}...")  # 앞 10바이트만 출력

    except Exception as ex:
        print(f"[{addr}] 예외 발생: {ex}")
    finally:
        client_socket.close()


# 서버 설정 및 클라이언트 연결 처리
def connectToClnt():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('10.10.20.116', 12345))
    server_socket.listen()
    print('서버 대기 중...')

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f'클라이언트 연결 성공: {addr}')

            # 수신 및 송신 쓰레드 시작
            recv_thread = threading.Thread(target=receiveMessages, args=(client_socket, addr))
            send_thread = threading.Thread(target=sendMessages, args=(client_socket,))
            recv_thread.start()
            send_thread.start()
    except Exception as e:
        print("서버 오류:", e)
    finally:
        server_socket.close()

# 메인 실행
if __name__ == "__main__":
    connectToClnt()
