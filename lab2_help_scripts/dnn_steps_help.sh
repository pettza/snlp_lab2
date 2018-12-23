# This is only a part of the script that you should include in your main script as a stage

# ------------------- Data preparation for DNN -------------------- #
# Compute cmvn stats for every set and save them in specific .ark files
# These will be used by the python dataset class that you were given
for set in train dev test; do
  compute-cmvn-stats --spk2utt=ark:data/${set}/spk2utt scp:data/${set}/feats.scp ark:data/${set}/${set}"_cmvn_speaker.ark"
  compute-cmvn-stats scp:data/${set}/feats.scp ark:data/${set}/${set}"_cmvn_snt.ark"
done

# --------------------- Alignment of validation and test set ----------------- #

workdir=tri1
steps/align_si.sh --nj ${nj} --cmd "$train_cmd" \
  data/dev data/lang exp/${workdir} exp/${workdir}_ali_dev
steps/align_si.sh --nj ${nj} --cmd "$train_cmd" \
  data/test data/lang exp/${workdir} exp/${workdir}_ali_test

# ------------------ Decoding ----------------- #

# The posteriors.ark file is produced by your PyTorch code (you can choose to save it in any directory,
# the example considers it is saved in the output directory exp/dnn)

workdir=tri1
graph_dir=exp/${workdir}/graph
data_dir=data/test
ali_dir=exp/${workdir}_ali
out_folder=exp/dnn

./decode_dnn.sh $graph_dir $data_dir $ali_dir $out_folder/decode_test "cat $out_folder"/posteriors.ark""