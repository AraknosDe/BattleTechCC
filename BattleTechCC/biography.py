from character import Character
import database
import btccutil
import copy
import pickle


def generatedropdowntext(option):
    if isinstance(option, Lifemodule):
        if option.cost != 0:
            return option.name + " (cost: {} XP)".format(option.cost)
        else:
            return option.name
    else:
        return option.name + " ({}{} XP)".format('+' if option.xps >= 0 else '', option.xps)

def resolvemacro(SAT, macrostring, marcroreplace):
    macbegin = SAT.find(macrostring)
    if macbegin == -1:
        return SAT
    macend = macbegin + len(macrostring)
    return SAT[:macbegin] + marcroreplace + SAT[macend:]

class Biography:

    def __init__(self, maxxp=5000, name="New Character"):
        self.lifemodules = []
        self.choiceselectionslist = []
        self.flexiblexps = []
        self.spentxp = 0
        self.maxxp = maxxp
        self.age = 0
        self.name = name
        self.flexiblexpslist = []
        self.finished = False

    #def __repr__(self):
        #return "Biography(lifemodules=%r, choiceselectionslist)" % ([lm for lm in self.lifemodules], )

    def finish(self):
        self.finished = True

    def isfinished(self):
        return self.finished

    def apply(self, char, module, choiceselections, flexiblexps={}):
        if isinstance(module, Lifemodule):
            self.applylifemoduletochar(char, module, choiceselections, flexiblexps)
        elif isinstance(module, ChoiceOption):
            if len(choiceselections[1]) > 0:#additional choice at end of tree
                print("ERROR: Trying to select a subchoice on a leaf")
            self.applychoiceoption(char, module)

    def applySAT(self, char:Character, SAT, xps):
        SAT = resolvemacro(SAT, 'Affiliation', char.affiliation)
        if database.isskill(SAT):
            char.addskillfree(SAT, xps)
        elif database.istrait(SAT):
            char.addtraitfree(SAT, xps)
        elif database.isattribute(SAT):
            char.addattributefree(SAT, xps)
        elif SAT == 'None':
            return
        else:
            print("SAT <{}> not found".format(SAT))
            return

    def applychoiceoption(self, char, choiceoption):
        self.applySAT(char, choiceoption.SAT, choiceoption.xps)
        char.prerequisites += choiceoption.prereq

    def addlifemodule(self, lifemodule):
        self.lifemodules.append(lifemodule)

    def changelifemodule(self, lifemodule):
        self.lifemodules[-1] = lifemodule

    def addchoices(self, choiceselections):
        self.choiceselectionslist.append(choiceselections)

    def changechoices(self, choiceselections):
        self.choiceselectionslist[-1] = choiceselections

    def addflexxpchoice(self, choiceselections):
        self.flexiblexpslist.append(choiceselections)

    def changeflexxpchoice(self, choiceselections):
        self.flexiblexpslist[-1] = choiceselections

    def removestage(self):
        self.lifemodules.pop()
        self.choiceselectionslist.pop()
        self.flexiblexpslist.pop()

    def getlatestvalidstage(self):
        for lifemodule in reversed(self.lifemodules):
            if lifemodule is not None:
                if lifemodule.stage is not None:
                    return lifemodule.stage
        print('no valid stage in lifemodules')
        return -1

    def getlatestchoices(self):
        return self.choiceselectionslist[-1]

    def getlatestflexxpchoices(self):
        return self.flexiblexpslist[-1]

    def getlatestlifemodule(self):
        return self.lifemodules[-1]

    def getnonnonelms(self):
        return [lm for lm in self.lifemodules if lm is not None]

    def getaffiliation(self):
        affiliation = None
        for lm in self.getnonnonelms():
            if lm.affiliation is not None:
                affiliation = lm.affiliation
        return affiliation

    def getclanrestrict(self):
        for lm in self.getnonnonelms():
            if lm.clanrestrict is not None and lm.stage == 0:
                return lm.clanrestrict
        return None

    def allowedclanrestrict(self, checklm):
        clanrestrict = self.getclanrestrict()
        if clanrestrict == "no" or checklm.clanrestrict == "no":
            return True
        return clanrestrict == checklm.clanrestrict


    # choiceselections = tuple[list[int], list[choiceselections]]
    # choices is a nested list that consists of 2-tuples (choice, subchoice)
    # subchoice is the same kind of list
    # choice is a list of indicies for the choice
    def applylifemoduletochar(self, char, lifemodule, choiceselections, flexiblexps={}):
        lifemodule = copy.deepcopy(lifemodule)
        char.age = lifemodule.getnewage(char.age)

        char.spentxp += lifemodule.cost
        char.applyprerequisites(lifemodule.prereq)

        char.maxxp += lifemodule.rebate

        if lifemodule.affiliation is not None:
            if char.affiliation is not None:
                print('affiliation conflict, {} vs {}:{}'.format(char.affiliation, lifemodule.name, lifemodule.affiliation))
            else:
                char.affiliation = lifemodule.affiliation


        for SAT, xps in lifemodule.getfixedxps().items():
            self.applySAT(char, SAT, xps)

        flexiblexpsum = 0
        for SAT, xps in flexiblexps.items():
            self.applySAT(char, SAT, xps)
            flexiblexpsum += xps

        if flexiblexpsum > lifemodule.flexiblexps:
            #print("Too many points spent on flexxp")
            return

        choices = lifemodule.getchoices(bio=self)


        if len(choices) == 0:
            if len(choiceselections) > 0 and len(choiceselections[0]) > 0:
                print("trying to make choice when none are available")
                print(choiceselections)
            return

        for choicelist, choiceindex, subchoiceselections in zip(choices, choiceselections[0], choiceselections[1]):
            if choiceindex >= 0 and choiceindex < len(choicelist):
                self.apply(char, choicelist[choiceindex], subchoiceselections)

    def generatecharacter(self):
        char = Character(name=self.name, maxxp=self.maxxp)
        for lifemodule, choiceselections, flexiblexps in zip(
                self.lifemodules, self.choiceselectionslist, self.flexiblexpslist):
            if lifemodule is not None:
                self.applylifemoduletochar(char, lifemodule, choiceselections, flexiblexps)
        return char




