import tkinter as tk
from tkinter import messagebox

def check_command():
    user_input = entry.get().strip()
    if user_input == "sudo":
        label_output.config(text="SUDO: This means 'SuperUser DO'. It gives you admin powers!")
    elif user_input == "i am a complete beginner":
        import webbrowser
        webbrowser.open("https://wiki.archlinux.org")
    elif user_input == "grep":
        label_output.config(text="grep means global regular expression print, in plain english, it means searching through a file")
    elif user_input == "ls":
        label_output.config(text="This is used for listing files or directories (folders)")
    elif user_input == "rm":
        label_output.config(text="be careful with rm. while it is useful for deleting files you no longer need, if you  type sudo rm -rf /, it is gonna vaporize your whole system")
    elif user_input == "i do not know what to type":
        label_output.config(text="get the hell out of here")
    elif user_input == "mkdir":
        label_output.config(text="this stands for make directory. in windows terms it simply creates a folder")
    elif user_input == "ping":
        label_output.config(text="this is used to check your internet status. even pros use it when their internet drops")
    elif user_input == "pwd":
        label_output.config(text="this is used to show you where you are in the filesystem, basically in which folder you are inside")
    elif user_input == "why do all this when i can just click buttons":
        label_output.config(text="good question. you are basically saying, why type all this cryptic text when i can just click? because it is more honest. when you click buttons, you trigger one of these under the hood.")

root = tk.Tk()
root.title("Linux Command Dictionary")
root.geometry("400x200")


entry = tk.Entry(root)
entry.pack(pady=10)

btn = tk.Button(root, text="Explain Command", command=check_command)
btn.pack(pady=5)

label_output = tk.Label(root, text="", wraplength=350)
label_output.pack(pady=10)

root.mainloop()