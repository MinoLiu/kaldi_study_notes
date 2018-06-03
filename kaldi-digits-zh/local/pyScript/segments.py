#!/usr/bin/env python3
from VAD import EEF_VAD
import numpy as np
import scipy.io.wavfile as wavfile

# frameSize < 100
frameSize = 50

text = []

with open('data/train/wav.scp', "r") as f:
    for x in f.readlines():
        uid, path = x.replace('\n', '').split(' ')
        rate , sig = wavfile.read(path)
        Pair = EEF_VAD(sig ,rate ,frameSize )
        if len(Pair):
            for x in Pair:
                text.append(uid + "_" + str(x[0]).zfill(6) + "-" + str(x[1]).zfill(6) + " " + uid + " " + "{0:.2f}".format(x[0]/1000.0) + " " + "{0:.2f}".format(x[1]/1000.0))
        #print(uid,np.array(Pair)/1000)



with open('data/train/segments', "w") as f:
    f.write("\n".join(text))


text = []

with open('data/test/wav.scp', "r") as f:
    for x in f.readlines():
        uid, path = x.replace('\n', '').split(' ')
        rate , sig = wavfile.read(path)
        Pair = EEF_VAD(sig ,rate ,frameSize )
        if len(Pair):
            for x in Pair:
                text.append(uid + "_" + str(x[0]).zfill(6) + "-" + str(x[1]).zfill(6) + " " + uid + " " + "{0:.2f}".format(x[0]/1000.0) + " " + "{0:.2f}".format(x[1]/1000.0))
        #print(uid,np.array(Pair)/1000)



with open('data/test/segments', "w") as f:
    f.write("\n".join(text))


