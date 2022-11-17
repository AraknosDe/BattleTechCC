import json
import sys
from biography import *

SATtypeslist = ['Interest/', 'Career/', 'Language/', 'Art/', 'Protocol/', 'Career/', 'Survival/', 'Animal Handling/']

attributeslist = ['STR', 'BOD', 'RFL', 'DEX', 'INT', 'WIL', 'CHA', 'EDG']

clanrestrictlist = ['clan', 'nonclan', 'no']

nonmilitarycareers = ['Career/Mining',
                    'Career/Ship’s Crew',
                    'Career/Agriculture',
                    'Career/Journalist',
                    'Career/Merchant',
                    'Career/Syndicate',
                    'Career/Scientist',
                    'Career/Anthropologist',
                    'Career/Archaeologist',
                    'Career/Cartographer',
                    'Career/Communications',
                    'Career/Doctor',
                    'Career/Engineer',
                    'Career/Lawyer',
                    'Career/Management',
                    'Career/Medtech',
                    'Career/Merchant Marine',
                    'Career/Aerospace Pilot',
                    'Career/Aircraft Pilot',
                    'Career/Politician',
                    'Career/Technician',
                    'Career/Detective',
                    'Career/Police',
                    'Career/Pilot',
                    'Career/Accountant',
                    'Career/Cook'
                    ]



if len(sys.argv) < 2:
    resourcedir = 'resource'
else:
    resourcedir = sys.argv[1]

with open(resourcedir + r"/affiliations.dat") as f:
    lines = f.readlines()
    affiliations = [line.rstrip() for line in lines]

with open(resourcedir + r"/allskills.dat") as f:
    lines = f.readlines()
    skillsraw = [line.rstrip() for line in lines]

skillstolinkdict = {}
skillstothreshdict = {}
skillstotypedict = {}
lifemodulelist = []
languagedict = {}

def getlangprimary(affiliation):
    if affiliation in languagedict.keys():
        if 'primary' in languagedict[affiliation].keys():
            return [languagedict[affiliation]['primary']]
    return []

def getlangsecondary(affiliation):
    if affiliation in languagedict.keys():
        if 'secondary' in languagedict[affiliation].keys():
            return languagedict[affiliation]['secondary']
    return []

def getlangall(affiliation):
    return getlangprimary(affiliation) + getlangsecondary(affiliation)

def isgenericlang(skill):
    if 'Any' not in skill: # 'Language/<affiliation>'
        start = skill.find('/')
        aff = skill[start + 1:]
        return aff in affiliationlist and skill[:start] == "Language"
    else: # 'Language/Any <affiliation> Secondary' or 'Language/Any <affiliation>'
        start = skill.find('Any ')
        end = skill.find(' Secondary')
        if end == -1: # 'Language/Any <affiliation>'
            aff = skill[start + len('Any '):]  # skip Any
        else: # 'Language/Any <affiliation> Secondary'
            aff = skill[start + len('Any '):end]  # skip Any
        return aff in affiliationlist and skill[:start] == "Language/"


#in form 'Language/<affiliation>' or 'Language/Any <affiliation> Secondary'
def resolvegenericlang(skill):
    if 'Any' not in skill: # 'Language/<affiliation>'
        # get all for aff
        start = skill.find('/')
        aff = skill[start + 1:]  # skip /
        return getlangall(aff)
    else: # 'Language/Any <affiliation> Secondary'
        start = skill.find('Any ')
        end = skill.find(' Secondary')
        if end == -1: # 'Language/Any <affiliation>'
            aff = skill[start + len('Any '):]  # skip Any
            return getlangall(aff)
        else: # 'Language/Any <affiliation> Secondary'
            aff = skill[start + len('Any '):end]  # skip Any
            return getlangsecondary(aff)

