import os
import subprocess
import time
import re
from threading import Thread
import customtkinter as ctk
from tkinter import filedialog, messagebox

status_labels = []

def update_status_label(task_id, text):
    """
    Update the status label for a specific task.
    """
    if task_id < len(status_labels):
        status_labels[task_id].configure(text=text)

def add_status_label(task_text):
    """
    Add a new status label for a new task.
    """
    label = ctk.CTkLabel(progress_frame, text=task_text)
    label.grid(row=8 + len(status_labels), column=0, columnspan=3, pady=2, sticky="ew")
    status_labels.append(label)
    return len(status_labels) - 1  # Return the task ID

def remove_status_label(task_id):
    """
    Remove a status label when a task is completed.
    """
    if task_id < len(status_labels):
        status_labels[task_id].grid_forget()
        status_labels.pop(task_id)

def convert_to_wsl_path(windows_path):
    """
    Convert Windows path to Linux path for WSL2.
    """
    wsl_path = re.sub(r"^([a-zA-Z]):", lambda m: f"/mnt/{m.group(1).lower()}", windows_path)
    return wsl_path.replace("\\", "/")

def replace_space_with_underscore(input_text):
    return input_text.replace(' ', '_')

def sanitize_and_rename_folder(path):
    sanitized_path = replace_space_with_underscore(path)
    if sanitized_path != path:
        try:
            os.rename(path, sanitized_path)  # Rename folder
        except OSError as e:
            output_text.insert("end", f"\nFailed to check folder Name: {str(e)}. Please avoid using file paths that contain spaces.")
            messagebox.showwarning("Fail To read Folder Name", "Please avoid using file paths that contain spaces.")
    return sanitized_path

def get_file_count(folder_path):
    if not os.path.exists(folder_path):
        return 0
    return len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])

def update_progress(input_path, translated_path):
    total_files = get_file_count(input_path)
    if total_files == 0:
        return

    while True:
        translated_files = get_file_count(translated_path)
        progress = int((translated_files / total_files) * 100)
       # status_label.configure("working...")

def run_docker_command():
    input_path = path_entry.get()
    if not input_path:
        output_text.insert("end", "Please enter a folder path.")
        return

    input_path = sanitize_and_rename_folder(input_path)
    translated_path = f"{input_path}-translated"

    # Convert to UTF-8 encoded path
    input_path = input_path.encode('utf-8').decode('utf-8')
    translated_path = translated_path.encode('utf-8').decode('utf-8')

    docker_env = docker_env_var.get()

    if docker_env == "wsl":
        # Convert to WSL path
        input_path_docker = convert_to_wsl_path(input_path)
        translated_path_docker = convert_to_wsl_path(translated_path)
    else:
        # Use Windows path for Docker Desktop
        input_path_docker = input_path
        translated_path_docker = translated_path

    cpus = cpu_combo.get()
    use_gpu = gpu_var.get() == "gpu"
    translator = translator_combo.get()
    lang = lang_combo.get()
    detector_type= detector_combo.get()
    direction_command = ""
    if direction_combo.get() == "vertical" :
        direction_command = "--force-vertical"
    elif direction_combo.get() == "horizontal" :
        direction_command = "--force-horizontal"

    mkdir_command = f"mkdir -p \"{translated_path}\""
    docker_command = (
        f"{'wsl ' if docker_env == 'wsl' else ''}docker run --cpus={cpus} "
        f"{'--gpus=all ' if use_gpu else ''} -v \"{input_path_docker}:/app/translatetarget\""
        f" -v \"{translated_path_docker}:/app/translatetarget-translated\" --ipc=host --rm "
        "zyddnys/manga-image-translator:main --mode=batch -i=/app/translatetarget"
        f" -l={lang} --translator={translator}"
        f" {direction_command}"
        f"{' --use-gpu ' if use_gpu else ''} --detector={detector_type}"
    )
    del_command = (
        f"'rd /S /Q \"{input_path_docker}\""
    )
    # Show confirmation popup
    confirm_debug_message = f"The following command will be executed:\n\n{docker_command}\n\nDo you want to proceed? \n\n※ Running multiple tasks simultaneously may slow down depending on your computer's performance."
    confirm_message = "Do you want to proceed? \n\n※ Running multiple tasks simultaneously may slow down depending on your computer's performance."
    user_response = messagebox.askyesno("Command Confirmation", confirm_message)
    # output_text.insert(tk.END, confirm_message)
    if not user_response:
        output_text.insert("end", "\nCommand execution canceled.")
        return

    def execute_commands():
        try:
            task_id = add_status_label(f"Task is Working... {input_path}")

            process = subprocess.Popen(
                mkdir_command,
                shell=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'  # Explicit UTF-8 setting
            )
            process.wait()

            process = subprocess.Popen(
                docker_command,
                shell=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'  # Explicit UTF-8 setting
            )
            for line in iter(process.stdout.readline, ""):
                output_text.insert("end", line)
                output_text.see("end")

            process.wait()
            if process.returncode == 0:
                output_text.insert("end", "\nCommand executed successfully!")
                time.sleep(2)
                remove_status_label(task_id)
                radio_del_yn = radio_del_var.get()
                if radio_del_yn == "Yes":
                    process = subprocess.Popen(
                        del_command,
                        shell=True,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        encoding='utf-8'  # Explicit UTF-8 setting
                    )
                    process.wait()
            else:
                error_output = process.stderr.read()
                output_text.insert("end", error_output)
                output_text.insert("end", "An error occurred. Check the output for details.")
                update_status_label(task_id, f"Task failed: {error_output}")
        except Exception as e:
            output_text.insert("end", f"Exception occurred: {str(e)}")
            update_status_label(task_id, f"Task failed: {str(e)}")

    Thread(target=execute_commands).start()
    #Thread(target=update_progress, args=(input_path, translated_path)).start()

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        sanitized_path = sanitize_and_rename_folder(folder_path)
        path_entry.delete(0, "end")
        path_entry.insert(0, sanitized_path)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Manga Translator Batch Executer V1.0")

