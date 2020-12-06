#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main codes of ATD Map Creator
"""

from json import dumps
import tkinter as tk


class Map:

    _maps = []

    def __init__(self):
        self._map = {"width": 10, "height": 15, "plateaus": [],
                     "paths": [{"wayPoints": []}]}
        Map._maps.append(self)

    def file(self, file):
        self._file = file

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
        elif first["y"] == 0 or first["y"] == h:
            first["y"] += first["y"]*(3/h)-1.5
        else:
            print("""Can't edit start or stop point.
Please make it manually or change them to right way.""")

    def fix(self):
        data = self._map
        w = data["width"]-1
        h = data["height"]-1
        dic = data["paths"][0]["wayPoints"]
        Map.addit(w, h, dic[0], dic[1])
        Map.addit(w, h, dic[-1], dic[-2])
        return data

    def write(self):
        file = self._file
        try:
            data = self.fix()
            with open(file, "w+") as file:
                file.write(dumps(data, indent=2, sort_keys=True))
        except Exception as e:
            print("Wrong path!")


class Path(tk.Toplevel):

    def __init__(self, parent, maps, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.maps = maps
        self.gui()

    def getCoor(self, r):
        return [x/self.sc for x in self.canvas.coords(r)]

    def isPoint(self, x, y):
        rects = self.rects
        try:
            prex = self.maps.get()[-1][-1]["x"]
            prey = self.maps.get()[-1][-1]["y"]
            if x > prex:
                for X in range(int(x-prex)):
                    X += prex+2
                    Y = y
                    if rects[Y*self.maps.get()[0]+X] != -1:
                        return False
            if x < prex:
                for X in range(int(prex-x)):
                    X += x+2
                    Y = y
                    if rects[Y*self.maps.get()[0]+X] != -1:
                        return False
            if y > prey:
                for Y in range(int(y-prey)):
                    X = x+2
                    Y += prey
                    if rects[Y*self.maps.get()[0]+X] != -1:
                        return False
            if y < prey:
                for Y in range(int(prey-y)):
                    X = x+2
                    Y += y
                    if rects[Y*self.maps.get()[0]+X] != -1:
                        return False
            return True
        except IndexError:
            return True

    def lclick(self, event):
        t = event.widget.find_closest(event.x, event.y)[0]
        rects = self.rects
        canvas = self.canvas
        if rects[t] == 0:
            rects[t] = 1
            canvas.itemconfig(t, fill="blue")
        elif rects[t] == 1:
            rects[t] = -1
            canvas.itemconfig(t, fill="yellow")
        else:
            rects[t] = 0
            canvas.itemconfig(t, fill="red")

    def rclick(self, event):
        t = event.widget.find_closest(event.x, event.y)[0]
        sc = self.sc
        maps = self.maps
        canvas = self.canvas
        c = self.getCoor(t)
        x = (c[0]+c[2])/2*sc
        y = (c[1]+c[3])/2*sc
        X = c[0]
        Y = self.maps.get()[1]-1-c[1]
        if self.rects[t] == -1:
            if len(maps.get()[3]) == 0 and maps.isEdge(X, c[1]):
                if self.isPoint(X, Y) and maps.point(X, Y):
                    canvas.create_text((x, y), text=f"{len(maps.get()[3])}")
            elif len(maps.get()[3]) == 0 and not(maps.isEdge(X, c[1])):
                print("Not edge!")
            else:
                if self.isPoint(X, Y) and maps.point(X, Y):
                    canvas.create_text((x, y), text=f"{len(maps.get()[3])}")

    def finish(self):
        for r in self.rects:
            if self.rects[r] == 1:
                c = self.getCoor(r)
                self.maps.plateau(c[0], self.maps.get()[1]-1-c[1])
        self.maps.write()
        self.destroy()

    def gui(self):
        self.title("Anuto TD Map Creator")
        data = self.maps.get()
        self.sc = 50
        sc = self.sc
        w = data[0]*sc
        h = data[1]*sc
        self.resizable(False, False)
        self.geometry(f"{w}x{h+160}")
        canvas = tk.Canvas(self, width=w, height=h)
        canvas.create_rectangle(0, 0, w-1, h-1, fill="red")
        self.canvas = canvas
        rects = {}
        for y in range(data[1]-1, -1, -1):
            for x in range(data[0]):
                rects[canvas.create_rectangle(x*sc, y*sc, (x+1)*sc, (y+1)*sc,
                                              fill="red")] = 0
        for r in rects:
            canvas.tag_bind(r, "<Button-1>", self.lclick)
            canvas.tag_bind(r, "<Button-3>", self.rclick)
        self.rects = rects
        tk.Label(self, text="Red : Empty\nBlue : Plateau\nYellow : Path",
                 font=("Arial", 28), width=15).pack()
        canvas.pack()
        tk.Button(self, text="Finish", font=("Arial", 16), width=10,
                  command=self.finish).pack()


class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.gui()

    def next(self, f, x, y):
        maps = Map()
        maps.file(f.get())
        try:
            maps.size(int(x.get()), int(y.get()))
        except Exception:
            pass
        self.path = Path(self, maps)

    def strings(self):
        self.F = tk.StringVar()
        self.F.set("map.json")
        self.X = tk.StringVar()
        self.X.set("Width (default 10)")
        self.Y = tk.StringVar()
        self.Y.set("Height (default 15)")

    def gui(self):
        self.title("Anuto TD Map Creator")
        self.geometry("350x300")
        self.resizable(False, False)
        self.strings()
        tk.Label(self, text="File Name", font=("Arial", 28), width=10).pack()
        E = tk.Entry(self, textvariable=self.F, font=("Arial", 20), width=20)
        E.pack()
        tk.Label(self, text="Size", font=("Arial", 28), width=10).pack()
        X = tk.Entry(self, textvariable=self.X, font=("Arial", 20), width=20)
        X.pack()
        Y = tk.Entry(self, textvariable=self.Y, font=("Arial", 20), width=20)
        Y.pack()
        tk.Label(self, text="", font=("Arial", 28), width=10).pack()
        tk.Button(self, text="Next", font=("Arial", 16), width=10,
                  command=lambda: self.next(E, X, Y)).pack()

if __name__ == "__main__":
    app = Main()
    app.mainloop()
