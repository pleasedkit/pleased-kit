# To do:
# - configure parameters
# - 
#
#
#
#


# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Report on the experiment on the signal generated when a gentle flame is applied to the leaf of a tomato plant

# <codecell>

'''
from IPython.core.display import Image
Image(filename='flame.jpg')
'''
# <codecell>

from numpy import *
from scipy import signal
from scipy.signal import filter_design as fd
#from matplotlib import pyplot as plt
import pylab as plt
import scipy
import scipy.fftpack
import numpy as np
import scipy
import scipy.fftpack
import pylab
from scipy import pi
from numpy import linspace, loadtxt, ones, convolve
import numpy as numpy
from scipy.signal import lfilter, firwin
import sys
import re
import os
# <codecell>
'''
from nptdms import TdmsFile
tdms_file_EL1_ref = TdmsFile("./flame/data/experimentLS.tdms")
tdms_file_EL2_ref = TdmsFile("./flame/data/experimentPS.tdms")

gruppi = tdms_file_EL2_ref.groups()
print gruppi
channels = tdms_file_EL2_ref.group_channels('Untitled')
print channels

channel1 = tdms_file_EL1_ref.object('Readings', 'Voltage_0')
data1 = channel1.data
time1 = channel1.time_track()
channel2 = tdms_file_EL2_ref.object('Untitled', 'Voltage_1')
data2 = channel2.data
time2 = channel2.time_track()
'''

data1=[]
stimoInit=[]
stimoEnd=[]
data2=[]
timeCounter=0

if len(sys.argv)==2:
    directory = sys.argv[1]
else:
    print("Usage: %s <path-to-file>" % sys.argv[0])
    sys.exit(2)
    

with open(directory, "r") as txt:
    for line in txt:
        if(re.match(r'>',line)):
            timeCounter=timeCounter+1
            appo1= line.split('>')
            appo1=appo1[1].split('\n')
            appo=appo1[0].split(',')
            data1.append(float(appo[0]))
            data2.append(float(appo[1]))
        elif(re.match(r'- INIT',line)):
            stimoInit.append(timeCounter)
        elif(re.match(r'- END',line)):
            stimoEnd.append(timeCounter)
if not os.path.exists(directory+"dir"):
    os.makedirs(directory+"dir")
    directory =directory+"dir"

zat = []
for x in range(0, len(stimoInit)):
    zat.append(0.1)

#data1, data2= np.loadtxt(open("flame07Mat","rb"),delimiter=",",unpack=True)

#print data1
# do stuff with data
#sample_per_sec = 1000
##figsize(20,5)
plt.figure(1)
plt.subplot(2,1,1)
plt.plot(data1)
#plt.scatter(stimoInit,zat,c='b')
#plt.scatter(stimoEnd,zat,c='r')
plt.xlim(0,len(data1))
plt.subplot(2,1,2)
plt.plot(data2)
#plt.scatter(stimoInit,zat,c='b')
#plt.scatter(stimoEnd,zat,c='r')
plt.xlim(0,len(data2))
plt.savefig(directory + "/rawdata.png")
'''
f = open("data_test.txt", "w")
f.write("1000 \n")
for item in data2:
   f.write(str(item))
   f.write(" ") 
f.close()
'''
# <codecell>

pippo=[]
f_s = 1000.0 # Hz
fft_x = np.fft.fft(data1)
pippo =  fft_x [50:len(fft_x)]
n = len(fft_x)
freq = np.fft.fftfreq(n, 1/f_s)
plt.figure(2)
plt.subplot(2,1,1)
plt.plot(np.abs(pippo))
fft_x_shifted = np.fft.fftshift(fft_x)
freq_shifted = np.fft.fftshift(freq)
plt.subplot(2,1,2)
plt.plot(freq_shifted, np.abs(fft_x_shifted))
plt.xlabel("Frequency (Hz)")
plt.savefig(directory + '/fft.png',dpi=100)
# <codecell>

t = scipy.linspace(0,1,1000)

FFT1 = abs(scipy.fft(data1))
FFT2 = abs(scipy.fft(data2))
freqs = scipy.fftpack.fftfreq(len(data1), t[1]-t[0])
plt.figure(3)
plt.subplot(2,1,1)
plt.plot(freqs,20*scipy.log10(FFT1),'xb')
plt.subplot(2,1,2)
plt.plot(freqs,20*scipy.log10(FFT2),'xr')
plt.savefig(directory + '/fftLogScale.png')
#pylab.show()

# <codecell>


#------------------------------------------------
# Create a FIR filter and apply it to signal.
#------------------------------------------------
# The Nyquist rate of the signal.
sample_rate = 1000.
nyq_rate = sample_rate / 2.
 
