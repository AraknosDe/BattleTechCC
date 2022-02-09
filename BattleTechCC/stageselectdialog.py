from tkinter import *
from tkinter.simpledialog import Dialog
from functools import partial

class StageSelectDialog(Dialog):

    def __init__(self, options=[], parent=None):
        self.options = options
        self.result = None
        Dialog.__init__(self, parent, 'Select next stage')

    def buttonbox(self):
        box = Frame(self)

        for i, option in enumerate(self.options):
            w = Button(box, text=option, width=10, command=partial(self.selecttoption, i))
            w.pack(side=LEFT, padx=5, pady=5)

        w = Button(box, text="Cancel", width=10, command=self.cancel, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Escape>", self.cancel)

        box.pack()

    def selecttoption(self, optionidx):
        self.result = optionidx
        self.cancel()

def askstageselect(stageoptions):
    s = StageSelectDialog(stageoptions)
    return s.result

