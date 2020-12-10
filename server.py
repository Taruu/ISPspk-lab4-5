from serverfunc.function_commands import Server_function
import socket

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('localhost', 9999))
sock.listen(1)

while True:
    conn, addr = sock.accept()
    sf = Server_function(conn)
    print('connected:', addr)
    while True:
        print("wait command")

        try:
            data = conn.recv(4096)
            sf.take_action(data)
        except:
            print("client lost")
            break
        if not data:
            break


#conn.close()