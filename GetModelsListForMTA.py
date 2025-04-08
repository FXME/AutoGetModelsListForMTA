import os
import sys
import threading
from xml.sax.saxutils import escape
from tkinter import *
from tkinter import ttk, filedialog, messagebox

class IDEProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IDE Files Processor | by e1ectr0venik | v1.0")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.setup_ui()
    
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.processing = False
        self.stop_flag = False
        self.output_dir = ""  # Добавляем переменную для пути сохранения

    def setup_ui(self):
        # Frame for directory selection
        dir_frame = Frame(self.root)
        dir_frame.pack(pady=10, padx=10, fill=X)

        self.dir_var = StringVar()
        self.dir_entry = Entry(dir_frame, textvariable=self.dir_var, width=50)
        self.dir_entry.pack(side=LEFT, fill=X, expand=True)

        Button(dir_frame, text="Обзор", command=self.browse_directory).pack(side=LEFT, padx=5)
        Button(dir_frame, text="Текущая папка", command=self.use_current_dir).pack(side=LEFT)

        # Progress and info
        info_frame = Frame(self.root)
        info_frame.pack(pady=10, padx=10, fill=X)

        self.progress = ttk.Progressbar(info_frame, orient=HORIZONTAL, mode='determinate')
        self.progress.pack(fill=X)

        self.info_label = Label(info_frame, text="Готов к работе", anchor=W)
        self.info_label.pack(fill=X, pady=5)

        self.log_text = Text(self.root, wrap=WORD, height=10)
        self.log_text.pack(pady=10, padx=10, fill=BOTH, expand=True)

        # Control buttons
        Button(self.root, text="Начать поиск", command=self.start_processing).pack(pady=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)

    def use_current_dir(self):
        self.dir_var.set(os.getcwd())

    def log_message(self, message):
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

    def start_processing(self):
        if self.processing:
            return

        directory = self.dir_var.get()
        if not directory or not os.path.isdir(directory):
            self.log_message("Ошибка: Неверная директория!")
            return

        self.processing = True
        self.log_message("Начало обработки...")
        threading.Thread(target=self.process_files, args=(directory,)).start()

    def process_files(self, root_dir):
        try:
            self.output_dir = root_dir  # Сохраняем путь для экспорта
            objects = []
            total_files = 0
            processed_files = 0

            # First pass - count files
            for root, dirs, files in os.walk(root_dir):
                total_files += sum(1 for f in files if f.lower().endswith(".ide"))
            
            self.root.after(0, self.progress.config, {'maximum': total_files})
            
            # Second pass - process files
            for root, dirs, files in os.walk(root_dir):
                for file in files:
                    if self.stop_flag:
                        return
                    
                    if file.lower().endswith(".ide"):
                        file_path = os.path.join(root, file)
                        self.root.after(0, self.log_message, f"Обработка: {file_path}")
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                capture = False
                                for line in f:
                                    line = line.strip().lower()
                                    if line == "objs":
                                        capture = True
                                        continue
                                    if capture:
                                        if line == "end":
                                            capture = False
                                            break
                                        parts = [p.strip() for p in line.split(',')]
                                        if len(parts) >= 2:
                                            try:
                                                obj_id = int(parts[0])
                                                obj_name = parts[1]
                                                objects.append((obj_id, obj_name))
                                            except ValueError:
                                                continue
                        except Exception as e:
                            self.root.after(0, self.log_message, f"Ошибка в файле {file}: {str(e)}")
                        
                        processed_files += 1
                        self.root.after(0, self.update_progress, processed_files)

            # Передаем output_dir в write_output_files
            self.write_output_files(objects, self.output_dir)
            
            self.root.after(0, self.log_message, 
                f"Готово! Обработано файлов: {processed_files}\n"
                f"Найдено объектов: {len(objects)}")
            
            # Показываем сообщение о сохранении
            self.show_completion_message()

        finally:
            self.processing = False
            self.stop_flag = False
            self.root.after(0, self.update_progress, 0)

    def write_output_files(self, objects, output_dir):
        sorted_objects = sorted(objects, key=lambda x: x[0])
        self.created_files = []  # Сохраняем пути созданных файлов
        
        try:
            # CModelNames.txt
            cmodel_path = os.path.join(output_dir, "CModelNames.txt")
            with open(cmodel_path, "w", encoding='utf-8') as f:
                for obj_id, obj_name in sorted_objects:
                    f.write(f'"{obj_name}", {obj_id},\n')
            self.created_files.append(cmodel_path)

            # objects.xml
            xml_path = os.path.join(output_dir, "objects.xml")
            with open(xml_path, "w", encoding='utf-8') as f:
                f.write('<catalog type="object">\n')
                f.write('   <group name="Main">\n')
                for obj_id, obj_name in sorted_objects:
                    safe_name = escape(obj_name)
                    f.write(f'      <object model="{obj_id}" name="{safe_name}" keywords="" />\n')
                f.write('   </group>\n')
                f.write('</catalog>\n')
            self.created_files.append(xml_path)

            # editor_main.txt
            editor_path = os.path.join(output_dir, "editor_main.txt")
            with open(editor_path, "w", encoding='utf-8') as f:
                for obj_id, obj_name in sorted_objects:
                    f.write(f'[{obj_id}]="{obj_name}",\n')
            self.created_files.append(editor_path)

            self.root.after(0, self.log_message, "Файлы успешно созданы!")
        except Exception as e:
            self.root.after(0, self.log_message, f"Ошибка записи файлов: {str(e)}")

    def show_completion_message(self):
        message = "Файлы успешно созданы в директории:\n"
        message += f"{self.output_dir}\n\n"
        message += "Созданные файлы:\n"
        for file in self.created_files:
            message += f"• {os.path.basename(file)}\n"
        
        messagebox.showinfo(
            "Обработка завершена",
            message,
            parent=self.root
        )
        self.log_message(f"Файлы сохранены в: {self.output_dir}")

if __name__ == "__main__":
    root = Tk()
    app = IDEProcessorApp(root)
    root.mainloop()