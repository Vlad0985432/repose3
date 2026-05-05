import requests

class GitHubAPI:
    def __init__(self):
        self.base_url = "https://api.github.com"

    def search_users(self, username, per_page=10):
        """
        Поиск пользователей по имени.

        Args:
            username (str): Имя или часть имени пользователя
            per_page (int): Количество результатов

        Returns:
            list: Список найденных пользователей или None при ошибке
        """
        try:
            url = f"{self.base_url}/search/users"
            params = {
                'q': username,
                'per_page': per_page
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            users = data.get('items', [])

            # Получаем полную информацию для каждого пользователя
            detailed_users = []
            for user in users:
                detailed_user = self.get_user_details(user['login'])
                if detailed_user:
                    detailed_users.append(detailed_user)

            return detailed_users

        except requests.exceptions.RequestException:
            return None

    def get_user_details(self, username):
        """
        Получение подробной информации о пользователе.

        Args:
            username (str): Логин пользователя

        Returns:
            dict: Информация о пользователе или None при ошибке
        """
        try:
            url = f"{self.base_url}/users/{username}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException:
            return None

