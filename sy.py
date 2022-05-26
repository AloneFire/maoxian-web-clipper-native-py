from utils.native_message import receive_message, send_message
from utils.siyuan_sdk import SYSDK
import logging
import requests
import re
import base64
import tempfile
import os

__version__ = "0.1.9"
DOWNLOAD_FOLDER = "/"


def message_process(message):
    logging.info(f"RECE: {message}")
    msg_type = message.get("type")
    response = {"type": msg_type}
    errmsg = None
    sy = SYSDK()
    if msg_type == "get.version":
        response["version"] = __version__
    elif msg_type == "get.downloadFolder":
        response["downloadFolder"] = DOWNLOAD_FOLDER
    elif msg_type == "download.text":
        filename = message.get("filename")
        logging.info(filename)
        content = message.get("text")
        ext = os.path.splitext(filename)[-1]
        if ext == ".md":
            try:
                sy.save_markdown_file(filename, content)
            except Exception as ex:
                errmsg = str(ex)
                logging.error(ex)
                raise ex
        response.update({
            "filename": filename,
            "taskFilename": message.get("filename"),
            "failed": bool(errmsg),
            "errmsg": errmsg
        })
    elif msg_type == "download.url":
        errmsg = None
        filename = message.get("filename")
        logging.info(filename)
        url = message.get("url")
        try:
            if url.startswith("data:"):
                # FORMAT: data:[<mime type>][;base64|encode],<data>
                r = re.compile("data:(.*);(.*),(.*)")
                m = r.match(url)
                if m:
                    encode = m.group(2)
                    content = m.group(3)
                    if encode == "base64":
                        content = base64.urlsafe_b64decode(
                            content + '=' * ((4 - len(content) % 4) % 4))
                        sy.save_asset_file(filename, content, "wb+")
                    else:
                        sy.save_asset_file(filename, content, "w+", encode)
                else:
                    raise Exception("url not math rule")
            else:
                url_resp = requests.get(url, headers=message.get("headers"))
                sy.save_asset_file(filename, url_resp.content, "wb+")

        except Exception as ex:
            errmsg = str(ex)
            logging.error(ex)
        response.update({
            "filename": filename,
            "taskFilename": message.get("filename"),
            "failed": bool(errmsg),
            "errmsg": errmsg
        })
        pass
    elif msg_type == "clipping.op.delete":
        pass
    elif msg_type == "history.refresh":
        # TODO: Refresh History
        response["ok"] = False

    logging.info(f"RESP: {response}")
    send_message(response)


if __name__ == "__main__":
    logging.basicConfig(
        filename="native.log",
        filemode="a+",
        format="%(asctime)s %(levelname)s %(pathname)s.%(funcName)s : %(message)s",
        datefmt="%d-%M-%Y %H:%M:%S",
        level=logging.DEBUG)
    try:
        receive_message(message_process)
    except Exception as ex:
        logging.error(ex)
