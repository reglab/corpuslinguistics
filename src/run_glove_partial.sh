#!/bin/bash

# Makes programs, downloads sample data, trains a GloVe model, and then evaluates it.
# One optional argument can specify the language used for eval script: matlab, octave or [default] python

RUNLABEL="$1"
GLOVELOCATION="$2"
SAVELOC="$3"
CORPUSFILENAME="$4"
K="$5"

VOCAB_FILE=${SAVELOC}${CORPUSFILENAME}vocab$RUNLABEL.txt
COOCCURRENCE_FILE=${SAVELOC}${CORPUSFILENAME}cooccurrence$RUNLABEL.bin
COOCCURRENCE_SHUF_FILE=${SAVELOC}${CORPUSFILENAME}cooccurrence$RUNLABEL.shuf.bin
BUILDDIR=build
SAVE_FILE=${SAVELOC}${CORPUSFILENAME}vectors$RUNLABEL
VERBOSE=0
MEMORY=12.0
VOCAB_MIN_COUNT=5
VECTOR_SIZE=300
MAX_ITER=100
WINDOW_SIZE=8
BINARY=0
MODEL=0
NUM_THREADS=20
X_MAX=50

echo "starting..."
$GLOVELOCATION$BUILDDIR/shuffle -temp-file temp_shuffle_$K_ -memory $MEMORY -verbose $VERBOSE < $COOCCURRENCE_FILE > $COOCCURRENCE_SHUF_FILE
echo "finished shuffling co-occurrence file"
if [[ $? -eq 0 ]]
  then
  echo "Training GloVe vectors.."
  $GLOVELOCATION$BUILDDIR/glove -save-file $SAVE_FILE -threads $NUM_THREADS -input-file $COOCCURRENCE_SHUF_FILE -x-max $X_MAX -iter $MAX_ITER -vector-size $VECTOR_SIZE -binary $BINARY -model $MODEL -vocab-file $VOCAB_FILE -verbose $VERBOSE
fi