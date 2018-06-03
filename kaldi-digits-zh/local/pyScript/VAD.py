#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 11:14:42 2018

@author: rocky
"""
import scipy.io.wavfile as wavfile
import numpy as np
import matplotlib.pyplot as plt 
from scipy.signal import stft
from librosa.core import to_mono
def mono_detection(sig):
    if len(sig.shape)== 2:
        sig = to_mono(sig.T)
        return sig
    else: 
        return sig 
    
def CompuEnergy(frameMatrix):
    frameNb = frameMatrix.shape[1]
    energyArr = np.zeros(frameNb)
    for i in range(frameNb):
        energyArr[i] = np.sum(np.abs(frameMatrix[:,i])**2)
    return energyArr

    
def frameMat(signal,frame,overlap):
    step = frame - overlap
    Signalsize = np.size(signal)
     # note: Signalsize和overlap都是int 型別所以必須轉型，另外ceil return float
     #或者使用 frameCount = np.ceil(( float(Signalsize - frame)/ step) ) +1  # method 2
    frameCount = np.ceil(float(Signalsize - overlap)/step)
    # create frameSize * frameCount matrix
    frameCut  =  np.zeros((frame,int(frameCount )))
    #知道frameSize ,overlap ,signalSize ,以補零的方式 將signalSize的長度補為可以被frame整除
    if (Signalsize-frame) % step != 0:
        addZeroCount =step-((Signalsize -overlap )%step)
        for i in range(1 ,addZeroCount+1,1 ):
            signal=np.insert(signal,Signalsize,0,axis = 0)
        '''    
        print signal
        print addZeroCount
        '''
    #依據frameSize ,overlap,來將signal排至每個行向量    
    for i in range(0, int(frameCount),1):
        if i == 0 : 
            frameCut [ :, i ] = signal[0 : frame]
            point = frame 
        else:
            start = point -overlap
            frameCut [ : , i ] = signal[ start : start + frame  ]
            point = start + frame 
    return frameCut
def draw_spectrogram(time,freq,Zxx):
    plt.pcolormesh(time,freq,np.abs(Zxx),cmap='terrain')
    plt.ylim([0,3500])
    plt.colorbar()
    plt.show()
    
def normoalization(freqbin,Zxx):
    #if freq <=250Hz or freq >=3750Hz that would be removed.  
    freqcut =  np.ones((Zxx.shape[0],1))
    for idx,element in enumerate(freqbin):
        if element <= 250 or element>=3500:
            freqcut[idx] = 0
    Zxx = Zxx * freqcut
    Zxx = np.abs(Zxx)**2
    summation =np.sum(Zxx,axis=0)
    for idx , ele in enumerate(summation):
        if ele == 0 or ele == np.nan:
            summation[idx] = 1
    Zxx = Zxx/summation
    return Zxx

def CompuEntropy(x):
    adder = 0 
    for element in x :
        if element != 0:
            adder = adder+(element*np.log2(element))
    return adder
    
def EntropyArr(Zxx):
    frameSize , frameCount  = Zxx.shape
    entArr = np.zeros(frameCount)
    for i in range(frameCount):
        entArr[i] = CompuEntropy(Zxx[:,i])         
    return entArr

def EEF(energy,entropy):
    C_e = np.sum(energy[:10])/10
    C_h = np.sum(entropy[:10])/10
    M_i = (energy - C_e)*(entropy[:-1] - C_h)
    return np.sqrt(1+np.abs(M_i))

def EEF_VAD(sig,fs,frameSize):
    # return shape =[frameLen,N_frame] 
    sig = mono_detection(sig)
    frameMatrix = frameMat(sig,frameSize,overlap=0)
    # stftMatrix dim is  [freq(frameSize),time(frameCount)]
    freq,time,stftMatrix = stft(sig,fs=fs,nperseg=frameSize,noverlap=0)   
    #draw_spectrogram(time,freq,stftMatrix)
    N_stft=normoalization(freq,stftMatrix)
    ent = EntropyArr(N_stft)
    energy=CompuEnergy(frameMatrix)
    EE = EEF(energy,ent)
    w_begin = [] 
    w_end = []
    PairPoint = []
    begCoff = 200
    end_Coff = 50
    RefSilence = 2
    begTh = begCoff * sum(EE[0:RefSilence])
    endTh = end_Coff * sum(EE[0:RefSilence])
    pos = RefSilence + 1 
    m_count = 0
    Triger_B = 5
    Triger_E = 7
    B_state = 0
    while(pos < len(EE)):
        if EE[pos] >= begTh:
            w_begin.append(pos)
            pos+=1
            B_state+=1
            if B_state ==  Triger_B :
                pos = w_begin[0]
                B_state = 0
                E_state = 0
                while(E_state != -1 and pos < len(EE) ):
                    if EE[pos] < endTh:
                        w_end.append(pos)
                        E_state+=1
                        #print(pos)
                        if E_state == Triger_E  :
                            PairPoint.append([int(w_begin[0])-1,int(w_end[0])+1])
                            pos = w_end[0]
                            E_state= -1
                            w_begin.clear()
                            w_end.clear()
                    else:
                        w_end.clear()
                        E_state=0
                    #print(pos)
                    # for last time still speaking
                    if pos == len(EE)-1:
                        PairPoint.append([int(w_begin[0])-1,pos])                            
                        E_state= -1
                        w_begin.clear()
                        w_end.clear()
                        
                    pos+=1
        else:
            B_state = 0
            w_begin.clear()
            pos+=1
    return PairPoint

def frameToTime(frameSize , overlap, numOfFrame,fs):
    hop = frameSize - overlap 
    return (frameSize+((numOfFrame-1)*hop)-(hop//2))/fs
def frameToSample(frameSize , overlap, numOfFrame):
    hop = frameSize - overlap 
    return (frameSize+((numOfFrame-1)*hop)-(hop//2)) 
def silenceRe(VADResult,sig,frameSize):
    silence_rm=[]
    for idx ,val in enumerate(VADResult):
        start = frameToSample(frameSize=frameSize,overlap=0,numOfFrame=val[0]-1)
        end = frameToSample(frameSize=frameSize,overlap=0,numOfFrame=val[1]+1)
        silence_rm.extend(sig[start:end])   
    return np.asarray(silence_rm)




if __name__ == '__main__':
    rate , sig = wavfile.read("test.wav")
    # frameSize < 100 
    frameSize = 50
    # given overlap has bug , 
    overlap = 0
    Pair = EEF_VAD(sig ,rate ,frameSize )
    color = [ 'g', 'r', 'c', 'm', 'y', 'k','b']
    print(Pair)
    plt.plot(np.arange(0,len(sig))/rate,sig)
    for idx ,val in enumerate(Pair):
        start =  frameToTime(frameSize=frameSize,overlap=overlap , numOfFrame=val[0]-1,fs=rate)
        end =  frameToTime(frameSize=frameSize,overlap=overlap,numOfFrame=val[1]+1,fs=rate)
        plt.axvline(x=start,c=color[idx%len(color)],linewidth=3)
        plt.axvline(x=end,c=color[idx%len(color)],linewidth=3)
    plt.savefig('test.jpg')
        



