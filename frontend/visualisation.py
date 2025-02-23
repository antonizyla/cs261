import sys
from PyQt5.QtWidgets import QGraphicsItem, QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsItemGroup
from PyQt5.QtGui import QPixmap, QBrush, QColor, QTransform
from PyQt5.QtCore import QRectF
from enum import Enum, Flag, auto, unique
from abc import ABC, abstractmethod, ABCMeta
from pathlib import Path
from typing import TypeVar, Generic, Optional, Callable, Any

_BASE_DIR = Path(__file__).parent

#Temporary data classes
# Gonna be replaced
class ExternalArmData():
    def __init__(self, lane_count_in, dedicated_lanes):
        self.lane_count_in = lane_count_in
        
        self.dedicated_left = dedicated_lanes[0]
        self.dedicated_bus = dedicated_lanes[1]
        self.dedicated_right = dedicated_lanes[2]

class JunctionData():
    def __init__(self, lane_counts, dedicated_lanes, has_crosswalk):
        self.arms = []
        for i in range(4):
            self.arms.append(ExternalArmData(lane_counts[i], dedicated_lanes[i]))
        
        self.has_crosswalk = has_crosswalk


class LaneType(Flag):
    STRAIGHT = auto()
    LEFT = auto()
    RIGHT = auto()
    BUS = auto()
    OUTGOING = auto()
    STRAIGHT_LEFT = STRAIGHT | LEFT
    STRAIGHT_RIGHT = STRAIGHT | RIGHT
    STRAIGHT_LEFT_RIGHT = STRAIGHT | LEFT | RIGHT


class LaneDividerType(Enum):
    INCOMING = auto()  # Between lanes going in
    CENTRAL = auto() # Between lanes going in and lanes going out
    OUTGOING = auto() # Between lanes going out