for line in skillsraw:
    skill = line[:line.find(';')]
    linktxt = line[line.find(';') + 1:line.find(',')]
    if linktxt.find('+') == -1:
        link = (linktxt)
    else:
        plusidx = linktxt.find('+')
        link = (linktxt[:plusidx], linktxt[plusidx+1:])
    skillstolinkdict[skill] = link

    thresh = line[-4:-3]
    thresh = int(thresh)
    skillstothreshdict[skill] = thresh

    type = line[-2:]
    skillstotypedict[skill] = type

skillslist = list(skillstolinkdict.keys())

with open(resourcedir + r"/alltraits.dat") as f:
    lines = f.readlines()
    traitsraw = [line.rstrip() for line in lines]

traitstopagedict = {l[:l.find(';')]:l[l.find(';')+1:] for l in traitsraw}

traitslist = list(traitstopagedict.keys())

natappg = traitstopagedict['Natural Aptitude']
for skill in skillslist:
    newtrait = 'Natural Aptitude/{}'.format(skill)
    traitstopagedict[newtrait] = natappg
    traitslist.append(newtrait)

with open(resourcedir + r"/lifemodules.json") as f:
    data = json.load(f)

    languagedict = data['macros']['Language']

    affiliationlist = languagedict.keys()

    swlink = skillstolinkdict['Streetwise']
    swthresh = skillstothreshdict['Streetwise']
    swtype = skillstotypedict['Streetwise']
    for affiliation in affiliationlist:
        newskill = 'Streetwise/{}'.format(affiliation)
        skillstolinkdict[newskill] = swlink
        skillstothreshdict[newskill] = swthresh
        skillstotypedict[newskill] = swtype
        skillslist.append(newskill)

alllist = attributeslist+skillslist+traitslist

with open(resourcedir + r"/career.dat") as f:
    lines = f.readlines()
    careers = [line.rstrip() for line in lines]

with open(resourcedir + r"\eyecolor.dat") as f:
    lines = f.readlines()
    eyecolors = [line.rstrip() for line in lines]

with open(resourcedir + r"/eyecolor.dat") as f:
        lines = f.readlines()
        eyecolors = [line.rstrip() for line in lines]

with open(resourcedir + r"/haircolor.dat") as f:
    lines = f.readlines()
    haircolors = [line.rstrip() for line in lines]

with open(resourcedir + r"/phenotype.dat") as f:
    lines = f.readlines()
    phenotypes = [line.rstrip() for line in lines]
    phenotypes = [l[l.find('/') + 1:] for l in phenotypes]





#TODO: import equipment

def getSATtypelist(type):
    return [item for item in alllist if type == item[:item.rfind('/')]]

def parsefieldmacro(curlm, field):
    if field in fielddict.keys():
        fieldlm = fielddict[field]
    else:
        print("Field {} not found".format(field))
        return

    curlm.cost += fieldlm.cost

    curlm.choices += fieldlm.choices
    for SAT, xp in fieldlm.fixedxps.items():
        curlm.addfixedxp(SAT, xp)
    curlm.rebate += fieldlm.rebate

    if curlm.stage is not None:
        if fieldlm.stage is not None:
            print('stage conflict, {}:{} vs {}:{}'.format(curlm.name, curlm.stage, fieldlm.name, fieldlm.stage))
            return None
    else:
        curlm.stage = fieldlm.stage

    curlm.prereq += fieldlm.prereq

