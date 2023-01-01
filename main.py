import urllib.request as req
import json
from typing import Any, Union

import matplotlib.pyplot as plt

try:
    import japanize_matplotlib
except ModuleNotFoundError:
    plt.rcParams["font.family"] = "meiryo"
    plt.rcParams["font.sans-serif"] = ["Yu Gothic", "Meirio", "Noto Sans CJK JP"]


class CloudVariable:
    def __init__(
            self,
            project_id: int,
            limit: int = 100,
            offset: int = 0,
            backup: Union[list[dict], str] = [],
            username: str = None
        ) -> None:

        api_responce = req.urlopen(
            f"https://clouddata.scratch.mit.edu/logs?projectid={project_id}&limit={limit}&offset={offset}"
        )
        self.user_name = username
        self.params = {"project_id": project_id, "limit": limit, "offset": offset}

        api_responce = json.loads(api_responce.read().decode())
        if not backup == []:
            backup = list(filter(lambda x:x not in api_responce, backup))
        vote_data = api_responce + backup
        self._logs = list(
            filter(lambda x: "☁ @scratchattach" not in x.values(), vote_data)
        )
        self.__graph_created = False

        if username:
            self._logs = [i for i in self._logs if not i["user"] == username]

    def latest_results(self, remove_duplicates: bool = True, allow_different_item: bool = True) -> dict:
        """Returns the latest vote results.

        Args:
            remove_duplicates (bool, optional): If a user voted for the same item, it will be removed.
            allow_different_item (bool, optional): Allow the same user to vote on different items.If the ``remove_duplicates`` argument is false, it is ignored.

        Returns:
            dict: Dictionaries of item names and vote counts
        """
        data = sorted(self._logs, key=lambda x: x["timestamp"], reverse=False)  # 一応
        if remove_duplicates:
            data = self._remove_duplicates(data, allow_different_item)
        result = dict()
        for i in data:
            if (var := i["name"][2:]) in result.keys():
                result[var] += 1
            else:
                result.update({var: int(i["value"])})
        return result

    @property
    def most_vote_key(self, remove_duplicates: bool = True) -> str:
        """Returns the name of the item with the most votes.

        Args:
            remove_duplicates (bool, optional): If a user voted for the same item, it will be removed.
            allow_different_item: (bool, optional): Allow the same user to vote on different items.
            If the ``remove_duplicates`` argument is false, it is ignored.

        Returns:
            str: Name of most common item
        """
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
            allow_different_item: bool = True,
            sort_list: list = None,
            colors: Union[list, tuple] = None,
            startangle: int = 90,
            title: str = "結果"
        ) -> None:
        """Create a graph of the voting results.

        Args:
            digit (int, optional): Number of digits to display the percentage
            remove_duplicates (bool, optional): If a user voted for the same item, it will be removed.
            allow_different_item: (bool, optional): Allow the same user to vote on different items.
            If the ``remove_duplicates`` argument is false, it is ignored.
            sort_list (list, optional): The order in which the graphs are displayed
            colors (Union[list, tuple], optional): Graph Color
            startangle (int, optional): Starting angle of pie chart
            title (str, optional): Graph title
        """

        data = self.latest_results(remove_duplicates, allow_different_item)
        graph_digit = f"%1.{digit}f%%"
        # 辞書の順番でグラフが変わる
        if not sort_list is None:
            data = sorted(data.items(), key=lambda x:list(map(lambda x:x.lower(), sort_list)).index(x[0].lower()))
            data = dict((x, y) for x, y in data)

        plt.pie(data.values(), labels=data.keys(),
                counterclock=False, startangle=startangle,
                colors=colors, autopct=graph_digit
        )
        plt.title(title)
        self.__graph_created = True

    def save_graph(self, name: str = "result.svg", dpi: int = 300):
        if self.__graph_created:
            plt.savefig(name, dpi=dpi)
        else:
            raise Exception("Use the \"create_graph\" method to create a graph before executing.")

    @staticmethod
    def _remove_duplicates(json_list: list[dict], allow_different_item: bool = True) -> list[dict]:
        all = list()
        for index, data in enumerate(json_list):
            if allow_different_item:
                vote_data = (data["user"], data["name"])
            else:
                vote_data = data["user"]

            if vote_data not in all:
                all.append(vote_data)
            else:
                json_list.pop(index)
        return json_list


if __name__ == "__main__":
    bkup = open(r"C:\Users\username\Desktop\data.json", "r", encoding="utf8")
    cloud_var = json.load(bkup)
    bkup.close()

    cloud_var = CloudVariable(643164196, username="henji243", backup=cloud_var)
    print("start")
    print(cloud_var.latest_results(remove_duplicates=True, allow_different_item=False))
    cloud_var.create_graph(remove_duplicates=True, sort_list=["windows", "mac", "linux", "chrome os", "その他"])
    cloud_var.save_graph("test.svg")