class Pixmap():
    __initialised = False
    STRAIGHT_LANE = None
    LEFT_LANE = None
    RIGHT_LANE = None
    BUS_LANE = None
    OUTGOING_LANE = None
    STRAIGHT_LEFT_LANE = None
    STRAIGHT_RIGHT_LANE = None
    STRAIGHT_LEFT_RIGHT_LANE = None
    __LANES = {}
    
    INGOING_DIVIDER = None
    CENTRAL_DIVIDER = None
    OUTGOING_DIVIDER = None
    __LANE_DIVIDERS = {}
    
    CROSSWALK = None
    NO_CROSSWALK = None
    
    CROSSWALK_DIVIDER = None
    NO_CROSSWALK_DIVIDER = None
    
    ISLAND_EDGE_LEFT = None
    ISLAND_CENTER = None
    ISLAND_EDGE_RIGHT = None
    
    CORNER = None
    
    def __guaranteeInitialised(func: Callable) -> Callable:
        def wrapper(clsOrSelf, *args, **kwargs) -> Any:
            if clsOrSelf.__initialised == False:
                raise RuntimeError("Attempted to access pixmaps before calling generate_pixmaps()")
            return func(clsOrSelf, *args, **kwargs)
        return wrapper
        
    
    @classmethod
    @__guaranteeInitialised
    def get_lane(cls, lane_type: LaneType) -> QPixmap:
        if lane_type not in cls.__LANES:
            raise ValueError(f"Invalid lane type: {lane_type}")
        return cls.__LANES[lane_type]

    @classmethod
    @__guaranteeInitialised
    def get_lane_divider(cls, lane_divider_type: LaneDividerType) -> QPixmap:
        if lane_divider_type not in cls.__LANE_DIVIDERS:
            raise ValueError(f"Invalid lane divider type: {lane_divider_type}")
        return cls.__LANE_DIVIDERS[lane_divider_type]

    @classmethod
    @__guaranteeInitialised
    def get_crosswalk(cls, has_crosswalk: bool) -> QPixmap:
        if has_crosswalk:
            return cls.CROSSWALK
        return cls.NO_CROSSWALK
    
    @classmethod
    @__guaranteeInitialised
    def get_crosswalk_divider(cls, has_crosswalk: bool) -> QPixmap:
        if has_crosswalk:
            return cls.CROSSWALK_DIVIDER
        return cls.NO_CROSSWALK_DIVIDER
    
    @classmethod
    def generate_pixmaps(cls) -> None:
        cls.STRAIGHT_LANE = QPixmap((_BASE_DIR / 'tiles/s_in.png').resolve().__str__())
        cls.LEFT_LANE = QPixmap((_BASE_DIR / 'tiles/l_in.png').resolve().__str__())
        cls.RIGHT_LANE = QPixmap((_BASE_DIR / 'tiles/r_in.png').resolve().__str__())
        cls.BUS_LANE = QPixmap((_BASE_DIR / 'tiles/bus_in.png').resolve().__str__())
        cls.OUTGOING_LANE = QPixmap((_BASE_DIR / 'tiles/out.png').resolve().__str__())
        cls.STRAIGHT_LEFT_LANE = QPixmap((_BASE_DIR / 'tiles/sl_in.png').resolve().__str__())
        cls.STRAIGHT_RIGHT_LANE = QPixmap((_BASE_DIR / 'tiles/sr_in.png').resolve().__str__())
        cls.STRAIGHT_LEFT_RIGHT_LANE = QPixmap((_BASE_DIR / 'tiles/slr_in.png').resolve().__str__())
        cls.__LANES = {
            LaneType.STRAIGHT: cls.STRAIGHT_LANE,
            LaneType.LEFT: cls.LEFT_LANE,
            LaneType.RIGHT: cls.RIGHT_LANE,
            LaneType.BUS: cls.BUS_LANE,
            LaneType.OUTGOING: cls.OUTGOING_LANE,
            LaneType.STRAIGHT_LEFT: cls.STRAIGHT_LEFT_LANE,
            LaneType.STRAIGHT_RIGHT: cls.STRAIGHT_RIGHT_LANE,
            LaneType.STRAIGHT_LEFT_RIGHT: cls.STRAIGHT_LEFT_RIGHT_LANE
        }
        
        cls.INGOING_DIVIDER = QPixmap((_BASE_DIR / 'tiles/in_div.png').resolve().__str__())
        cls.CENTRAL_DIVIDER = QPixmap((_BASE_DIR / 'tiles/dir_div.png').resolve().__str__())
        cls.OUTGOING_DIVIDER = QPixmap((_BASE_DIR / 'tiles/out_div.png').resolve().__str__())
        cls.__LANE_DIVIDERS = {
            LaneDividerType.INCOMING: cls.INGOING_DIVIDER,
            LaneDividerType.CENTRAL: cls.CENTRAL_DIVIDER,
            LaneDividerType.OUTGOING: cls.OUTGOING_DIVIDER
        }
        
        cls.CROSSWALK = QPixmap((_BASE_DIR / 'tiles/cw').resolve().__str__())
        cls.NO_CROSSWALK = QPixmap((_BASE_DIR / 'tiles/no_cw').resolve().__str__())
        
        cls.CROSSWALK_DIVIDER = QPixmap((_BASE_DIR / 'tiles/cw_div.png').resolve().__str__())
        cls.NO_CROSSWALK_DIVIDER = QPixmap((_BASE_DIR / 'tiles/no_cw_div.png').resolve().__str__())
        
        cls.ISLAND_EDGE_LEFT = QPixmap((_BASE_DIR / 'tiles/island_edge.png').resolve().__str__())
        cls.ISLAND_CENTER = QPixmap((_BASE_DIR / 'tiles/island_center.png').resolve().__str__())
        cls.ISLAND_EDGE_RIGHT = cls.ISLAND_EDGE_LEFT.transformed(QTransform().scale(-1, 1))

        cls.CORNER = QPixmap((_BASE_DIR / 'tiles/corner.png').resolve().__str__())

        cls.__initialised = True


class SizeAndPos():
    def width(self):
        raise NotImplementedError("width() not implemented")
    
    def height(self):
        raise NotImplementedError("height() not implemented")
    
    def set_pos(self, x, y):
        raise NotImplementedError("set_pos() not implemented")
    

# Cant use ABC since it has a conflicting metaclass with PyQt classes
class Tile(QGraphicsItem, SizeAndPos):
    def __init__(self):
        super().__init__()
    
    def width(self):
        return self.boundingRect().width()
    
    def height(self):
        return self.boundingRect().height()
    
    def set_pos(self, x, y):
        return self.setPos(x, y)
    
    def arrange(self):
        pass


class PixmapTile(QGraphicsPixmapItem, Tile):
    def __init__(self, pixmap):
        QGraphicsPixmapItem.__init__(self)
        Tile.__init__(self)
        self.setPixmap(pixmap)
    
class TileGroup(QGraphicsItemGroup, Tile):
    def __init__(self):
        super().__init__()
        Tile.__init__(self)
        self.items = []
    
    def add_to_group(self, item):
        super().addToGroup(item)
        self.items.append(item)
    
    def arrange(self):
        raise NotImplementedError("arrange_items() not implemented")
    
    def set_pos(self, x ,y):
        self.setPos(x,y)
        
    def boundingRect(self):
        boundingRect = QRectF()
        for item in self.childItems():
            boundingRect |= self.mapFromScene(item.sceneBoundingRect()).boundingRect()
        return boundingRect
    
    def sceneBoundingRect(self):
        boundingRect = QRectF()
        for item in self.childItems():
            boundingRect |= item.sceneBoundingRect()
        return boundingRect
        
        