# The cutoff frequency of the filter: 6KHz = 6000.0
cutoff_hz = 1
#cutoff_hz = 0.003
 
# Length of the filter (number of coefficients, i.e. the filter order + 1)
numtaps = 29
 
# Use firwin to create a lowpass FIR filter
fir_coeff = firwin(numtaps, cutoff_hz/nyq_rate)
 
# Use lfilter to filter the signal with the FIR filter
filtered_data1 = lfilter(fir_coeff, 1.0, data1)
filtered_data2 = lfilter(fir_coeff, 1.0, data2)

# <codecell>

#figsize(20,5)
plt.figure(4)
plt.subplot(2,1,1)
plt.plot(filtered_data1)
#plt.scatter(stimoInit,zat,c='b')
#plt.scatter(stimoEnd,zat,c='r')
plt.xlim(0,len(data1))
plt.subplot(2,1,2)
plt.plot(filtered_data2)
#plt.scatter(stimoInit,zat,c='b')
#plt.scatter(stimoEnd,zat,c='r')
plt.xlim(0,len(data2))
plt.savefig(directory + '/filteredData.png')

'''
f = open("first_elec.txt", "w")
for item in filtered_data1:
   f.write(str(item))
   f.write("\n") 
f.close()
f = open("second_elec.txt", "w")
for item in filtered_data2:
   f.write(str(item))
   f.write("\n") 
f.close()
'''
# <markdowncell>

# The flame has been applied at time 300. Note the delay in the propagation of the signal which is about 2 minute (120 secs)

# <codecell>



#http://blogs.mathworks.com/videos/2012/04/17/using-convolution-to-smooth-data-with-a-moving-average-in-matlab/
def movingaverage(interval, window_size):
    window = numpy.ones(int(window_size))/float(window_size)
    return numpy.convolve(interval, window, 'same')

def raise_event(v1,window_size,th):
    events = [0] * len(v1)
    moving_average_v1 = movingaverage(v1,window_size)
    for i in range(len(v1)):
        if (abs(v1[i]-moving_average_v1[i])/abs(moving_average_v1[i]))>th :
            events[i] = -0.1
    return events


# <codecell>

filtered_data1_av = movingaverage(filtered_data1, 1000)
filtered_data2_av = movingaverage(filtered_data2, 1000)

# <codecell>

#figsize(20,5)
plt.figure(5)
plt.subplot(2,1,1)
plt.plot(filtered_data1_av,"r")
#plt.scatter(stimoInit,zat,c='b')
#plt.scatter(stimoEnd,zat,c='r')
plt.xlim(0,len(data1))
plt.subplot(2,1,2)
plt.plot(filtered_data2_av,"r")
#plt.scatter(stimoInit,zat,c='b')
#plt.scatter(stimoEnd,zat,c='r')
plt.xlim(0,len(data2))
plt.savefig(directory + '/filteredDataMobAverage.png')

# <codecell>

#figsize(20,10)
plt.figure(6,figsize=(20,10))
plt.subplot(2,1,1)
plt.plot(data1,"b", label="raw data")
#plt.scatter(stimoInit,zat,c='b')
#plt.scatter(stimoEnd,zat,c='r')
plt.plot(filtered_data1,"y", label="low pass filter")
plt.plot(filtered_data1_av,"k", label="moving average")
plt.xlim(0,len(data1))
plt.legend(loc=2,prop={'size':6})
#show()
plt.subplot(2,1,2)
#figure(2)
plt.plot(data2,"r", label="raw data")
#plt.scatter(stimoInit,zat,c='b')
#plt.scatter(stimoEnd,zat,c='r')
plt.plot(filtered_data2,"y", label="low pass filter")
plt.plot(filtered_data2_av,"k", label="moving average")
plt.xlim(0,len(data2))
plt.legend(loc=2,prop={'size':6})
plt.savefig(directory + '/totalreport.png')
#plt.show()

# <codecell>
'''
take_one_every=500
under_filtered_data1_av = filtered_data1_av[0::take_one_every]
figure(1)
plot(filtered_data1_av, label="moving average "+ str(len(filtered_data1_av)) + " samples")
legend()
show()
print len(under_filtered_data1_av)
figure(2)
plot(under_filtered_data1_av, label="moving average "+ str(len(under_filtered_data1_av)) + " samples")
legend()
show()
print len(filtered_data1_av)
'''
# <codecell>
'''
take_one_every=1000
win = 40
th = 0.105
#figsize(20,5)
figure(1)
under_filtered_data1_av = filtered_data1_av[0::take_one_every]
plot(under_filtered_data1_av)
plot(movingaverage(under_filtered_data1_av,win),"g")
plot(raise_event(under_filtered_data1_av,win,th),"r")
figure(2)
under_filtered_data2_av = filtered_data2_av[0::take_one_every]
plot(under_filtered_data2_av)
plot(movingaverage(under_filtered_data2_av,win),"g")
plot(raise_event(under_filtered_data2_av,win,th),"r")
print len(filtered_data2_av[0::take_one_every])
'''
# <codecell>

