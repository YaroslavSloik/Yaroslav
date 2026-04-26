import threading
from socket import *
from customtkinter import *
import random


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")

        self.username = "User"

        # emojis прикол
        self.emojis = ["😂", "🔥", "👍", "😎", "💀", "✨"]

        # THEME
        self.current_theme = "dark"
        set_appearance_mode(self.current_theme)

        # MENU
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.is_menu = False

        self.menu_btn = CTkButton(self, text="▶️", width=30, command=self.toggle_menu)
        self.menu_btn.place(x=0, y=0)

        self.theme_btn = CTkButton(self, text="🌙", width=30, command=self.toggle_theme)
        self.theme_btn.place(x=35, y=0)

        # CHAT
        self.chat = CTkTextbox(self, state="disabled", font=("Arial", 13))
        self.chat.place(x=0, y=0)

        self.entry = CTkEntry(self, placeholder_text="Повідомлення")
        self.entry.place(x=0, y=0)

        self.send_btn = CTkButton(self, text=">", width=40, command=self.send)
        self.send_btn.place(x=0, y=0)

        # SOCKET
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(("localhost", 1111))
            threading.Thread(target=self.recv, daemon=True).start()
            self.sock.send(f"NAME@{self.username}\n".encode())
        except:
            pass

        self.ui()

    # THEME
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        set_appearance_mode(self.current_theme)

        self.theme_btn.configure(text="☀️" if self.current_theme == "light" else "🌙")

        if self.is_menu:
            if self.current_theme == "dark":
                self.menu_frame.configure(fg_color="#222")
            else:
                self.menu_frame.configure(fg_color="white")

    # MENU
    def toggle_menu(self):
        self.is_menu = not self.is_menu
        self.menu_btn.configure(text="◀️" if self.is_menu else "▶️")

        for w in self.menu_frame.winfo_children():
            w.destroy()

        if self.is_menu:
            self.menu_frame.configure(width=200, fg_color="#222")

            self.name_label = CTkLabel(self.menu_frame, text="Змінити ім'я")
            self.name_label.pack(pady=20)

            self.name_entry = CTkEntry(self.menu_frame)
            self.name_entry.insert(0, self.username)
            self.name_entry.pack(pady=10)

            self.save_btn = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name)
            self.save_btn.pack(pady=10)

        else:
            self.menu_frame.configure(width=30)

    def save_name(self):
        if hasattr(self, "name_entry"):
            name = self.name_entry.get().strip()
            if name:
                self.username = name
                self.add(f"Ім'я змінено → {self.username}")

    # UI
    def ui(self):
        self.menu_frame.configure(height=self.winfo_height())

        menu_width = self.menu_frame.winfo_width()

        self.chat.place(x=menu_width, y=0)
        self.chat.configure(
            width=self.winfo_width() - menu_width,
            height=self.winfo_height() - 40
        )

        self.entry.place(x=menu_width, y=self.winfo_height() - 40)
        self.entry.configure(width=self.winfo_width() - menu_width - 40)

        self.send_btn.place(x=self.winfo_width() - 40, y=self.winfo_height() - 40)

        self.after(50, self.ui)

    # CHAT + EMOJI
    def add(self, text):
        emoji = random.choice(self.emojis)
        self.chat.configure(state="normal")
        self.chat.insert(END, f"{emoji} {text}\n")
        self.chat.configure(state="disabled")
        self.bell()

    # SEND
    def send(self):
        msg = self.entry.get()
        if msg:
            self.add(f"{self.username}: {msg}")
            try:
                self.sock.send(f"TEXT@{self.username}@{msg}\n".encode())
            except:
                pass
        self.entry.delete(0, END)

    # RECEIVE
    def recv(self):
        buffer = ""
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break

                buffer += data.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.after(0, self.handle, line.strip())
            except:
                break

    def handle(self, line):
        if not line:
            return

        parts = line.split("@", 2)

        if parts[0] == "TEXT" and len(parts) >= 3:
            self.add(f"{parts[1]}: {parts[2]}")


win = MainWindow()
win.mainloop()