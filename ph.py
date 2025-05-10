import tkinter as tk
from tkinter import ttk

RELIEF_STYLES = [
    "flat",
    "raised",
    "sunken",
    "groove",
    "ridge",
    "solid"
]
TK_COLORS = {
    "white": "#FFFFFF",
    "black": "#000000",
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "gray": "#808080",
    "lightgray": "#D3D3D3",
    "darkgray": "#A9A9A9",
    "orange": "#FFA500",
    "pink": "#FFC0CB",
    "purple": "#800080",
    "brown": "#A52A2A",
    "navy": "#000080",
    "teal": "#008080",
    "lime": "#00FF00",
    "olive": "#808000",
    "maroon": "#800000",
    "gold": "#FFD700",
    "skyblue": "#87CEEB",
    "indigo": "#4B0082",
    "turquoise": "#40E0D0",
}

class MainWindow(tk.Tk):
    frame_padding = 0
    widget_padding = 0
    frame_border = 7

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Styles ttk")
        self.geometry("1600x600")

        # Канвас
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbarx = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbarx.set)

        scrollbar.pack(side="right", fill="y")
        scrollbarx.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        

        # Контейнер для фреймов (вместо create_window)
        self.content_frame = tk.Frame(self.canvas)

        # Размещаем content_frame внутри канваса с помощью create_window
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        # Добавляем фреймы динамически
        self.add_frames()

        # Настроим scrollregion после того, как фреймы добавлены
        self.canvas.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def add_frames(self):
        # Динамически добавляем фреймы с контентом
        row = 0
        for relief in RELIEF_STYLES:
            clmn = 0
            for color in TK_COLORS:
                self.create_frame(relief=relief, bg=color, clmn=clmn, row=row)
                clmn += 1
            row += 1

    def create_frame(self, relief="solid", clmn=0, row=0, bg="lightblue"):
        # Создаем фрейм и добавляем его в content_frame
        frame = tk.Frame(self.content_frame, bg=bg, bd=MainWindow.frame_border, relief=relief)
        frame.grid(row=row, column=clmn)

        style = ttk.Style(self.canvas)
        style.configure(f"Custom{row}a{clmn}.TButton",
                        background=bg,
                        padding=10,
                        font=("Arial", 12, ""))

        style.configure(f"Custom{row}a{clmn}.TLabel",
                        background=bg,
                        padding=10,
                        font=("Times", 14, "bold"))

        style.configure(f"Custom{row}a{clmn}a.TButton",
                        background=bg,
                        padding=12,
                        font=("Arial", 10, "italic"))

        ttk.Label(frame, style=f"Custom{row}a{clmn}.TLabel", text=f" {relief} {bg}").pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        ttk.Button(frame, style=f"Custom{row}a{clmn}.TButton", text="Close1", command=self.destroy).pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        ttk.Button(frame, style=f"Custom{row}a{clmn}a.TButton", text="Close2", command=self.destroy).pack(side=tk.TOP, expand=True, fill=tk.BOTH)


# Запуск приложения
app = MainWindow()
app.mainloop()
