from tkinter import messagebox
from tkinter import *
from multicolumnlistbox import MultiColumnListbox

def insert_list(listbox:Listbox, list):
    for i, e in enumerate(list):
        listbox.insert(i, e)

class ListSelectionFrame(Frame):

    def __init__(self, master, header, addfunc, removefunc, labeltext=None):
        self.header = header
        self.addfunc = addfunc
        self.removefunc = removefunc
        self.labeltext = labeltext
        super().__init__(master)
        self._setup_widgets()

    def _setup_widgets(self):
        self.store = Frame(self)
        self.store.grid(row=0, column=0, columnspan=1, rowspan=5, sticky=NSEW)

        self.storescroll = Scrollbar(self.store)
        self.storelist = Listbox(self.store, yscrollcommand=self.storescroll.set)
        self.storescroll.config(command=self.storelist.yview)

        self.storelist.pack(side=LEFT, fill=BOTH, expand=1)
        self.storescroll.pack(side=RIGHT, fill=Y)

        # control panel
        self.controlpanelframe = Frame(self)
        self.controlpanelframe.grid(row=2, column=1, columnspan=1, rowspan=1, sticky=NSEW)

        self.infolabel = Label(self.controlpanelframe, text=self.labeltext)
        self.infolabel.grid(column=0, row=0, columnspan=2, rowspan=1, sticky=NSEW)

        self.skilladd = Button(self.controlpanelframe, text="Add", command=self.addfunc)
        self.skilladd.grid(column=0, row=1, columnspan=1, rowspan=1, sticky=NSEW)

        self.skillremove = Button(self.controlpanelframe, text="Remove", command=self.removefunc)
        self.skillremove.grid(column=1, row=1, columnspan=1, rowspan=1, sticky=NSEW)

        self.xpamtvalue = StringVar(value=0)

        self.xpamt = Spinbox(self.controlpanelframe, from_=0, wrap=0, textvariable=self.xpamtvalue)
        self.xpamt.grid(column=0, row=2, columnspan=2, rowspan=1, sticky=NSEW)

        # character skill list
        self.statstate = MultiColumnListbox(self, self.header, ())
        self.statstate.grid(row=0, column=2, columnspan=1, rowspan=5, sticky=NSEW)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, minsize=70, weight=0)
        self.columnconfigure(2, weight=1)

        for i in range(5):
            self.rowconfigure(i, weight=1)

    def putlistinstore(self, list):
        insert_list(self.storelist, list)
        # maxwidthpix = max([btccutil.measuretext(t) for t in list])
        # self.storelist.configure(width=maxwidthpix)
        self.storelist.config(width=0)

    def puttuplesinstatstate(self, tuples):
        self.statstate.update_tree(self.header, tuples)

    def getselectedstatstateitem(self):
        return self.statstate.getselectedfirstcolumn()

    def getselectedstoreitem(self):
        return self.storelist.get(self.storelist.curselection())

    def isstoreselected(self):
        return len(self.storelist.curselection()) != 0

    def isstatstateselected(self):
        return len(self.statstate.getselecteditem()['values']) != 0

    def getxpamt(self):
        try:
            return int(self.xpamtvalue.get())
        except:
            messagebox.showerror("Error", "Please input an integer xp amount")
            return None

    def setlabeltext(self, text):
        self.infolabel.configure(text=text)