class HorizontalTileGroup(TileGroup):
    def __init__(self):
        super().__init__()
    
    def arrange(self):
        offset = 0
        for item in self.items:
            item.set_pos(offset, 0)
            item.arrange()
            offset += item.width()
        self.update()
        
        
class VerticalTileGroup(TileGroup):
    def __init__(self):
        super().__init__()
    
    def arrange(self):
        offset = 0
        for item in self.items:
            item.set_pos(0, offset)
            item.arrange()
            offset += item.height()
        self.update()
            

T = TypeVar("T")

class LaneCrosswalkGroup(VerticalTileGroup, Generic[T]):
    def __init__(self, lane_type, has_crosswalk: bool):
        super().__init__()
        self.add_to_group(self._create_crosswalk_item(has_crosswalk))
        self.add_to_group(self._create_lane_item(lane_type))
            
    def _create_crosswalk_item(self, has_crosswalk: bool) -> PixmapTile:
        raise NotImplementedError("_create_crosswalk_item() not implemented")
    
    def _create_lane_item(self, lane_type: T) -> PixmapTile:
        raise NotImplementedError("_create_lane_item() not implemented")   


class Lane(LaneCrosswalkGroup[LaneType]):
    def __init__(self, lane_type: LaneType, has_crosswalk: bool):
        super().__init__(lane_type, has_crosswalk)
        
    def _create_crosswalk_item(self, has_crosswalk: bool) -> PixmapTile:
        return PixmapTile(Pixmap.get_crosswalk(has_crosswalk))
        
    def _create_lane_item(self, lane_type: LaneType) -> PixmapTile:
        return PixmapTile(Pixmap.get_lane(lane_type))


class LaneDivider(LaneCrosswalkGroup[LaneDividerType]):
    def __init__(self, lane_type: LaneDividerType, has_crosswalk: bool):
        super().__init__(lane_type, has_crosswalk)
        
    def _create_crosswalk_item(self, has_crosswalk: bool) -> PixmapTile:
        return PixmapTile(Pixmap.get_crosswalk_divider(has_crosswalk))
        
    def _create_lane_item(self, lane_divider_type: LaneDividerType) -> PixmapTile:
        return PixmapTile(Pixmap.get_lane_divider(lane_divider_type))      
            

class CentralIsland(HorizontalTileGroup):
    def __init__(self, tile_count):
        super().__init__()
        self.add_to_group(PixmapTile(Pixmap.ISLAND_EDGE_LEFT))
        for i in range(tile_count):
            self.add_to_group(PixmapTile(Pixmap.ISLAND_CENTER))
        self.add_to_group(PixmapTile(Pixmap.ISLAND_EDGE_RIGHT))
    
    def arrange(self):
        offset = 0
        for item in self.items:
            item.set_pos(offset, 0)
            item.arrange()
            offset += item.width()
            

class Arm(HorizontalTileGroup):
    def __init__(self, arm_data):
        super().__init__()
        incoming_lanes = self.calculate_incoming_lanes(arm_data)
        print(arm_data.lane_count_in, len(incoming_lanes))

        if len(incoming_lanes) >= 1:
            self.add_to_group(Lane(incoming_lanes[0], arm_data.has_crosswalk))
            for i in range(1, len(incoming_lanes)):
                self.add_to_group(LaneDivider(LaneDividerType.INCOMING, arm_data.has_crosswalk))
                self.add_to_group(Lane(incoming_lanes[i], arm_data.has_crosswalk))
        
        self.add_to_group(CentralIsland(arm_data.center_count))
        
        if arm_data.lane_count_out >= 1:
            self.add_to_group(Lane(LaneType.OUTGOING, arm_data.has_crosswalk))
            for i in range(1, arm_data.lane_count_out):
                self.add_to_group(LaneDivider(LaneDividerType.OUTGOING, arm_data.has_crosswalk))
                self.add_to_group(Lane(LaneType.OUTGOING, arm_data.has_crosswalk))
                
        self.add_to_group(PixmapTile(Pixmap.CORNER))
    
    def arrange(self):
        offset = 0
        for item in self.items:
            item.set_pos(offset, 0)
            item.arrange()
            offset += item.width()   
             
    
    def calculate_incoming_lanes(self, arm_data):
        lanes = []

        if arm_data.dedicated_bus:
            lanes.append(LaneType.BUS)
        
        if arm_data.dedicated_left:
            lanes.append(LaneType.LEFT)
        
        lanes += self.calculate_straight_lanes(arm_data)

        if arm_data.dedicated_right:
            lanes.append(LaneType.RIGHT)

        return lanes
    
    def calculate_straight_lanes(self, arm_data):
        lanes = []
        print("\n", arm_data.lane_count_in)
        lane_count = arm_data.lane_count_in
        if arm_data.dedicated_left:
            print("left")
            lane_count -= 1

        if arm_data.dedicated_right:
            print("right")
            lane_count -= 1

        if lane_count == 0:
            return []
        
        for i in range(lane_count):
            lanes.append(LaneType.STRAIGHT)
        
        if len(lanes) >= 1:
            lanes[0] |= LaneType.LEFT
            lanes[-1] |= LaneType.RIGHT
            
        print(lanes)
        return lanes

