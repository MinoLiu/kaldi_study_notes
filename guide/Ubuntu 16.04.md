# Ubuntu 16.04 kaldi 安裝教學

### 1. 安裝依賴項目
```bash
$ sudo apt update
$ sudo apt install autoconf automake libtool subversion libatlas-dev libatlas-base-dev zlib1g-dev gawk git gfortran gcc g++ make unzip sox python2.7
```

### 2. 下載kaldi
```bash
$ git clone https://github.com/kaldi-asr/kaldi
```

### 3. 編譯kaldi tools
根據Kaldi INSTALL指南
首先去kaldi/tools進行編譯
```bash
$ cd kaldi/tools
$ extras/check_dependencies.sh
```
有問題的話就根據其提示繼續安裝所需的依賴
如果回傳 `extras/check_dependencies.sh: all OK.`
那就可以進行編譯，這需要等待一段時間
```bash
$ make
```
如果需要IRSTLM與srilm
```bash
# IRSTLM
$ extras/install_irstlm.sh

# srilm 
# 去http://www.speech.sri.com/projects/srilm/download.html 下載
# 並且命名成srilm.tgz 放在tools下
$ ./install_srilm.sh
```

### 4. 編譯kaldi source code
```bash
$ cd ../src  
$ ./configure --shared
$ make -j clean depend; make
```

### 5. 編譯完成後測試
```bash
$ cd ../egs/yesno/s5
$ ./run.sh
```
如果成功會顯示如下訊息
```
%WER 0.00 [ 0 / 232, 0 ins, 0 del, 0 sub ] exp/mono0a/decode_test_yesno/wer_10
```
