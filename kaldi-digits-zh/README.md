# kaldi-digits-zh
> 0-9 中文數字辨識
> 本文是參考Lu Huang的[Kaldi構建一個簡單的英文數字串識別系統][1] <br>
> 還有kaldi官方文件[Kaldi for Dummies tutorial][2] 所撰寫的

[1]: https://hlthu.github.io/2017/02/22/kaldi-numbers-asr.html
[2]: http://kaldi-asr.org/doc/kaldi_for_dummies.html

本文將主要分為以下幾個部分：
* [流程圖](#流程圖)
* [錄製語音](#錄製語音)
* [數據準備](#數據準備)
    * [聲學數據](#聲學數據)
        * [聲學訓練數據準備](#聲學訓練數據準備)
            * [spk2gender](#spk2gender)
            * [wav.scp](#wavscp)
            * [text](#text)
            * [utt2spk](#utt2spk)
        * [聲學測試數據準備](#聲學訓練數據準備)
        * [語料庫](#語料庫)
    * [語言數據](#語言數據)
        * [lexicon.txt](#lexicontxt)
        * [nonsilence_phones.txt](#nonsilence_phonestxt)
        * [silence_phones.txt](#silence_phonestxt)
        * [optional_silence.txt](#optional_silencetxt)
* [環境準備](#環境準備)
* [編寫腳本](#編寫腳本)
* [結果](#結果)
* [WebDemo](#WebDemo)

## 流程圖
![Imgur](https://i.imgur.com/a8aG722.png)


## 錄製語音
這裡是中文數字串識別，因此需要一些用中文朗讀數字的語音。我錄製了 144 個語音文件，分別是兩個人朗讀，其中每個文件只包含三個數字。這 144 文件中 90 個用於訓練， 54 個用於測試。並且訓練數據和測試數據都被分成了 9 部分（可以假裝成 9 個人），每部分分別 10 個 和 6 個。訓練集和測試集的前五個目錄是我組員(男)朗讀，後面四個是我(男)朗讀的。

我的錄音是 44.1 kHz 採樣，16 位量化的。如果是 8 kHz 採樣，需要在提特徵時指明採樣頻率。將conf/mfcc.conf裡面的--sample-frequency改成8000

目錄結構如下：
```
waves_digits/
├── test
│   ├── 1
│   ├── 2
│   ├── 3
│   ├── 4
│   ├── 5
│   ├── 6
│   ├── 7
│   ├── 8
│   └── 9
└── train
    ├── 1
    ├── 2
    ├── 3
    ├── 4
    ├── 5
    ├── 6
    ├── 7
    ├── 8
    └── 9
```

當然您也可以選擇自己錄音，也歡迎你把你的錄音共享。

從數據準備到編寫腳本一直都是在為最後做準備，如果都完成了的話，你的目錄應該長這樣：
```
.
├── cmd.sh
├── conf
│   ├── decode.config
│   └── mfcc.conf
├── data
│   ├── local
│   │   ├── corpus.txt
│   │   └── dict
│   │       ├── lexicon.txt
│   │       ├── nonsilence_phones.txt
│   │       ├── optional_silence.txt
│   │       └── silence_phones.txt
│   ├── test
│   │   ├── spk2gender
│   │   ├── text
│   │   ├── utt2spk
│   │   └── wav.scp
│   └── train
│       ├── spk2gender
│       ├── text
│       ├── utt2spk
│       └── wav.scp
├── local
│   ├── make_mfcc.sh
│   └── score.sh
├── path.sh
├── run.sh
├── steps
└── utils
```

## 數據準備

數據的準備包括聲學數據和語言數據。首先建立一個目錄 data/。
### 聲學數據

聲學數據主要包括訓練集和測試集的數據，以及一個語料庫，在 data/ 目錄下新建兩個目錄：train/ 、test/ 和 local。
### 聲學訓練數據準備

這些數據主要是四個文件：spk2gender、wav.scp、text 和 utt2spk，都保存在 data/train/ 目錄下。
#### spk2gender

這個文件主要描述說話人編號和性別的對應關係，具有這樣的形式：<speakerID> <gender>，比如我這裡訓練集是「9」個人，都是個男(Male)的，所以
```
1 m
2 m
3 m
4 m
5 m
6 m
7 m
8 m
9 m
```
如果是女(Female)的就用小寫f代替m

#### wav.scp
這個文件主要是保存了語音編號和語音文件的對應關係，具有這樣的形式：<uterranceID> <full_path_to_audio_file>。比如
```
1-040 waves_digits/train/1/1-040.wav
1-089 waves_digits/train/1/1-089.wav
1-104 waves_digits/train/1/1-104.wav
1-231 waves_digits/train/1/1-231.wav
1-327 waves_digits/train/1/1-327.wav
1-413 waves_digits/train/1/1-413.wav
1-462 waves_digits/train/1/1-462.wav
...
```

#### text
這個文件主要是標註，描述了語音編號和標註之間的對應關係，具有這樣的形式：<utterranceID> <text_transcription>。比如
```
1-040 零 四 零
1-089 零 八 九
1-104 一 零 四
1-231 二 三 一
1-327 三 二 七
1-413 四 一 三
1-462 四 六 二
1-468 四 六 八
1-470 四 七 零
1-560 五 六 零
...
```

#### utt2spk
這個文件是聯繫說話人編號和語音編號，具有這樣的形式：<uterranceID> <speakerID>。比如
```
1-040 1
1-089 1
1-104 1
1-231 1
1-327 1
1-413 1
1-462 1
1-468 1
1-470 1
1-560 1
...
```
這裡我們建議把說話人的編號放在語音編號的前綴。至此，訓練集的聲學數據準備好了。
還有一些檔案spk2utt 可以利用utils/utt2spk_to_spk2utt.pl自動生成
skp2utt顧名思義就是<speakerID> <uterranceID>

### 聲學測試數據準備
和訓練集數據一樣，這些數據也主要是四個文件：spk2gender、wav.scp、text 和 utt2spk，都保存在 data/test/ 目錄下。這些目錄的形式和之前一樣，只是 wav.scp 需要映射到測試集的數據，重新修改語音編號。

### 語料庫
我們還需要一個語料庫，其包含了所有訓練集數據的標註，請命名為 corpus.txt，並保存在 data/local/ 目錄下。比如
```
零 四 零
零 八 九
一 零 四
二 三 一
三 二 七
四 一 三
四 六 二
四 六 八
四 七 零
五 六 零
...
```
### 語言數據
語言數據主要包括 lexicon.txt 、optional_silence.txt、nonsilence_phones.txt、silence_phones.txt，並在 data/local/ 目錄下新建文件夾 dict，將這四個文件保存到那裡。

#### lexicon.txt 
這個文件應該包括你標註裡所有出現的詞的發音，即音素表達，由於這裡只有十個單詞，再加上靜音，因此不管是詞還是音素，數量都比較少。

```
!SIL sil
<UNK> spn
零 l ing2
一 ii i1
二 er4
三 s an1
四 s iy4
五 uu u3
六 l iu4
七 q i1
八 b a1
九 j iu3
```

#### nonsilence_phones.txt
這個文件列出了上面出現的所有的非靜音音素。

```
l      
ing2   
ii     
i1     
er4    
s      
an1    
iy4    
uu     
u3     
iu4    
q      
b      
a1     
j      
iu3    
```

#### silence_phones.txt
這裡面包含了靜音音素。

```
sil
spn
```

#### optional_silence.txt
只有可選的靜音音素。

```
sil
```

## 環境準備

回到項目根目錄。首先我們需要定義文件 cmd.sh 和 path.sh，其中前者主要包括運行的形式，而後者主要包括 kaldi 依賴的路徑。

cmd.sh：
```bash
export train_cmd="run.pl"
export decode_cmd="run.pl"
export mkgraph_cmd="run.pl"
```

path.sh：
```bash
export KALDI_ROOT="/PATH/TO/YOUR/KALDI/ROOT"                                                                                                                                                                                                             [ -f $KALDI_ROOT/tools/env.sh ] && . $KALDI_ROOT/tools/env.sh
export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$PWD:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file $KALDI_ROOT/tools/config/common_path.sh is not present -> Exit!" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh
export LC_ALL=C
```

最後就是建立目錄 conf，存放一些配置文件。包括：

decode.config：
```
first_beam=10.0
beam=13.0
lattice_beam=6.0
```

mfcc.conf:
```
--use-energy=false
--sample-frequency=44100
```

## 編寫腳本

在根目錄下建立一個 run.sh 腳本，輸入以下內容：

```bash
#!/bin/bash

nj=4
lm_order=1



. utils/parse_options.sh || exit 1
[[ $# -ge 1 ]] && { echo "Wrong arguments!"; exit 1; }


# Removing previously created data (from last run.sh execution)
rm -rf exp mfcc data/train data/test data/local/lang data/lang data/lang_test_tg data/local/tmp \
	data/local/dict/lexiconp.txt data/local/corpus.txt

mkdir -p data/train
mkdir -p data/test
mkdir -p data/local

echo
echo "===== PREPARING TRAIN/TEST DATA ====="
echo


# 自行撰寫的script通通都放在local裡
# local/data_prep.sh就是用來處理語音數據的
./local/data_prep.sh

# corpus.txt 將train text的右半擷取即可
cat data/train/text | awk '{first=$1;$1=""}sub(FS,"")' > data/local/corpus.txt

# source env
# 放在data_prep後面是因為path.sh的export LC_ALL=C
# 會讓utf-8字串處理有問題 所以先處理完在source
. ./path.sh || exit 1
. ./cmd.sh || exit 1

echo
echo "===== PREPARING ACOUSTIC DATA ====="
echo

# Making spk2utt files
utils/utt2spk_to_spk2utt.pl data/train/utt2spk > data/train/spk2utt
utils/utt2spk_to_spk2utt.pl data/test/utt2spk > data/test/spk2utt


echo
echo "===== FEATURES EXTRACTION ====="
echo

mfccdir=mfcc


steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" data/train \
	exp/make_mfcc/train $mfccdir
steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" data/test \
	exp/make_mfcc/test $mfccdir


# Making cmvn.scp files
steps/compute_cmvn_stats.sh data/train exp/make_mfcc/train $mfccdir
steps/compute_cmvn_stats.sh data/test exp/make_mfcc/test $mfccdir


echo
echo "===== PREPARING LANGUAGE DATA ====="
echo
# Preparing language data
utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang




local=data/local
mkdir $local/tmp
ngram-count -order $lm_order -write-vocab $local/tmp/vocab-full.txt \
	-wbdiscount -text $local/corpus.txt -lm $local/tmp/lm.arpa


echo
echo "===== MAKING G.fst ====="
echo

lang=data/lang
arpa2fst --disambig-symbol=#0 --read-symbol-table=$lang/words.txt \
	$local/tmp/lm.arpa $lang/G.fst



echo
echo "===== MONO TRAINING ====="
echo

steps/train_mono.sh --nj $nj --cmd "$train_cmd" data/train data/lang exp/mono  || exit 1

echo
echo "===== MONO DECODING ====="
echo


utils/mkgraph.sh --mono data/lang exp/mono exp/mono/graph || exit 1
steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" \
	exp/mono/graph data/test exp/mono/decode
local/score.sh data/test data/lang exp/mono/decode/


echo
echo "===== MONO ALIGNMENT ====="
echo

steps/align_si.sh --nj $nj --cmd "$train_cmd" data/train data/lang exp/mono exp/mono_ali || exit 1

echo
echo "===== TRI1 (first triphone pass) TRAINING ====="
echo

steps/train_deltas.sh --cmd "$train_cmd" 2000 11000 data/train data/lang exp/mono_ali exp/tri1 || exit 1

echo
echo "===== TRI1 (first triphone pass) DECODING ====="
echo

utils/mkgraph.sh data/lang exp/tri1 exp/tri1/graph || exit 1
steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" \
	exp/tri1/graph data/test exp/tri1/decode
local/score.sh data/test data/lang exp/tri1/decode/


echo
echo "===== TRI1 ALIGNMENT ====="
echo

steps/align_si.sh --nj $nj --cmd "$train_cmd" \
  --use-graphs true data/train data/lang exp/tri1 exp/tri1_ali

echo
echo "===== best_wer ====="
echo

local/best_wer.sh

echo
echo "===== copy models to demo ====="
echo

rm -rf pykaldi_web_demo/models 
cp -r exp pykaldi_web_demo/models

echo
echo "===== run.sh script is finished ====="
echo
```

## 結果
Word error rate
```bash
%WER 0.00 [ 0 / 162, 0 ins, 0 del, 0 sub ] exp/mono/decode/wer_10
%WER 0.62 [ 1 / 162, 1 ins, 0 del, 0 sub ] exp/tri1/decode/wer_10
```

## WebDemo
跑完run.sh後  
需要安裝Docker && docker-compose
```bash
docker-compose up -d
```
然後在<http://localhost:8000>進行Demo  
注意Chrome禁止no ssl使用MediaRecord  
建議使用Firefox

如不想安裝Docker的話  
需要先去安裝[pykaldi](https://github.com/pykaldi/pykaldi)
```bash
cd pykaldi_web_demo
python3 -m pip install -r requirements.txt
python3 runtime.py
```
