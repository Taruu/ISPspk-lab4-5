import asyncio
import json
import socket
import base64
from PIL import Image
import sys
import os
from io import BytesIO
class SysFunction():
    def decode_base64(self, in_b64:str) -> str:
        """Декодирование строки base64 в обычную строку"""
        msg_bytes = base64.b64decode(in_b64.encode())
        msg = msg_bytes.decode()
        return msg

    def encode_base64(self,in_str:str) -> str:
        """Кодирование строки в base64"""
        to_send = base64.b64encode(in_str.encode("UTF-8"))
        return to_send.decode()

    def image_hash_check(self,hash,image):
        """Функция проверки изображения"""
        return True



class Client_commands():
    def __init__(self, conn):
        self.SF = SysFunction()
        self.conn = conn
        pass


    def send_json(self,json_to_send:dict):
        if isinstance(json_to_send,dict):
            json_dumps_text = json.dumps(json_to_send)
            bs64_to_send = self.SF.encode_base64(json_dumps_text).encode()
            self.conn.send(bs64_to_send)
            return True
        else:
            return False

    def recv_json(self):
        len_recv = self.conn.recv(2048)
        len_data_raw = self.SF.decode_base64(len_recv.decode('ascii'))
        try:
            len_json_data = json.loads(len_data_raw)
        except:
            return None
        result_json_raw = b""

        while sys.getsizeof(result_json_raw) < len_json_data.get("LEN"):
            result_json_raw+=self.conn.recv(102400) #100 КБ
            print(round(sys.getsizeof(result_json_raw)/1048576, 2),"/",round(len_json_data.get("LEN")/1048576, 2), "МБ")
        result_json_text = self.SF.decode_base64(result_json_raw.decode('ascii'))
        result_json_data = json.loads(result_json_text)
        return result_json_data

    def get_image(self):
        print("request image")
        self.send_json({"COMMAND":"GET_IMAGES",
                        "COUNT" : 1})
        data = self.recv_json()

        if data.get("RELPY") == "ERROR_HTTPS":
            print("Ошибка изображения")
            return None

        image_data = base64.b64decode(data["RELPY"][0]["data"].encode())
        image_hash = data["RELPY"][0]["originalHash"]
        image_name = data["RELPY"][0]["id"]

        if not self.SF.image_hash_check(image_hash,image_data):
            print(f"Ошибка хеша {image_name}.jpeg")
            return None
        if input("Показать картинку? Y/N ") == "Y":
            img = Image.open(BytesIO(image_data))
            img.show()
        if input("Сохранить картинку? Y/N ") == "Y":
            with open(f"downloads_images/{image_name}.jpeg","wb") as file:
                file.write(image_data)



    def get_images(self):

        self.send_json({"COMMAND": "GET_IMAGES",
                        "COUNT": int(input("Ведите кол во картинок: "))})
        data = self.recv_json()


        if not data.get("RELPY"):
            return None
        if data["RELPY"] == "ERROR_HTTPS":
            print("Ошибка изображения")
            return None


        list_images = data.get("RELPY")
        len_images = len(list_images)
        now_len_image = 0
        for image_dict in list_images:
            image_data = base64.b64decode(image_dict["data"].encode())
            image_hash = image_dict["originalHash"]
            image_name = image_dict["id"]
            if not self.SF.image_hash_check(image_hash, image_data):
                print(f"Ошибка хеша {image_name}.jpeg")
                continue
            else:
                with open(f"downloads_images/{image_name}.jpeg", "wb") as file:
                    file.write(image_data)
                now_len_image+=1

        print(f"Получено {now_len_image} из {len_images}")
        print(f"Потеряно {len_images-now_len_image}")

    def menu(self):
        if not os.path.exists("downloads_images"):
            os.mkdir("downloads_images")
        print("""
        1 - Получить одну картинку.
        2 - Получить N кол во картинок
        3 - Отключится от сервера.
        """)
        func = {"1": self.get_image,
                "2": self.get_images,
                "3": self.conn.close
                }.get(input("Выбраем:"))
        if func:
            func()
        else:
            return



sock = socket.socket()
sock.connect(('localhost', 9999))

Client_commands = Client_commands(sock)
while True:
    Client_commands.menu()
    # to_send = base64.b64encode(input().encode())
    # print(to_send)
    # if to_send == "0":
    #     sock.close()
    # sock.send(to_send)

    # print("server reply:",decode_base64(data.decode()))
