import os
import io
import tkinter as tk

from PIL import ImageGrab
from google.cloud import vision

# globals defaults:
x = 0  # left
y = 150  # top
width = 800  # width
height = 470  # height
# entry data:
texts = []
# screenarea:
screenshot_area = None


class ApiClient:
    _client = None

    @classmethod
    def get_instance(cls):
        if cls._client is None:
            cls._client = vision.ImageAnnotatorClient()
        return cls._client


# Setups:
def setup_conf():
    path = os.path.dirname(os.path.abspath(__file__))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(path, "keys.json")


def setup_root():
    root = tk.Tk()
    root.geometry(f"1000x900+{width}+0")
    root.title("Распознавание текста")
    root.focus_set()
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))

    return root


def setup_canvas(root):
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbarx = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    canvas.config(yscrollcommand=scrollbar.set, xscrollcommand=scrollbarx.set)

    scrollbar.pack(side="right", fill="y")
    scrollbarx.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    return canvas


def setup_root_buttons(root, canvas):
    tk.Button(
        root,
        text="Сделать скриншот и показать",
        command=capture_screenshot_event,
    ).pack(side="top", pady="10")
    entry1 = tk.Entry(root)
    entry1.pack(pady=(20, 0))

    tk.Button(
        root, text="Получить текст", command=lambda: get_input(entry1, canvas)
    ).pack(pady="10")

    entry2 = tk.Entry(root)
    entry2.pack(pady=(10, 0))

    tk.Button(
        root, text="Получить текст", command=lambda: get_input(entry2, canvas)
    ).pack(pady="10")

    entry3 = tk.Entry(root)
    entry3.pack(pady=(10, 0))

    tk.Button(
        root, text="Получить текст", command=lambda: get_input(entry3, canvas)
    ).pack(pady="10")

    tk.Button(
        root,
        text="Распознать текст или Delete",
        command=lambda: ScreenRecongizePaste(canvas),
    ).pack(pady=(200, 10))

    tk.Button(
        root, text="Создать пустой or Home", command=lambda: create_text(canvas=canvas)
    ).pack(pady="5")

    tk.Button(root, text="Сохранить файл", command=save).pack(pady="5")

    tk.Button(root, text="X(2) or End", command=multy).pack(pady="5")

    # Hotkeys
    root.bind("<Delete>", lambda event: ScreenRecongizePaste(canvas))
    root.bind("<End>", multy)
    root.bind("<Home>", lambda event: create_text(canvas=canvas))
    root.bind("<Escape>", lambda event: root.destroy() if root else ...)


def setup_screenshot_area(root):
    global screenshot_area
    screenshot_area = create_screenschot_area(root)

    tk.Button(
        root, text="Scren shot area on/off", command=lambda: ss_area_visible(root)
    ).pack(pady="5")


# Utils:
def create_screenschot_area(root):
    screenshot_area = tk.Toplevel(root, bg="red")
    screenshot_area.title("Screen shot area")
    screenshot_area.geometry(f"{width}x{height}+{x}+{y}")
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
        global width, height, x, y
        width = screenshot_area.winfo_width()
        height = screenshot_area.winfo_height()
        x = screenshot_area.winfo_rootx()
        y = screenshot_area.winfo_rooty()
        # label.config(text=f"{x} {y} {width} {height}")

    screenshot_area.bind("<Configure>", on_resize)
    return screenshot_area


def create_text(content=None, canvas=None):
    global texts
    text_idx = len(texts)
    text_area = tk.Text(canvas, height=7, width=56, font=("Arial", 9))
    label = tk.Label(canvas, text=f"{int(text_idx + 1)}", font=("Arial", 13))

    height_delta = 58
    width_delta = 400
    if text_idx % 2 == 0:
        canvas.create_window(0, (text_idx) * height_delta, window=label, anchor="nw")
        canvas.create_window(
            24, (text_idx) * height_delta, window=text_area, anchor="nw"
        )
    else:
        canvas.create_window(
            0 + width_delta, (text_idx - 1) * height_delta, window=label, anchor="nw"
        )
        canvas.create_window(
            24 + width_delta,
            (text_idx - 1) * height_delta,
            window=text_area,
            anchor="nw",
        )

    if not content:
        text_area.insert(f"{float(text_area.index('end-1c')) - 0.1}", "")

    else:
        text_area.insert(tk.END, content)
    text_area.config(bg="#A8D5BA")
    if len(texts) != 0:
        texts[-1].config(bg="white")

    texts.append(text_area)
    text_idx += 1
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(1)


def recognize(frame):
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


def capture_screenshot():
    global width, height, x, y
    magic_delta_x = 0
    magic_delta_y = 0
    screenshot = ImageGrab.grab(
        bbox=(
            x,
            y,
            x + width,
            y + height,
        )
    )

    return screenshot


# Callbacks
def capture_screenshot_event():
    screenshot = capture_screenshot()
    screenshot.show()


def multy(event=None):
    if len(texts) > 0:
        text = texts[-1].get("1.0", "end-1c")
        if len(text) < 3:
            text += "(2)"
        else:
            if text[-3] == "(" and text[-2].isdigit() and text[-1] == ")":
                tmp = list(text)
                tmp[-2] = str(int(tmp[-2]) + 1)
                text = "".join(tmp)
            else:
                text += "(2)"

        texts[-1].delete("1.0", tk.END)
        texts[-1].insert("1.0", text)


def save():
    global texts

    with open("result.txt", "w", encoding="utf-8") as f:
        for text in texts:
            f.write(text.get("1.0", tk.END) + "\n")


def ss_area_visible(root):
    global screenshot_area
    if screenshot_area.winfo_exists() == 0:
        screenshot_area = create_screenschot_area(root)
    if screenshot_area.winfo_viewable():
        screenshot_area.withdraw()
    else:
        screenshot_area.deiconify()


def get_input(entry, canvas):
    user_input = entry.get()

    if user_input.isdigit():
        texts[-1].config(bg="white")
        create_text(texts[int(user_input) - 1].get("1.0", "end-1c"), canvas=canvas)
    print(f"Запрошена копия по айди {user_input}")


def ScreenRecongizePaste(canvas):
    scr = capture_screenshot()
    recognized_text = recognize(scr)
    create_text(recognized_text, canvas)


def on_close(root):
    global texts

    with open("reserv save.txt", "w", encoding="utf-8") as f:
        for text in texts:
            f.write(text.get("1.0", tk.END) + "\n")
    root.destroy()


def main():
    setup_conf()

    root = setup_root()
    canvas = setup_canvas(root=root)
    setup_root_buttons(root=root, canvas=canvas)
    setup_screenshot_area(root=root)

    root.mainloop()


if __name__ == "__main__":
    main()
