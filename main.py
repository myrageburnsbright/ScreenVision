import os
import io
import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab
from google.cloud import vision


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


class MyTextBox(ttk.Frame):
    def __init__(self, content_frame, id, content=""):
        ttk.Frame.__init__(
            self,
            master=content_frame,
            padding=1,
            border=1,
            relief="sunken",
            style="My.TFrame",
        )
        self.id = id
        frame = tk.Frame(self)
        frame.pack(side="left", fill="y")

        self.button = ttk.Button(
            frame, text=str(id), style="My.TButton", width=3, command=self.__copy_in_new
        )
        self.button.pack(side="top", fill="y", expand=True)
        self.buttonDel = tk.Button(
            frame, text="X", width=1, height=1, command=self.__del_row
        )
        self.buttonDel.pack(side="left", fill="y")

        self.text = tk.Text(self, height=5, font=("Arial", 12))
        self.text.insert("1.0", content)
        self.text.pack(side="left", fill="x")
        self.text.config(bg="#A8D5BA")

    def _change_id(self, id):
        self.id = id
        self.button.config(text=str(id))

    def __del_row(self):
        self.destroy()
        self.master._relayout_grid(self.id)

    def __copy_in_new(self):
        self.master.add_row(self.text.get("1.0", "end"))


class Control_Frame(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, master=parent, padding=4, border=4, relief="sunken")
        pack_params = {"side": "top", "fill": "x", "padx": 5, "pady": 6}
        pack_params_bottom = {"side": "bottom", "fill": "x", "padx": 5, "pady": 6}

        frame = ttk.Frame(self)
        frame.pack(side="top", fill="both", padx=5, pady=6)
        for row in range(6):
            frame.rowconfigure(row, weight=1)
            frame.columnconfigure(0, weight=0)
            frame.columnconfigure(1, weight=5)
            entry = tk.Entry(frame, width=4, font=("Arial", 17))
            entry.grid(row=row, column=0, padx=2, pady=5, sticky="nsew")
            tk.Button(
                frame,
                text="  Получить текст по ID  ",
                command=lambda e=entry: self.get_input(e),
            ).grid(row=row, column=1, padx=2, pady=5, sticky="nsew")

        tk.Button(
            self,
            text="Распознать текст или Delete",
            command=self.master.ScreenShotRecongize,
        ).pack(**pack_params)

        tk.Button(
            self, text="Создать пустой or Home", command=lambda: self.master.add_row()
        ).pack(**pack_params)

        tk.Button(self, text="Сохранить файл", command=self.master.save).pack(
            **pack_params_bottom
        )

        tk.Button(self, text="X(2) or End", command=self.master.multy).pack(
            **pack_params
        )

        tk.Button(
            self,
            text="Scren shot area on/off",
            command=lambda: self.master.ss_area_visible(),
        ).pack(**pack_params_bottom)

        tk.Button(
            self,
            text="Сделать скриншот и показать",
            command=self.master.capture_screenshot_and_show,
        ).pack(**pack_params_bottom)

    def get_input(self, entry):
        user_input = entry.get()
        if user_input.isdigit():

            id = int(user_input)
            self.master.copy_from_row(id)

        print(f"Запрошена копия по айди {user_input}")


class Content_Frame(ttk.Frame):
    def __init__(self, canvas):
        ttk.Frame.__init__(self, master=canvas, padding=4, border=4, relief="sunken")
        content_window_id = canvas.create_window((0, 0), window=self, anchor="nw")

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
        self.texts = []
        self.canvas = canvas

    def copy_from_row(self, id):
        if id >= 0 and id < len(self.texts):
            self.add_row(self.texts[id].text.get("1.0", "end-1c"))
        else:
            print("Id out of range")

    def add_row(self, content=""):
        if len(self.texts) > 0:
            self.texts[-1].text.config(bg="white")
        id = len(self.texts)
        mtxt2 = MyTextBox(self, id, content)
        mtxt2.grid(row=id // 2, column=id % 2, padx=2, pady=5, sticky="nsew")
        self.texts.append(mtxt2)

    def _relayout_grid(self, id):
        self.texts[id].destroy()
        self.texts.pop(id)
        for i in range(id, len(self.texts)):
            self.texts[i].grid_forget()
            self.texts[i]._change_id(i)
            self.texts[i].grid(row=i // 2, column=i % 2, padx=2, pady=5, sticky="nsew")

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


class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Recognizer")
        self.geometry(f"1000x800+800+0")

    def setup(self):
        # <self>   <canvas> <content_frame> </canvas> <controll_frame> <sb>  </self>
        self.canvas = tk.Canvas(self, bg="lightblue")

        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        self.control_frame = Control_Frame(self)
        self.control_frame.pack(side="right", fill="y")

        self.canvas.pack(side="right", fill="both", expand=True)

        self.content_frame = Content_Frame(self.canvas)

        self.screenshot_manager = ScreenShotManager(600, 370, 150, 150)
        self.screenshot_manager.create_screenschot_area(self)

        self.bind("<Delete>", lambda event: self.ScreenShotRecongize())
        self.bind("<End>", lambda event: self.multy())
        self.bind("<Home>", lambda event: self.add_row())
        self.bind("<Escape>", lambda event: self.destroy() if self else ...)
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", lambda: self.__on_close())

    def add_row(self, content=""):
        self.content_frame.add_row(content)
        self.canvas.yview_moveto(1)

    def copy_from_row(self, id):
        self.content_frame.copy_from_row(id)

    def capture_screenshot_and_show(self):
        self.screenshot_manager.show_screenshot()

    def ss_area_visible(self):
        self.screenshot_manager.ss_area_visible(self)

    def ScreenShotRecongize(self):
        recognized_text = self.screenshot_manager.GetAnnotations()
        self.add_row(recognized_text)

    def save(self):
        with open("result.txt", "w", encoding="utf-8") as f:
            for fr in self.content_frame.texts:
                f.write(fr.text.get("1.0", tk.END) + "\n")

    def multy(self):
        self.content_frame.multy()

    def __on_close(self):
        texts = self.content_frame.texts

        with open("reserv save.txt", "w", encoding="utf-8") as f:
            for fr in texts:
                f.write(fr.text.get("1.0", tk.END) + "\n")
        self.destroy()


class ScreenShotManager:

    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.screenshot_area = None

    def GetAnnotations(self):
        scr = self.__capture_screenshot()
        return self.__annotate(scr)

    def show_screenshot(self):
        scr = self.__capture_screenshot()
        scr.show()

    def __capture_screenshot(self):
        magic_delta_x = 0
        magic_delta_y = 0
        screenshot = ImageGrab.grab(
            bbox=(
                self.x,
                self.y,
                self.x + self.width,
                self.y + self.height,
            )
        )

        return screenshot

    def ss_area_visible(self, root):
        if self.screenshot_area.winfo_exists() == 0:
            self.screenshot_area = self.create_screenschot_area(root)
        if self.screenshot_area.winfo_viewable():
            self.screenshot_area.withdraw()
        else:
            self.screenshot_area.deiconify()

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


if __name__ == "__main__":
    setup_conf()
    root = MainWindow()
    reg_styles()
    root.setup()
    root.mainloop()
