import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import random

class GameThread(QThread):
    def __init__(self, Win):
        super(GameThread, self).__init__()
        self.Win = Win
        self.Flag = True

    def run(self):
        while self.Flag:
            self.Win.update()
            time.sleep(0.1)

    def stop(self):
        self.Flag = False
        self.quit()

class Spike:
    def __init__(self):
        self.Position = [random.randint(0, 49) * 10, random.randint(0, 49) * 10]

class SnakeChild:
    def __init__(self, Position):
        self.Position = Position
        self.OldPosition = self.Position

    def UpdatePos(self, OldPos):
        self.OldPosition = [coords for coords in self.Position]
        self.Position = OldPos

class Food:
    def __init__(self):
        self.Position = [random.randint(0, 49) * 10, random.randint(0, 49) * 10]

class Snake:
    def __init__(self):
        self.Position = [0, 0]
        self.Direction = "Right"
        self.ChildrenList = []
        self.SpikeList = []
        self.Error = False

        self.SpawnFood()

    def AddChild(self):
        self.ChildrenList.append(SnakeChild(Position = [coord for coord in self.Position]))

    def Move(self):
        Step = 10
        self.OldPosition = [coord for coord in self.Position]
        if self.Direction == "Left":
            self.Position[0] -= Step
        elif self.Direction == "Right":
            self.Position[0] += Step
        elif self.Direction == "Up":
            self.Position[1] -= Step
        else:
            self.Position[1] += Step
        self.UpdateChildren()

    def UpdateChildren(self):
        for x in range(0, len(self.ChildrenList)):
            if x == 0:
                self.ChildrenList[0].UpdatePos(self.OldPosition)
            else:
                self.ChildrenList[x].UpdatePos(self.ChildrenList[x - 1].OldPosition)

    def SpawnFood(self):
        self.Food = Food()

    def SpawnSpike(self):
        SpikeChance = random.randint(1, 10)
        if SpikeChance == 5:
            NewSpike = Spike()
            for child in self.ChildrenList:
                if NewSpike.Position == child.Position:
                    pass
                else:
                    self.SpikeList.append(NewSpike)

    def MakeChecks(self):
        if (self.Direction == "Up" and self.Position[1] < 0)\
                or (self.Direction == "Down" and self.Position[1] > 500)\
                or (self.Direction == "Right" and self.Position[0] > 500)\
                or (self.Direction == "Left" and self.Position[0] < 0):
            self.Error = True
        for child in self.ChildrenList:
            if self.Position == child.Position:
                self.Error = True
        for spike in self.SpikeList:
            if self.Position == spike.Position:
                self.Error = True

    def FoodCheck(self):
        if self.Position == self.Food.Position:
            self.SpawnFood()
            self.AddChild()
            self.SpawnSpike()

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.show()
        self.setFixedSize(500, 500)

        self.setStyleSheet("background-color: black;")

        self.MainGameThread = GameThread(Win=self)
        self.MainGameThread.start()

        self.GameOverInstance = GameOver()
        self.GameOverInstance.PlayAgainSignal.connect(self.PlayAgainSlot)
        self.GameOverInstance.hide()

        self.Snake = Snake()

    def PlayAgainSlot(self):
        self.Snake = Snake()
        self.MainGameThread = GameThread(Win=self)
        self.MainGameThread.start()

    def FailSlot(self, Specifier):
        pass

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Up:
            self.Snake.Direction = "Up"
        elif QKeyEvent.key() == Qt.Key_Down:
            self.Snake.Direction = "Down"
        elif QKeyEvent.key() == Qt.Key_Left:
            self.Snake.Direction = "Left"
        elif QKeyEvent.key() == Qt.Key_Right:
            self.Snake.Direction = "Right"
        elif QKeyEvent.key() == Qt.Key_T:
            self.Snake.AddChild()
        else:
            pass

    def paintEvent(self, QPaintEvent):
        SnakePainter = QPainter()
        SnakePainter.begin(self)
        SnakePainter.setBrush(Qt.red)
        SnakePainter.drawRect(self.Snake.Position[0], self.Snake.Position[1], 10, 10)
        for kid in self.Snake.ChildrenList:
            SnakePainter.drawRect(kid.Position[0], kid.Position[1], 10, 10)
        SnakePainter.setBrush(Qt.green)
        SnakePainter.drawRect(self.Snake.Food.Position[0], self.Snake.Food.Position[1], 10, 10)
        SpikePic = QPixmap("Spike.png")
        for Spike in self.Snake.SpikeList:
            SnakePainter.drawPixmap(Spike.Position[0], Spike.Position[1], SpikePic)
        SnakePainter.end()
        self.Snake.Move()
        self.Snake.MakeChecks()
        self.Snake.FoodCheck()
        if self.Snake.Error:
            self.Snake.Error = False
            self.MainGameThread.stop()
            self.GameOverInstance.show()
            self.GameOverInstance.move(int(self.x() + 250 - (self.GameOverInstance.width() / 2)), int(self.y() + 250 - (self.GameOverInstance.height() / 2)))


class GameOver(QWidget):
    PlayAgainSignal = pyqtSignal()
    def __init__(self):
        super(GameOver, self).__init__()
        self.VBL = QVBoxLayout()
        self.setLayout(self.VBL)

        self.MainLBL = QLabel("Game Over!")
        self.MainLBL.setStyleSheet("font-weight: bold; font-size: 20px")
        self.VBL.addWidget(self.MainLBL)

        self.PlayAgainBTN = QPushButton("Play Again")
        self.PlayAgainBTN.clicked.connect(self.PlayAgain)
        self.VBL.addWidget(self.PlayAgainBTN)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setStyleSheet("QWidget { background-color: rgb(169,169,169) } QPushButton { background-color: rgb(128,128,128) }")

    def PlayAgain(self):
        self.PlayAgainSignal.emit()
        self.close()

def main():
    App = QApplication(sys.argv)
    Root = Window()
    sys.exit(App.exec())

if __name__ == "__main__":
    main()