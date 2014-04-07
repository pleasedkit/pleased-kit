import time
import u6
import pylab
from pylab import *
import Tkinter
from PIL import ImageTk,Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

#INSTANTIATE THE U6 OBJECT
d= u6.U6()
d.configU6()

#STOP A PREVIOUS STREAM IF SOMETHING WENT WRONG ON PREVIOUS ACQUISITION
try: d.streamStop()
except: pass

#CONFIGURE THE STREAMING PARAMETERS
d.streamConfig(
               NumChannels = 2,
               ResolutionIndex = 2, #2	4000 15.9 13.7 +-2.5 < 250
               #	SamplesPerPacket = 25,
               #	SettlingFactor = 0,
               #	InternalStreamClockFrequency = 0,
               #	DivideClockBy256 = False,
               #	ScanInterval = 1,
               ChannelNumbers = [0,1], #CHOOSE THE ADC CHANNELS TO USE
               ChannelOptions = [16,16], #CONFIGURE THE TYPE OF ACQUISITION: single-ended, gain 10 (i.e. +1V,-1V)
               ScanFrequency = 1000, #SET THE FREQUENCY OF SAMPLES: 1KHz for each channel
               #	SampleFrequency = None
               )


#DEFINE THE MAIN WINDOW AS root
root = Tkinter.Tk()
root.wm_title("Pleased-Kit Visualizer")

#GET THE WIDTH AND HEIGHT OF THE SCREEN
widthW=root.winfo_screenwidth()
heightW = root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (widthW,heightW))


#TEST VALUE COUNTER
#valueCounter =0

#STIMULUS COUNTER
counterSimolo = 1


imageCanvas=Tkinter.Canvas(root,height=800)
imageCanvas.pack(side=Tkinter.LEFT)
img = Image.open("background.png")
img = img.resize((widthW*2/9, heightW-80), Image.ANTIALIAS)
photo = ImageTk.PhotoImage(img)
imageCanvas.create_image(0,0, image=photo,anchor="nw")



maxP1=0
minP1=0
maxP2=0
minP2=0

record_file=None
xAchse=pylab.arange(0,100,1)
yAchse=pylab.array([0]*100)
fig = pylab.figure(2,facecolor='white')
ax = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
ax.grid(True)
ax.set_title("Electrode1")
ax.set_xlabel("")
ax.set_ylabel("volts")
ax.axis([0,100,-1.5,1.5])
ax.patch.set_facecolor("grey")
line1=ax.plot(xAchse,yAchse,'-')


ax2.grid(True)
ax2.set_title("Electrode2")
ax2.set_xlabel("Samples")
ax2.set_ylabel("volts")
ax2.axis([0,100,-1.5,1.5])
ax2.patch.set_facecolor("grey")
line2=ax2.plot(xAchse,yAchse,'-')



canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tkinter.TOP,fill="both")
canvas._tkcanvas.pack(side=Tkinter.TOP, expand=1)


multSamples=0
values=[]
values = [0 for x in range(600)]

values2=[]
values2 = [0 for x in range(600)]

writeFila = False
atLeastOnePress = False

Ta=0.01
fa=1.0/Ta
fcos=3.5
startTime = time.time()

Konstant=cos(2*pi*fcos*Ta)
T0=1.0
T1=Konstant
f=None

d.streamStart()

def measure():
    try:
        for r in d.streamData():
            if r is not None:
                if r['errors'] or r['numPackets'] != d.packetsPerRequest or r['missed']:
                    print "error: errors = '%s', numpackets = %d, missed = '%s'" % (r['errors'], r['numPackets'], r['missed'])
                    return False
                break
    finally:
        pass
    return r


def writeData():
    global values,values2,valueCounter,maxP1,minP1,maxP2,minP2
    r = measure()
    if r != False:
        chans = [ r['AIN%d' % (n)] for n in range(2) ]
        #print len(chans)
        for i in range(len(chans[0])):
            #valueCounter +=1
            if(chans[0][i]>maxP1):
                maxP1=chans[0][i] + 0.02
            if(chans[0][i]<minP1):
                minP1=chans[0][i] - 0.02
            if(chans[0][i]>maxP2):
                maxP2=chans[0][i] + 0.02
            if(chans[0][i]<minP2):
                minP2=chans[0][i] - 0.02
            values.append(chans[0][i])
            values2.append(chans[1][i])
            if writeFila==True:
                f.write(">" + str(chans[0][i]) + "," + str(chans[1][i]) + "\n")
    root.after(300,writeData)





#BUTTERWORTH 2 ORDER FILTER CUTOFF 2Hz
def IIR2BUTT(o1,o2,i,i1,i2):
    filteredVal=0.00003913*i +0.000078260*i1+ 0.00003913*i2 + 1.9822*o1 - 0.9824*o2
    return filteredVal


