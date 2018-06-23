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