class Lifemodule:

    def __init__(self, name, stage=None, cost=0, agedelta=None, setage=None, prereq=[], flexiblexps=0, affiliation=None, clanrestrict="no"):
        self.choices: list = []
        self.fixedxps: dict = {}
        self.name: str = name
        self.stage: int = stage
        self.cost: int = cost
        self.agedelta: int = agedelta
        self.setage: int = setage
        self.prereq = prereq
        self.flexiblexps: int = flexiblexps
        self.rebate: int = 0
        self.affiliation: str = affiliation
        #clanrestrict can be 'no', 'clan', or 'nonclan'
        self.clanrestrict: str = clanrestrict

    def __repr__(self):
        return "Lifemodule(name=%r, stage=%r, cost=%r, agedelta=%r, setage=%r, prereq=%r, flexiblexps=%r, affiliation=%r, clanrestrict=%r, choices=%r)"\
               % (self.name, self.stage, self.cost, self.agedelta, self.setage, self.prereq, self.flexiblexps, self.affiliation, self.clanrestrict, self.choices)

    def addchoice(self, choice:[]):
        self.choices.append(choice)

    def addfixedxp(self, SAT, xp):
        self.fixedxps[SAT] = xp

    def addrebatexp(self, xp):
        self.rebate += xp

    def getfixedxps(self):
        return self.fixedxps

    def getmaxchoices(self, bio: Biography=None):
        maxchoice = len(self.getchoices(bio=bio))
        for choice in self.getchoices(bio=bio):
            for option in choice:
                if isinstance(option, Lifemodule):
                    #subtract 1 to account for the choice this option is a part of
                    maxchoice = maxchoice + max(option.getmaxchoices(), 0)
        return maxchoice

    #depth of 0 is no choices at all
    def getmaxchoicedepth(self, bio: Biography=None):
        choicedepth = 0
        for choice in self.getchoices(bio=bio):
            choicedepth = 1
            for option in choice:
                if isinstance(option, Lifemodule):
                    # subtract 1 to account for the choice this option is a part of
                    choicedepth = max(1 + option.getmaxchoicedepth(), choicedepth)
        return choicedepth

    def getmaxwidthpix(self, bio: Biography = None):
        return max([btccutil.measuretext(n) for n in self.getallgeneratednames(bio=bio)])

    def getallgeneratednames(self, bio: Biography = None):
        names = [generatedropdowntext(self)]
        for choice in self.getchoices(bio=bio):
            for option in choice:
                names.append(generatedropdowntext(option))
                if isinstance(option, Lifemodule):
                    names = names + option.getallgeneratednames()
        return names

    def getgeneratednamepix(self):
        return btccutil.measuretext(generatedropdowntext(self))

    def getchoices(self, bio: Biography = None):
        returnedchoices = []
        if bio is not None:
            for choice in self.choices:
                if len(choice) == 1 and choice[0].name == 'Language/Affiliation':
                    aff = bio.getaffiliation()
                    if aff is None:
                        #print('no affiliation when replacement required')
                        return self.choices
                    langlist = database.getlangall(aff)
                    if len(langlist) == 0:
                        print("affiliation {} has no languages associated".format(aff))
                    optionlist = [ChoiceOption(lang, choice[0].xps, prereq=[]) for lang in langlist]
                    returnedchoices.append(optionlist)
                else:
                    returnedchoices.append(choice)
            return returnedchoices
        return self.choices

    def getname(self):
        return self.name

    def getnewage(self, age):
        if self.setage != None:
            return self.setage
        if self.agedelta != None:
            return age + self.agedelta
        return age

