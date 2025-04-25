import keyboard
from PIL import ImageGrab
import time
from google.cloud import vision
import os
import io
import time
import tkinter as tk

if __name__== "__main__":
    x = 0  # Левый верхний угол
    y = 150   # Верхний
    width = 800  # Ширина
    height = 470  # Высота

    path = os.path.dirname(os.path.abspath(__file__))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(path, "keys.json")

    def recognize(frame):
        with io.BytesIO() as output:
            frame.save(output, format="PNG")
            content = output.getvalue()

        image_context = vision.ImageContext(language_hints=["ru"])
        image = vision.Image(content=content)
        
        client = vision.ImageAnnotatorClient()

        response = client.text_detection(image=image, image_context=image_context)
        texts = response.text_annotations
        print(texts[0].description)
        return texts[0].description

    def capture_screenshot(show=False):
        global width, height, x, y
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        if show:
            screenshot.show()
        return screenshot

    def create_overlay(x=100, y=100, w=300, h=200):
        root = tk.Tk()

        root.geometry(f"{w}x{h}+{x}+{y}")
        root.attributes("-topmost", True)  # Поверх всех окон
        root.attributes("-alpha", 0.4)     # Прозрачность окна (0.0 - полностью прозрачно, 1.0 - непрозрачно)

        frame = tk.Frame(root, background='red', borderwidth=4, relief="solid")
        frame.pack(fill="both", expand=True)

        # Закрыть окно по нажатию ESC
        root.bind("<Escape>", lambda e: root.destroy())
        def on_window_resize(event):
            global width, height, x, y
            width = root.winfo_width()
            height = root.winfo_height()
            x = root.winfo_x()
            y = root.winfo_y()
    
        # Привязываем событие изменения окна
        root.bind("<Configure>", on_window_resize)
        root.mainloop()

    create_overlay(x=x, y=y, w=width, h=height)

    root = tk.Tk()
    root.geometry(f"1000x900+{width}+0")
    root.title("Распознавание текста")
    root.focus_set()

    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbarx = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    canvas.config(yscrollcommand=scrollbar.set, xscrollcommand=scrollbarx.set)
    
    scrollbar.pack(side="right", fill="y")
    scrollbarx.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    result = ""
    def create_text(content=None):
        global text_idx
        global texts
        global result
        text_area = tk.Text(canvas, height=7, width=56, font=("Arial", 9)) 
        label = tk.Label(canvas, text=f"{int(text_idx + 1)}", font=("Arial", 13))

        height_delta = 58
        width_delta = 400
        if text_idx % 2 == 0:
            canvas.create_window(0, (text_idx) * height_delta, window=label, anchor="nw")
            canvas.create_window(24, (text_idx) * height_delta, window=text_area, anchor="nw")
        else:
            canvas.create_window(0 + width_delta, (text_idx-1) * height_delta, window=label, anchor="nw")
            canvas.create_window(24 + width_delta, (text_idx-1) * height_delta, window=text_area, anchor="nw")

        if not content:
            text_area.insert(f"{float(text_area.index('end-1c')) - 0.1}", "")
            
        else:
            text_area.insert(tk.END, content)
        text_area.config(bg="#A8D5BA")
        if len(texts) !=0:
            texts[-1].config(bg="white")

        texts.append(text_area)
        text_idx += 1
        canvas.config(scrollregion=canvas.bbox("all"))
        canvas.yview_moveto(1)

    capture_button = tk.Button(root, text="Сделать скриншот и показать", command= lambda: capture_screenshot(True))
    capture_button.pack(side="top", pady="10")

    def ScreenRecongizePaste(event=None):
        scr = capture_screenshot()
        recognized_text = recognize(scr)
        create_text(recognized_text)

    def get_input(entry):
        user_input = entry.get()
        
        if user_input.isdigit():
            texts[-1].config(bg="white")
            create_text(texts[int(user_input)- 1].get("1.0", "end-1c"))
        print(f"Запрошена копия по айди {user_input}")

    entry1 = tk.Entry(root)
    entry1.pack(pady=(20,0))

    button = tk.Button(root, text="Получить текст", command=lambda: get_input(entry1))
    button.pack(pady="10")

    entry2 = tk.Entry(root)
    entry2.pack(pady=(10,0))

    button = tk.Button(root, text="Получить текст", command=lambda: get_input(entry2))
    button.pack(pady="10")

    entry3 = tk.Entry(root)
    entry3.pack(pady=(10,0))

    button = tk.Button(root, text="Получить текст", command=lambda: get_input(entry3))
    button.pack(pady="10")

    button = tk.Button(root, text="Распознать текст или Delete", command=lambda: ScreenRecongizePaste())
    button.pack(pady=(200,10))

    button = tk.Button(root, text="Создать пустой or Home", command=lambda: create_text())
    button.pack(pady="5")

    def save():
        global texts
        with open("result.txt", "w", encoding="utf-8") as f:
            for text in texts:
                f.write(text.get("1.0", tk.END) + "\n")

    button = tk.Button(root, text="Сохранить файл", command=lambda: save())
    button.pack(pady="5")

    texts = []
    text_idx = 0

    root.bind("<Escape>", lambda event: root.destroy() if root else ...)
    
    def multy(event=None):
        if len(texts) > 0:
            text = texts[-1].get("1.0", "end-1c")
            if len(text) < 3:
                text +="(2)"
            else:
                if text[-3] =='(' and text[-2].isdigit() and text[-1] == ')':
                    tmp = list(text)
                    tmp[-2] = str(int(tmp[-2]) + 1)
                    text = "".join(tmp)
                else:
                    text += "(2)"

            texts[-1].delete("1.0",tk.END)
            texts[-1].insert("1.0", text)

    button = tk.Button(root, text="X(2) or End", command=lambda: multy())
    button.pack(pady="5")
    root.bind("<Delete>", ScreenRecongizePaste)
    root.bind("<End>", multy)
    root.bind("<Home>", lambda event: create_text())
    root.mainloop()
    root.destroy()
    