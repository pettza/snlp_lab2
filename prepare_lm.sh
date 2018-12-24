#!/bin/bash

python3 prepare_data.py || exit 1

. ./path.sh || exit 1
. ./cmd.sh || exit 1

rm -rf data/lang/*
rm -rf data/local/lm_tmp/*
rm -rf data/local/nist_lm/*
rm data/local/dict/lexiconp.txt
rm -rf exp mfcc 
rm -rf data/train/spk2utt data/train/cmvn.scp data/train/feats.scp data/train/split1 
rm -rf data/test/spk2utt data/test/cmvn.scp data/test/feats.scp data/test/split1 
rm -rf data/test/spk2utt data/test/cmvn.scp data/test/feats.scp data/test/split1 

LOCAL_TMP_FOLDER=./data/local/lm_tmp
LOCAL_NIST_FOLDER=./data/local/nist_lm
DICT_FOLDER=./data/local/dict
LANG_FOLDER=./data/lang
NGRAM=1

utils/utt2spk_to_spk2utt.pl data/train/utt2spk > data/train/spk2utt
utils/utt2spk_to_spk2utt.pl data/test/utt2spk > data/test/spk2utt
utils/utt2spk_to_spk2utt.pl data/dev/utt2spk > data/dev/spk2utt

mfccdir=mfcc

steps/make_mfcc.sh --cmd "$train_cmd" data/train exp/make_mfcc/train $mfccdir
steps/make_mfcc.sh --cmd "$train_cmd" data/test exp/make_mfcc/test $mfccdir
steps/make_mfcc.sh --cmd "$train_cmd" data/dev exp/make_mfcc/dev $mfccdir

steps/compute_cmvn_stats.sh data/train exp/make_mfcc/train $mfccdir
steps/compute_cmvn_stats.sh data/test exp/make_mfcc/test $mfccdir
steps/compute_cmvn_stats.sh data/dev exp/make_mfcc/dev $mfccdir

for lm_suffix in ug bg; do 
    mkdir ${LANG_FOLDER}/${lm_suffix}
    ILM=${LOCAL_TMP_FOLDER}/${lm_suffix}.ilm.gz
    build-lm.sh -i ${DICT_FOLDER}/lm_train.txt -n ${NGRAM} -o ${ILM}


    compile-lm ${ILM} -t=yes /dev/stdout | grep -v unk | gzip -c > ${LOCAL_NIST_FOLDER}/${lm_suffix}.arpa.gz
    ./utils/prepare_lang.sh ${DICT_FOLDER} "<oov>" ${LOCAL_TMP_FOLDER}  ${LANG_FOLDER}/${lm_suffix}

    gunzip -c ${LOCAL_NIST_FOLDER}/${lm_suffix}.arpa.gz | \
        arpa2fst --disambig-symbol=#0 \
                --read-symbol-table=${LANG_FOLDER}/${lm_suffix}/words.txt - ${LANG_FOLDER}/${lm_suffix}/G.fst
    fstisstochastic ${LANG_FOLDER}/${lm_suffix}/G.fst
    ((NGRAM++))

    steps/train_mono.sh --cmd "$train_cmd" data/train ${LANG_FOLDER}/${lm_suffix} exp/${lm_suffix}/mono  || exit 1

    utils/mkgraph.sh --mono ${LANG_FOLDER}/${lm_suffix} exp/${lm_suffix}/mono exp/${lm_suffix}/mono/graph || exit 1
    steps/decode.sh --config conf/decode.config --cmd "$decode_cmd" exp/${lm_suffix}/mono/graph data/test exp/${lm_suffix}/mono/decode
    steps/decode.sh --config conf/decode.config --cmd "$decode_cmd" exp/${lm_suffix}/mono/graph data/dev exp/${lm_suffix}/mono/decode



    steps/align_si.sh --cmd "$train_cmd" data/train ${LANG_FOLDER}/${lm_suffix} exp/${lm_suffix}/mono exp/${lm_suffix}/mono_ali || exit 1


    steps/train_deltas.sh --cmd "$train_cmd" 2000 11000 data/train ${LANG_FOLDER}/${lm_suffix} exp/${lm_suffix}/mono_ali exp/${lm_suffix}/tri1 || exit 1

    utils/mkgraph.sh ${LANG_FOLDER}/${lm_suffix} exp/${lm_suffix}/tri1 exp/${lm_suffix}/tri1/graph || exit 1
    steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" exp/${lm_suffix}/tri1/graph data/test exp/${lm_suffix}/tri1/decode
    steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" exp/${lm_suffix}/tri1/graph data/dev exp/${lm_suffix}/tri1/decode


done