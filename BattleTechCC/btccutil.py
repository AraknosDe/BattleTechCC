import tkinter.font as tkFont

def getmaxwidth(values):
    if len(values) == 0:
        print("btccutil getmaxwidth values is empty")
        return 0
    return max([len(e) for e in values]) + 3

def measuretext(text):
    return tkFont.Font(font='TkDefaultFont').measure(text)