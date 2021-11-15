#Opencv GUI

##Revisions##
#positions should be stored in the window class with the items instead of in the object's class
#############

import cv2
import numpy as np
import warnings
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

screenSize = (480, 800)
winName = 'Window'
screen = []
#cv2.namedWindow(winName, cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty(winName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

#Adds any number of touples (length of two)
def addT(*args):

    s = (0,0)
    for arg in args:
        a, b = arg
        s = (s[0]+a, s[1]+b)
    return s

#Adds Long tuples
def addLT(a, b):
    s = ()
    if len(a)==len(b):
        for i in range(len(a)):
            s = s + (a[i]+b[i],)
        return s
    else:
        raise Exception('lengths of a and b do not match')
        return None

#Called for all cv2 functions to switch coordinates to (row, col)
def flip(var):
    a, b = var
    return (b, a)

def neg(tup):
    var = ()
    for n in tup:
        var = var+(-n,)
    return var

def mult(var, mult):
    a, b = var
    return (a*mult, b*mult)

def div(var, div):
    a,b, = var
    return (a//div, b//div)

class Theme():
    mainColor = (255, 255, 0)
    backgroundColor = (0, 0, 0)
    highlightColor = (255, 200, 0)
    style = 'square' #rounded or square (not yet supported)
    font = cv2.FONT_HERSHEY_TRIPLEX
    textColor = (255, 255, 255)

class Button():
    global screen
    
    def __init__(self, text, pos, image=np.array([]), highlight=False, fontScale=0.75, pad=(20,20), textThickness=1):

        self.image = image
        self.pos  = pos
        self.text = Text(text, addT(pos,pad), size=fontScale, thickness=textThickness)
        self.highlight = highlight
        self.size = (0,0)
        self.pad = pad
        
        if image.shape[0]==0:
            self.sizeTo('text')
        else:
            self.sizeTo('image')  
        

    def selected(self,h):
        self.highlight = h
        

    def sizeTo(self, prop: str):
        if prop=='text':
            self.sizeTo = 'text'
            textBound, base = cv2.getTextSize(self.text.text, Theme.font, self.text.fsize, self.text.thickness)
            self.size = addT(flip(textBound), mult(self.pad,2))
            if self.image.shape[0] is not 0:
                self.image = cv2.resize(self.image, flip(self.size))
           
        elif prop=='image':
            self.sizeTo = 'image'
            self.size = self.image.shape[:2]
            self.text.fsize, self.text.thickness, self.text.size = Text.autosizeText(self.text.text, addT(self.image.shape[:2], mult(self.pad,-2)))
            textBound, base = cv2.getTextSize(self.text.text, Theme.font, self.text.fsize, self.text.thickness)
            textBound = flip(textBound)
            #center text on image
            self.text.pos = addT(self.pos,div(self.size, 2), div(textBound, -2))
            #self.text.pos = (self.pos[0]-self.size[0]//2+textBound[0]//2, self.pos[1]+self.size[1]//2-textBound[1]//2)
        else:
            raise Exception('Cannot size to {}'.format(prop))

    #Renders the object to the window
    def draw(self, window):
        if self.image.shape[0]==0:         
            if self.highlight:
                cv2.rectangle(window, flip(self.pos), flip(addT(self.pos,self.size)), Theme.highlightColor, thickness=cv2.FILLED)
                cv2.rectangle(window, flip(self.pos), flip(addT(self.pos,self.size)), Theme.mainColor, thickness=2)
                self.text.draw(window, color=Theme.highlightColor)
                self.text.draw(window, color=addLT((255,255,255), neg(Theme.highlightColor))) #invert color
        
            else:
                cv2.rectangle(window, flip(self.pos), flip(addT(self.pos,self.size)), Theme.backgroundColor, thickness=cv2.FILLED)
                cv2.rectangle(window, flip(self.pos), flip(addT(self.pos,self.size)), Theme.mainColor, thickness=2)
                self.text.draw(window, color=Theme.backgroundColor)
                self.text.draw(window)

        else:
            pos = self.pos
            window[pos[0]:pos[0]+self.size[0],pos[1]:pos[1]+self.size[1],:] = self.image
            self.text.draw(window)
        

class Text():

    def __init__(self, text, pos, size=0.75, thickness=1, color=Theme.textColor):
        self.text = text
        self.pos  = pos
        self.fsize = size
        self.thickness = thickness
        self.color = color
        self.size, base = cv2.getTextSize(text, Theme.font, size, thickness)
        self.size = flip(self.size)
    
    #Renders the text to the window drawing from pos = top-left
    def draw(self, window, color=None):
        if color==None:
            color=self.color
        cv2.putText(window, self.text, (self.pos[1], self.pos[0]+self.size[0]), Theme.font, self.fsize, color, self.thickness)

    #Changes the text and redraws the object
    def update(self, window, text):
        #self.draw(window, color=Theme.backgroundColor) #erase current text
        self.text = text
        self.draw(window)

    #Finds font size to match given area
    def autosizeText(text: str, shape: tuple)->(float, int, (int, int)):
        inc = 0.1
        fsize = 72.0
        thick = round(fsize/2)+1
        textSize = (0,0)
        while True:
            fsize = fsize/2
            thick = round(fsize/2)+1
            textSize, base = cv2.getTextSize(text, Theme.font, fsize, thick)
            #       compare y               compare x
            if textSize[1]<shape[0] and textSize[0]<shape[1]:
                break
            
        while True:
            fsize = fsize+inc
            thick = round(fsize/2)+1
            textSize, base = cv2.getTextSize(text, Theme.font, fsize, thick)
            #       compare y               compare x
            if textSize[1]>=shape[0] or textSize[0]>=shape[1]:
                fsize = fsize-inc
                thick = round(fsize/2)+1
                break
            
        return fsize, thick, flip(textSize)

class Plot:

    def __init__(self, size, pos, x_label, x, y_label, y, title):
        self.x_series = x
        self.x_label = x_label
        self.y_label = y_label
        self.y_series = y
        self.title = title
        self.size = size
        self.pos = pos
        self.fig = Figure()
        self.figure = []

    def draw(self, window):
        canvas = FigureCanvas(self.fig)
        ax = self.fig.gca()

        ax.plot(self.x_series, self.y_series)
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        ax.set_title(self.title)
        ax.grid(True)

        canvas.draw()       # draw the canvas, cache the renderer

        width, height = self.fig.get_size_inches() * self.fig.get_dpi()
        self.figure = np.fromstring(canvas.tostring_rgb(), dtype='uint8').reshape(int(height), int(width), 3)
        self.figure = cv2.resize(self.figure, flip(self.size))
        window[self.pos[0]:self.pos[0]+self.size[0], self.pos[1]:self.pos[1]+self.size[1], :] = self.figure

class Container:
    
    def __init__(self, size, pos, contents=np.array([])):
        self.items = {}
        self.hidden = []
        self.size = size
        self.pos = pos
        if contents.shape[0]==0:
            self.contents = np.zeros(self.size+(3,), dtype='uint8')
            self.contents[:,:] = Theme.backgroundColor
        else:
            self.contents = contents

    def add(self, **item):
        self.items.update(item)

    def hide(self, items):
        if items is None:
            self.hidden = []
        else:
            self.hidden.append(items)
            
    def draw(self, window):
        self.clear()
        for n in self.items:
            if n not in self.hidden:
                self.items[n].draw(self.contents)

        #Write container to window
        if self.size == window.shape[:2]:
            window = self.contents
        else:
            window[self.pos[0]:self.pos[0]+self.size[0], self.pos[1]:self.pos[1]+self.size[1], :] = self.contents

    def clear(self):
        self.contents[:,:] = Theme.backgroundColor

    def autoArrange(self, style='GRID'):
        #Get used space
        used = (0,0)
        for n in self.items:
            if n not in self.hidden:
                used = addT(used, self.items[n].size)
                
        if style=='GRID':
            print('Grid autosize not yet supported')

        elif style=='VERTICAL_CENTERED' or style=='VERTICAL':
            space = self.size[0] - used[0]
            space = space//(len(self.items)+1)
            place = 0
            for n in self.items:
                if n not in self.hidden:
                    self.items[n].pos = (place+space, self.items[n].pos[1] if style=='VERTICAL' else self.size[1]//2-self.items[n].size[1]//2)
                    if isinstance(self.items[n], Button):
                        self.items[n].text.pos = addT(self.items[n].pos, self.items[n].pad)
                    place = place + space + self.items[n].size[0]
                        
        elif style=='HORIZONTAL_CENTERED' or style=='HORIZONTAL':
            space = self.size[1] - used[1]
            space = space//(len(self.items)+1)
            place = 0
            for n in self.items:
                if n not in self.hidden:
                    self.items[n].pos = (self.items[n].pos[0] if style=='HORIZONTAL' else self.size[0]//2-self.items[n].size[0]//2, place+space)
                    if isinstance(self.items[n], Button):
                        self.items[n].text.pos = addT(self.items[n].pos, self.items[n].pad)
                    place = place + space + self.items[n].size[1]

        else:
            raise Exception('Cannot arrange in {} style'.format(style))

class popUp:

    def __init__(self, handler, text, size, buttons=['OK'], allign='LEFT'):
        
        self.size = size
        self.window = Window(size)
        self.b_container = Container((75, size[1]), (size[0]-75, 0))
        self.t_container = Container((size[0]-75, size[1]), (0,0))
        text = text.split('\n')

        i=0
        for t in text:
            i+=1
            self.t_container.add(**{str(i):Text(t, (0, 10))})
        self.t_container.autoArrange(style='VERTICAL' if allign=='LEFT' else 'VERTICAL_CENTERED')
        self.window.add(text=self.t_container)
        
        for b in buttons:
            
            self.b_container.add(**{b:Button(b, (0,0), pad=(10,25))})
        self.b_container.autoArrange(style='HORIZONTAL_CENTERED')
        self.window.add(buttons=self.b_container)
        
        select = 0
        options = list(self.b_container.items.keys())
        while True:
            s = options[select]
            self.window.items['buttons'].items[s].selected(True)
            self.window.show()
            event = handler()
            self.window.items['buttons'].items[s].selected(False)
            if event=='right':
                select = (select+1)%len(buttons)
            elif event=='left':
                select = (select-1)%len(buttons)
            elif event=='ent':
                break
        self.event = buttons[select]
            
class ProgressBar:
    
    def __init__(self, size, pos):
        self.size = size
        self.pos = pos
        
    def draw(self, window):
        print('draw')
        
    def progress(self):
        print('prog')

#Enables a mutiple instances of screen layouts
class Window:
    global screen, screenSize, winName
    
    def __init__(self, size='FULL_SCREEN'):
        global screenSize, screen

        self.items = {}
        
        if size=='FULL_SCREEN':
            self.size = screenSize
        else:
            self.size = size
            if len(size) is not 2:
                raise Exception('Invalid window size')
            if size[0]>screenSize[0] or size[1]>screenSize[1]:
                warnings.warn('Occlusion warning: window is larger than screen.')
            
        self.screen = np.zeros(self.size+(3,), dtype='uint8')
        self.screen[:,:] = Theme.backgroundColor

    def add(self, **item):
        self.items.update(item)

    def clear(self):
        self.screen[:,:] = Theme.backgroundColor
    
    def show(self, pos=None):
        global screen, screenSize, winName
        #Center the window by default
        if pos==None:
            self.pos = addT(div(screenSize, 2), div(self.size, -2))
        else:
            self.pos = pos

        self.screen[:,:] = Theme.backgroundColor
        for n in self.items:
            self.items[n].draw(self.screen)

        #Write window to screen
        if self.size == screenSize:
            screen = self.screen
        else:
            screen[self.pos[0]:self.pos[0]+self.size[0], self.pos[1]:self.pos[1]+self.size[1], :] = self.screen
            #add boarder
            cv2.rectangle(screen, addT(flip(self.pos),(-3,-3)), flip(addT(self.pos,self.size,(3,3))), addLT(Theme.highlightColor,(-30,-30,-30)), 4)
            cv2.rectangle(screen, flip(self.pos), flip(addT(self.pos,self.size)), Theme.highlightColor, 2)
        cv2.imshow(winName, screen)

    def autoArrange(self, style='VERTICAL_CENTERED'):
        #Get used space
        used = (0,0)
        for n in self.items:
            used = addT(used, self.items[n].size)
                
        if style=='GRID':
            print('Grid autosize not yet supported')

        elif style=='VERTICAL_CENTERED' or style=='VERTICAL':
            space = self.size[0] - used[0]
            space = space//(len(self.items)+1)

            place = 0
            for n in self.items:
                self.items[n].pos = (place+space, self.items[n].pos[1] if style=='VERTICAL' else self.size[1]//2-self.items[n].size[1]//2)
                if isinstance(self.items[n], Button):
                    self.items[n].text.pos = addT(self.items[n].pos, self.items[n].pad)
                place = place + space + self.items[n].size[0]
                        
        elif style=='HORIZONTAL_CENTERED' or style=='HORIZONTAL':
            space = self.size[1] - used[1]
            space = space//(len(self.items)+1)

            place = 0
            for n in self.items:
                self.items[n].pos = (self.items[n].pos[0] if style=='HORIZONTAL' else self.size[0]//2-self.items[n].size[0]//2, place+space)
                if isinstance(self.items[n], Button):
                    self.items[n].text.pos = addT(self.items[n].pos, self.items[n].pad)
                place = place + space + self.items[n].size[1]

        else:
            raise Exception('Cannot arrange in {} style'.format(style))
                
    
def setScreen(name, shape):
    global screen, winName, screenSize
    screenSize = shape
    winName = name
    screen = np.zeros(shape+(3,), dtype='uint8')
    #cv2.destroyAllWindows()
    #cv2.namedWindow(winName, cv2.WND_PROP_FULLSCREEN)
    #cv2.setWindowProperty(winName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    

def show():
    cv2.imshow(winName, screen)
