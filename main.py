from utils.native_message import receive_message, send_message
import logging
import os
import requests
import re
import base64
import shutil

__version__ = "0.1.9"
DOWNLOAD_FOLDER = "./download/"


def message_process(message):
    logging.info(f"RECE: {message}")
    msg_type = message.get("type")
    response = {"type": msg_type}
    if msg_type == "get.version":
        response["version"] = __version__
    elif msg_type == "get.downloadFolder":
        response["downloadFolder"] = DOWNLOAD_FOLDER
    elif msg_type == "download.text":
        filename = os.path.join(DOWNLOAD_FOLDER, message.get("filename"))
        filename = os.path.abspath(filename)
        errmsg = None
        try:
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            with open(filename, "w", encoding="utf-8") as f:
                f.write(message.get("text"))
        except Exception as ex:
            errmsg = str(ex)
            logging.error(ex)
        response.update({
            "filename": filename,
            "taskFilename": message.get("filename"),
            "failed": bool(errmsg),
            "errmsg": errmsg
        })
    elif msg_type == "download.url":
        filename = os.path.join(DOWNLOAD_FOLDER, message.get("filename"))
        filename = os.path.abspath(filename)
        errmsg = None
        try:
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))

            url = message.get("url")

            if url.startswith("data:"):
                # FORMAT: data:[<mime type>][;base64|encode],<data>
                r = re.compile("data:(.*);(.*),(.*)")
                m = r.match(url)
                if m:
                    encode = m.group(2)
                    content = m.group(3)
                    if encode == "base64":
                        with open(filename, "wb") as f:
                            content = base64.urlsafe_b64decode(
                                content + '=' * ((4 - len(content) % 4) % 4))
                            f.write(content)
                    else:
                        with open(filename, "w", encoding=encode) as f:
                            f.write(content)
                else:
                    raise Exception("url not math rule")
            else:
                url_resp = requests.get(url, headers=message.get("headers"))
                with open(filename, "wb") as f:
                    f.write(url_resp.content)

        except Exception as ex:
            errmsg = str(ex)
            logging.error(ex)
        response.update({
            "filename": filename,
            "taskFilename": message.get("filename"),
            "failed": bool(errmsg),
            "errmsg": errmsg
        })
    elif msg_type == "clipping.op.delete":
        errmsg = None
        try:
            del_folder = os.path.dirname(message.get("path"))
            if os.path.exists(del_folder):
                shutil.rmtree(del_folder)
        except Exception as ex:
            errmsg = str(ex)
            logging.error(ex)
        response.update({
            "clip_id": message.get("clip_id"),
            "ok": not errmsg,
            "message": errmsg
        })
    elif msg_type == "history.refresh":
        # TODO: Refresh History
        response["ok"] = False

    logging.info(f"RESP: {response}")
    send_message(response)


if __name__ == "__main__":
    logging.basicConfig(
        filename="native.log",
        filemode="a+",
        format=
        "%(asctime)s %(levelname)s %(pathname)s.%(funcName)s : %(message)s",
        datefmt="%d-%M-%Y %H:%M:%S",
        level=logging.DEBUG)
    try:
        receive_message(message_process)
    except Exception as ex:
        logging.error(ex)