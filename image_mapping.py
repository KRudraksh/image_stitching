import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
from pathlib import Path
from PIL import Image, ImageTk

def select_video():
    global video_path, video_name, video_size
    video_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
    if video_path:
        video_name.set(f"Name: {os.path.basename(video_path)}")
        try:
            video_size.set(f"Size: {os.path.getsize(video_path) / (1024 * 1024):.2f} MB")
        except OSError:
            video_size.set("Size: Unable to determine")

def start_process():
    if not video_path:
        messagebox.showerror("Error", "No video selected!")
        return

    video_name_only = os.path.basename(video_path).rsplit(".", 1)[0]
    output_folder = Path(f"log_{video_name_only}")  # Prefix the folder with 'log_'
    compressed_folder = output_folder / "compressed_data"
    destination_folder = Path(f"results_{video_name_only}")  # Prefix the results folder with 'results_'

    # Update status display
    def update_status(step):
        status.set(f"Current step: {step}")
        root.update_idletasks()  # Ensures the GUI updates immediately

    try:
        # Step 1: Execute convert.py
        update_status("Extracting images...")
        subprocess.run(["python", "convert.py", video_path,"--output_folder", str(output_folder)], check=True)

        # Step 2: Execute resize.py
        update_status("Resizing images...")
        if not output_folder.exists():
            raise FileNotFoundError(f"Output folder {output_folder} not found!")
        compressed_folder.mkdir(parents=True, exist_ok=True)
        subprocess.run(["python", "resize.py", str(output_folder), str(compressed_folder)], check=True)

        # Step 3: Execute main.py
        update_status("Creating map...")
        destination_folder.mkdir(parents=True, exist_ok=True)  # Ensure destination folder exists
        subprocess.run(["python", "main.py", str(compressed_folder), str(destination_folder)], check=True)

        update_status("Process completed successfully!")
        messagebox.showinfo("Success", "Process completed successfully!")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error during execution: {e}")
        update_status("Error occurred during processing.")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")
        update_status("Error occurred during processing.")

# Tkinter GUI
root = tk.Tk()
root.title("Image Mapping Software")
root.geometry("800x600")  # Set window size to 800x600 pixels


video_name = tk.StringVar(value="Name: Not selected")
video_size = tk.StringVar(value="Size: Not available")
status = tk.StringVar(value="Status: Waiting for user input...")
video_path = ""

# Layout
tk.Label(root, text="IMAGE MAPPING", font=("Helvetica", 20)).pack(pady=20)
tk.Label(root, text="Bombay Dynamics - WWF India", font=("Helvetica", 14)).pack(pady=5)  # New text line


tk.Button(root, text="Select Video", command=select_video, width=20).pack(pady=10)
tk.Label(root, textvariable=video_name, font=("Helvetica", 14)).pack(pady=5)
tk.Label(root, textvariable=video_size, font=("Helvetica", 14)).pack(pady=5)

tk.Button(root, text="Start Process", command=start_process, width=20, bg="green", fg="white").pack(pady=30)
tk.Label(root, textvariable=status, font=("Helvetica", 14), fg="blue").pack(pady=20)

root.mainloop()
