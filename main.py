import os
import sys
import json
import appdirs
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import filedialog
from tkinter import font



recent_files_list = []
current_file = ""

# Get the path to the user's data directory
app_data_dir = appdirs.user_data_dir(appname='NotepadV', appauthor='vorlie')
os.makedirs(app_data_dir, exist_ok=True)

# Function to update recent files list
def update_recent_files(file_path):
    global recent_files_list
    if file_path in recent_files_list:
        recent_files_list.remove(file_path)
    recent_files_list.insert(0, file_path)
    # Limit the list to 10 recent files
    recent_files_list = recent_files_list[:10]
    # Save recent files list to a JSON file
    recent_files_path = os.path.join(app_data_dir, 'recent_files.json')
    with open(recent_files_path, 'w') as file:
        json.dump(recent_files_list, file)

# Function to open a recent file
def open_recent_file(file_path):
    global current_file
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            text_area.delete(1.0, "end") # Clear the text area
            text_area.insert("end", file_content) # Insert the file content into the text area
            current_file = file_path
            root.title(f"Notepad by Vorlie - {file_path}")  # Update the window title to include the full file path
            update_recent_files(file_path) # Update the recent files list
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
        else:
            save_as_file()
    else:  # If the function was called without an event, use the provided file_path
        if file_path:
            with open(file_path, 'w') as file:
                file_content = text_area.get("1.0", "end-1c")
                file.write(file_content)
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
    global current_file  # Declare current_file as a global variable
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        current_file = file_path  # Store the file path in the current_file variable
        root.title(f"Notepad by Vorlie - {file_path}")  # Set the window title to display the file path
        update_recent_files(file_path)
        with open(file_path, 'r') as file:
            text = file.read()
            text_area.delete("1.0", "end")
            text_area.insert("1.0", text)


current_font_size = 12
# Function to zoom in and out
def zoom_in():
    global current_font_size
    text_area.configure(font=(default_font.actual("family"), current_font_size, "normal"))
    current_font_size += 2

def zoom_out():
    global current_font_size
    text_area.configure(font=(default_font.actual("family"), current_font_size, "normal"))
    current_font_size -= 2
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

# Create the main window
root = tk.Tk()
root.title("Notepad by Vorlie - Untitled")
root.geometry("800x600")
icon_path = os.path.join(os.path.dirname(__file__), "icont.ico")
root.iconbitmap(icon_path)
# Create the text area
default_font = font.Font(family="Montserrat", size=12)
dark_mode_enabled = False
text_area = tk.Text(root, wrap="word", font=default_font)
text_area.pack(fill="both", expand=True)
# Create the menu bar
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
recent_menu = tk.Menu(file_menu, tearoff=0)

if len(sys.argv) > 1: 
    file_path = sys.argv[1] 
    with open(file_path, 'r') as file:
        file_content = file.read() 
    text_area.insert('1.0', file_content)
    root.title(f"Notepad by Vorlie - {file_path}") 

# Load recent files from JSON
try:
    recent_files_path = os.path.join(app_data_dir, 'recent_files.json')
    with open(recent_files_path, 'r') as file:
        recent_files_list = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    recent_files_list = []

# Add recent files to the recent menu
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

# Bind the zoom_in function to the Ctrl++ key combination
root.bind("<Control-equal>", lambda event: zoom_in())
# Bind the zoom_out function to the Ctrl+- key combination
root.bind("<Control-minus>", lambda event: zoom_out())
# Bind the toggle_dark_mode function to the Ctrl+D key combination
root.bind("<Control-d>", lambda event: toggle_dark_mode())
# Bind the open_file function to the Ctrl+O key combination
root.bind("<Control-o>", lambda event: open_file())
# Bind the save_file function to the Ctrl+S key combination
root.bind("<Control-s>", lambda event: save_file())
# Bind the save_as_file function to the Ctrl+Shift+S key combination
root.bind("<Control-Shift-s>", lambda event: save_as_file())
# Bind the create_new_document function to the Ctrl+N key combination
root.bind("<Control-n>", lambda event: create_new_document())

# Start the main event loop
root.mainloop()