# Configure grid layout for root
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Main Frame
main_frame = ctk.CTkFrame(root)
main_frame.grid(padx=10, pady=10, sticky="nsew")
main_frame.grid_rowconfigure(9, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Folder Path Input
path_frame = ctk.CTkFrame(main_frame)
path_frame.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")
path_frame.columnconfigure(1, weight=1)

path_label = ctk.CTkLabel(path_frame, text="Folder Location:")
path_label.grid(row=0, column=0, padx=5)

path_entry = ctk.CTkEntry(path_frame)
path_entry.grid(row=0, column=1, padx=5, sticky="ew")

browse_button = ctk.CTkButton(path_frame, text="Browse", command=browse_folder, width=80)
browse_button.grid(row=0, column=2, padx=2)

run_button = ctk.CTkButton(path_frame, text="Execute", command=run_docker_command, width=150, bg_color="red", fg_color="black")
run_button.grid(row=0, column=3, padx=2)

# Language Selection

option_base_frame = ctk.CTkFrame(main_frame)
option_base_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")
option_base_frame.columnconfigure(1, weight=1)

option_base_label = ctk.CTkLabel(option_base_frame, text="Base Options")
option_base_label = option_base_label.grid(row=0, column=0, padx=5, sticky="ew")

lang_label = ctk.CTkLabel(option_base_frame, text="Target Language:")
lang_label.grid(row=1, column=0, padx= 5, pady=5, sticky="w")
lang_combo = ctk.CTkComboBox(option_base_frame, values=["KOR", "ENG", "CHS", "JPN"])
lang_combo.set("KOR")
lang_combo.grid(row=1, column=1, pady=5, sticky="ew")

# Delete Origin Radio Buttons
radio_del_label = ctk.CTkLabel(option_base_frame, text="Delete Origin:")
radio_del_label.grid(row=1, column=2, padx= 10, pady=5, sticky="w")
radio_del_var = ctk.StringVar(value="Yes")

radio_del_yes = ctk.CTkRadioButton(option_base_frame, text="Yes", variable=radio_del_var, value="Yes")
radio_del_yes.grid(row=1, column=3, sticky="w")

radio_del_no = ctk.CTkRadioButton(option_base_frame, text="No", variable=radio_del_var, value="No")
radio_del_no.grid(row=1, column=4, sticky="w")


# Translator Selection
translator_label = ctk.CTkLabel(option_base_frame, text="Translator:")
translator_label.grid(row=2, column=0, padx= 5, pady=5, sticky="w")
translator_combo = ctk.CTkComboBox(option_base_frame, values=["papago", "google", "Textless", "m2m100"])
translator_combo.set("papago")
translator_combo.grid(row=2, column=1, pady=5, sticky="ew")

direction_label = ctk.CTkLabel(option_base_frame, text="Direction:")
direction_label.grid(row=2, column=2, pady=5, padx=10, sticky="w")
direction_combo = ctk.CTkComboBox(option_base_frame, values=["auto", "horizontal", "vertical"])
direction_combo.set("auto")
direction_combo.grid(row=2, column=3, pady=5, sticky="ew")

# Docker Environment Selection
option_env_frame = ctk.CTkFrame(main_frame)
option_env_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")
option_env_frame.columnconfigure(1, weight=5)
option_env_frame.columnconfigure(2, weight=5)

env_label = ctk.CTkLabel(option_env_frame, text="System Environment")
env_label.grid(row=1, column=0, pady=1, padx=5, sticky="ew")

docker_env_label = ctk.CTkLabel(option_env_frame, text="Docker Environment :")
docker_env_label.grid(row=2, column=0, pady=5, padx=5, sticky="w")
docker_env_var = ctk.StringVar(value="desktop")
radio_docker_desktop = ctk.CTkRadioButton(option_env_frame, text="Docker Desktop", variable=docker_env_var, value="desktop")
radio_docker_desktop.grid(row=2, column=1, sticky="w")
radio_wsl = ctk.CTkRadioButton(option_env_frame, text="WSL", variable=docker_env_var, value="wsl")
radio_wsl.grid(row=2, column=2, sticky="w")

# Detector Selection
detector_label = ctk.CTkLabel(option_env_frame, text="Detector :")
detector_label.grid(row=2, column=3, pady=5, padx=5, sticky="w")
detector_combo = ctk.CTkComboBox(option_env_frame, values=["default", "dbconvnext", "ctd", "craft"])
detector_combo.set("default")
detector_combo.grid(row=2, column=4, pady=5, padx=5,  sticky="ew")

# CPU/GPU Options

option_gpu_frame = ctk.CTkFrame(main_frame)
option_gpu_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")

# 열 비율 조정
option_gpu_frame.columnconfigure(0, weight=1)  # 라벨 열
option_gpu_frame.columnconfigure(1, weight=2)  # GPU/CPU 버튼 열
option_gpu_frame.columnconfigure(2, weight=2)  # CPU Cores 열
option_gpu_frame.columnconfigure(3, weight=1)  # 추가 설명 열

# 옵션 라벨
option_gpu_label = ctk.CTkLabel(option_gpu_frame, text="CPU/GPU Options")
option_gpu_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="w")  # 전체 폭으로 배치

