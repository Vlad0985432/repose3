import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from api_handler import GitHubAPI

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("700x600")
        self.api = GitHubAPI()
        self.favorites_file = "favorites.json"
        self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        # Поле поиска
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Поиск пользователя:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", lambda e: self.search_user())

        ttk.Button(search_frame, text="Поиск", command=self.search_user).pack(side=tk.LEFT, padx=5)

        # Результаты поиска
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_listbox = tk.Listbox(results_frame, yscrollcommand=scrollbar.set, height=10)
        self.results_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_listbox.yview)
        self.results_listbox.bind("<<ListboxSelect>>", self.on_result_select)

        # Информация о пользователе
        info_frame = ttk.LabelFrame(self.root, text="Информация о пользователе", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.info_text = tk.Text(info_frame, height=6, width=60)
        self.info_text.pack(fill=tk.BOTH)
        self.info_text.config(state=tk.DISABLED)

        # Кнопки действий
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Добавить в избранное", command=self.add_to_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Мои избранные", command=self.show_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить из избранного", command=self.remove_from_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспортировать", command=self.export_favorites).pack(side=tk.LEFT, padx=5)

        self.current_user = None
        self.search_results = []
        self.is_favorites_view = False

    def search_user(self):
        username = self.search_var.get().strip()

        if not username:
            messagebox.showwarning("Ошибка", "Поле поиска не должно быть пустым!")
            return

        results = self.api.search_users(username)

        if results is None:
            messagebox.showerror("Ошибка", "Ошибка подключения к GitHub API")
            return

        self.results_listbox.delete(0, tk.END)
        self.search_results = results
        self.is_favorites_view = False

        if not results:
            messagebox.showinfo("Результаты", "Пользователи не найдены")
            return

        for user in results:
            self.results_listbox.insert(tk.END, user['login'])

    def on_result_select(self, event):
        selection = self.results_listbox.curselection()
        if not selection:
            return

        self.current_user = self.search_results[selection[0]]
        self.display_user_info(self.current_user)

    def display_user_info(self, user):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        info = f"Имя: {user.get('name', 'N/A')}\n"
        info += f"Логин: {user['login']}\n"
        info += f"Профиль: {user['html_url']}\n"
        info += f"Репозиториев: {user.get('public_repos', 'N/A')}\n"
        info += f"Подписчиков: {user.get('followers', 'N/A')}\n"
        info += f"Описание: {user.get('bio', 'N/A')}"

        if self.is_favorites_view and 'date_added' in user:
            info += f"\n\nДобавлено: {user['date_added']}"

        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)

    def add_to_favorites(self):
        if not self.current_user:
            messagebox.showwarning("Ошибка", "Выберите пользователя!")
            return

        login = self.current_user['login']

        if any(fav['login'] == login for fav in self.favorites):
            messagebox.showinfo("Информация", "Этот пользователь уже в избранном!")
            return

        user_with_date = self.current_user.copy()
        user_with_date['date_added'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.favorites.append(user_with_date)
        self.save_favorites()
        messagebox.showinfo("Успех", f"Пользователь {login} добавлен в избранное!")

    def show_favorites(self):
        self.results_listbox.delete(0, tk.END)
        self.search_results = self.favorites
        self.is_favorites_view = True

        if not self.favorites:
            messagebox.showinfo("Избранное", "Список избранных пуст")
            return

        for user in self.favorites:
            self.results_listbox.insert(tk.END, user['login'])

    def remove_from_favorites(self):
        if not self.current_user:
            messagebox.showwarning("Ошибка", "Выберите пользователя!")
            return

        login = self.current_user['login']
        self.favorites = [fav for fav in self.favorites if fav['login'] != login]
        self.save_favorites()
        messagebox.showinfo("Успех", f"Пользователь {login} удален из избранного!")

        if self.is_favorites_view:
            self.show_favorites()

    def export_favorites(self):
        if not self.favorites:
            messagebox.showwarning("Ошибка", "Список избранных пуст!")
            return

        export_file = f"favorites_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("Успех", f"Избранные экспортированы в {export_file}")

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке избранного: {e}")
                self.favorites = []
        else:
            self.favorites = []

    def save_favorites(self):
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении избранного: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
