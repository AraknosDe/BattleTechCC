import json
import sys
import os
from pathlib import Path
from biography import *

SATtypeslist = ['Interest/', 'Career/', 'Language/', 'Art/', 'Protocol/', 'Career/', 'Survival/']

skillgenerics = ['Streetwise/']

attributeslist = ['STR', 'BOD', 'RFL', 'DEX', 'INT', 'WIL', 'CHA', 'EDG']

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
                    'Career/Pilot'
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
    return [item for item in alllist if type in item]

def parselangmacro(lm, SAT, xps):
    pass

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

def parseANYmacro(SAT, xps):
    choice = []
    if SAT == "Any":
        for option in alllist:
            choice.append(ChoiceOption(option, xps, prereq=[]))

    type = SAT[:SAT.find('/')]

    for option in getSATtypelist(type):
        choice.append(ChoiceOption(option, xps, prereq=[]))

    # for interesttype in SATtypeslist:
    #     if interesttype in SAT:
    #         for option in getSATtypelist(interesttype):
    #             choice.append(ChoiceOption(option, xps, prereq=[]))
    #         break

    if len(choice) == 0:
        print("No values found for ANY macro <{}>".format(SAT))
        return

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
                    flexiblexps=flexiblexps, affiliation=affiliation)

    if 'fixedxps' in dict.keys():
        for fixedxp in dict['fixedxps']:
            SAT, xps = list(fixedxp.items())[0]
            if "Any" in SAT:
                lm.addchoice(parseANYmacro(SAT, xps))
            elif SAT == 'Language/Affiliation':
                lm.addchoice([ChoiceOption(SAT, xps, prereq=[])])
            elif SAT in macros.keys():
                lm.addchoice(parselistmacro(SAT, xps))
            else:
                lm.addfixedxp(SAT, xps)

    if 'choices' in dict.keys():
        for choicedict in dict['choices']:
            xps = choicedict['XPs']
            choice = []
            #each option is a string
            for option in choicedict['options']:
                if "Any" in option:
                    choice = choice + parseANYmacro(lm, option, xps)
                else:
                    choice.append(ChoiceOption(option, xps, prereq=[]))
            if len(choice) > 0:
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

lifemodulelist = []
languagedict = {}

with open(resourcedir + r"/lifemodules.json") as f:
    data = json.load(f)
    macros = data['macros']
    fieldmacros = data['macros']['Fields']
    elementcost = fieldmacros.pop('elementcost')
    elementrebate = fieldmacros.pop('elementrebate')
    for field in fieldmacros.items():
        fields.append(parselifemodule(field))
        numelems = len(fields[-1].fixedxps)
        fields[-1].cost = numelems * elementcost
        fields[-1].rebate = numelems * elementrebate
        fielddict[fields[-1].name] = fields[-1]
        fieldnames.append(fields[-1].name)

    languagedict = data['macros']['Language']

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
    for skillgeneric in skillgenerics:
        if skillgeneric in SAT:
            return True
    return SAT in skillslist

def istrait(SAT):
    return SAT in traitslist

def isattribute(SAT):
    return SAT in attributeslist

def getstagexlms(stage):
    return [lm for lm in lifemodulelist if lm.stage == stage]

def getalllist():
    return alllist

def getlangprimary(affiliation):
    if affiliation in languagedict.keys():
        if 'primary' in languagedict[affiliation].keys():
            return languagedict[affiliation]['primary']
    return None

def getlangsecondary(affiliation):
    if affiliation in languagedict.keys():
        if 'secondary' in languagedict[affiliation].keys():
            return languagedict[affiliation]['secondary']
    return []

def getlangall(affiliation):
    primary = getlangprimary(affiliation)
    if primary is not None:
        return [primary] + getlangsecondary(affiliation)
    else:
        return getlangsecondary(affiliation)

#in form 'Language/<affiliation>' or 'Language/Any <affiliation> Secondary'
def resolvegenericlang(skill):
    if 'Any' not in skill:  # 'Language/<affiliation>'
        # get all for aff
        start = skill.find('/')
        aff = skill[start + 1:]  # skip /
        return getlangall(aff)
    else:  # 'Language/Any <affiliation> Secondary'
        start = skill.find('Any')
        aff = skill[start + len('Any '):]  # skip /
        return getlangsecondary(aff)













