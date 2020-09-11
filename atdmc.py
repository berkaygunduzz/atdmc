#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main codes of ATD Map Creator
"""

from json import dumps
from tkinter import *


class Map:

    _maps = []

    def __init__(self):
        self._map = {"width": 10, "height": 10, "plateaus": [],
                     "paths": [{"wayPoints": []}]}
        Map._maps.append(self)

    def size(self, width, height):
        self._map["width"] = width
        self._map["height"] = height

    def check(self, x, y):
        w = self._map["width"]
        h = self._map["height"]
        if x < w and x >= 0:
            if y < h and y >= 0:
                return True
        return False

    def checkpl(self, x, y):
        for pl in self._map["plateaus"]:
            if pl["x"] == x and pl["y"] == y:
                return False
        return True

    def plateau(self, x, y):
        if self.checkpl(x, y) and self.check(x, y):
            self._map["plateaus"].append({"name": "basic", "x": x, "y": y})
        else:
            print("Invalid plateau!")

    def replateau(self):
        try:
            self._map["plateaus"].pop()
        except Exception as e:
            # Returns 'pop from empty list' when list is empty
            return str(e)

    def emptypl(self):
        msg = ""
        while msg != "pop from empty list":
            self.replateau()

    def checkpt(self, x, y):
        try:
            pre_x = self._map["paths"][0]["wayPoints"][-1]["x"]
            pre_y = self._map["paths"][0]["wayPoints"][-1]["y"]
        except IndexError:
            return True
        if pre_x == x and pre_y == y:
            return False
        elif (pre_x-x)*(pre_y-y) == 0:
            return True
        else:
            return False

    def point(self, x, y):
        if self.checkpt(x, y) and self.check(x, y):
            self._map["paths"][0]["wayPoints"].append({"x": x, "y": y})
            return True
        else:
            print("Invalid path!")
            return False

    def repoint(self):
        try:
            self._map["paths"][0]["wayPoints"].pop()
        except Exception as e:
            # Returns 'pop from empty list' when list is empty
            return str(e)

    def emptypt(self):
        msg = ""
        while msg != "pop from empty list":
            self.repoint()

    def isEdge(self, x, y):
        w = self._map["width"]-1
        h = self._map["height"]-1
        if (x == 0 or x == w) or (y == 0 or y == h):
            return True
        return False

    def get(self):
        data = [self._map["width"], self._map["height"]]
        data.append(self._map["plateaus"])
        data.append(self._map["paths"][0]["wayPoints"])
        return data

    def addit(w, h, first, sec):
        if first["x"] == 0 or first["x"] == w:
            first["x"] += first["x"]*(3/w)-1.5
        elif first["y"] == 0 or first["y"] == w:
            first["y"] += first["y"]*(3/h)-1.5
        else:
            print("""Can't edit start and stop point.
