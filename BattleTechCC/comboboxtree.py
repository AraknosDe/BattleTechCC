from tkinter.ttk import Combobox
from tkinter import StringVar
from btccutil import getmaxwidth


class Comboboxtreeelem:

    def __init__(self, parent=None, comboboxmaster=None, row=0, column=0, columnspan=1, rowspan=1):
        self.children = []
        self.parent = parent
        self.comboval = StringVar()
        self.combobox = Combobox(comboboxmaster, textvariable=self.comboval, state='readonly')
        self.column = column
        self.row = row
        self.columnspan = columnspan
        self.rowspan = rowspan
        self.numvals = 0

    def setvalues(self, values):
        maxwidth = getmaxwidth(values)
        self.numvals = len(values)
        self.combobox.configure(values=values, width=maxwidth-7)

    def getselectedname(self):
        return self.comboval.get()

    def getselectedindex(self):
        return self.combobox.current()

    def setselectedindex(self, idx):
        return self.combobox.current(idx)

    def getnumoptions(self):
        return self.numvals

    def getchoiceselections(self):
        return [c.getselectedindex() for c in self.children], [b.getchoiceselections() for b in self.children]

    def configrowcol(self, row=0, column=0, columnspan=1, rowspan=1):
        self.column = column
        self.row = row
        self.columnspan = columnspan
        self.rowspan = rowspan

    def destroy(self):
        for child in self.children:
            child.destroy()
        self.children = []
        self.combobox.destroy()

    def destroychildren(self):
        for child in self.children:
            child.destroy()
        self.children = []

    def addchild(self, child):
        self.children.append(child)

    def isoptionselected(self):
        return self.getselectedindex() != -1

