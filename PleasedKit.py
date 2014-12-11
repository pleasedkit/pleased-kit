import time
import sys
import pylab
from driver.PleasedDriver import PleasedDriver
from pylab import *
from Tkinter import *
import Tkconstants
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import SubplotParams

################### PleasedKit Configuration Variables #####################

#Maximum amount of values to keep in memory, for each channel
MAX_LEN=100000
#Data acquisition period (in milliseconds)
WRITE_PERIOD=300
#Plot function period (in milliseconds)
PLOT_PERIOD=500
#Initial graph offset (in V)
OFFSET=0.010
#Offset boundaries and resolution (in V)
MIN_OFFSET=0.000
MAX_OFFSET=0.05
RES_OFFSET=0.001
#Initial sample window (#Samples)
WIN_SIZE=300
#Sample window boundaries and resolution (#Samples)
MIN_WIDTH=100
MAX_WIDTH=10000
RES_WIN=100

PLOT_HEIGHT = 6
DPI = 96


assert MAX_LEN > MAX_WIDTH, "Max amount of values needs to be bigger than the sample window size"

#electrodes numbers
elect_num = 2
chnum = 0

#values: 1 array for each electrode
values=[ [0 for x in range(WIN_SIZE)] for i in range(elect_num) ]

#stimulus counter
counterSimolo = 1

record_file=None
multSamples=0
writeFila = False
atLeastOnePress = False

Ta=0.01
fa=1.0/Ta
fcos=3.5
startTime = time.time()

Konstant=cos(2*pi*fcos*Ta)
T0=1.0
T1=Konstant

figPlot=[ 0 ] * 4
framePlot=None
canvasPlot=None

###### Init device ######
device = PleasedDriver(elect_num)

################### start acquiring data ###################
device.acquireData()

def addFigure(figure, frame):
    global mplCanvas, cwid
    # set up a canvas with scrollbars
    canvas = Canvas(frame, width=frame.winfo_width(),bd=0,highlightthickness=0)
    canvas.grid(row=0, column=0, sticky=Tkconstants.NSEW)

    yScrollbar = Scrollbar(frame)

    yScrollbar.grid(row=0, column=1, sticky=Tkconstants.NS)

    canvas.config(yscrollcommand=yScrollbar.set)
    yScrollbar.config(command=canvas.yview)

    # plug in the figure
    figAgg = FigureCanvasTkAgg(figure, canvas)
    mplCanvas = figAgg.get_tk_widget()
    mplCanvas.config(width=frame.winfo_width())
    mplCanvas.grid(sticky=Tkconstants.NSEW)

    # and connect figure with scrolling region
    cwid = canvas.create_window(0, 0, window=mplCanvas)
    canvas.config(scrollregion=canvas.bbox(Tkconstants.ALL))

    return canvas

def measure():
    global chans
    # read the data gathered so far, start a new acquisition thread
    data = device.readData()
    chans  = [ data['AIN%d' % (n)] for n in range(elect_num) ]

def writeData():
    global f
    measure()

    l=[0 for x in range(elect_num)]
    out=[0 for x in range(elect_num)]
    samples=[0 for x in range(elect_num)]

    e = 0
    while e < elect_num:
        if chans != False:
            values[e].extend(chans[e])
            values[e+1].extend(chans[e+1])
            if writeFila==True:
                l[e] = len(chans[e])
                l[e+1] = len(chans[e+1])
                out[e] = False
                out[e+1] = False
                for i in range(max(l[e],l[e+1])):
                    if (i == l[e]):
                        out[e] = True
                    if (i == l[e+1]):
                        out[e+1] = True

                    samples[e] = str(chans[e][i]) if not out[e] else str(chans[l[e]-1])
                    samples[e+1] = str(chans[e+1][i]) if not out[e+1] else str(chans[l[e+1]-1])

                    f.write(samples[e] + "," + samples[e+1])
                    if(e==(elect_num)-2):
                        f.write("\n")
                    else:
                        f.write(",")
        e += 2

    root.after(WRITE_PERIOD,writeData)

