import json
from tkinter import *
from tkinter import ttk

import tkinter as tk

def parsexp(xpstr):
    if xpstr[0] == '–':
        return -int(xpstr[1:])
    else:
        return int(xpstr)


class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)

        self.entrythingy = tk.Text()
        self.entrythingy.pack(fill='both', expand=True, anchor=N)

        self.name = tk.Text(height=20)
        self.name.pack(fill='both', expand=False, anchor=CENTER)

        self.output = tk.Text()
        self.output.pack(fill='both', expand=False, anchor=S)

        # # Create the application variable.
        # self.contents = tk.StringVar()
        # # Set it to some value.
        # self.contents.set("this is a variable")
        # # Tell the entry widget to watch this variable.
        # self.entrythingy["textvariable"] = self.contents

        # Define a callback for when the user hits return.
        # It prints the current value of the variable.
        self.entrythingy.bind('<Key-Return>',
                             self.parse_lm)




    def parse_lm(self, event):
        s = self.entrythingy.get("1.0",END)

        s = re.sub(r'/\n', lambda m: '/', s)
        s = re.sub(r'\n', lambda m: ' ', s)
        name = re.search(r'([^[]*)\[', s).group(1).strip()
        s = re.sub(r'[^[]*', lambda m: ('' if m.group(0).strip() == name else m.group(0)), s)
        s = re.sub(r'\[[^]]*\]', lambda m: '', s)

        self.name.delete('1.0', END)
        self.name.insert('1.0', name)

        outstr = ''

        for i, m in enumerate(re.finditer(r'([^()]*) \(([^()]*) XP\)[;,]? ?', s)):
            if i != 0:
                outstr += ',\n'
            outstr += '{{"{}": {}}}'.format(m.group(1).strip(), parsexp(m.group(2).strip()))

        # outstr += '\n'
        self.output.delete('1.0', END)
        self.output.insert('1.0', outstr)




if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('640x640')
    app = App(master=root)
    app.mainloop()

