import socket

HOST = '10.10.20.105'  # 서버 IP
PORT = 12346  # 서버 포트

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# 전송할 데이터 준비
type = '10'
sender_id = "1"  # 클라이언트 ID
msg = "hello!"  # 보낼 메시지

# 데이터를 '/ '로 구분하여 하나의 문자열로 합침
data = f"{type}/{sender_id}/{msg}"
print("보낼 데이터:",data)
# 데이터를 바이트로 변환
en_data = data.encode('utf-8')  # UTF-8로 인코딩
length = len(en_data)  # 데이터 길이

# 서버로 데이터 길이 전송 (4바이트)
# client_socket.sendall(length.to_bytes(4, byteorder="little"))
# 서버로 실제 데이터 전송
client_socket.sendall(en_data)
print("보낼 데이터 길이:",len(en_data))
print("인코딩 한 데이터 : ",en_data)

# 서버로부터 응답 받기
# length_data = client_socket.recv(4)  # 서버가 전송한 응답 길이 받기
# response_length = int.from_bytes(length_data, byteorder="big")  # 응답 길이
data = client_socket.recv(1024)
msg = data.decode()  # 데이터를 출력한다.
print('서버에서 온 데이터 : ', msg)

# 연결 종료
client_socket.close()
