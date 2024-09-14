import os
import glob
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from stride_gt_helper_augmented_new import stride_gt_creator  # Existing import
from Hop_New import stride_gt_creator as hop_new_function  # Import from Hop_New.py
from three2five_gt_csv import stride_gt_creator as three_to_five_csv  # Import from three2five_gt_csv.py
import threading
import time
import io
import sys

class RedirectedOutput:
    def __init__(self):
        self.output = io.StringIO()

    def write(self, message):
        self.output.write(message)

    def flush(self):
        pass

    def get_output(self):
        return self.output.getvalue()

def run_script():
    video_path = entry_video_path.get()

    if not os.path.isdir(video_path):
        messagebox.showerror("Error", "Invalid video folder path. Please select a valid directory.")
        return

    gt_path = os.path.join(video_path, "GT")

    if not os.path.exists(gt_path):
        os.makedirs(gt_path)

    selected_option = combobox_var.get()

    if selected_option not in ["XY", "HOP", "GT"]:
        messagebox.showerror("Invalid Input", "Please select a valid option from the dropdown.")
        return

    # Search for video files with .MP4 and .mov extensions
    video_files = sorted(glob.glob(f"{video_path}/*.MP4") + glob.glob(f"{video_path}/*.mp4") + glob.glob(f"{video_path}/*.mov") + glob.glob(f"{video_path}/*.MOV"))
    if not video_files:
        messagebox.showerror("Error", "No video files found in the selected directory.")
        return

    # Start the stopwatch
    start_stopwatch()

    # Run the script in a separate thread to avoid blocking the GUI
    threading.Thread(target=execute_script, args=(video_files, gt_path, selected_option)).start()

def execute_script(video_files, gt_path, selected_option):
    global redirected_output
    redirected_output = RedirectedOutput()
    original_stdout = sys.stdout
    sys.stdout = redirected_output

    try:
        for i in video_files:
            v = i
            vbn = os.path.basename(i)[:-4]  # Remove file extension from the base name

            if selected_option == "XY":
                print(vbn)
                csv_files = glob.glob(f"{gt_path}/GT_{vbn}*csv")
                if csv_files:
                    g = csv_files[0]
                    # Call the function from three2five_gt_csv.py
                    three_to_five_csv(video_path=v, old_gt_csv_path=g, out_dir=gt_path)
                else:
                    print(f"No CSV files found for {vbn} in {gt_path}.")
                print("////////////////////////////////////////////////////////////////////////////////")

            elif selected_option == "HOP":
                print(vbn)
                # Call the function from Hop_New.py
                hop_new_function(video_path=v, out_dir=gt_path)
                print("/////////////////////////////////////////////////////////////////////////////////")

            elif selected_option == "GT":
                print(vbn)
                try:
                    # Call the function from stride_gt_helper_augmented_new.py
                    stride_gt_creator(video_path=v, out_dir=gt_path)
                except Exception as e:
                    print(f"Failed to run stride_gt_creator: {e}")
                    return
                print("/////////////////////////////////////////////////////////////////////////////////")

        for i in glob.glob(f"{video_files[0].rsplit('/', 1)[0]}/*.xlsx"):
            shutil.move(i, f"{video_files[0].rsplit('/', 1)[0]}/InputVideos")

        messagebox.showinfo("Process Complete", "The script has been successfully executed.")
    finally:
        sys.stdout = original_stdout  # Restore original stdout
        stop_stopwatch()  # Stop the stopwatch once script execution is complete
        show_summary_page()  # Show summary page with execution time and terminal output

def show_summary_page():
    elapsed_time = time.time() - start_time
    mins, secs = divmod(elapsed_time, 60)
    hours, mins = divmod(mins, 60)
    time_taken = f"{int(hours):02}:{int(mins):02}:{int(secs):02}"

    summary_window = tk.Toplevel(root)
    summary_window.title("Execution Summary")

    tk.Label(summary_window, text=f"Time Taken: {time_taken}", font=("Helvetica", 14)).pack(pady=10)

    output_text = scrolledtext.ScrolledText(summary_window, width=100, height=30)
    output_text.pack(padx=10, pady=10)
    output_text.insert(tk.END, redirected_output.get_output())
    output_text.config(state=tk.DISABLED)  # Make the text area read-only

    tk.Button(summary_window, text="Close", command=summary_window.destroy).pack(pady=10)

# Stopwatch functions
def start_stopwatch():
    global stopwatch_running, start_time
    stopwatch_running = True
    start_time = time.time()  # Initialize start_time here
    update_stopwatch()

def stop_stopwatch():
    global stopwatch_running
    stopwatch_running = False

def update_stopwatch():
    if stopwatch_running:
        elapsed_time = time.time() - start_time
        mins, secs = divmod(elapsed_time, 60)
        hours, mins = divmod(mins, 60)
        time_display.set(f"{int(hours):02}:{int(mins):02}:{int(secs):02}")
        root.after(1000, update_stopwatch)  # Update every second

def select_video_folder():
    folder = filedialog.askdirectory()
    entry_video_path.delete(0, tk.END)
    entry_video_path.insert(0, folder)

# Initialize GUI
root = tk.Tk()
root.title("Script Runner")

frame = tk.Frame(root)
frame.pack(pady=10)

# Video Folder Path
tk.Label(frame, text="Video Folder Path:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
entry_video_path = tk.Entry(frame, width=50)
entry_video_path.grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame, text="Browse", command=select_video_folder).grid(row=0, column=2, padx=5, pady=5)

# Combobox for Option Selection
tk.Label(frame, text="Select Option:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
combobox_var = tk.StringVar()
combobox = ttk.Combobox(frame, textvariable=combobox_var, values=["XY", "HOP", "GT"], state="readonly")
combobox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
combobox.current(0)  # Set default selection to "XY"

# Run Button
tk.Button(frame, text="Run Script", command=run_script).grid(row=2, column=0, columnspan=3, pady=20)

# Stopwatch Display
time_display = tk.StringVar()
time_display.set("00:00:00")
tk.Label(root, textvariable=time_display, font=("Helvetica", 16)).pack(pady=10)

root.mainloop()

