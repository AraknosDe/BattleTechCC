import tkinter.font as tkFont

def getmaxwidth(values):
    return max([len(e) for e in values]) + 3

def measuretext(text):
    return tkFont.Font(font='TkDefaultFont').measure(text)