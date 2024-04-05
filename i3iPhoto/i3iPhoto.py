from codecs import backslashreplace_errors
import tkinter as tk
from tkinter import ttk, filedialog
from turtle import bgcolor
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
from io import BytesIO

class PhotoiSiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("i3iPhoto")

        # Отримання розмірів екрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 500
        window_height = 400
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        
        self.root.resizable(width=False, height=False)

        # Встановлення нових розмірів та позиції вікна
        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        self.root.configure(bg='#001F3F')

        # Верхнє меню
        self.menu_frame = tk.Frame(root, bg='#001F3F')
        self.menu_frame.pack(side=tk.TOP, fill=tk.X)

        # Кнопки
        self.choose_button = tk.Button(self.menu_frame, text="Choose Photo", command=self.open_image, bg='#00FFFF', fg='#001F3F', relief=tk.RAISED, bd=3)
        self.choose_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.improve_button = tk.Button(self.menu_frame, text="Improve Photo Quality", command=self.improve_quality, state=tk.DISABLED, bg='#00FFFF', fg='#800080', relief=tk.RAISED, bd=3)
        self.improve_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.info_button = tk.Button(self.menu_frame, text="Information", command=self.show_info_window, bg='#00FFFF', fg='#800080', relief=tk.RAISED, bd=3)
        self.info_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.save_button = tk.Button(self.menu_frame, text="Save Photo", command=self.save_image, state=tk.DISABLED, bg='#00FFFF', fg='#006400', relief=tk.RAISED, bd=3)
        self.save_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Нижнє меню
        self.bottom_frame = tk.Frame(root, bg='lightgray')
        self.bottom_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        # Розмір фото
        label_size = tk.Label(self.bottom_frame, text="Photo Size:", bg='lightgray', fg='blue')
        label_size.grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)

        self.size_var = tk.StringVar()
        self.size_var.set("A1")

        sizes = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"]
        self.size_dropdown = tk.OptionMenu(self.bottom_frame, self.size_var, *sizes)
        self.size_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.size_dropdown.config(bg='#800080', fg='yellow')

        self.size_var.trace_add("write", self.on_size_change)

        # Формат фото
        label_format = tk.Label(self.bottom_frame, text="Photo Format:", bg='lightgray', fg='blue')
        label_format.grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)

        self.format_var = tk.StringVar()
        self.format_var.set("png")

        # Оновлені формати
        all_formats = ["png", "jpg", "jpeg", "ico", "bmp"]
        self.format_dropdown = tk.OptionMenu(self.bottom_frame, self.format_var, *all_formats)
        self.format_dropdown.config(bg='#800080', fg='yellow')

        self.format_dropdown.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        self.format_dropdown.bind("<<ComboboxSelected>>", self.on_combobox_select)

        # Текстові поля для висоти та ширини з валідацією
        label_height = tk.Label(self.bottom_frame, text="Height:", bg='lightgray', fg='blue')
        label_width = tk.Label(self.bottom_frame, text="Width:", bg='lightgray', fg='blue')

        label_height.grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        label_width.grid(row=2, column=2, padx=5, pady=5, sticky=tk.E)

        validate_float = (root.register(self.validate_float), '%P')

        self.height_entry = tk.Entry(self.bottom_frame, width=10, validate='key', validatecommand=validate_float, bg='lightgray', fg='#006400')
        self.width_entry = tk.Entry(self.bottom_frame, width=10, validate='key', validatecommand=validate_float, bg='lightgray', fg='#006400')

        self.height_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.width_entry.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)

        self.height_entry.insert(0, "0")
        self.width_entry.insert(0, "0")

        self.height_entry.bind("<FocusOut>", self.on_focus_out_height)
        self.width_entry.bind("<FocusOut>", self.on_focus_out_width)

        # ImageBox та Label
        self.image_frame = tk.Frame(root, bg='#001F3F')
        self.image_frame.pack(expand=True)

        self.image_label = tk.Label(self.image_frame, bg='#001F3F')
        self.image_label.pack(pady=10)

        self.label_under_image = tk.Label(self.image_frame, text="", fg='lightgreen', bg='#001F3F')
        self.label_under_image.pack()

        self.status_label = tk.Label(root, text="", bg='#001F3F', fg='yellow')
        self.status_label.pack(pady=5)

    def on_combobox_select(self, event):
        self.root.focus_set()
    
    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.ico;*.bmp")])
        if file_path:
            self.display_image(file_path)
            self.improve_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)

    def display_image(self, file_path):
        image = Image.open(file_path)
        self.original_image = image.copy()

        original_width, original_height = image.size

        fixed_width = 400
        width_percent = (fixed_width / float(original_width))
        fixed_height = int((float(original_height) * float(width_percent)))

        resized_image = image.resize((fixed_width, fixed_height), Image.LANCZOS)

        self.update_text_fields(original_width, original_height)

        photo = ImageTk.PhotoImage(resized_image)
        self.image_label.config(image=photo)
        self.image_label.image = photo
        self.status_label.config(text=f"Selected photo: {file_path}")

        file_name = file_path.split("/")[-1]
        self.label_under_image.config(text=f"Photo: {file_name}")

        file_format = file_path.split(".")[-1]
        self.format_var.set(file_format.lower())
        self.format_dropdown.update()

        # Отримання розмірів екрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Отримання розмірів та позиції вікна
        window_width = fixed_width + 40  # Додатковий простір для відступів та рамок
        window_height = fixed_height + 200  # Додаткова висота для інших віджетів та відступів
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    def update_text_fields(self, width, height):
        self.height_entry.delete(0, tk.END)
        self.width_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(height))
        self.width_entry.insert(0, str(width))

    def resize_image(self, width, height):
        resized_image = self.original_image.resize((width, height))
        return resized_image

    def improve_quality(self):
        if hasattr(self, 'original_image'):
            enhanced_image = self.original_image.copy()

            # Корекція експозиції
            enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = enhancer.enhance(1.2)  # фактор енгансмента

            # Корекція кольору
            enhancer = ImageEnhance.Color(enhanced_image)
            enhanced_image = enhancer.enhance(1.2)

            self.status_label.config(text="Photo improved")
            self.improved_image = enhanced_image

            self.save_improved_image()

    def save_improved_image(self, quality=95):
        if hasattr(self, 'improved_image'):
            selected_format = "png"
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())

            resized_image = self.resize_image(width, height)

            file_path = filedialog.asksaveasfilename(defaultextension=f".{selected_format}",
            filetypes=[(f"{selected_format.upper()} files", f"*.{selected_format}")])
            
            if file_path:
                try:
                    self.improved_image.save(file_path, format=selected_format.upper(), quality=quality)
                    self.status_label.config(text=f"Improved photo saved at path: {file_path}")
                except Exception as e:
                    self.status_label.config(text=f"Error while saving: {e}")

    def save_image(self):
        selected_format = self.format_var.get()
        width = int(self.width_entry.get())
        height = int(self.height_entry.get())
        resized_image = self.resize_image(width, height)

        file_path = filedialog.asksaveasfilename(defaultextension=f".{selected_format}", filetypes=[(f"{selected_format.upper()} files", f"*.{selected_format}")])

        if file_path:
            try:
                if selected_format.lower() == "jpg":
                    quality = 95
                    dpi = (300, 300)
                    resized_image.save(file_path, format="JPEG", quality=quality, dpi=dpi)
                elif selected_format.lower() == "ico":
                    icon_sizes = [(256, 256)]
                    resized_image.save(file_path, format="ICO", sizes=icon_sizes)
                else:
                    resized_image.save(file_path, format=selected_format.upper())
                self.status_label.config(text=f"Photo saved at path: {file_path}")
            except Exception as e:
                self.status_label.config(text=f"Error while saving: {e}")

    def on_size_change(self, *args):
        selected_size = self.size_var.get()
        width, height = self.get_dimensions_for_size(selected_size)

        self.height_entry.delete(0, tk.END)
        self.width_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(height))
        self.width_entry.insert(0, str(width))

    def get_dimensions_for_size(self, selected_size):
        size_dimensions = {
            "A1": (594, 841),
            "A2": (420, 594),
            "A3": (297, 420),
            "A4": (210, 297),
            "A5": (148, 210),
            "A6": (105, 148),
            "A7": (74, 105),
            "A8": (52, 74),
            "A9": (37, 52),
            "A10": (26, 37),
        }
        return size_dimensions.get(selected_size, (0, 0))

    def validate_float(self, value):
        try:
            if not value:
                return True
            float(value)
            return True
        except ValueError:
            return False

    def on_focus_out_height(self, event):
        if not self.height_entry.get():
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, "0")

    def on_focus_out_width(self, event):
        if not self.width_entry.get():
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, "0")
            
    def disable_cascades(self):
        self.file_menu.entryconfig("Improve Photo Quality", state=tk.DISABLED)
        self.file_menu.entryconfig("Save Photo", state=tk.DISABLED)

    def enable_cascades(self):
        self.file_menu.entryconfig("Improve Photo Quality", state=tk.NORMAL)
        self.file_menu.entryconfig("Save Photo", state=tk.NORMAL)
        
    def show_info_window(self):
        if hasattr(self, 'info_window') and self.info_window.winfo_exists():
            return

        self.info_window = tk.Toplevel(self.root)
        self.info_window.title("Information")

        window_width = 300
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        self.info_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        self.info_window.configure(bg='lightgray')
        self.info_window.resizable(width=False, height=False)

        info_label = tk.Text(self.info_window, wrap=tk.WORD, font=("Helvetica", 16), height=10, width=40)
        info_label.pack(pady=20)

        info_label.tag_configure('black', foreground='black', justify='center')
        info_label.tag_configure('purple', foreground='#800080', justify='center')
        info_label.tag_configure('green', foreground='#006400', justify='center')

        info_label.insert(tk.END, "i3iPhoto\n", 'purple')
        info_label.insert(tk.END, "(Photo Editor)\n", 'black')
        info_label.insert(tk.END, "created in 2024\n", 'black')
        info_label.insert(tk.END, "Project Author: ", 'black')
        info_label.insert(tk.END, "Arthur Zavada", 'green')
        
        info_label.config(state=tk.DISABLED)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoiSiApp(root)
    root.mainloop()