def parseANYmacro(SAT, xps, anyprereq=[]):
    choice = []
    if SAT == "Any":
        for option in alllist:
            choice.append(ChoiceOption(option, xps, prereq=anyprereq))
    elif SAT == "Any Trait":
        for option in traitslist:
            choice.append(ChoiceOption(option, xps, prereq=anyprereq))
    elif SAT == "Any Skill":
        for option in skillslist:
            choice.append(ChoiceOption(option, xps, prereq=anyprereq))
    elif SAT == "Any Attribute":
        for option in attributeslist:
            choice.append(ChoiceOption(option, xps, prereq=anyprereq))
    elif isgenericlang(SAT):
        return [ChoiceOption(SAT, xps, prereq=[])]

    type = SAT[:SAT.find('/')]

    for option in getSATtypelist(type):
        choice.append(ChoiceOption(option, xps, prereq=anyprereq))

    # for interesttype in SATtypeslist:
    #     if interesttype in SAT:
    #         for option in getSATtypelist(interesttype):
    #             choice.append(ChoiceOption(option, xps, prereq=[]))
    #         break

    if len(choice) == 0:
        print("No values found for ANY macro <{}>".format(SAT))
        return

    return choice

def isregularmacro(SAT):
    return SAT in macros.keys()

def parseregularmacro(SAT, xps, anyprereq=[]):
    choice = []
    for option in macros[SAT]:
        choice.append(ChoiceOption(option, xps, prereq=anyprereq))
    return choice

def parselistmacro(SAT, xps):
    choice = []
    for option in macros[SAT]:
        choice.append(ChoiceOption(option, xps, prereq=[]))

    if len(choice) == 0:
        print("No values found for macro <{}>".format(SAT))
        return

    return choice

fielddict = {}
fields = []
fieldnames = []

def parselifemodule(lmitem):
    name, dict = lmitem
    if 'stage' in dict.keys():
        stage = dict['stage']
    else:
        stage = None
    if 'cost' in dict.keys():
        cost = dict['cost']
    else:
        cost = 0

    if 'affiliation' in dict.keys():
        affiliation = dict['affiliation']
    else:
        affiliation = None

    if 'clanrestrict' in dict.keys():
        clanrestrict = dict['clanrestrict']
        if clanrestrict not in clanrestrictlist: #none of valid
            print("{} clanrestrict '{}' is not allowed".format(name, clanrestrict))
            clanrestrict = None
    else:
        clanrestrict = None

    agedelta = None
    setage = None
    prereq = []
    flexiblexps = 0

    if 'agedelta' in dict.keys():
        agedelta = dict['agedelta']
    if 'setage' in dict.keys():
        setage = dict['setage']
    if 'prereq' in dict.keys():
        prereqdict = dict['prereq']
        for SAT, cond in prereqdict.items():
            prereq.append(Prerequisite(SAT, cond[0], cond[1]))
    if 'flexiblexps' in dict.keys():
        flexiblexps = dict['flexiblexps']

    lm = Lifemodule(name, stage=stage, cost=cost, agedelta=agedelta, setage=setage, prereq=prereq,
                    flexiblexps=flexiblexps, affiliation=affiliation, clanrestrict=clanrestrict)

    if 'fixedxps' in dict.keys():
        for fixedxp in dict['fixedxps']:
            SAT, xps = list(fixedxp.items())[0]
            if "Any" in SAT:
                lm.addchoice(parseANYmacro(SAT, xps))
            elif isregularmacro(SAT):
                lm.addchoice(parseregularmacro(SAT, xps))
            elif SAT == 'Language/Affiliation':
                lm.addchoice([ChoiceOption(SAT, xps, prereq=[])])
            elif 'Language' in SAT and SAT not in skillslist:
                aff = SAT[SAT.find('/'):]
                if aff in affiliationlist:
                    lm.addchoice(getlangall(aff))
            elif SAT in macros.keys():
                lm.addchoice(parselistmacro(SAT, xps))
            else:
                lm.addfixedxp(SAT, xps)

    if 'choices' in dict.keys():
        for choicedict in dict['choices']:
            xps = choicedict['XPs']
            choice = []
            #each option is a string
            if 'prereqs' in choicedict.keys():
                for option, optprereq in zip(choicedict['options'], choicedict['prereqs']):
                    optprereqparsed = []
                    if len(optprereq) != 0:
                        optprereqSAT, (optprereqSATval, optprereqSATcond) = list(optprereq.items())[0]
                        optprereqparsed = [Prerequisite(optprereqSAT, optprereqSATval, optprereqSATcond)]
                    if "Any" in option:
                        choice = choice + parseANYmacro(option, xps, optprereqparsed)
                    elif isregularmacro(option):
                        choice = choice + parseregularmacro(option, xps, optprereqparsed)
                    elif 'Language' in option and option not in skillslist:
                        aff = option[option.find('/')+1:]
                        if aff in affiliationlist:
                            choice = choice + [ChoiceOption(lang, xps, prereq=optprereqparsed) for lang in getlangall(aff)]
                    else:
                        choice.append(ChoiceOption(option, xps, prereq=optprereqparsed))
            else:
                for option in choicedict['options']:
                    if "Any" in option:
                        choice = choice + parseANYmacro(option, xps)
                    elif isregularmacro(option):
                        choice = choice + parseregularmacro(option, xps)
                    elif 'Language' in option and option not in skillslist:
                        aff = option[option.find('/')+1:]
                        if aff in affiliationlist:
                            choice = choice + [ChoiceOption(lang, xps, prereq=[]) for lang in getlangall(aff)]
                    else:
                        choice.append(ChoiceOption(option, xps, prereq=[]))

            if len(choice) > 0:
                choice = list(set(choice))
                lm.addchoice(choice)

    if 'substage1' in dict.keys():
        choicedict = dict['substage1']['options']
        choice = []
        for lmchoice in choicedict.items():
            sublm = parselifemodule(lmchoice)
            sublm.stage = lm.stage + 0.1
            choice.append(sublm)
        if len(choice) > 0:
            lm.addchoice(choice)

    if 'substage2' in dict.keys():
        choicedict = dict['substage2']['options']
        choice = []
        for lmchoice in choicedict.items():
            sublm = parselifemodule(lmchoice)
            sublm.stage = lm.stage + 0.2
            choice.append(sublm)
        if len(choice) > 0:
            lm.addchoice(choice)

    if 'substage3' in dict.keys():
        choicedict = dict['substage3']['options']
        choice = []
        for lmchoice in choicedict.items():
            sublm = parselifemodule(lmchoice)
            sublm.stage = lm.stage + 0.3
            choice.append(sublm)
        if len(choice) > 0:
            lm.addchoice(choice)

    if 'field' in dict.keys():
        fieldmacro = dict['field']
        parsefieldmacro(lm, fieldmacro)

    return lm

