import requests


class AtCoderAPIError(Exception):
    """AtCoder API通信に関するエラー"""
    pass


class AtCoderUserNotFoundError(AtCoderAPIError):
    """指定したユーザー名が AtCoder に存在しない"""
    pass


class AtCoderClient:
    BASE_URL = "https://atcoder.jp"

    def __init__(self, timeout=10):
        self.timeout = timeout

    def get_user_history(self, username):
        if not username:
            raise AtCoderAPIError(
                "AtCoder のユーザー名が空です。"
            )

        url = f"{self.BASE_URL}/users/{username}/history/json"

        try:
            response = requests.get(
                url,
                timeout=self.timeout
            )

        except requests.RequestException as error:
            raise AtCoderAPIError(
                "AtCoder に接続できませんでした。"
            ) from error

        if response.status_code != 200:
            raise AtCoderAPIError(
                f"AtCoder からエラーが返りました（HTTP {response.status_code}）。"
            )

        try:
            return response.json()

        except ValueError as error:
            raise AtCoderAPIError(
                "AtCoder からの応答を読み取れませんでした。"
            ) from error

    def user_exists(self, username):
        """プロフィールページの有無でユーザーの存在を確認する。

        履歴API は存在しないユーザーにも空の配列を返すため、
        「参加履歴なし」と区別するのに使う。
        """
        url = f"{self.BASE_URL}/users/{username}"

        try:
            response = requests.get(url, timeout=self.timeout)
        except requests.RequestException as error:
            raise AtCoderAPIError(
                "AtCoder に接続できませんでした。"
            ) from error

        if response.status_code == 404:
            return False

        if response.status_code != 200:
            raise AtCoderAPIError(
                f"AtCoder からエラーが返りました（HTTP {response.status_code}）。"
            )

        return True

    def get_user_info(self, username):
        history = self.get_user_history(username)

        # 履歴が空のときだけ、ユーザーが存在するかを確認する
        if not history and not self.user_exists(username):
            raise AtCoderUserNotFoundError(
                f"ユーザー「{username}」は AtCoder に存在しません。"
            )

        # 最終参加コンテスト（Unrated も含む）
        last_contest = None
        if history:
            last = history[-1]
            last_contest = {
                "contest_name": last.get("ContestName", ""),
                "end_time": last.get("EndTime"),
                "is_rated": bool(last.get("IsRated")),
            }

        rated_history = [
            item
            for item in history
            if item.get("IsRated")
            and item.get("NewRating") is not None
        ]

        if not rated_history:
            # Rated 参加がない場合、レート関連は None（画面では「-」表示）
            return {
                "username": username,
                "rating": None,
                "highest": None,
                "color": None,
                "updated_at": None,
                "performances": [],
                "rated_count": 0,
                "last_contest": last_contest,
            }

        latest = rated_history[-1]

        ratings = [
            item["NewRating"]
            for item in rated_history
        ]

        performances = [
            {
                "contest_name": item.get("ContestName", ""),
                "performance": item.get("Performance"),
                "end_time": item.get("EndTime"),
                "rating": item.get("NewRating"),
            }
            for item in rated_history
        ]

        rating = ratings[-1]
        highest = max(ratings)

        return {
            "username": username,
            "rating": rating,
            "highest": highest,
            "color": self.get_rating_color(rating),
            "updated_at": latest.get("EndTime"),
            "performances": performances,
            "rated_count": len(rated_history),
            "last_contest": last_contest,
        }

    @staticmethod
    def get_rating_color(rating):
        if rating >= 2800:
            return "red"
        elif rating >= 2400:
            return "orange"
        elif rating >= 2000:
            return "yellow"
        elif rating >= 1600:
            return "blue"
        elif rating >= 1200:
            return "cyan"
        elif rating >= 800:
            return "green"
        elif rating >= 400:
            return "gray"
        else:
            return "brown"