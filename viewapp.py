#!/usr/bin/env python
""" Test Viewer Application for Foscam Camera module """

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import foscam
import Image
from StringIO import StringIO

ImageReadyEventId = 1382

class ImageReadyEvent(QEvent):

    def __init__(self, image):
        QEvent.__init__(self, ImageReadyEventId)
        self._image = image

    def image(self):
        return self._image


def videoCallback(frame, userdata=None):
    ire = ImageReadyEvent(frame)
    qApp.postEvent(userdata, ire)
                      
class ViewApp(QWidget):

    def __init__(self, *args, **kw):
        apply(QWidget.__init__, (self,)+args, kw)

        bup = QPushButton('Up', self)
        bdn = QPushButton('Down', self)
        ble = QPushButton('Left', self)
        bri = QPushButton('Right', self)
        play = QPushButton('Play', self)
        stop = QPushButton('Stop', self)

        hbox = QHBoxLayout(self)
        self.setLayout(hbox)

        frame = QWidget(self)
        grid = QGridLayout(frame)
        frame.setLayout(grid)

        grid.addWidget(bup, 0, 1)
        grid.addWidget(bdn, 2, 1)
        grid.addWidget(ble, 1, 0)
        grid.addWidget(bri, 1, 2)
        grid.addWidget(play, 7, 1)
        grid.addWidget(stop, 8, 1)

        hbox.addWidget(frame)

        self.image_label = QLabel('Hello', self)
        self.image_label.resize(640, 480)
        hbox.addWidget(self.image_label)

        buttons = [bup, bdn, ble, bri]
        downs = [self.up, self.down, self.left, self.right]
        for i in range(len(buttons)):
            buttons[i].pressed.connect(downs[i])
            buttons[i].released.connect(self.stop)

        play.clicked.connect(self.playVideo)
        stop.clicked.connect(self.stopVideo)

        qApp.lastWindowClosed.connect(self.stopVideo)
        
        self.direction = 0

        self.foscam = foscam.FoscamCamera('192.168.0.120', 'admin')
        
    def up(self):
        self.direction = self.foscam.UP
        self.foscam.move(self.direction)
        
    def down(self):
        self.direction = self.foscam.DOWN
        self.foscam.move(self.direction)
        
    def left(self):
        self.direction = self.foscam.LEFT
        self.foscam.move(self.direction)
        
    def right(self):
        self.direction = self.foscam.RIGHT
        self.foscam.move(self.direction)

    def stop(self):
        self.foscam.move(self.direction + 1)

    def playVideo(self):
        self.foscam.startVideo(videoCallback, self)

    def stopVideo(self):
        self.foscam.stopVideo()
        
    def event(self, e):
        if e.type() == ImageReadyEventId:
            data = e.image()
            im = Image.open(StringIO(data))
            self.qim = QImage(im.tostring(), im.size[0], im.size[1], QImage.Format_RGB888)
            self.pm = QPixmap.fromImage(self.qim)
            self.image_label.setPixmap(self.pm)
            self.image_label.update()
            return 1
        
        return QWidget.event(self, e)
            
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    mw = ViewApp()
    mw.resize(720, 480)
    mw.show()
    app.exec_()
