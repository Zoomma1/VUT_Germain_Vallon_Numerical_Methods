import tkinter as tk

class SafeToolTip:
    def __init__(self, widget, *, bg='#FFFFEA', pad=(5, 3, 5, 3), text='widget info', waittime=400, wraplength=250):
        self.waittime = waittime 
        self.wraplength = wraplength
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.onEnter)
        self.widget.bind("<Leave>", self.onLeave)
        self.widget.bind("<ButtonPress>", self.onLeave)
        self.bg = bg
        self.pad = pad
        self.id = None
        self.tw = None

    def onEnter(self, event=None):
        self.schedule()

    def onLeave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self):
        def tip_pos_calculator(widget, label, *, tip_delta=(10, 5), pad=(5, 3, 5, 3)):
            w = widget
            s_width = w.winfo_screenwidth()
            s_height = w.winfo_screenheight()
            width = pad[0] + label.winfo_reqwidth() + pad[2]
            height = pad[1] + label.winfo_reqheight() + pad[3]

            mouse_x = w.winfo_pointerx()
            mouse_y = w.winfo_pointery()

            x1 = mouse_x + tip_delta[0]
            y1 = mouse_y + tip_delta[1]
            x2 = x1 + width
            y2 = y1 + height

            x_delta = max(0, x2 - s_width)
            y_delta = max(0, y2 - s_height)

            if x_delta > 0:
                x1 -= width + tip_delta[0] * 2
            if y_delta > 0:
                y1 -= height + tip_delta[1] * 2

            if y1 < 0:
                y1 = 0  # Prevent going above screen

            return x1, y1

        bg = self.bg
        pad = self.pad

        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)

        frame = tk.Frame(self.tw, background=bg, borderwidth=0)
        label = tk.Label(
            frame, text=self.text, justify=tk.LEFT,
            background=bg, relief=tk.SOLID, borderwidth=0,
            wraplength=self.wraplength
        )
        label.grid(padx=(pad[0], pad[2]), pady=(pad[1], pad[3]), sticky=tk.NSEW)
        frame.grid()

        x, y = tip_pos_calculator(self.widget, label)
        self.tw.wm_geometry(f"+{x}+{y}")

    def hide(self):
        tw = self.tw
        if tw:
            tw.destroy()
        self.tw = None   