#BUTTERWORTH 2 ORDER FILTER CUTOFF 2Hz
def IIR2BUTT(o1,o2,i,i1,i2):
    filteredVal=0.00003913*i +0.000078260*i1+ 0.00003913*i2 + 1.9822*o1 - 0.9824*o2
    return filteredVal


def plotter():
    global wScale,wOffset,multSamples
    e = 0
    while e < elect_num:
        if (len(values[e]) > MAX_LEN):
            del values[e][:MAX_LEN]
        if (len(values[e+1]) > MAX_LEN):
            del values[e+1][:MAX_LEN]

        xLength = min(len(values[e]),len(values[e+1]))
        NumberSamples = min(xLength, wScale.get())
        CurrentXAxis=pylab.arange(xLength-NumberSamples, xLength, 1)

        line[e][0].set_data(CurrentXAxis,pylab.array(values[e][-NumberSamples:]))
        line[e+1][0].set_data(CurrentXAxis,pylab.array(values[e+1][-NumberSamples:]))

        maxP1 = max(values[e][-NumberSamples:])
        minP1 = min(values[e][-NumberSamples:])
        maxP2 = max(values[e+1][-NumberSamples:])
        minP2 = min(values[e+1][-NumberSamples:])

        offset = wOffset.get()
        ax[e].axis([CurrentXAxis.min(),CurrentXAxis.max(),minP1-offset,maxP1+offset])
        ax[e+1].axis([CurrentXAxis.min(),CurrentXAxis.max(),minP2-offset,maxP2+offset])

        mplCanvas.config(width=framePlot.winfo_width())
        canvasPlot.itemconfigure(cwid, width=framePlot.winfo_width())
        canvasPlot.config(scrollregion=canvasPlot.bbox(Tkconstants.ALL))

        figPlot[e/2].canvas.draw()
        e += 2

    root.after(PLOT_PERIOD,plotter)

def _quit():
    global startTime
    print time.time() - startTime

    device.close()
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent

def _quitGetFileName():
    global subroot
    subroot.destroy()  # this is necessary on Windows to prevent

def _getNameFile():
    global e,writeFila,buttonRec,buttonStop,subroot,f
    print("start recording")
    f = open(e.get(), 'a')
    f.write(str(time.time()) + "\n")
    writeFila = True
    _quitGetFileName()

def _record():
    global buttonRec,buttonStop,e,b,subroot
    buttonRec.grid_forget()
    buttonStop.grid(row=3,column=3, sticky=E+W)
    subroot = Tk()
    subroot.wm_title("Experiment Description:")
    L1 = Label(master=subroot, text="Insert File Name")
    L1.pack()
    e = Entry(master=subroot)
    e.pack()
    e.focus_set()
    b = Button(master=subroot, text="Save", width=10, command=_getNameFile)
    b.pack(side=TOP)


def _stopRecord():
    global f,writeFila,buttonRec,buttonStop
    writeFila = False
    f.close()
    buttonStop.grid_forget()
    buttonRec.grid(row=3,column=3, sticky=E+W)
    counterSimolo=1
    print("stop recording")

def _stimoloStart():
    global buttonStop,buttonStimulusStart,buttonStimulusEnd,counterSimolo
    f.write("- INIT,"+ str(counterSimolo) +","+ str(time.time()) + "\n")
    buttonStop['state'] = 'disabled'
    buttonStimulusStart.pack_forget()
    buttonStimulusEnd.pack(side=TOP)

def _stimoloEnd():
    global buttonStop,buttonStimulusStart,buttonStimulusEnd,counterSimolo
    f.write("- END,"+ str(counterSimolo)  + "\n")
    counterSimolo = counterSimolo+1
    buttonStop['state'] = 'active'
    buttonStimulusEnd.pack_forget()
    buttonStimulusStart.pack(side=TOP)

def _nextFig():
    global chnum
    chnum += 1
    if (chnum == elect_num/2 - 1):
        buttonNext['state'] = 'disabled'
    else:
        buttonNext['state'] = 'active'

    canvasPlot = addFigure(figPlot[chnum],framePlot)
    buttonPrev['state'] = 'active'


