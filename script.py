import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import requests
from PIL import Image, ImageTk
import io
import platform
import socket
import psutil
import subprocess
import sys

def load_image_from_url(url, max_height):
    try:
        response = requests.get(url)
        response.raise_for_status()
        img_data = response.content
        pil_image = Image.open(io.BytesIO(img_data))
        ratio = max_height / pil_image.height
        new_width = int(pil_image.width * ratio)
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.ANTIALIAS
        resized_image = pil_image.resize((new_width, max_height), resample)
        return ImageTk.PhotoImage(resized_image)
    except Exception as e:
        print("Ошибка загрузки изображения:", e)
        return None

def get_geolocation(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        info = (
            f"IP: {data.get('ip', 'N/A')}\n"
            f"Город: {data.get('city', 'N/A')}\n"
            f"Регион: {data.get('region', 'N/A')}\n"
            f"Страна: {data.get('country', 'N/A')}\n"
            f"Провайдер: {data.get('org', 'N/A')}\n"
            f"Часовой пояс: {data.get('timezone', 'N/A')}"
        )
        return info
    except Exception as e:
        return f"Ошибка при получении геолокации: {e}"

def ping_ip(ip):
    try:
        param = '-n' if sys.platform.lower().startswith('win') else '-c'
        command = ['ping', param, '1', ip]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "Доступен (ping успешен)" if result.returncode == 0 else "Недоступен (ping неудачен)"
    except Exception as e:
        return f"Ошибка при пинге: {e}"

def get_system_info():
    username = platform.node()
    user_login = socket.gethostname()
    os_info = f"{platform.system()} {platform.release()} ({platform.architecture()[0]})"
    cpu = platform.processor()
    ram = round(psutil.virtual_memory().total / (1024**3), 2)
    return (
        f"Имя компьютера: {username}\n"
        f"Имя пользователя (хост): {user_login}\n"
        f"Операционная система: {os_info}\n"
        f"Процессор: {cpu}\n"
        f"Оперативная память: {ram} ГБ"
    )

def center_window(window, width, height):
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_result_window(info_text):
    result_win = tk.Toplevel()
    result_win.title("IPLOCATE")
    width, height = 500, 380
    center_window(result_win, width, height)

    label = ttk.Label(result_win, text=info_text, font=("Arial", 9), justify='left', anchor='nw')
    label.pack(padx=20, pady=20, fill='both', expand=True)

    btn_frame = ttk.Frame(result_win)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Другой IP", command=lambda: [result_win.destroy(), start_process(result_win.master)]).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Закрыть", command=result_win.destroy).grid(row=0, column=1, padx=10)


def start_process(root):
    root.withdraw()

    ip_dialog = tk.Toplevel()
    ip_dialog.title("IPLOCATE")
    center_window(ip_dialog, 400, 150)

    container = ttk.Frame(ip_dialog)
    container.pack(expand=True, fill='both', pady=10)

    ttk.Label(container, text="Введите IP-адрес:", font=("Arial", 11)).pack(pady=(10, 5))
    ip_entry = ttk.Entry(container, font=("Arial", 11), width=40)
    ip_entry.pack(pady=5)
    ip_entry.focus()

    btn_frame = ttk.Frame(container)
    btn_frame.pack(pady=(10, 5))

    def on_submit(event=None):
        ip = ip_entry.get().strip()
        if not ip:
            messagebox.showerror("Ошибка", "IP-адрес не введён", parent=ip_dialog)
            return
        ip_dialog.destroy()

        geo_info = get_geolocation(ip)
        ping_result = ping_ip(ip)
        system_info = get_system_info()

        full_message = (
            f"Информация по IP-адресу [{ip}]:\n\n"
            f"{geo_info}\n\n"
            f"Результат проверки доступности:\n{ping_result}\n\n"
            f"Технические характеристики компьютера:\n{system_info}"
        )

        show_result_window(full_message)

    ip_entry.bind('<Return>', on_submit)  # Enter = OK

    ttk.Button(btn_frame, text="OK", command=on_submit).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Отмена", command=lambda: [ip_dialog.destroy(), root.deiconify()]).grid(row=0, column=1, padx=10)

def create_welcome_window():
    root = tk.Tk()
    root.title("IPLOCATE")
    width, height = 500, 320
    center_window(root, width, height)
    root.resizable(False, False)

    image_url = "https://raw.githubusercontent.com/Gndrgno/img44/refs/heads/main/IPLOCATE.png"
    img = load_image_from_url(image_url, max_height=320)

    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)

    if img:
        img_label = ttk.Label(main_frame, image=img)
        img_label.image = img
        img_label.grid(row=0, column=0, sticky='w', padx=(0, 20))
    else:
        ttk.Label(main_frame, text="[Изображение не доступно]").grid(row=0, column=0, sticky='w')

    right_frame = ttk.Frame(main_frame)
    right_frame.grid(row=0, column=1, sticky='nsew')
    main_frame.columnconfigure(1, weight=1)

    # Фиксированный блок текста с выравниванием по центру
    text_container = tk.Frame(right_frame, width=350, height=220)
    text_container.grid(row=0, column=0, pady=(20, 10))
    text_container.pack_propagate(False)  # Чтобы сохранить фиксированный размер

    text_label = ttk.Label(
        text_container,
        text=(
            "Добро пожаловать в IPLOCATE!\n\n"
            "Эта программа поможет найти данные о пользователе через IP-адрес.\n"
            "Введите IP-адрес для проверки, и программа покажет геолокацию,\n"
            "проверит доступность и отобразит технические характеристики вашего компьютера."
        ),
        wraplength=330,
        font=("Arial", 10),
        justify='center',
        anchor='center'
    )
    text_label.pack(expand=True, fill='both')

    btn_frame = ttk.Frame(right_frame)
    btn_frame.grid(row=1, column=0, sticky='se', pady=10)

    ttk.Button(btn_frame, text="Начать", command=lambda: start_process(root)).grid(row=0, column=0, padx=5)
    ttk.Button(btn_frame, text="Отмена", command=root.destroy).grid(row=0, column=1, padx=5)

    root.mainloop()

if __name__ == "__main__":
    create_welcome_window()
