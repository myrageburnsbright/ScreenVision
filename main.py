import os
import io
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageGrab
from google.cloud import vision
from tkinter import dnd
class ApiClient:
    _client = None

    @classmethod
    def get_instance(cls):
        if cls._client is None:
            cls._client = vision.ImageAnnotatorClient()
        return cls._client

def setup_conf():
    path = os.path.dirname(os.path.abspath(__file__))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(path, "keys.json")

class AppMediator:
    def __init__(self, content_frame, text_recognizer):
        self.content_frame = content_frame
        self.text_recognizer = text_recognizer

    def add_empty_row(self):
        self.content_frame.add_row()

    def delete_row(self, row_id):
        self.content_frame._handle_delete_row(row_id)

    def copy_row(self, content):
        self.content_frame.add_row(content)

    def copy_from_row(self, id):
        self.content_frame.copy_from_row(id)

    def multy(self):
        self.content_frame.multy()

    def save(self, reserve=False):
        try:
            with open("result.txt" if not reserve else "reserv save.txt", "w", encoding="utf-8") as f:
                for fr in self.content_frame.texts:
                    f.write(fr.text.get("1.0", tk.END).strip() + "\n\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def show_screenshot(self):
        self.text_recognizer.show_screenshot()

    def toggle_screenshot_area(self, root):
        self.text_recognizer.toggle_screenshot_area(root)
    
    def recognize_text(self): 
        content = self.text_recognizer.recognize_text()
        self.copy_row(content)

class MyTextBox(ttk.Frame):
    def __init__(self, parent, mediator, id: int, content: str = ""):
        ttk.Frame.__init__(
            self,
            master=parent,
            padding=1,
            border=1,
            relief="sunken",
            style="My.TFrame",
        )
        self.id = id
        self.mediator = mediator

        frame = tk.Frame(self)
        frame.pack(side="left", fill="y")

        self.button = ttk.Button(
            frame, text=str(id), style="My.TButton", width=3, command=self._copy_in_new
        )
        self.button.pack(side="top", fill="y", expand=True)
        self.buttonDel = tk.Button(
            frame, text="X", width=1, height=1, command=self._del_row
        )
        self.buttonDel.pack(side="left", fill="y")
        self.buttonDnd = tk.Button(
            frame, text="sw"
        )
        self.buttonDnd.bind("<Button-1>", self._start_dnd)
        self.buttonDnd.pack(side="left", fill="both", expand=True)

        self.text = tk.Text(self, height=5, font=("Arial", 12))
        self.text.insert("1.0", content)
        self.text.pack(side="left", fill="x")
        self.text.config(bg="#A8D5BA")

    def update_id(self, new_id):
        self.id = new_id
        self.button.config(text=str(new_id))

    def _del_row(self):
        self.mediator.delete_row(self.id)
        

    def _copy_in_new(self):
        content = self.text.get("1.0", "end-1c")
        self.mediator.copy_row(content)

    def _start_dnd(self, event):
        if self.text.cget("bg") != "blue":
            self.org_color = self.text.cget("bg")
        dnd.dnd_start(self, event)

    def dnd_commit(self, source, event):
        if self != source:
            temp = self.text.get("1.0", tk.END)
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", source.text.get("1.0", tk.END))
            source.text.delete("1.0", tk.END)
            source.text.insert("1.0", temp)

    def dnd_leave(self, source, event):
        if self != source:
            self.text.config(bg=self.org_color)

    def dnd_accept(self, source, event):
        if self.text.cget("bg") != "blue":
            self.org_color = self.text.cget("bg")
        self.text.config(bg="blue")
        return self

    def dnd_enter(self, source, event):
        pass

    def dnd_motion(self, source, event):
        pass

    def dnd_end(self,target, event):
        if target:
            target.text.config(bg=target.org_color)
        self.text.config(bg=self.org_color)

class Content_Frame(ttk.Frame):
    def __init__(self, canvas, mediator=None):
        ttk.Frame.__init__(self, master=canvas, padding=4, border=4, relief="sunken")
        content_window_id = canvas.create_window((0, 0), window=self, anchor="nw")
        self.mediator = mediator
        self.canvas = canvas
        self.texts = []

        self.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfig(content_window_id, width=event.width),
        )
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def set_mediator(self, mediator):
        self.mediator = mediator

    def add_row(self, content=""):
        if len(self.texts) > 0:
            self.texts[-1].text.config(bg="white")
        id = len(self.texts)
        mtxt = MyTextBox(self, self.mediator, id, content)
        mtxt.grid(row=id // 2, column=id % 2, padx=2, pady=5, sticky="nsew")
        self.texts.append(mtxt)

    def _handle_delete_row(self, row_id):
        if row_id < len(self.texts):
            self.texts[row_id].destroy()
            self.texts.pop(row_id)
            for i in range(row_id, len(self.texts)):
                self.texts[i].grid_forget()
                self.texts[i].update_id(i)
                self.texts[i].grid(row=i // 2, column=i % 2, padx=2, pady=5, sticky="nsew")
            if len(self.texts) > 0:
                self.texts[-1].text.config(bg="#A8D5BA")

    def copy_from_row(self, id):
        if 0 <= id < len(self.texts):
            self.add_row(self.texts[id].text.get("1.0", "end-1c"))
        else:
            messagebox.showerror("Error", "Invalid ID")

    def multy(self):
        if len(self.texts) > 0:
            text = self.texts[-1].text.get("1.0", "end-1c")
            if len(text) < 3:
                text += "(2)"
            else:
                if text[-3] == "(" and text[-2].isdigit() and text[-1] == ")":
                    tmp = list(text)
                    tmp[-2] = str(int(tmp[-2]) + 1)
                    text = "".join(tmp)
                else:
                    text += "(2)"
            self.texts[-1].text.delete("1.0", tk.END)
            self.texts[-1].text.insert("1.0", text)

class Control_Frame(ttk.Frame):
    def __init__(self, parent, mediator):
        ttk.Frame.__init__(self, master=parent, padding=4, border=4, relief="sunken")
        self.mediator = mediator
        pack_params = {"side": "top", "fill": "x", "padx": 5, "pady": 6}
        pack_params_bottom = {"side": "bottom", "fill": "x", "padx": 5, "pady": 6}

        frame = ttk.Frame(self)
        frame.pack(side="top", fill="both", padx=5, pady=6)
        for row in range(8):
            frame.rowconfigure(row, weight=1)
            frame.columnconfigure(0, weight=0)
            frame.columnconfigure(1, weight=5)
            entry = tk.Entry(frame, width=4, font=("Arial", 17))
            entry.grid(row=row, column=0, padx=2, pady=5, sticky="nsew")
            tk.Button(
                frame,
                text="Получить текст по ID",
                command=lambda e=entry: self.__get_input(e),
            ).grid(row=row, column=1, padx=2, pady=5, sticky="nsew")

        tk.Button(
            self,
            text="Распознать текст <Delete>",
            command=self.mediator.recognize_text,
        ).pack(**pack_params)

        tk.Button(
            self,
            text="Добавить пустую <Home>",
            command=self.mediator.add_empty_row,
        ).pack(**pack_params)

        tk.Button(
            self,
            text="Сохранить файл",
            command=self.mediator.save,
        ).pack(**pack_params_bottom)

        tk.Button(
            self,
            text="Дублировать(X2) <End>",
            command=self.mediator.multy,
        ).pack(**pack_params)

        tk.Button(
            self,
            text="Показать/скрыть область скриншота",
            command=lambda: self.mediator.toggle_screenshot_area(parent),
        ).pack(**pack_params_bottom)

        tk.Button(
            self,
            text="Сделать скриншот и показать",
            command=self.mediator.show_screenshot,
        ).pack(**pack_params_bottom)

    def __get_input(self, entry):
        user_input = entry.get()
        if user_input.isdigit():
            id = int(user_input)
            self.mediator.copy_from_row(id)
        else:
            messagebox.showerror("Error", "Please enter a valid ID")

class ScreenShotManager:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.screenshot_area = None

    def recognize_text(self):
        return self.GetAnnotations()

    def GetAnnotations(self):
        scr = self.__capture_screenshot()
        return self.__annotate(scr)

    def show_screenshot(self):
        scr = self.__capture_screenshot()
        scr.show()

    def toggle_screenshot_area(self, root):
        if self.screenshot_area is None or not self.screenshot_area.winfo_exists():
            self.screenshot_area = self.create_screenschot_area(root)
        if self.screenshot_area.winfo_viewable():
            self.screenshot_area.withdraw()
        else:
            self.screenshot_area.deiconify()

    def __capture_screenshot(self):
        screenshot = ImageGrab.grab(
            bbox=(self.x, self.y, self.x + self.width, self.y + self.height)
        )
        return screenshot

    def create_screenschot_area(self, root):
        screenshot_area = tk.Toplevel(root, bg="red")
        screenshot_area.title("Screen shot area")
        screenshot_area.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
        screenshot_area.attributes("-topmost", True)
        screenshot_area.attributes("-transparentcolor", "white")
        screenshot_area.attributes("-alpha", 0.5)

        label = tk.Label(
            screenshot_area,
            text="Screen shot area",
            bg="red",
            fg="blue",
            font=("Arial", 44),
        )
        label.pack(expand=True)

        def on_resize(event):
            self.width = screenshot_area.winfo_width()
            self.height = screenshot_area.winfo_height()
            self.x = screenshot_area.winfo_rootx()
            self.y = screenshot_area.winfo_rooty()

        screenshot_area.bind("<Configure>", on_resize)
        self.screenshot_area = screenshot_area
        return screenshot_area

    def __annotate(self, frame):
        try:
            with io.BytesIO() as output:
                frame.save(output, format="PNG")
                content = output.getvalue()

            image_context = vision.ImageContext(language_hints=["ru"])
            image = vision.Image(content=content)

            client = ApiClient.get_instance()

            response = client.text_detection(image=image, image_context=image_context)
            annotations = response.text_annotations
            print(annotations[0].description)
            return annotations[0].description
        except Exception as e:
            raise Exception(f"Failed to annotate image: {e}")

def pack_and_setup(root, mediator, canvas, control_frame, screenshot_manager, content_frame):
    root.set_mediator(mediator)
    content_frame.set_mediator(mediator)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    control_frame.pack(side="right", fill="y")
    canvas.pack(side="right", fill="both", expand=True)
    screenshot_manager.create_screenschot_area(root)

def reg_styles():
    style = ttk.Style()
    style.configure(
        "My.TButton",
        width=4,
        font=("Times", 13, "bold"),
        padding=2,
        background="lightblue",
        foreground="black",
    )
    ttk.Style().configure("My.TFrame", background="lightgray")


class Root(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Recognizer")
        self.geometry(f"1000x800+800+0")
        self.iconbitmap("dnd.ico")
        self.bind("<Delete>", lambda event: self.mediator.recognize_text())
        self.bind("<Home>", lambda event: self.mediator.add_empty_row())
        self.bind("<End>", lambda event: self.mediator.multy())
        self.bind("<Escape>", lambda event: self.__on_close())
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", lambda: self.__on_close())

    def set_mediator(self, mediator):
        self.mediator = mediator

    def __on_close(self):
        self.mediator.save(True)
        self.destroy()

if __name__ == "__main__":
    setup_conf()
    root = Root()
    
    reg_styles() # create tk.Tk if no instance presented
    
    canvas = tk.Canvas(root, bg="lightblue")
    
    content_frame = Content_Frame(canvas)
    screenshot_manager = ScreenShotManager(600, 370, 150, 150)

    mediator = AppMediator(content_frame, screenshot_manager)
    
    control_frame = Control_Frame(root, mediator)

    pack_and_setup(root, mediator, canvas, control_frame, screenshot_manager, content_frame)
    
    root.mainloop()