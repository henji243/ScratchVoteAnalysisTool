from operator import index
import matplotlib.pyplot as plt
import urllib.request as req
import json

from typing import Any, Union
from functools import cache


class CloudVariable:
    def __init__(
            self,
            project_id: int,
            limit: int = 100,
            offset: int = 0,
            backup: Union[list[dict], str] = None,
            username: str = None
        ) -> None:

        response = req.urlopen(
            f"https://clouddata.scratch.mit.edu/logs?projectid={project_id}&limit={limit}&offset={offset}"
        )
        self._user_name = username
        self.params = {"project_id": project_id, "limit": limit, "offset": offset}
        api_responce = json.loads(response.read().decode())
        self._logs = list(
            filter(lambda x: "☁ @scratchattach" not in x.values(), api_responce)
        )
        self.__graph_created = False

        if username:
            self._logs = [i for i in self._logs if not i["user"] == username]

    def latest_results(self, remove_duplicates: bool = True) -> dict:
        """_summary_

        Args:
            remove_duplicates (bool, optional): 同じユーザーによる投票を除去します。 Defaults to True.

        Returns:
            dict: 変数名と数の辞書を返します
        """
        data = sorted(self._logs, key=lambda x: x["timestamp"], reverse=False)  # 一応
        if remove_duplicates:
            data = self.remove_duplicates(data)
        result = dict()
        for i in data:
            if (var := i["name"][2:]) in result.keys():
                result[var] += 1
            else:
                result.update({var: int(i["value"])})
        return result

    @property
    def most_vote_key(self, remove_duplicates: bool = True) -> str:
        vote_result = self.latest_results(remove_duplicates=remove_duplicates)
        return max(vote_result, key=vote_result.get)

    @property
    def keys(self) -> list:
        log_keys = [d["name"] for d in self._logs if "@scratchattach" not in d["name"]]
        log_keys = list(set(log_keys))
        return log_keys

    def create_graph(
            self,
            digit: int = 2,
            remove_duplicates: bool = True,
            sort_list: list = None,
            colors: Union[list, tuple] = None,
            startangle: int = 90,
            title: str = "結果"
        ) -> Any:

        data = self.latest_results(remove_duplicates)
        graph_digit = f"%1.{digit}f%%"
        # 辞書の順番でグラフが変わる
        if not sort_list is None:
            data = sorted(data.items(), key=lambda x:list(map(lambda x:x.lower(), sort_list)).index(x[0].lower()))
            data = dict((x, y) for x, y in data)

        plt.rcParams["font.family"] = "meiryo"
        plt.rcParams["font.sans-serif"] = ["Yu Gothic", "Meirio", "Noto Sans CJK JP"]
        plt.pie(data.values(), labels=data.keys(),
                counterclock=False, startangle=startangle,
                colors=colors, autopct=graph_digit,
        )
        plt.title(title)
        self.__graph_created = True

    def save_graph(self, name: str = "result.svg", dpi: int = 300):
        if self.__graph_created:
            plt.savefig(name, dpi=dpi)
        else:
            raise Exception("Use the \"create_graph\" method to create a graph before executing.")

    # @cache ←こいつが元凶
    @staticmethod
    def remove_duplicates(json_list: list[dict]) -> list[dict]:
        all = list()
        for index, data in enumerate(json_list):
            if (data := (data["user"], data["name"])) not in all:
                all.append(data)
            else:
                json_list.pop(index)
        return json_list


if __name__ == "__main__":
    a = CloudVariable(643164196, username="henji243")
    print("start")
    print(a.latest_results(remove_duplicates=True))
    a.create_graph(remove_duplicates=True, sort_list=["windows", "mac", "linux", "chrome os", "その他"])
    a.save_graph("test.png")
