from qtpy import QtCore
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
import copy
import utils
import functools


class Plugin():

    # polygon, rectangle, line, or point
    _createMode = 'polygon'

    def __init__(self, canvas = None, parent = None):
        self.canvas = canvas
        self.parent = parent
        # Initialise local state.
        self.shapes = []
        self.shapesBackups = []
        self.current = None
        self.selectedShapes = []  # save the selected shapes here
        self.selectedShapesCopy = []

        action = functools.partial(utils.newAction, self.parent)

        '''
        self.lineColor = QtGui.QColor(0, 0, 255)
        # self.line represents:
        #   - createMode == 'polygon': edge from last point to current
        #   - createMode == 'rectangle': diagonal line of the rectangle
        #   - createMode == 'line': the line
        #   - createMode == 'point': the point
        self.line = Shape(line_color=self.lineColor)
        self.prevPoint = QtCore.QPoint()
        self.prevMovePoint = QtCore.QPoint()
        self.offsets = QtCore.QPoint(), QtCore.QPoint()
        self.scale = 1.0
        self.pixmap = QtGui.QPixmap()
        self.visible = {}
        self._hideBackround = False
        self.hideBackround = False
        self.hShape = None
        self.hVertex = None
        self.hEdge = None
        self.movingShape = False
        self._painter = QtGui.QPainter()
        self._cursor = CURSOR_DEFAULT
        '''

    def difference(self):
        selectedShape = self.canvas.selectedShapes
        shapes = list()
        if len(selectedShape) == 1:
            print('shape selected')
            polygon = self.shape2polygon(selectedShape[0])
            for s in self.canvas.shapes:
                diff = self.shape2polygon(s).difference(polygon)
                if diff.is_empty:
                    continue
                elif isinstance(diff, MultiPolygon):
                    for p in diff:
                        points = self.polygon2shape(p)
                        s.points = points
                        shapes.append(s.copy())
                else:
                    points = self.polygon2shape(diff)
                    s.points = points
                    shapes.append(s.copy())
            shapes.append(selectedShape[0])
            self.parent.loadShapes(shapes)
        else:
            print('no shape :(')

    def union(self):
        selectedShapes = self.canvas.selectedShapes
        shapes = self.canvas.shapes
        if len(selectedShapes) > 1:
            print('shape selected')
            polygon = self.shape2polygon(selectedShapes[0])
            for s in selectedShapes[1:]:
                if self.shape2polygon(s).intersection(polygon).is_empty:
                    continue
                polygon = self.shape2polygon(s).union(polygon)
                self.canvas.shapes.remove(s)
            shape = selectedShapes[0].copy()
            shapes.remove(selectedShapes[0])
            points = self.polygon2shape(polygon)
            shape.points = points
            shapes.append(shape)
            self.parent.loadShapes(shapes, replace = True)
        else:
            print('no shape :(')

    def deletePoint(self):
        shapes = self.canvas.shapes
        point = self.canvas.hVertex
        if point is None:
            return
        print(point)
        shape = self.canvas.hShape.copy()
        shapes.remove(self.canvas.hShape)
        shape.points.pop(point)
        self.canvas.hVertex = None
        shapes.append(shape)
        self.parent.loadShapes(shapes, replace = True)

    def shape2polygon(self, shape):
        points = list()
        for p in shape.points:
            points.append((p.x(), p.y()))
        polygon = Polygon(points)
        return polygon

    def polygon2shape(self, polygon):
        shape = list()
        polygon_array = list(zip(*polygon.exterior.coords.xy))
        for p in polygon_array[:-1]:
            shape.append(QtCore.QPointF(p[0], p[1]))
        return shape