# Translator 라벨
gpuopt_label = ctk.CTkLabel(option_gpu_frame, text="Translator:")
gpuopt_label.grid(row=1, column=0, pady=5, padx=5, sticky="w")

# GPU/CPU 라디오 버튼
gpu_var = ctk.StringVar(value="cpu")
radio_cpu = ctk.CTkRadioButton(option_gpu_frame, text="Use CPU", variable=gpu_var, value="cpu")
radio_cpu.grid(row=1, column=1, pady=5, sticky="w")

radio_gpu = ctk.CTkRadioButton(option_gpu_frame, text="Use GPU", variable=gpu_var, value="gpu")
radio_gpu.grid(row=1, column=2, pady=5, sticky="w")

# CPU Cores 라벨 및 콤보박스
cpu_label = ctk.CTkLabel(option_gpu_frame, text="CPU Cores:")
cpu_label.grid(row=2, column=0, pady=5, padx=5, sticky="w")

cpu_combo = ctk.CTkComboBox(option_gpu_frame, values=["1", "2", "3", "4", "5", "6"])
cpu_combo.set("2")
cpu_combo.grid(row=2, column=1, columnspan=2, pady=5, sticky="ew")  # CPU 콤보박스가 열을 차지

# 설명 라벨 (별도 행으로 분리)
cpu_comment_label1 = ctk.CTkLabel(option_gpu_frame, text="Typically, avoid setting the CPU to more than 2 cores.")
cpu_comment_label1.grid(row=3, column=0, columnspan=4, pady=1, padx=5, sticky="w")

cpu_comment_label2 = ctk.CTkLabel(option_gpu_frame, text="If WSL2 with Nvidia is available, consider using the GPU instead.")
cpu_comment_label2.grid(row=4, column=0, columnspan=4, pady=1, padx=5, sticky="w")

# Progress Check
progress_frame = ctk.CTkFrame(main_frame, width=600, height=60)
progress_frame.grid(row=4, column=0, columnspan=3, pady=5, sticky="ew")
#status_label = ctk.CTkLabel(main_frame, text="Wait Operation...(When running multiple tasks simultaneously, it does not display correctly.)")
#status_label.grid(row=8, column=0, columnspan=3, pady=10, sticky="ew")

# Output Box
output_text = ctk.CTkTextbox(main_frame, width=600, height=100)
output_text.grid(row=5, column=0, columnspan=3, pady=10, sticky="nsew")

# Comments Section
comment_frame = ctk.CTkFrame(main_frame)
comment_frame.grid(row=6, column=0, columnspan=3, pady=0, sticky="ew")

comment_label_1 = ctk.CTkLabel(comment_frame, text="This is a GUI application designed to provide users with easy access", text_color="green")
comment_label_1.grid(row=0, column=0, pady=0, sticky="w")
comment_label_1 = ctk.CTkLabel(comment_frame, text="to the zyddnys/manga-image-translator project.", text_color="green")
comment_label_1.grid(row=1, column=0, pady=0, sticky="w")
comment_label_2 = ctk.CTkLabel(comment_frame, text="I respect all translators. Thank you.", text_color="green")
comment_label_2.grid(row=2, column=0, pady=0, sticky="w")
comment_label_3 = ctk.CTkLabel(comment_frame, text="Created By FromWhiteAsh", text_color="gray")
comment_label_3.grid(row=3, column=0, pady=0, sticky="w")

root.mainloop()