class ChoiceOption:

    def __init__(self, SAT, xps, prereq=[], name=None):
        self.xps = xps
        self.SAT = SAT
        self.prereq = prereq
        if name == None:
            self.name = SAT
        else:
            self.name = name

    def __repr__(self):
        return "ChoiceOption(SAT=%r, xps=%r, prereq=%r, name=%r)"\
               % (self.SAT, self.xps, self.prereq, self.name)

    def getname(self):
        return self.name

    def __eq__(self, other):
        if type(other) == type(self):
            return self.xps == other.xps and self.SAT == other.SAT and self.prereq == other.prereq and self.name == other.name
        return False

    def __hash__(self):
        return hash((self.xps, self.SAT, hash(tuple(self.prereq)), self.name))

class Prerequisite:

    def __init__(self, SAT, level, minmax='min'):
        self.SAT = SAT
        self.level = level
        if minmax != 'min' and minmax != 'max':
            print("minmax value <{}> not allowed".format(minmax))
        self.minmax = minmax

    def getSAT(self):
        return self.SAT

    def getlevel(self):
        return self.level

    def getminmax(self):
        return self.minmax

    def issatisfied(self, level):
        if self.minmax == 'min':
            return level >= self.level
        else:
            return level <= self.level

    def __repr__(self):
        return "Prerequisite(SAT=%r, level=%r, minmax=%r)"\
               % (self.SAT, self.level, self.minmax)

    def __str__(self):
        return "Prerequisite(%s %s %r)" \
               % (self.SAT, '>=' if self.minmax == min else '<=', self.level)

    def __hash__(self):
        return hash((self.minmax, self.SAT, self.level))

    def __eq__(self, other):
        if type(other) == type(self):
            return self.minmax == other.minmax and self.SAT == other.SAT and self.level == other.level
        return False

class SaveBlob():

    def __init__(self, char: Character=None, bio: Biography=None):
        self.char = char
        self.bio = bio

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)


def load_SaveBlob(filename) -> SaveBlob:
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except pickle.UnpicklingError:
        return None