def _prevFig():
    global chnum
    chnum -= 1
    if (chnum == 0):
        buttonPrev['state'] = 'disabled'
    else:
        buttonPrev['state'] = 'active'

    canvasPlot = addFigure(figPlot[chnum],framePlot)
    buttonNext['state'] = 'active'


################### GUI #####################

#DEFINE THE MAIN WINDOW AS root
root = Tk()
root.wm_title("Pleased-Kit Visualizer")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

#GET THE WIDTH AND HEIGHT OF THE SCREEN
widthW=root.winfo_screenwidth()
heightW = root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (widthW,heightW))

root.rowconfigure(0, weight=100)
root.rowconfigure(1, weight=10)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=10)
root.rowconfigure(4, weight=10)
root.rowconfigure(5, weight=5)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=20)
root.columnconfigure(2, weight=1)
root.columnconfigure(4, weight=1)
root.columnconfigure(6, weight=1)


framePlot = Frame(root)
framePlot.grid(row = 0, column = 0, columnspan = 7, sticky = W+E+N+S)

framePlot.rowconfigure(0, weight=1)
framePlot.columnconfigure(0, weight=1)

#PLOTS
xAchse=pylab.arange(0,100,1)
yAchse=pylab.array([0]*100)


j = 0
ax=[0 for x in range(elect_num)]
line=[ [0 for x in range(elect_num)] for y in range(elect_num)]
for i in range(0,elect_num):
    if i%2 == 0:
        j = i/2
        figPlot[j] = pylab.figure(j,facecolor='white',dpi=DPI,figsize=(5,PLOT_HEIGHT), subplotpars=SubplotParams(top=0.90,bottom=0.06,hspace=0.8,right=0.95, left=0.1))
    ax[i]=figPlot[j].add_subplot(2,1, i%2+1)
    ax[i].grid(True)
    ax[i].set_title("Electrode "+str(i+1))
    ax[i].set_xlabel("")
    ax[i].set_ylabel("volts")
    ax[i].axis([0,100,-1.5,1.5])
    ax[i].patch.set_facecolor("grey")
    line[i]=ax[i].plot(xAchse,yAchse,'-')

chnum = 0
canvasPlot = addFigure(figPlot[chnum],framePlot)

wScale = Scale(root,label="View Width (#Samples):", from_=MIN_WIDTH, to=MAX_WIDTH,length=ax[0].get_window_extent().width, orient=HORIZONTAL, resolution=RES_WIN)
wScale.grid(row=3,column=1, sticky=W+E)
wOffset = Scale(root,label="Graph Offset (V):", from_=MIN_OFFSET, to=MAX_OFFSET,length=ax[0].get_window_extent().width, orient=HORIZONTAL, resolution=RES_OFFSET)
wOffset.grid(row=4,column=1, sticky=W+E)

wScale.set(WIN_SIZE)
wOffset.set(OFFSET)

if elect_num == 2:
    buttonState = 'disabled'
else:
    ButtonState = 'active'
buttonNext = Button(root, text="Next", state=buttonState, command=_nextFig)
buttonNext.grid(row=2,column=5, sticky=E)

buttonPrev = Button(root, text="Previous", state='disabled', command=_prevFig)
buttonPrev.grid(row=2,column=1, sticky=W)

buttonAn = Button(root, text="Analyze")
buttonAn.grid(row=3,column=5, sticky=E+W)

buttonQuit = Button(root, text="Quit", command=_quit)
buttonQuit.grid(row=4,column=3, columnspan=3, sticky=E+W)

buttonStop = Button(root, text='Stop recording', command=_stopRecord)
buttonStop.grid(row=3,column=3, sticky=E+W)

buttonRec = Button(root, text="Record", state='active', command=_record)
buttonRec.grid(row=3,column=3, sticky=E+W)

root.protocol("WM_DELETE_WINDOW", _quit)
#Start acquiring data in 10ms, start plotting in 100ms
root.after(10,writeData)
root.after(50,plotter)
root.mainloop()