Please make it manually or change them to right way.""")

    def fix(self):
        data = self._map
        w = data["width"]-1
        h = data["height"]-1
        dic = data["paths"][0]["wayPoints"]
        Map.addit(w, h, dic[0], dic[1])
        Map.addit(w, h, dic[-1], dic[-2])
        return data

    def write(self, file):
        try:
            data = self.fix()
            with open(file, "w+") as file:
                file.write(dumps(data, indent=2, sort_keys=True))
        except Exception:
            print("Wrong path!")


def draw(window, ENTRY_FILE, ENTRY_S_X, ENTRY_S_Y):
    global maps

    def getCoor(r):
        return [x/sc for x in canvas.coords(r)]

    def isPoint(x, y):
        try:
            prex = maps.get()[-1][-1]["x"]
            prey = maps.get()[-1][-1]["y"]
            if x > prex:
                for X in range(int(x-prex)):
                    X += prex+2
                    Y = y
                    if rects[Y*maps.get()[0]+X] != -1:
                        return False
            if x < prex:
                for X in range(int(prex-x)):
                    X += x+2
                    Y = y
                    if rects[Y*maps.get()[0]+X] != -1:
                        return False
            if y > prey:
                for Y in range(int(y-prey)):
                    X = x+2
                    Y += prey
                    if rects[Y*maps.get()[0]+X] != -1:
                        return False
            if y < prey:
                for Y in range(int(prey-y)):
                    X = x+2
                    Y += y
                    if rects[Y*maps.get()[0]+X] != -1:
                        return False
            return True
        except IndexError:
            return True

    def lclick(event):
        t = event.widget.find_closest(event.x, event.y)[0]
        if rects[t] == 0:
            rects[t] = 1
            canvas.itemconfig(t, fill="blue")
        elif rects[t] == 1:
            rects[t] = -1
            canvas.itemconfig(t, fill="yellow")
        else:
            rects[t] = 0
            canvas.itemconfig(t, fill="red")

    def rclick(event):
        t = event.widget.find_closest(event.x, event.y)[0]
        c = getCoor(t)
        x = (c[0]+c[2])/2*sc
        y = (c[1]+c[3])/2*sc
        X = c[0]
        Y = maps.get()[1]-1-c[1]
        if rects[t] == -1:
            if len(maps.get()[3]) == 0 and maps.isEdge(X, c[1]):
                if isPoint(X, Y) and maps.point(X, Y):
                    canvas.create_text((x, y), text=f"{len(maps.get()[3])}")
            elif len(maps.get()[3]) == 0 and not(maps.isEdge(X, c[1])):
                print("Not edge!")
            else:
                if isPoint(X, Y) and maps.point(X, Y):
                    canvas.create_text((x, y), text=f"{len(maps.get()[3])}")

    def finish():
        global maps
        for r in rects:
            if rects[r] == 1:
                c = getCoor(r)
                maps.plateau(c[0], maps.get()[1]-1-c[1])
        maps.write(file)
        window.destroy()

    file = ENTRY_FILE.get()
    try:
        maps.size(int(ENTRY_S_X.get()), int(ENTRY_S_Y.get()))
    except Exception:
        pass
    data = maps.get()
    sc = 50
    w = data[0]*sc
    h = data[1]*sc
    table = Toplevel(window)
    table.resizable(False, False)
    table.geometry(f"{w}x{h+160}")
    canvas = Canvas(table, width=w, height=h)
    canvas.create_rectangle(0, 0, w-1, h-1, fill="red")
    rects = {}
    for y in range(data[1]-1, -1, -1):
        for x in range(data[0]):
            rects[canvas.create_rectangle(x*sc, y*sc, (x+1)*sc, (y+1)*sc,
                                          fill="red")] = 0

    for r in rects:
        canvas.tag_bind(r, "<Button-1>", lclick)
        canvas.tag_bind(r, "<Button-3>", rclick)

    CHOOSE_LABEL = Label(table,
                         text="Red : Empty\nBlue : Plateau\nYellow : Path",
                         font=("Arial", 28), width=15)
    CHOOSE_LABEL.pack()
    canvas.pack()
    BUTTON_FINISH = Button(table, text="Finish", font=("Arial", 16), width=10,
                           command=finish)
    BUTTON_FINISH.pack()

if __name__ == "__main__":
    maps = Map()

    window = Tk()
    window.title("Anuto TD Map Creator")
    window.geometry("350x300")
    window.resizable(False, False)

    # File Name
    STR_FILE = StringVar()
    LABEL_FILE = Label(window, text="File Name", font=("Arial", 28), width=10)
    LABEL_FILE.pack()
    ENTRY_FILE = Entry(window, textvariable=STR_FILE, font=("Arial", 20),
                       width=20)
    ENTRY_FILE.pack()
    STR_FILE.set("map.json")

    # Size
    STR_S_X = StringVar()
    STR_S_Y = StringVar()
    LABEL_SIZE = Label(window, text="Size", font=("Arial", 28), width=10)
    LABEL_SIZE.pack()
    ENTRY_S_X = Entry(window, textvariable=STR_S_X, font=("Arial", 20),
                      width=20)
    ENTRY_S_X.pack()
    ENTRY_S_Y = Entry(window, textvariable=STR_S_Y, font=("Arial", 20),
                      width=20)
    ENTRY_S_Y.pack()
    STR_S_X.set("Width (default 10)")
    STR_S_Y.set("Height (default 10)")

    # Next
    BUTTON_MAKE = Button(window, text="Next", font=("Arial", 16), width=10,
                         command=lambda: draw(window, ENTRY_FILE, ENTRY_S_X,
                                              ENTRY_S_Y))
    EMPTY_LABEL = Label(window, text="", font=("Arial", 28), width=10)
    EMPTY_LABEL.pack()
    BUTTON_MAKE.pack()

    window.mainloop()

