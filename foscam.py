#!/usr/bin/env python
"""
A simple module to exploit my Foscam F1891W pan/tilt camera.

I obtained information on the CGI interface from Foscam's document
entitled "MJPEG Camera CGI v1.21.pdf" from www.foscam.com

Only the functionality that interested me is implemented here.

Additional functions can be easily added by referencing the above
CGI documentation.

Ken Ramsey, 18Feb2013
"""

import urllib
import time
from threading import Thread
import sys

   
def dummy_videoframe_handler(frame, userdata=None):
    """test video frame handler. It assumes the userdata coming
    in is a Counter object with an increment method and a count method"""
    sys.stdout.write('Got frame %d\r' % userdata.count())
    sys.stdout.flush()
    userdata.increment()

def findFrame(parent, fp, callback=None, userdata=None):
    while parent.isPlaying():
        line = fp.readline()
        if line[:len('--ipcamera')] == '--ipcamera':
            fp.readline()
            content_length = int(fp.readline().split(':')[1].strip())
            fp.readline()
            jpeg = fp.read(content_length)
            if callback:
                callback(jpeg, userdata)

class FoscamCamera(object):

    UP = 0
    STOP_UP = 1
    DOWN = 2
    STOP_DOWN = 3
    LEFT = 4
    STOP_LEFT = 5
    RIGHT = 6
    STOP_RIGHT = 7
    
    def __init__(self, url='', user='', pwd=''):
        super(FoscamCamera, self).__init__()
        self._user = user
        self._pwd = pwd
        self._url = url
        self._isPlaying = 0

    def isPlaying(self):
        return self._isPlaying

    def setIsPlaying(self, val):
        self._isPlaying = val

    def setURL(self, url):
        self._url = url

    def url(self):
        return self._url
    
    def setUser(self, usr):
        self._user = usr

    def user(self):
        return self._user

    def setPassword(self, pwd):
        self._pwd = pwd

    def password(self):
        return self._pwd

    def setUserAndPassword(self, user, password):
        self.setUser(user)
        self.setPassword(password)

    def move(self, direction):
        cmd = {'command':direction}
        f = self.sendCommand('decoder_control.cgi', cmd)
        
    def snapshot(self):
        f = self.sendCommand('snapshot.cgi', {})
        return f.read()                                                     
    
    def startVideo(self, callback=None, userdata=None):
        if not self.isPlaying():
            cmds = { 'resolution':32, 'rate':0 }
            f = self.sendCommand('videostream.cgi', cmds)

            self.videothread = Thread(target=findFrame,
                                      args=(self, f, callback, userdata))
            self.setIsPlaying(1)
            self.videothread.start()

    def stopVideo(self):
        if self.isPlaying():
            self.setIsPlaying(0)
            self.videothread.join()
        
    def sendCommand(self, cgi, parameterDict):
        url = 'http://%s/%s?user=%s&pwd=%s' % (self.url(),
                                               cgi,
                                               self.user(),
                                               self.password())
        for param in parameterDict:
            url = url + '&%s=%s' % (param, parameterDict[param])

        return urllib.urlopen(url)
    
if __name__ == '__main__':

    TESTURL = '192.168.0.120'

    print
    print 'testing the Foscam camera code'
    print
    
    foscam = FoscamCamera(TESTURL, 'admin')

    def move_a_little(fos, go, stop):
        fos.move(go)
        time.sleep(2)
        print ' - stopping move'
        fos.move(stop)
        
    print 'moving up'
    move_a_little(foscam, foscam.UP, foscam.STOP_UP)
    print 'moving down'
    move_a_little(foscam, foscam.DOWN, foscam.STOP_DOWN)
    print 'moving left'
    move_a_little(foscam, foscam.LEFT, foscam.STOP_LEFT)
    print 'moving right'
    move_a_little(foscam, foscam.RIGHT, foscam.STOP_RIGHT)

    print
    print 'taking a few snapshots'
    for i in xrange(1, 11):
        data = foscam.snapshot()
        open('snapshot-%02d.jpg' % i, 'wb').write(data)
        sys.stdout.write('wrote snapshot %d\r' % i)
        sys.stdout.flush()

    print

    class Counter(object):
        def __init__(self):
            super(Counter,self).__init__()
            self._count = 0
        def increment(self):
            self._count += 1
        def count(self):
            return self._count

    print       
    print 'playing a little video (30 seconds worth)'
    counter = Counter()
    foscam.startVideo(dummy_videoframe_handler, counter)
    time.sleep(30)
    print
    print 'stopping video'
    foscam.stopVideo()
    print

    nframes = counter.count() - 1

    print
    print nframes, 'frames in ~30 secs for ~', nframes/30.0, 'fps'
    print
    print 'done!'
    
    
