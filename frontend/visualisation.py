import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QBrush, QColor
from PyQt5.QtCore import QRectF
from enum import Enum, Flag, auto, unique

LANE_WIDTH = 31

class DivType(Enum):
    IN = auto()  # Between lanes going in
    DIR = auto() # Between lanes going in and lanes going out
    OUT = auto() # Between lanes going out


class LaneType(Flag):
    S = auto()
    L = auto()
    R = auto()
    BUS = auto()
    OUT = auto()
    SL = S | L
    SR = S | R
    SLR = S | L | R


class LaneComponent():
    def __init__(self):
        self.crosswalkPixmap = None
        self.lanePixmap = None

    def pixmapsToScene(self, scene):
        # Add crosswalk divider to scene
        self.crosswalkItem = QGraphicsPixmapItem(self.crosswalkPixmap)
        scene.addItem(self.crosswalkItem)

        # Add lane divider to scene
        self.laneItem = QGraphicsPixmapItem(self.lanePixmap)
        scene.addItem(self.laneItem)
    
    def setPos(self, x, y):
        self.crosswalkItem.setPos(x, y)
        self.laneItem.setPos(x, y+22)


class DividerTile(LaneComponent):
    def __init__(self, scene, dividerType, hasCrosswalk):
        super().__init__()

        if hasCrosswalk:
            self.crosswalkPixmap = QPixmap('tiles/cw_div.png')
        else:
            self.crosswalkPixmap = QPixmap('tiles/no_cw_div.png')

        # Get pixmap for lane divider
        match dividerType:
            case DivType.IN:
                self.lanePixmap = QPixmap('tiles/in_div.png')
            case DivType.DIR:
                self.lanePixmap = QPixmap('tiles/dir_div.png')
            case DivType.OUT:
                self.lanePixmap = QPixmap('tiles/out_div.png')
            case _:
                raise ValueError('Invalid divider style')

        self.pixmapsToScene(scene)


class LaneTile(LaneComponent):
    def __init__(self, scene, laneType, hasCrosswalk):
        super().__init__()

        # Get pixmap for crosswalk divider
        if hasCrosswalk:
            self.crosswalkPixmap = QPixmap('tiles/cw')
        else:
            self.crosswalkPixmap = QPixmap('tiles/no_cw')

        # Get pixmap for lane divider
        match laneType:
            case LaneType.S:
                self.lanePixmap = QPixmap('tiles/s_in.png')
            case LaneType.SL:
                self.lanePixmap = QPixmap('tiles/sl_in.png')
            case LaneType.SR:
                self.lanePixmap = QPixmap('tiles/sr_in.png')
            case LaneType.SLR:
                self.lanePixmap = QPixmap('tiles/slr_in.png')
            case LaneType.L:
                self.lanePixmap = QPixmap('tiles/l_in.png')
            case LaneType.R:
                self.lanePixmap = QPixmap('tiles/r_in.png')
            case LaneType.BUS:
                self.lanePixmap = QPixmap('tiles/bus_in.png')
            case LaneType.OUT:
                self.lanePixmap = QPixmap('tiles/out.png')
            case _:
                raise ValueError('Invalid lane style')

        self.pixmapsToScene(scene)


class Lane():
    def __init__(self, scene, laneType, prevLaneType, hasCrosswalk):
        self.laneTile = LaneTile(scene, laneType, hasCrosswalk)

        if prevLaneType is None:
            self.dividerTile = None
            self.width = LANE_WIDTH
            return
        
        self.width = LANE_WIDTH + 1

        if laneType is not LaneType.OUT: 
            divType = DivType.IN
        elif prevLaneType is not LaneType.OUT:
            divType = DivType.DIR
        else:
            divType = DivType.OUT
        self.dividerTile = DividerTile(scene, divType, hasCrosswalk)
        
    
    def setPos(self, x, y):
        if self.dividerTile is None:
            self.laneTile.setPos(x, y)
            return

        self.dividerTile.setPos(x, y)
        self.laneTile.setPos(x+1, y)
    
    def getWidth(self):
        return self.width


class Arm():
    def __init__(self, scene, laneCountIn, hasBus, hasLeft, hasRight, laneCountOut, hasCrosswalk):
        laneTypes = self.calculateAllLanes(laneCountIn, hasBus, hasLeft, hasRight, laneCountOut)

        self.lanes = []
        if len(laneTypes) == 0:
            return

        self.lanes.append(Lane(scene, laneTypes[0], None, hasCrosswalk))

        for i in range(1, len(laneTypes)):
            self.lanes.append(Lane(scene, laneTypes[i], laneTypes[i-1], hasCrosswalk))

        self.cornerPixmap = QPixmap('tiles/corner.png')
        self.cornerItem = QGraphicsPixmapItem(self.cornerPixmap)
        scene.addItem(self.cornerItem)
    
    def calculateStraightLanes(self, laneCountIn, hasLeft, hasRight):
        lanes = []
        if hasLeft:
            laneCountIn -= 1

        if hasRight:
            laneCountIn -= 1

        if laneCountIn == 0:
            return []
        
        for i in range(laneCountIn):
            lanes.append(LaneType.S)
        
        if hasLeft:
            lanes[0] |= LaneType.L

        if hasRight:
            lanes[-1] |= LaneType.R
        return lanes
    
    def calculateAllLanes(self, laneCountIn, hasBus, hasLeft, hasRight, laneCountOut):
        lanes = []

        if hasBus:
            lanes.append(LaneType.BUS)
        
        if hasLeft:
            lanes.append(LaneType.L)
        
        lanes += self.calculateStraightLanes(laneCountIn, hasLeft, hasRight)

        if hasRight:
            lanes.append(LaneType.R)

        lanes += [LaneType.OUT] * laneCountOut
        return lanes

    def setPos(self, x, y):
        if len(self.lanes) == 0:
            self.cornerItem.setPos(x,0)
            return
        
        offset = 0
        self.lanes[0].setPos(x,y)
        offset += self.lanes[0].getWidth()

        for i in range(1, len(self.lanes)):
            self.lanes[i].setPos(x+offset, y)
            offset += self.lanes[i].getWidth()
            
        self.cornerItem.setPos(x+offset, 0)
    
    def getWidth(self):
        print(len(self.lanes))
        return len(self.lanes) * 32 - 1 + 70


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualisation")
        self.setGeometry(100, 100, 600, 500)

        # Create a QGraphicsView
        self.view = QGraphicsView(self)
        self.view.setStyleSheet("border: 2px solid black;")

        # Create a QGraphicsScene
        self.scene = QGraphicsScene(0, 0, 100, 100)  # Set scene size to 200x200
        self.scene.setBackgroundBrush(QBrush(QColor(0, 0, 255)))  # Set background to blue
        self.view.setScene(self.scene)

        # Initialise junction with paramaters
        arm = Arm(self.scene, 5, True, True, True, 3, True)
        arm.setPos(0,0)

        # Resizes window
        width = arm.getWidth()
        self.resize(width + 4, 74)
        self.view.resize(width + 4, 74)
        self.scene.setSceneRect(QRectF(0, 0, width, 70))
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())
