import requests
import base64
import json
import sys
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

class Server_commands():
    def __init__(self,conn):
        #self.Networking_function = Networking_function()
        self.conn = conn
        self.SF = SysFunction()
    def get_random_image(self):
        """Получить картинку"""
        image = self.get_random_images(1)
        if image:
            return image[0]
        else:
            return None



    def get_random_images(self,count):
        list_images = []
        count_download = 0
        data = requests.get("https://nekos.moe/api/v1/random/image", params={"nsfw": "false", "count": str(count)})
        if data.status_code != 200:
            return None

        for image in data.json()["images"]:
            image_hash_orginal = image["originalHash"]
            image_id = image["id"]
            count_download += 1
            image_data = requests.get(f"https://nekos.moe/image/{image_id}").content
            print(f"get image: {image_id}.jpeg {count}/{count_download}")
            if self.SF.image_hash_check(image_hash_orginal,image_data):


                list_images.append({"id":image_id,
                                    "originalHash":image_hash_orginal,
                                    "data": base64.b64encode(image_data).decode()})
        if list_images:
            return list_images
        else:
            return None

class Server_function():
    def __init__(self,conn):
        self.conn = conn

        self.SF = SysFunction()
        self.SC = Server_commands(self.conn)

    def send_json(self,json_to_send:dict):
        json_dumps_text = json.dumps(json_to_send)
        bs64_to_send = self.SF.encode_base64(json_dumps_text).encode()
        print("SIZE TO SEND", sys.getsizeof(bs64_to_send))
        #Длина данных
        len_json_text = json.dumps({"LEN":sys.getsizeof(bs64_to_send)})
        b64_len_json = self.SF.encode_base64(len_json_text).encode()
        self.conn.send(b64_len_json)
        self.conn.send(bs64_to_send)




    def take_action(self,command_base64):
        """Выбор действия по пришедшей команде"""
        command = self.SF.decode_base64(command_base64.decode('ascii'))
        try:
            command_json = json.loads(command)
        except:
            #Если мы не получили json
            self.send_json({"RELPY": "ERROR_JSON",
                        "INPUT": command_base64.decode("ascii")})
            return

        print("take command")
        if command_json.get("COMMAND") == "GET_IMAGES":
            list_images = self.SC.get_random_images(command_json.get("COUNT"))
            if not list_images:
                self.send_json({"RELPY": "ERROR_HTTPS"})
                return
            self.send_json({"RELPY": list_images})
        elif command_json.get("COMMAND") == "DISCONNECT":
            self.conn.close()
            return True
        else:
            self.send_json({"RELPY": "COMMAND_NOT_SUPPORTED"})

