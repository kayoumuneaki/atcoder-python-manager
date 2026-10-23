import requests


class AtCoderAPIError(Exception):
    """AtCoder API通信に関するエラー"""
    pass


class AtCoderClient:
    BASE_URL = "https://atcoder.jp"

    def __init__(self, timeout=10):
        self.timeout = timeout

    def get_user_history(self, username):
        if not username:
            raise AtCoderAPIError(
                "AtCoder username is empty."
            )

        url = f"{self.BASE_URL}/users/{username}/history/json"

        try:
            response = requests.get(
                url,
                timeout=self.timeout
            )

        except requests.RequestException as error:
            raise AtCoderAPIError(
                "Failed to connect to AtCoder."
            ) from error

        if response.status_code != 200:
            raise AtCoderAPIError(
                f"AtCoder returned HTTP {response.status_code}."
            )

        try:
            return response.json()

        except ValueError as error:
            raise AtCoderAPIError(
                "Invalid JSON response from AtCoder."
            ) from error

    def get_user_info(self, username):
        history = self.get_user_history(username)

        rated_history = [
            item
            for item in history
            if item.get("IsRated")
            and item.get("NewRating") is not None
        ]

        if not rated_history:
            return {
                "username": username,
                "rating": 0,
                "highest": 0,
                "color": "gray",
                "updated_at": None,
                "performances": [],
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