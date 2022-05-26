import tempfile
import requests
import re

SIYUAN_HOST = "http://127.0.0.1:6806"
SUYUAN_HEADERS = {}

with open("sy-token", "r") as t:
    SUYUAN_HEADERS["Authorization"] = "Token " + t.read()


class SYSDK(object):
    def __init__(self) -> None:
        self.notebooks = self.get_notebooks()

    def api_request(self, api, **kwargs):
        url = SIYUAN_HOST + api
        resp = requests.post(url, timeout=10, headers=SUYUAN_HEADERS, **kwargs)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(resp.content)

    def get_notebooks(self):
        resp = self.api_request("/api/notebook/lsNotebooks")
        return resp["data"]["notebooks"]

    def get_notebook_id(self, name):
        self.notebooks
        q = list(filter(lambda n: n["name"] == name, self.notebooks))
        if q:
            return q[0]["id"]
        return name

    def save_asset_file(self, file_name, content=None, mode="wb+", encoding=None):
        # file_name process to path
        # data/20210808180117-czj9bvb/政策｜灵活用工大势所趋-劳动保障亟待完善/assets/1653470828-1a49e8e01f0d94b65946716800c80a37.png
        m = re.search(r"^/?data/(.*?)/.*/(.*)", file_name)
        if m:
            notbook = self.get_notebook_id(m.group(1))
            path = "data/" + notbook + "/assets/" + m.group(2)
            with tempfile.TemporaryFile(mode=mode, encoding=encoding) as file:
                file.write(content)
                file.seek(0)
                return self.api_request("/api/file/putFile", data={
                    "path": path,
                    "isDir": False
                }, files={
                    "file": file
                })
        raise Exception("file path process error")

    def save_markdown_file(self, file_name, content):
        # file_name proecss
        # data/20210808180117-czj9bvb/政策｜灵活用工大势所趋-劳动保障亟待完善/index.md
        # data/{notebook name}/path/{file name}/index.md
        m = re.search(r"^/?data/(.*?)/(.*)/index.md", file_name)
        if m:
            notbook = self.get_notebook_id(m.group(1))
            path = m.group(2)
            resp = self.api_request("/api/filetree/createDocWithMd", json={
                "notebook": notbook,
                "path": path,
                "markdown": content
            })
            return resp
        raise Exception("file path process error")