def plotter():
    global values,values2,wScale,wScale2,multSamples,maxP1,minP1,maxP2,minP2
    if(len(values)>100000):
        del values[0:(len(values)-100000)]
        del values2[0:(len(values)-100000)]
        multSamples +=1
        ax2.set_xlabel("Samples")
    NumberSamples=min(len(values),wScale.get())
    CurrentXAxis=pylab.arange(len(values)-NumberSamples,len(values),1)
    line1[0].set_data(CurrentXAxis,pylab.array(values[-NumberSamples:]))
    line2[0].set_data(CurrentXAxis,pylab.array(values2[-NumberSamples:]))
    ax.axis([CurrentXAxis.min(),CurrentXAxis.max(),maxP1,minP1])
    ax2.axis([CurrentXAxis.min(),CurrentXAxis.max(),maxP2,minP2])
    canvas.draw()
    root.after(800,plotter)
#canvas.draw()

#manager.show()

def _quit():
    global startTime,d
    #print valueCounter
    print time.time() - startTime
    d.streamStop()
    d.close()
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
#record_file.close();
# Fatal Python Error: PyEval_RestoreThread: NULL tstate

def _quitGetFileName():
    global subroot
    subroot.destroy()  # this is necessary on Windows to prevent
#record_file.close();
# Fatal Python Error: PyEval_RestoreThread: NULL tstate

def _getNameFile():
    global e,writeFila,button,buttonStop,subroot,f
    button.pack_forget()
    buttonStop.pack(side=Tkinter.TOP)
    buttonStimulusStart.pack(side=Tkinter.TOP)
    print("start recording") 
    f = open(e.get(), 'a')
    f.write(str(time.time()) + "\n")
    writeFila = True
    _quitGetFileName()



def _record():
    global button,buttonStop,e,b,subroot
    button['state']='disabled'
    subroot = Tkinter.Tk()
    subroot.wm_title("Experiment Description:")
    L1 = Tkinter.Label(master=subroot, text="Insert File Name")
    L1.pack()
    e = Tkinter.Entry(master=subroot)
    e.pack()
    e.focus_set()
    b = Tkinter.Button(master=subroot, text="get", width=10, command=_getNameFile)
    b.pack(side=Tkinter.TOP)


def _stopRecord():
    global writeFila,button,buttonStop
    writeFila = False
    f.close()
    buttonStop.pack_forget()
    buttonStimulusStart.pack_forget()
    buttonStimulusEnd.pack_forget()
    button['state']='active'
    button.pack(side=Tkinter.TOP)
    counterSimolo=1
    print("stop recording")

def _stimoloStart():
    global f,buttonStop,buttonStimulusStart,buttonStimulusEnd,counterSimolo
    f.write("- INIT,"+ str(counterSimolo) +","+ str(time.time()) + "\n")
    buttonStop['state'] = 'disabled'
    buttonStimulusStart.pack_forget()
    buttonStimulusEnd.pack(side=Tkinter.TOP)

def _stimoloEnd():
    global f,buttonStop,buttonStimulusStart,buttonStimulusEnd,counterSimolo
    f.write("- END,"+ str(counterSimolo)  + "\n")
    counterSimolo = counterSimolo+1
    buttonStop['state'] = 'active'
    buttonStimulusEnd.pack_forget()
    buttonStimulusStart.pack(side=Tkinter.TOP)

button = Tkinter.Button(master=root, text='Quit', command=_quit)
button.pack(side=Tkinter.BOTTOM)


button = Tkinter.Button(master=root, text='Record',state='active', command=_record, fg='red' ,bg='blue')
button.pack(side=Tkinter.TOP)

buttonStop = Tkinter.Button(master=root, text='Stop recording', command=_stopRecord)
buttonStop.pack_forget()


buttonStimulusStart = Tkinter.Button(master=root, text='start Stimolo', command=_stimoloStart, fg='red' ,bg='blue')
buttonStimulusStart.pack_forget()


buttonStimulusEnd = Tkinter.Button(master=root, text='end Stimolo', command=_stimoloEnd, fg='red' ,bg='blue')
buttonStimulusEnd.pack_forget()


wScale = Tkinter.Scale(master=root,label="View Width:", from_=600, to=60000,sliderlength=30,length=ax.get_window_extent().width, orient=Tkinter.HORIZONTAL)
wScale2 = Tkinter.Scale(master=root,label="Generation Speed:", from_=1, to=200,sliderlength=30,length=ax.get_window_extent().width, orient=Tkinter.HORIZONTAL)
wScale2.pack(side=Tkinter.BOTTOM)
wScale.pack(side=Tkinter.BOTTOM)

wScale.set(100)
wScale2.set(wScale2['to']-100)

root.protocol("WM_DELETE_WINDOW", _quit)
root.after(10,writeData)
root.after(100,plotter)
Tkinter.mainloop()