#TODO


class ArmData():
    def __init__(self, lane_counts, dedicated_lanes, has_crosswalk):
        self.lane_count_in = lane_counts[0]
        self.center_count = lane_counts[1]
        self.lane_count_out = lane_counts[2]
        
        self.dedicated_left = dedicated_lanes[0]
        self.dedicated_bus = dedicated_lanes[1]
        self.dedicated_right = dedicated_lanes[2]
        
        self.has_crosswalk = has_crosswalk
        

class Junction(TileGroup):
    def __init__(self, junction_data):
        super().__init__()
        self.arms = []
        
        out_lane_counts = []
        
        for i in range(4):
            left_data = junction_data.arms[(i + 3) % 4]
            left_lanes = (
                left_data.dedicated_left
                + left_data.dedicated_bus
                + (left_data.lane_count_in - left_data.dedicated_left - left_data.dedicated_right) >= 1
            )
            
            straight_data = junction_data.arms[(i + 2) % 4]
            straight_lanes = (
                straight_data.dedicated_bus
                + max(0, straight_data.lane_count_in - straight_data.dedicated_left - straight_data.dedicated_right)
            )
            
            right_data = junction_data.arms[(i + 1) % 4]
            right_lanes = (
                right_data.dedicated_right
                + (right_data.lane_count_in - right_data.dedicated_left - right_data.dedicated_right) >= 1
            )
            
            out_lane_counts.append(max(left_lanes, straight_lanes, right_lanes))

        center_lane_counts = []
        for i in range(4):
            this_arm = junction_data.arms[i]
            opposite_arm = junction_data.arms[(i + 2) % 4]
            
            this_arm_lane_count = this_arm.dedicated_bus + this_arm.lane_count_in + out_lane_counts[i]
            opposite_arm_lane_count = opposite_arm.dedicated_bus + opposite_arm.lane_count_in + out_lane_counts[(i+2)%4]
            
            center_lane_counts.append(max(0, opposite_arm_lane_count - this_arm_lane_count))
            arm_data = junction_data.arms[i]
            self.add_to_group(
                Arm(
                    ArmData(
                        [arm_data.lane_count_in, center_lane_counts[i], out_lane_counts[i]], 
                        [arm_data.dedicated_left, arm_data.dedicated_bus, arm_data.dedicated_right], 
                        junction_data.has_crosswalk)
                    )
                )

        self.arrange()
    
    def arrange(self):
        for i in range(4):
            self.items[i].arrange()

        # Entering north
        self.items[0].setRotation(180)
        self.items[0].set_pos(self.items[0].width(), self.items[0].height())
        
        # Entering east
        self.items[1].setRotation(270)
        self.items[1].set_pos(self.items[0].width(), self.items[1].width())
        
        
        # Entering south
        self.items[2].set_pos(self.items[3].height(), self.items[1].width())
        
        # # Entering west
        self.items[3].setRotation(90)
        self.items[3].set_pos(self.items[3].height(), self.items[0].height())


        
            
            
        
    
    


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
        self.scene.setBackgroundBrush(QBrush(QColor(70, 70, 70)))  # Set background to blue
        self.view.setScene(self.scene)

        # Initialise junction with paramaters
        Pixmap.generate_pixmaps()
        data = JunctionData(
            [2, 5, 3, 4],
            [
                [True, True, False],
                [False, True, True],
                [True, False, False],
                [True, True, True]
            ],
            True
        )
        junction = Junction(data)
        junction.set_pos(0,0)
        self.scene.addItem(junction)

        # # Resizes window
        width = int(junction.width())
        height = int(junction.height())
        
        
        self.resize(width + 4, height + 4)
        self.view.resize(width + 4, height + 4)
        self.scene.setSceneRect(QRectF(0, 0, width, height))
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())
