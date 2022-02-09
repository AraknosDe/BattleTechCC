import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import btccutil
from tkinter import NO

coltitleaddlpix=12
colvaladdlpix=16

def get_coltitlewidth_pix(val):
    return btccutil.measuretext(str(val))+coltitleaddlpix

def get_colvalwidth_pix(val):
    return btccutil.measuretext(str(val))+colvaladdlpix

def get_width(item):
    return tkFont.Font().measure(item) + 2
    # if isinstance(item, int) or isinstance(item, float):
    #     return tkFont.Font().measure(item)+2
    # else:
    #     return len(item)+2

class MultiColumnListbox(ttk.Frame):
    """use a ttk.TreeView as a multicolumn ListBox"""

    def __init__(self, master, header, data):
        super().__init__(master)
        self.tree = None
        self.header = header
        self._setup_widgets(header)
        self._build_tree(header, data)
        self._pack_widgets()

    def _setup_widgets(self, header):
        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(self, columns=header, show=["headings"])
        self.vsb = ttk.Scrollbar(self, orient="vertical",
            command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)

    def _pack_widgets(self):
        self.tree.pack(side='left', fill='both', expand=True)
        self.vsb.pack(side='right', fill='y')


    def _build_tree(self, header, data):
        for col in header:
            self.tree.heading(col, text=str(col),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=get_coltitlewidth_pix(col.title()), stretch=NO)#tkFont.Font().measure(col.title()))

        for item in data:
            self.tree.insert('', 'end', item[0], values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = get_colvalwidth_pix(val)
                if self.tree.column(header[ix],width=None)<col_w:
                    self.tree.column(header[ix], width=col_w, stretch=NO)

    def getnumcolumns(self):
        return len(self.header)

    def update_tree(self, header, data):
        self.tree.delete(*self.tree.get_children())

        self.header = header

        for item in data:
            self.tree.insert('', 'end', item[0], values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = get_colvalwidth_pix(val)
                if self.tree.column(header[ix],width=None)<col_w:
                    self.tree.column(header[ix], width=col_w, stretch=NO)
        self.tree.event_generate("<<ThemeChanged>>")
        self.event_generate("<<ThemeChanged>>")

    def getselectedfirstcolumn(self):
        return self.tree.item(self.tree.focus())['values'][0]

    def getselecteditem(self):
        return self.tree.item(self.tree.focus())

    def setselecteditembyfirstcolumn(self, item):
        for item in self.tree.get_children():
            if ['values'][0] == item:
                self.tree.set_selection(item)
                self.tree.focus_set(item)
                return

def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child) \
        for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    #data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
        int(not descending)))