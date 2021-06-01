#!/usr/bin/python

# модуль TkInter для GUI
from tkinter import *
from tkinter import messagebox
# вспомогательные модули
from datetime import datetime
import random

# размер поля
(width, height) = (16, 16)

buttons = {
    "click": "<Button-1>", # левая кнопка мыши - открыть ячейку
    "flag": "<Button-3>" # правая кнопка мыши - поставить флаг
}

class Game:

    def __init__(self, tk):

        # инициализируем окно
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()

        # импортируем графику
        self.images = {
            "unsolved": PhotoImage(file = "tiles/unsolved.png"),
            "empty": PhotoImage(file = "tiles/empty.png"),
            "mine": PhotoImage(file = "tiles/mine.png"),
            "flag": PhotoImage(file = "tiles/flag.png"),
            "wrong": PhotoImage(file = "tiles/wrong.png"),
            "numbers": [
                PhotoImage(file = "tiles/1.png"),
                PhotoImage(file = "tiles/2.png"),
                PhotoImage(file = "tiles/3.png"),
                PhotoImage(file = "tiles/4.png"),
                PhotoImage(file = "tiles/5.png"),
                PhotoImage(file = "tiles/6.png"),
                PhotoImage(file = "tiles/7.png"),
                PhotoImage(file = "tiles/8.png")
            ]
        }

        # устанавливаем счетчики
        self.labels = {
            "time": Label(self.frame, text = "00:00:00"),
            "mines": Label(self.frame, text = "Мин: 0"),
            "flags": Label(self.frame, text = "Флагов: 0")
        }
        self.labels["mines"].grid(
            row = width+1, 
            column = 0, 
            columnspan = int(height/3)
        ) 
        self.labels["time"].grid(
            row = width+1, 
            column = int(height/3), 
            columnspan = int(height/3)
        ) 
        self.labels["flags"].grid(
            row = width+1, 
            column = int(height/3)*2, 
            columnspan = int(height/3)
        ) 

        self.restart() 
        self.updateTimer() 

    # инициализация поля
    def generateField(self):
        self.flagCount = 0
        self.clickedCount = 0
        self.startTime = None

        # кнопки поля
        self.tiles = dict({})
        self.mines = 0
        for x in range(0, width):
            for y in range(0, height):
                if y == 0:
                    self.tiles[x] = {}

                id = str(x) + "_" + str(y)
                isMine = False

                if random.uniform(0.0, 1.0) < 0.1:
                    isMine = True
                    self.mines += 1

                tile = {
                    "id": id,
                    "isMine": isMine,
                    "state": "default",
                    "coords": {
                        "x": x,
                        "y": y
                    },
                    "button": Button(self.frame, image = self.images["unsolved"]),
                    "mines": 0 # количество мин вокруг ячейки, далее подсчитается вторым циклом
                }

                tile["button"].bind(buttons["click"], self.onClickWrapper(x, y))
                tile["button"].bind(buttons["flag"], self.onRightClickWrapper(x, y))
                tile["button"].grid( row = x+1, column = y )

                self.tiles[x][y] = tile

        # еще раз проходимся циклом, чтобы проставить цифры
        for x in range(0, width):
            for y in range(0, height):
                mc = 0
                for n in self.getNeighbors(x, y):
                    mc += 1 if n["isMine"] else 0
                self.tiles[x][y]["mines"] = mc

    def restart(self):
        self.generateField()
        self.updateStats()

    def updateStats(self):
        self.labels["flags"].config(text = "Флагов: "+str(self.flagCount))
        self.labels["mines"].config(text = "Мин: "+str(self.mines))

    def gameOver(self, won):
        for x in range(0, width):
            for y in range(0, height):
                if self.tiles[x][y]["isMine"] == False and self.tiles[x][y]["state"] == "flagged":
                    self.tiles[x][y]["button"].config(image = self.images["wrong"])
                if self.tiles[x][y]["isMine"] == True and self.tiles[x][y]["state"] != "flagged":
                    self.tiles[x][y]["button"].config(image = self.images["mine"])

        self.tk.update()

        msg = "Вы победили! Начать сначала?" if won else "Вы проиграли! Начать сначала?"
        res = messagebox.askyesno("Игра окончена", msg)
        if res:
            self.restart()
        else:
            self.tk.quit()

    def updateTimer(self):
        ts = "00:00:00"
        if self.startTime != None:
            delta = datetime.now() - self.startTime
            ts = str(delta).split('.')[0] 
            if delta.total_seconds() < 36000:
                ts = "0" + ts
        self.labels["time"].config(text = ts)
        self.frame.after(100, self.updateTimer)

    def getNeighbors(self, x, y):
        neighbors = []
        coords = [
            {"x": x-1,  "y": y-1},  
            {"x": x-1,  "y": y},    
            {"x": x-1,  "y": y+1},  
            {"x": x,    "y": y-1},  
            {"x": x,    "y": y+1},  
            {"x": x+1,  "y": y-1},  
            {"x": x+1,  "y": y},    
            {"x": x+1,  "y": y+1},  
        ]
        for n in coords:
            try:
                neighbors.append(self.tiles[n["x"]][n["y"]])
            except KeyError:
                pass
        return neighbors

    def onClickWrapper(self, x, y):
        return lambda Button: self.onClick(self.tiles[x][y])

    def onRightClickWrapper(self, x, y):
        return lambda Button: self.onRightClick(self.tiles[x][y])

    def onClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        # проверяем, является ли ячейка миной
        if tile["isMine"] == True:
            self.gameOver(False)
            return

        # меняем тайл при нажатии на клетку
        if tile["mines"] == 0:
            tile["button"].config(image = self.images["empty"])
            self.clearSurroundingTiles(tile["id"])
        else:
            tile["button"].config(image = self.images["numbers"][tile["mines"]-1])
        if tile["state"] != "clicked":
            tile["state"] = "clicked"
            self.clickedCount += 1
        if self.clickedCount == (width * height) - self.mines:
            self.gameOver(True)

    def onRightClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        # ставим флаг, если его не было
        if tile["state"] == "default":
            tile["button"].config(image = self.images["flag"])
            tile["state"] = "flagged"
            # убираем возможность клика
            tile["button"].unbind(buttons["click"])
            self.flagCount += 1
            self.updateStats()
        # убираем флаг, если он был
        elif tile["state"] == "flagged":
            tile["button"].config(image = self.images["unsolved"])
            tile["state"] = "default"
            # возвращаем возможность клика
            tile["button"].bind(buttons["click"], self.onClickWrapper(tile["coords"]["x"], tile["coords"]["y"]))
            self.flagCount -= 1
            self.updateStats()

    # раскрываем соседние ячейки, в которых нет бомб
    def clearSurroundingTiles(self, id):
        queue = [id]

        while len(queue) != 0:
            key = queue.pop(0)
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])

            for tile in self.getNeighbors(x, y):
                self.clearTile(tile, queue)

    def clearTile(self, tile, queue):
        if tile["state"] != "default":
            return

        if tile["mines"] == 0:
            tile["button"].config(image = self.images["empty"])
            queue.append(tile["id"])
        else:
            tile["button"].config(image = self.images["numbers"][tile["mines"]-1])

        tile["state"] = "clicked"
        self.clickedCount += 1

window = None

def main():
    window = Tk()
    window.title("Сапёр")
    Game(window)
    window.mainloop()

if __name__ == "__main__":
    main()
