import os
import sys
import json
import appdirs
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import filedialog
from tkinter import font
from winreg import ConnectRegistry, HKEY_CURRENT_USER, OpenKey, QueryValueEx
from plyer import notification

# Global variables
current_font_size = 12
recent_files_list = []
current_file = ""
icon_path = os.path.join(os.path.dirname(__file__), "icont.ico")
app_data_dir = appdirs.user_data_dir(appname='NotepadV', appauthor='vorlie')
os.makedirs(app_data_dir, exist_ok=True)

# Function to update recent files list
def update_recent_files(file_path):
    global recent_files_list
    if file_path in recent_files_list:
        recent_files_list.remove(file_path)
    recent_files_list.insert(0, file_path)
    recent_files_list = recent_files_list[:15]
    recent_files_path = os.path.join(app_data_dir, 'recent_files.json')
    with open(recent_files_path, 'w') as file:
        json.dump(recent_files_list, file)

# Function to open a recent file
def open_recent_file(file_path):
    global current_file
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            text_area.delete(1.0, "end") 
            text_area.insert("end", file_content)
            current_file = file_path
            root.title(f"Notepad by Vorlie - {file_path}")  
            update_recent_files(file_path)
            #print("DEBUG: Opened recent file:", file_path, current_file)
    except FileNotFoundError:
        messagebox.showerror("File Not Found", f"File {file_path} not found")

# Function to save a file
def save_file(event=None, file_path=None):
    global current_file
    if event:  # Check if the function was called by a keyboard shortcut event
        if current_file:
            with open(current_file, 'w') as file:
                file_content = text_area.get("1.0", "end-1c")
                file.write(file_content)
            update_recent_files(file_path)
        else:
            save_as_file()
    else:  # If the function was called without an event, use the provided file_path
        if file_path:
            with open(file_path, 'w') as file:
                file_content = text_area.get("1.0", "end-1c")
                file.write(file_content)
            update_recent_files(file_path)
        else:
            save_as_file()

# Function to save a file as
def save_as_file():
    file_path = filedialog.asksaveasfilename(initialfile="Untitled.txt",defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'w') as file:
            text = text_area.get("1.0", "end-1c")
            file.write(text)
            root.title(f"Notepad by Vorlie - {file_path}")
    update_recent_files(file_path)

# Function to open a file
def open_file():
    global current_file 
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        current_file = file_path 
        root.title(f"Notepad by Vorlie - {file_path}") 
        update_recent_files(file_path)
        with open(file_path, 'r') as file:
            text = file.read()
            text_area.delete("1.0", "end")
            text_area.insert("1.0", text)

# Function to zoom in and out
def zoom_in():
    global current_font_size
    text_area.configure(font=(default_font.actual("family"), current_font_size, "normal"))
    current_font_size += 2
def zoom_out():
    global current_font_size
    text_area.configure(font=(default_font.actual("family"), current_font_size, "normal"))
    current_font_size -= 2

# Function to check if dark mode is enabled in the system
def is_dark_mode_enabled():
    try:
        key = OpenKey(ConnectRegistry(None, HKEY_CURRENT_USER), r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except Exception as e:
        print("Error:", e)
        return False

# Function to apply dark mode or light mode based on system setting
def apply_system_theme(text_area):
    if is_dark_mode_enabled():
        text_area.configure(bg="gray20", fg="white")
    else:
        text_area.configure(bg="white", fg="black")

# Function to toggle dark mode
def toggle_dark_mode():
    global dark_mode_enabled
    if dark_mode_enabled:
        text_area.configure(bg="white", fg="black")
        dark_mode_enabled = False
    else:
        text_area.configure(bg="gray20", fg="white")
        dark_mode_enabled = True

# Function to create a new document
def create_new_document():
    text_area.delete(1.0, "end")  
    root.title("Notepad by Vorlie - Untitled") 
    global current_file
    current_file = None 

# Function to automatically save the file
def auto_save(text_area, current_file):
    if current_file:
        content = text_area.get("1.0", "end-1c") 
        with open(current_file, "w") as file:
            file.write(content)
            notification.notify(
                        title='Auto-Save',
                        message='Document auto-saved successfully',
                        app_name='NotepadV',
                        app_icon=icon_path)
            #print(f"DEBUG: Auto-saved {current_file}")

# Create the main window
root = tk.Tk()
root.title("Notepad by Vorlie - Untitled")
root.geometry("800x600")
root.iconbitmap(icon_path)
default_font = font.Font(family="Montserrat", size=12)
dark_mode_enabled = False
text_area = tk.Text(root, wrap="word", font=default_font)
text_area.pack(fill="both", expand=True)
apply_system_theme(text_area)
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
recent_menu = tk.Menu(file_menu, tearoff=0)

# Function to trigger auto-save
def trigger_auto_save():
    auto_save(text_area, current_file)
    root.after(300000, trigger_auto_save)

if len(sys.argv) > 1:
    file_path = sys.argv[1] 
    with open(file_path, 'r') as file:
        file_content = file.read()

    text_area.insert('1.0', file_content)  
    root.title(f"Notepad by Vorlie - {file_path}")  

# Recent files menu items
try:
    recent_files_path = os.path.join(app_data_dir, 'recent_files.json')
    with open(recent_files_path, 'r') as file:
        recent_files_list = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    recent_files_list = []

for file_path in recent_files_list:
    if file_path.endswith('.txt') and os.path.exists(file_path):
        recent_menu.add_command(label=os.path.basename(file_path), command=lambda path=file_path: open_recent_file(path))

# Add commands to the file menu
file_menu.add_command(label="Open", command=open_file, accelerator="Ctrl+O")
file_menu.add_command(label="New Document", command=create_new_document, accelerator="Ctrl+N")
file_menu.add_cascade(label="Recent Documents", menu=recent_menu)
file_menu.add_command(label="Save", command=save_file, accelerator="Ctrl+S")
file_menu.add_command(label="Save As", command=save_as_file, accelerator="Ctrl+Shift+S")
file_menu.add_command(label="Dark Mode", command=toggle_dark_mode, accelerator="Ctrl+D")
menu_bar.add_cascade(label="File", menu=file_menu)

# Add the zoom menu to the menu bar
zoom_menu = tk.Menu(menu_bar, tearoff=0)
zoom_menu.add_command(label="Zoom In", command=zoom_in, accelerator="Ctrl+=")
zoom_menu.add_command(label="Zoom Out", command=zoom_out, accelerator="Ctrl+-")
menu_bar.add_cascade(label="Zoom", menu=zoom_menu)

# Configure the menu bar
root.config(menu=menu_bar)

# Bind keyboard shortcuts
root.bind("<Control-equal>", lambda event: zoom_in())
root.bind("<Control-minus>", lambda event: zoom_out())
root.bind("<Control-d>", lambda event: toggle_dark_mode())
root.bind("<Control-o>", lambda event: open_file())
root.bind('<Control-s>', save_file)
root.bind("<Control-Shift-s>", lambda event: save_as_file())
root.bind("<Control-n>", lambda event: create_new_document())

# Trigger auto-save
root.after(300000, trigger_auto_save)

# Start the main event loop
root.mainloop()
