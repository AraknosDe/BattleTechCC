import database

skillleveltable = [20, 30, 50, 80, 120, 170, 230, 300, 380, 470, 570]
skillleveltablefast = [18, 27, 45, 72, 108, 153, 207, 270, 342, 423, 513]
skillleveltableslow = [22, 33, 55, 88, 132, 187, 253, 330, 418, 517, 627]

class Character:
    def __init__(self, name='New Character', maxxp=5000):
        self.skills = {}
        self.traits = {}
        self.equipment = {}
        self.attributes = {'STR':0, 'BOD':0, 'RFL':0, 'DEX':0, 'INT':0, 'WIL':0, 'CHA':0, 'EDG':0}
        self.lifemodules = []
        self.spentxp = 0
        self.maxxp = maxxp
        self.spentcb = 0
        self.totalweight = 0
        self.age = 0
        self.name = name
        self.prerequisites = []
        self.affiliation = None

    def get_freexps(self):
        return self.maxxp - self.spentxp

    def addSAT(self, SAT, xp):
        if database.isskill(SAT):
            self.addskill(SAT, xp)
        elif database.istrait(SAT):
            self.addtrait(SAT, xp)
        elif database.isattribute(SAT):
            self.addattribute(SAT, xp)
        else:
            print("addSAT <{}> not found".format(SAT))
            return

    def addSATfree(self, SAT, xp):
        if database.isskill(SAT):
            self.addskillfree(SAT, xp)
        elif database.istrait(SAT):
            self.addtraitfree(SAT, xp)
        elif database.isattribute(SAT):
            self.addattributefree(SAT, xp)
        else:
            print("addSATfree <{}> not found".format(SAT))
            return

    def addequipment(self, item, qty, cb, weight):
        self.spentcb += cb
        self.totalweight += weight
        if item in self.equipment:
            self.equipment[item] += qty
        else:
            self.equipment[item] = qty

    def addskill(self, skill, xp):
        self.spentxp += xp
        self.addskillfree(skill, xp)

    def addtrait(self, trait, xp):
        self.spentxp += xp
        self.addtraitfree(trait, xp)

    def addattribute(self, attribute, xp):
        self.spentxp += xp
        self.addattributefree(attribute, xp)


    def addskillfree(self, skill, xp):
        if skill in self.skills:
            self.skills[skill] += xp
        else:
            self.skills[skill] = xp
        if self.skills[skill] == 0:
            self.skills.pop(skill)

    def addtraitfree(self, trait, xp):
        if trait in self.traits:
            self.traits[trait] += xp
        else:
            self.traits[trait] = xp
        if self.traits[trait] == 0:
            self.traits.pop(trait)

    def addattributefree(self, attribute, xp):
        if attribute in self.attributes:
            self.attributes[attribute] += xp
        else:
            self.attributes[attribute] = xp
        if self.attributes[attribute] == 0:
            self.attributes.pop(attribute)

    def getSATtuples(self):
        return [(skill, xp, self.getskilllevel(xp)) for skill, xp in self.skills.items()] + \
            [(trait, xp, self.getATlevel(xp)) for trait, xp in self.traits.items()] + \
            [(attribute, xp, self.getATlevel(xp)) for attribute, xp in self.attributes.items()]

    def getprereqtuples(self):
        return [(p.getSAT(), p.getlevel(), p.getminmax()) for p in self.prerequisites]

    def getskilllevel(self, xp):
        if 'Fast Learner' in self.traits.keys() and self.getATlevel(self.traits['Fast Learner']) >= 3:
            tabletouse = skillleveltablefast
        elif 'Slow Learner' in self.traits.keys() and self.getATlevel(self.traits['Slow Learner']) <= -3:
            tabletouse = skillleveltableslow
        else:
            tabletouse = skillleveltable
        for level, thresh in enumerate(tabletouse):
            if xp < thresh:
                return level-1
        return 10

    def getATlevel(self, xp):
       return int(xp/100)

