# import asyncio

#
# class Server_connection(asyncio.Protocol):
#     def connection_made(self, transport):
#         peername = transport.get_extra_info('peername')
#         print('Подключен клиент по {}'.format(peername))
#         self.transport = transport
#         self.sf = Server_function(self.transport)
#
#     def data_received(self, data):
#         message = data.decode()
#         self.sf.take_action(message)
#
#
#
#
#
# async def main():
#     # Получаем ссылку на цикл событий, т.к. планируем
#     # использовать низкоуровневый API.
#     loop = asyncio.get_running_loop()
#
#     server = await loop.create_server(
#         lambda: Server_connection(),
#         '127.0.0.1', 8888)
#
#     async with server:
#         await server.serve_forever()
#
# asyncio.run(main())

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
        data = conn.recv(4096)
        try:
            sf.take_action(data)
        except:
            break
        if not data:
            break


#conn.close()