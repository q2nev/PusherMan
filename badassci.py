import threading
import Queue
from msvcrt import getch, putch

SPECIAL_KEY = 224
ESCAPE_KEY = 27
ENTER_KEY = 13
BACKSPACE_KEY = 8

class time_keeper(threading.Thread):

    def __init__(self, outQ = Queue.Queue()):
        super(time_keeper, self).__init__()
        self.outQ = outQ

    def run(self):
        line = ""
        while 1:
            c = getch()
            if ord(c) == SPECIAL_KEY:
                c = getch()
                self.outQ.put((SPECIAL_KEY,ord(c)))
            elif ord(c) == ESCAPE_KEY:
                self.outQ.put(False)
                break
            elif ord(c) == ENTER_KEY:
                self.outQ.put(line)
                line = ""
            elif ord(c) == BACKSPACE_KEY:
                line = line[:-1]
                putch(c)
                putch(" ")
                putch(c)
            else:
                line += c
                putch(c)

class screenprinter(threading.Thread):

    def __init__(self, inQ = Queue.Queue()):
        super(screenprinter, self).__init__()
        self.inQ = inQ

    def run(self):
        while 1:
            line = self.inQ.get()
            print "new line recieved",line
            if line == False:
                break

if __name__ == "__main__":
    Q = Queue.Queue()
    kb = keyboard(Q)
    sp = screenprinter(Q)
    kb.start()
    sp.start()