with open(resourcedir + r"/lifemodules.json") as f:
    data = json.load(f)
    macros = data['macros']
    fieldmacros = data['macros']['Fields']
    elementcost = fieldmacros.pop('elementcost')
    elementrebate = fieldmacros.pop('elementrebate')
    for field in fieldmacros.items():
        fields.append(parselifemodule(field))
        numelems = len(fields[-1].fixedxps) + len(fields[-1].choices)
        fields[-1].cost = numelems * elementcost
        fields[-1].rebate = numelems * elementrebate
        fielddict[fields[-1].name] = fields[-1]
        fieldnames.append(fields[-1].name)

    lifemodules = data['lifemodules']
    for lmitem in lifemodules.items():
        lifemodulelist.append(parselifemodule(lmitem))

def getlink(skill):
    return skillstolinkdict[skill]

def getthresh(skill):
    return skillstothreshdict[skill]

def gettype(skill):
    return skillstotypedict[skill]

def gettraitpage(trait):
    return traitstopagedict[trait]

def getallskills():
    return skillslist

def isskill(SAT):
    # for skillgeneric in skillgenerics:
    #     if skillgeneric in SAT:
    #         return True
    return SAT in skillslist

def istrait(SAT):
    return SAT in traitslist

def isattribute(SAT):
    return SAT in attributeslist

def getstagexlms(stage):
    return [lm for lm in lifemodulelist if lm.stage == stage]

def getalllist():
    return alllist















