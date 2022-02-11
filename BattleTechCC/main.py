import database
from tkinter import ttk
from character import Character
from biography import Biography
from biography import Lifemodule
from tkinter import filedialog as fd
from functools import partial
from comboboxtree import Comboboxtreeelem
import stageselectdialog
from listselectionframe import *
from biography import generatedropdowntext
from biography import SaveBlob
from biography import load_SaveBlob
from math import ceil
from btccutil import *
from pathlib import Path

chars_folder = (Path.home() / 'btccchars')

SATheader = ['Skill/Attr/Trait', 'XPs', 'Level']
flexxpheader = ['Skill/Attr/Trait', 'XPs']
prereqheader = ['Skill/Attr/Trait', 'Level', 'Min/Max']
numchoicecolumns = 9
maxnumchoices = 8
choicecolumnspan = 8
cboxwidthaddlpix = 30

def getmaxwidthfontmeasure(list):
    return max([tkFont.Font().measure(e) for e in list])

def getmaxlen(list):
    return max([len(e) for e in list])

combobox_xpad = 2

stageheaders = ['Stage 0: Affiliation', 'Stage 1: Early Childhood', 'Stage 2: Late Childhood',
                'Stage 3: Higher Education', 'Stage 4: Real Life']

class CharCreator(Frame):

    def __init__(self, master):
        super().__init__(master)
        #self.configure(height=500, width=1600)
        self.pack_propagate(True)
        self.pack(fill='both', expand=True)
        self.setup_menuwork()
        self.setup_main()
        self.current_char = Character()
        self.current_bio = Biography()
        self.currentlmlist = []
        self.currentchoices = ()
        self.currentflexxpchoices = {}
        self.freeflexxp = 0
        self.master = master
        self.nextstageoptions = []
        self.titlefont = tkFont.Font(font='TkDefaultFont')
        self.titlefont.configure(size=18)

    def update_windowsize(self):
        self.master.geometry('')

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def clear_workarea(self):
        self.workarea.destroy()
        self.workarea = Frame(self)
        self.workarea.pack(expand=1, fill=BOTH, anchor=CENTER)

    def clear_lmframe(self):
        for widget in self.lmframe.winfo_children():
            widget.destroy()

    def setup_menuwork(self):
        self.clear_frame()

        self.workarea = Frame(self)
        self.workarea.pack(expand=1, fill=BOTH, anchor=CENTER)

        self.menubar = Menu(self)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Save", command=self.save_char)
        self.filemenu.add_command(label="Open", command=self.load_char)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Start Pointbuy", command=self.start_pointbuy)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Start Wizard", command=self.start_wizard)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.master.config(menu=self.menubar)

    def setup_main(self):
        self.clear_workarea()

        self.lifemodule_wizard_button = ttk.Button(self.workarea, text="Lifemodule Wizard", command=self.start_wizard)
        self.load_button = ttk.Button(self.workarea, text="Load Character", command=self.load_char)

        self.lifemodule_wizard_button.grid(column=0, row=0, sticky=NSEW)
        self.load_button.grid(column=1, row=0, sticky=NSEW)
        self.workarea.columnconfigure(0, weight=1, uniform='mainbutton')
        self.workarea.columnconfigure(1, weight=1, uniform='mainbutton')
        self.workarea.rowconfigure(0, weight=1)


    def start_wizard(self):
        self.stage = -1

        self.setup_wizard()

    def setup_wizard(self):
        self.clear_workarea()

        self.lmframe = Frame(self.workarea)
        self.lmframe.grid(row=0, column=0, sticky=NSEW)
        self.workarea.rowconfigure(0, weight=1)

        self.navframe = Frame(self.workarea)
        self.navframe.grid(row=1, column=0, sticky=NSEW, pady=3)
        self.workarea.rowconfigure(1, weight=0)

        self.workarea.columnconfigure(0, weight=1)

        self.backbutton = Button(self.navframe, text='Back', width=10)
        self.nextbutton = Button(self.navframe, text='Next', width=10)
        self.finishbutton = Button(self.navframe, text='Finish', width=10)


        self.backbutton.grid(row=0, column=1)
        self.nextbutton.grid(row=0, column=2)
        self.finishbutton.grid(row=0, column=3, padx=5)
        self.navframe.columnconfigure(0, weight=1)

        if self.stage == -1:
            self.setup_stageneg1()
        else:
            self.setup_stage()

    def updatecharfrombio(self):
        self.current_char = self.current_bio.generatecharacter()

    def setup_stageneg1(self):
        self.clear_lmframe()

        self.namelabel = Label(self.lmframe, text='Name: ')
        self.nameentryvar = StringVar(value='New Character')
        self.nameentry = Entry(self.lmframe, textvariable=self.nameentryvar)

        self.startxplabel = Label(self.lmframe, text='Starting XPs: ')
        self.startxpentryvar = StringVar(value='5000')
        self.startxpentry = Entry(self.lmframe, textvariable=self.startxpentryvar)

        self.namelabel.grid(column=0, row=0)
        self.nameentry.grid(column=1, row=0)
        self.startxplabel.grid(column=0, row=1)
        self.startxpentry.grid(column=1, row=1)

        self.lmframe.columnconfigure(2, weight=1)
        self.lmframe.rowconfigure(2, weight=1)

        self.backbutton.configure(command=self.setup_main)
        self.nextbutton.configure(command=self.bio_setup)
        self.finishbutton.configure(command=self.finish_char)

    def bio_setup(self):
        self.current_bio = Biography(name=self.nameentryvar.get(),
                                     maxxp=int(self.startxpentryvar.get()))
        baselm = database.getstagexlms(-1)
        if len(baselm) != 1:
            print("duplicate base lm or no base lm")
            self.setup_main()
            return
        self.current_bio.addlifemodule(baselm[0])
        self.current_bio.addchoices(())
        self.current_bio.addflexxpchoice({})
        self.updatecharfrombio()
        self.advancestage()

    def generatechoicesfromtree(self, root: Comboboxtreeelem):
        optionlist = [child.getselectedindex() for child in root.children]
        choicelist = [self.generatechoicesfromtree(child) for child in root.children]
        return optionlist, choicelist

    def generatetreefromchoices(self, parent: Comboboxtreeelem=None, choiceselections=None, thislm=None):
        root = False
        if parent is None:  # root node
            root = True
            choiceselections = self.currentchoices
            chosenlm = self.current_bio.getlatestlifemodule()
            lmselect = [lm for lm in self.currentlmlist if lm.name == chosenlm.name]
            if len(lmselect) > 0:
                thislm = lmselect[0]
                self.combotreehead.setselectedindex(self.currentlmlist.index(thislm))
            else:
                return
            parent = self.combotreehead

        if thislm != None:
            for choice, choiceindex, subchoiceselections in zip(thislm.getchoices(bio=self.current_bio), choiceselections[0], choiceselections[1]):
                child = Comboboxtreeelem(parent=parent, comboboxmaster=self.comboframe)
                child.setvalues([generatedropdowntext(option) for option in choice])
                child.combobox.bind("<<ComboboxSelected>>", partial(self.updatecombos, child))
                if choiceindex != -1:
                    child.setselectedindex(choiceindex)
                parent.addchild(child)
                nextlm = choice[choiceindex]
                if not isinstance(nextlm, Lifemodule):
                    nextlm = None
                self.generatetreefromchoices(parent=child, choiceselections=subchoiceselections, thislm=nextlm)

        if root:
            self.redrawtree()

    def redrawtree(self, root: Comboboxtreeelem=None):
        if root is None:
            root = self.combotreehead
        self.redrawcombosplace(root)

        for child in root.children:
            self.redrawtree(child)

    def updatewizardcharacterdisplay(self):
        self.currentchoices = self.generatechoicesfromtree(self.combotreehead)
        self.current_bio.changechoices(self.currentchoices)

        self.flexiblexpslistselect.puttuplesinstatstate(self.genflexxptuples())
        self.current_bio.changeflexxpchoice(self.currentflexxpchoices)

        self.current_char = self.current_bio.generatecharacter()
        self.wizardcharacterdisplay.update_tree(SATheader, self.current_char.getSATtuples())
        self.prereqdisplay.update_tree(prereqheader, self.current_char.getprereqtuples())
        self.update_freeflexxpdisplay()
        curstagelabeltext = self.stagelabeltext + ' ({}, Age: {}, Free XP: {})'.format(
            self.current_char.name, self.current_char.age, self.current_char.get_freexps())
        self.stagelabel.configure(text=curstagelabeltext)

    #gets the lm associated with this treeelem, or None if it isn't an lm
    def getassociatedlm(self, treeelem:Comboboxtreeelem) -> Lifemodule:
        choicelist = []
        curelem = treeelem
        while curelem != self.combotreehead:
            optionselect = curelem.getselectedindex()
            #find which child this is
            choiceselect = [i for i, child in enumerate(curelem.parent.children) if child == curelem][0]
            choicelist = [(choiceselect, optionselect)] + choicelist
            curelem = curelem.parent

        #when done, curelem == self.combotreehead
        curlm = self.currentlmlist[self.combotreehead.getselectedindex()]
        for choice in choicelist:
            #unselected choice
            if choice[1] == -1:
                return None
            curlm = curlm.getchoices(bio=self.current_bio)[choice[0]][choice[1]]

        if isinstance(curlm, Lifemodule):
            return curlm
        else:
            return None

    def getallassociatedlms(self, treeelem:Comboboxtreeelem) -> [Lifemodule]:
        choicelist = []
        curelem = treeelem
        while curelem != self.combotreehead:
            optionselect = curelem.getselectedindex()
            #find which child this is
            choiceselect = [i for i, child in enumerate(curelem.parent.children) if child == curelem][0]
            choicelist = [(choiceselect, optionselect)] + choicelist
            curelem = curelem.parent

        # make last unselected choice
        choicelist[-1] = choicelist[-1][0], -1

        #when done, curelem == self.combotreehead
        curlm = self.currentlmlist[self.combotreehead.getselectedindex()]
        for choice in choicelist:
            #unselected choice
            if choice[1] == -1:
                lms = []
                for i in range(treeelem.getnumoptions()):
                    possiblelm = curlm.getchoices(bio=self.current_bio)[choice[0]][i]
                    if isinstance(possiblelm, Lifemodule):
                        lms.append(possiblelm)
                return lms

            curlm = curlm.getchoices(bio=self.current_bio)[choice[0]][choice[1]]

    def redrawcombos(self, treeelem:Comboboxtreeelem):
        info = treeelem.combobox.grid_info()
        col, row = info['column'], info['row']
        targetcol = col+1
        targetrow = row+1
        for child in treeelem.children:
            child.combobox.grid(row=targetrow, column=targetcol, columnspan=choicecolumnspan, sticky=EW, padx=combobox_xpad)
            childlm = self.getassociatedlm(child)
            if childlm != None:
                targetrow += childlm.getmaxchoices()
            else:
                targetrow += 1

    def redrawcombosplace(self, treeelem:Comboboxtreeelem):
        col, row = treeelem.column, treeelem.row
        targetcol = col+1
        targetrow = row+1
        for i, child in enumerate(treeelem.children):
            childlms = self.getallassociatedlms(child)
            x, y = self.longestcolumnwidthpix*targetcol, self.choicerowheightpix*targetrow
            height = self.choicerowheightpix
            width = self.longestcolumnwidthpix*choicecolumnspan
            child.combobox.pack()
            child.combobox.place(x=x, y=y, height=height, width=width)
            child.configrowcol(row=targetrow, column=targetcol, columnspan=choicecolumnspan, rowspan=1)

            if len(childlms) != 0:
                targetrow += max([childlm.getmaxchoices() for childlm in childlms]) + 1
            else:
                targetrow += 1

    def update_freeflexxpdisplay(self):
        self.flexiblexpslistselect.setlabeltext("Flexible Xps: " + str(self.freeflexxp))

    def wizard_update_lm(self, thislm):
        self.current_bio.changelifemodule(thislm)
        self.freeflexxp = thislm.flexiblexps
        self.currentflexxpchoices = {}


    def updatecombos(self, treeelem:Comboboxtreeelem, event):
        thislm = self.getassociatedlm(treeelem)
        if treeelem == self.combotreehead:
            self.wizard_update_lm(thislm)
        treeelem.destroychildren()
        if thislm != None:
            for choice in thislm.getchoices(bio=self.current_bio):
                child = Comboboxtreeelem(parent=treeelem, comboboxmaster=self.comboframe)

                child.setvalues([generatedropdowntext(option) for option in choice])
                child.combobox.bind("<<ComboboxSelected>>", partial(self.updatecombos, child))
                treeelem.addchild(child)
        self.redrawcombosplace(treeelem)
        self.updatewizardcharacterdisplay()

    def wizardcombo(self):
        pass

    def setup_combos(self, stagelabeltext):
        self.stagelabeltext = stagelabeltext
        curstagelabeltext = self.stagelabeltext + ' ({}, Age: {}, Free XP: {})'.format(
            self.current_char.name, self.current_char.age, self.current_char.get_freexps())
        self.stagelabel = Label(self.lmframe, text=curstagelabeltext, font=self.titlefont)
        self.stagelabel.grid(column=0, row=0, columnspan=4)
        self.lmframe.rowconfigure(0, weight=0)

        maxchoicedepth = max([lm.getmaxchoicedepth(bio=self.current_bio) for lm in self.currentlmlist])
        usedcolumns = choicecolumnspan + maxchoicedepth

        longestnamepix = max([lm.getmaxwidthpix(bio=self.current_bio) for lm in self.currentlmlist])
        self.longestcolumnwidthpix = ceil((longestnamepix+cboxwidthaddlpix) / choicecolumnspan)
        self.choicerowheightpix = tkFont.Font(font='TkDefaultFont').metrics('linespace')+6
        self.choiceallcolumnwidthpix = self.longestcolumnwidthpix*usedcolumns

        self.comboframe = Frame(self.lmframe, width=self.choiceallcolumnwidthpix, height=self.choicerowheightpix*maxnumchoices)
        self.comboframe.grid(column=0, row=2, rowspan=1, sticky=NSEW, padx=5)
        self.comboframe.grid_propagate(False)
        self.lmframe.columnconfigure(0, weight=0)
        self.lmframe.rowconfigure(1, weight=0)
        self.lmframe.rowconfigure(2, weight=0)



        # for i in range(numchoicecolumns):
        #     self.comboframe.columnconfigure(i, weight=0, minsize=longestcolumnwidth, maxsize=longestcolumnwidth)#, uniform='choicesc')
        # for i in range(0, maxnumchoices):
        #     self.comboframe.rowconfigure(i, weight=0, uniform='choicesr')

        self.wizardchoicelabel = Label(self.lmframe, text='Choices')
        self.wizardchoicelabel.grid(row=1, column=0, rowspan=1, sticky=NSEW)

        self.wizardcharlabel = Label(self.lmframe, text='Character')
        self.wizardcharlabel.grid(row=1, column=1, rowspan=1, sticky=NSEW)
        self.wizardprereqlabel = Label(self.lmframe, text='Prerequisites')
        self.wizardprereqlabel.grid(row=1, column=2, rowspan=1, sticky=NSEW)
        self.wizardflexxplabel = Label(self.lmframe, text='Flexible XP')
        self.wizardflexxplabel.grid(row=1, column=3, rowspan=1, sticky=NSEW)

        self.wizardcharacterdisplay = MultiColumnListbox(self.lmframe, SATheader, self.current_char.getSATtuples())
        self.wizardcharacterdisplay.grid(row=2, column=1, rowspan=2, sticky=NSEW)

        self.prereqdisplay = MultiColumnListbox(self.lmframe, prereqheader, self.current_char.getprereqtuples())
        self.prereqdisplay.grid(row=2, column=2, rowspan=2, sticky=NSEW)

        self.flexiblexpslistselect = ListSelectionFrame(self.lmframe, flexxpheader, self.addSATflexxp, self.removeSATflexxp)
        self.flexiblexpslistselect.grid(row=2, column=3, rowspan=2, sticky=N+S+W)
        self.flexiblexpslistselect.putlistinstore(database.getalllist())
        self.update_freeflexxpdisplay()

        # last row has weight so it can expand
        self.lmframe.rowconfigure(3, weight=1)
        # last column has weight so it can expand
        self.lmframe.columnconfigure(1, weight=1)
        self.lmframe.columnconfigure(2, weight=0)
        self.lmframe.columnconfigure(3, weight=0)

        lmnamelist = [generatedropdowntext(lm) for lm in self.currentlmlist]

        self.combotreehead = Comboboxtreeelem(None, self.comboframe)
        self.combotreehead.setvalues(lmnamelist)
        self.combotreehead.combobox.bind("<<ComboboxSelected>>", partial(self.updatecombos, self.combotreehead))
        self.combotreehead.combobox.place(
            x=0, y=0, width=self.longestcolumnwidthpix*choicecolumnspan, height=self.choicerowheightpix)

        # self.combotreehead.combobox.grid(row=0, column=0, columnspan=choicecolumnspan, sticky=EW, padx=combobox_xpad)

    def advancestage(self):
        if self.stage > -1 and not self.combotreehead.isoptionselected():
            messagebox.showerror("Error", "Please select a lifemodule")
            return
        if self.stage > -1 and self.freeflexxp > 0:
            messagebox.showerror("Error", "Please spend all flexible XPs")
            return
        if self.stage > -1 and self.freeflexxp < 0:
            messagebox.showerror("Error", "Too many spent flexible XPs")
            return

        if self.stage == 3:
            self.nextstageoptions = [3, 4]
        elif self.stage == 4:
            self.nextstageoptions = [4]
        else:
            self.nextstageoptions = [self.stage+1]

        if len(self.nextstageoptions) > 1 or self.stage == 4:
            idx = stageselectdialog.askstageselect(["Stage " + str(stageidx) for stageidx in self.nextstageoptions])
            if idx == None:
                return
            self.stage = self.nextstageoptions[idx]
        else:
            self.stage = self.nextstageoptions[0]

        self.current_bio.addlifemodule(Lifemodule(name='Placeholder', stage=self.stage))
        self.currentchoices = ([], [])
        self.current_bio.addchoices(self.currentchoices)
        self.currentflexxpchoices = {}
        self.current_bio.addflexxpchoice(self.currentflexxpchoices)
        self.freeflexxp = 0
        self.setup_stage()

    def reversestage(self):
        if self.stage == 0:
            self.start_wizard()
            return

        self.current_bio.removestage()
        self.stage = self.current_bio.getlatestvalidstage()

        self.currentchoices = self.current_bio.getlatestchoices()
        self.currentflexxpchoices = self.current_bio.getlatestflexxpchoices()

        #self.current_bio.removestage()

        # self.current_bio.addlifemodule(None)
        # self.currentchoices = ()
        # self.current_bio.addchoices(self.currentchoices)
        # self.currentflexxpchoices = {}
        # self.current_bio.addflexxpchoice(self.currentflexxpchoices)
        # self.freeflexxp = 0

        self.setup_stage()

    def get_valid_lms(self):
        possible_lms = database.getstagexlms(self.stage)
        final_lms = [possible_lm for possible_lm in possible_lms if self.current_bio.allowedclanrestrict(possible_lm)]
        return final_lms

    def setup_stage(self):
        self.clear_lmframe()

        self.currentlmlist = self.get_valid_lms()

        self.setup_combos(stageheaders[self.stage])

        self.nextbutton.configure(command=self.advancestage)
        self.backbutton.configure(command=self.reversestage)
        self.finishbutton.configure(command=self.finish_char)

        self.generatetreefromchoices()

        self.updatecharfrombio()

        self.updatewizardcharacterdisplay()

    def finish_char(self):
        self.current_bio.finish()
        self.setup_load()

    def setup_load(self):
        self.clear_workarea()

        #self.freexpframe = Frame(self.workarea)
        #self.freexpframe.grid(row=0, column=2, rowspan=1, columnspan=1, sticky=NE)
        #self.freexpvalue = StringVar(value=str(self.current_char.get_freexps()))
        #self.freexpnumber = Label(self.freexpframe, textvar=self.freexpvalue)
        #self.freexpnumber.pack(side=RIGHT)
        self.loadlabel = Label(self.workarea, text='', font=self.titlefont)
        self.update_freexps()
        self.loadlabel.grid(row=0, column=0, rowspan=1, columnspan=3, sticky=NSEW)

        self.load_tab_parent = ttk.Notebook(self.workarea)

        self.load_tab_parent.grid(row=1, column=0, rowspan=1, columnspan=3, sticky=NSEW)

        self.workarea.rowconfigure(0, minsize=5, weight=0)
        self.workarea.rowconfigure(1, weight=1)
        for i in range(3):
            self.workarea.columnconfigure(i, weight=1)


        self.skillstab = Frame(self.load_tab_parent)
        self.equipmenttab = Frame(self.load_tab_parent)

        self.load_tab_parent.add(self.skillstab, text="Skills")
        self.load_tab_parent.add(self.equipmenttab, text="Equipment")

        self.setup_skillstab()


    def setup_skillstab(self):
        self.skillstablistselect = ListSelectionFrame(self.skillstab, SATheader, self.addSATload, self.removeSATload)
        self.skillstablistselect.pack(expand=1, fill=BOTH)
        self.updatecharSATlistload()
        self.skillstablistselect.putlistinstore(database.getalllist())

    def update_freexps(self):
        self.loadlabel.configure(text='{}, Age: {}, Free Xps: {}'.format(
            self.current_char.name, self.current_char.age, self.current_char.get_freexps()))

    def updatecharSATlistload(self):
        self.skillstablistselect.puttuplesinstatstate(self.current_char.getSATtuples())

    def updatecharSATlistwizard(self):
        self.wizardcharacterdisplay.update_tree(SATheader, self.current_char.getSATtuples())

    def update_charinfoload(self):
        self.updatecharSATlistload()
        self.update_freexps()

    def update_charinfowizard(self):
        self.updatecharSATlistwizard()

    def addSATload(self):
        if not self.skillstablistselect.isstoreselected():
            return
        selectedSAT = self.skillstablistselect.getselectedstoreitem()
        xpamt = self.skillstablistselect.getxpamt()
        if xpamt is None:
            return
        self.current_char.addSAT(selectedSAT, xpamt)
        self.update_charinfoload()

    def removeSATload(self):
        selectedSAT = self.skillstablistselect.getselectedstatstateitem()
        xpamt = self.skillstablistselect.getxpamt()
        if xpamt is None:
            return

        self.current_char.addSAT(selectedSAT, -xpamt)
        self.update_charinfoload()

    def changeSATflexxp(self, SAT, xp):
        self.freeflexxp += -xp
        if SAT in self.currentflexxpchoices:
            self.currentflexxpchoices[SAT] += xp
        else:
            self.currentflexxpchoices[SAT] = xp
        if self.currentflexxpchoices[SAT] == 0:
            self.currentflexxpchoices.pop(SAT)

    def genflexxptuples(self):
        return [(SAT, xp) for SAT, xp in self.currentflexxpchoices.items()]

    def addSATflexxp(self):
        if not self.flexiblexpslistselect.isstoreselected():
            return
        selectedSAT = self.flexiblexpslistselect.getselectedstoreitem()
        xpamt = self.flexiblexpslistselect.getxpamt()
        if xpamt is None or xpamt < 0:
            return

        self.changeSATflexxp(selectedSAT, xpamt)
        self.flexiblexpslistselect.puttuplesinstatstate(self.genflexxptuples())
        self.current_bio.changeflexxpchoice(self.currentflexxpchoices)
        self.update_freeflexxpdisplay()
        self.updatecharfrombio()
        self.update_charinfowizard()
        self.flexiblexpslistselect.grid()

    def removeSATflexxp(self):
        if not self.flexiblexpslistselect.isstatstateselected():
            return
        selectedSAT = self.flexiblexpslistselect.getselectedstatstateitem()
        #xpamt = self.flexiblexpslistselect.getxpamt()
        #if xpamt is None:
        #    return
        #print(self.currentflexxpchoices.items())
        removexpamt = [xp for SAT, xp in self.currentflexxpchoices.items() if SAT == selectedSAT][0]

        self.changeSATflexxp(selectedSAT, -removexpamt)
        self.flexiblexpslistselect.puttuplesinstatstate(self.genflexxptuples())
        self.current_bio.changeflexxpchoice(self.currentflexxpchoices)
        self.update_freeflexxpdisplay()
        self.updatecharfrombio()
        self.update_charinfowizard()

    def start_pointbuy(self):
        self.current_char = Character()
        self.setup_load()

    def restoreflexxp(self):
        self.freeflexxp = self.current_bio.getlatestlifemodule().flexiblexps
        for SAT, xp in self.current_bio.getlatestflexxpchoices().items():
            self.changeSATflexxp(SAT, xp)

    def resumefromloaded(self):
        if self.current_bio.isfinished():
            self.setup_load()
            self.update_charinfoload()
        else:  # resume from last stage
            self.stage = self.current_bio.getlatestvalidstage()
            self.currentchoices = self.current_bio.getlatestchoices()
            self.restoreflexxp()
            self.setup_wizard()

    def save_char(self):
        filetypes = (
            ('character files', '*.btcc'),
            ('All files', '*.*')
        )

        charname = self.current_char.name

        chars_folder.mkdir(parents=True, exist_ok=True)

        filename = fd.asksaveasfile(
            title='Save a file',
            initialdir=chars_folder,
            initialfile='{}.btcc'.format(charname),
            filetypes=filetypes,
            defaultextension='.btcc')

        if filename is None:
            return

        filename = filename.name
        SaveBlob(char=self.current_char, bio=self.current_bio).save(filename)

    def load_char(self):
        filetypes = (
            ('character files', '*.btcc'),
            ('All files', '*.*')
        )

        chars_folder.mkdir(parents=True, exist_ok=True)

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir=chars_folder,
            filetypes=filetypes,
            multiple=False)

        if filename == '':
            return

        sb = load_SaveBlob(filename)
        if sb is None:
            messagebox.showerror("Error", "Cannot read character file")
            return

        self.current_char = sb.char
        self.current_bio = sb.bio

        self.resumefromloaded()






if __name__ == '__main__':
    toplevel = Tk();
    toplevel.title("BattleTech Character Creator")
    toplevel.resizable(True, True)
    toplevel.minsize(height=500, width=800)
    #toplevel.geometry('1600x500')
    toplevel.geometry('')
    app = CharCreator(toplevel)
    app.mainloop()