'''
from numpy import *

# example data with some peaks:
x = linspace(0,4,1e3)
data = .2*sin(10*x)+ exp(-abs(2-x)**2)

# that's the line, you need:
a = diff(sign(diff(data))).nonzero()[0] + 1 # local min+max
b = (diff(sign(diff(data))) > 0).nonzero()[0] + 1 # local min
c = (diff(sign(diff(data))) < 0).nonzero()[0] + 1 # local max


# graphical output...
from pylab import *
plot(x,data)
plot(x[b], data[b], "o", label="min")
plot(x[c], data[c], "o", label="max")
legend()
show()
'''

# <codecell>
'''
# that's the line, you need:
data = filtered_data2_av[0::take_one_every]
x=arange(0,len(data),1)
a = diff(sign(diff(data))).nonzero()[0] + 1 # local min+max
b = (diff(sign(diff(data))) > 0).nonzero()[0] + 1 # local min
c = (diff(sign(diff(data))) < 0).nonzero()[0] + 1 # local max
'''
'''
# graphical output...
from pylab import *
plot(x,data)
plot(x[b], data[b], "o", label="min")
plot(x[c], data[c], "o", label="max")
legend()
show()

# <codecell>

def index_max(x):
    M = 0
    index = 0
    for i in range(len(x)):
        if x[i] > M:
            M = x[i]
            index = i
    return index

def index_min(x):
    m = 10000000
    index = 0
    for i in range(len(x)):
        if x[i] < m:
            m = x[i]
            index = i
    return index

#derivative filter
data = filtered_data2_av[0::take_one_every]
x=arange(0,len(data),1)
alpha = 5
derivative = diff(data[0::alpha])
#needed to avoid border effects
derivative[0]=0
y=arange(0,alpha*len(derivative),alpha)

#derivative2 = diff(derivative)
#needed to avoid border effects
#derivative2[0]=0
#y2=arange(0,alpha*len(derivative2),alpha)

# graphical output...
from pylab import *
plot(x,data,label="filtered data")
plot(y,derivative,label="derivative")
#plot(y2,derivative2,label="derivative2")
M=index_max(derivative)
m=index_min(derivative)
plot(x[m]*alpha,data[m*alpha],"og",x[M]*alpha,data[M*alpha],"og")
extension = 5
M=index_max(derivative)+extension
m=index_min(derivative)-extension
plot(x[m]*alpha,data[m*alpha],"xr",x[M]*alpha,data[M*alpha],"xr")
x_extract= [i for  i in range(int(m*alpha),int(M*alpha))]
data_extract = [data[i] for  i in range(int(m*alpha),int(M*alpha))]
plot(x_extract, data_extract,"r", label="detection")
legend()
show()

# <codecell>

from scipy.interpolate import Rbf, InterpolatedUnivariateSpline

# use RBF method
rbf = Rbf(x_extract, data_extract, function = 'linear' )
fi = rbf(x_extract)
print ("----------------")
for property, value in vars(rbf).iteritems():
    print property, ": ", value
print ("----------------")
#plot(x_extract, data_extract,"r", label="detection")
plot(x_extract, data_extract,"r", label="data")
plot(x_extract, fi,"b", label="interpolation")
show()

# <codecell>

x = np.linspace(0, 10, 9)
y = np.sin(x)
xi = np.linspace(0, 10, 101)
print x,y,xi
# use fitpack2 method
ius = InterpolatedUnivariateSpline(x, y)
yi = ius(xi)

plt.subplot(2, 1, 1)
plt.plot(x, y, 'bo')
plt.plot(xi, yi, 'g')
plt.plot(xi, np.sin(xi), 'r')
plt.title('Interpolation using univariate spline')

# use RBF method
rbf = Rbf(x, y)
print ("----------------")
for property, value in vars(rbf).iteritems():
    print property, ": ", value
fi = rbf(xi)
print ("----------------")
plt.subplot(2, 1, 2)
plt.plot(x, y, 'bo')
plt.plot(xi, yi, 'g')
plt.plot(xi, np.sin(xi), 'r')
plt.title('Interpolation using RBF - multiquadrics')
plt.savefig('rbf1d.png')
'''
# <codecell>


