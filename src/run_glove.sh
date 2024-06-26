#!/bin/bash

# Makes programs, downloads sample data, trains a GloVe model, and then evaluates it.
# One optional argument can specify the language used for eval script: matlab, octave or [default] python

RUNLABEL="$1"
GLOVELOCATION="$2"
SAVELOC="$3"
CORPUSLOC="$4"
CORPUSFILENAME="$5"

CORPUS=${CORPUSLOC}$CORPUSFILENAME$RUNLABEL.txt
VOCAB_FILE=${SAVELOC}${CORPUSFILENAME}vocab$RUNLABEL.txt
COOCCURRENCE_FILE=${SAVELOC}${CORPUSFILENAME}cooccurrence$RUNLABEL.bin
COOCCURRENCE_SHUF_FILE=${SAVELOC}${CORPUSFILENAME}cooccurrence$RUNLABEL.shuf.bin
BUILDDIR=build
SAVE_FILE=${SAVELOC}${CORPUSFILENAME}vectors$RUNLABEL
OVERFLOW_FILE=${SAVELOC}overflow$RUNLABEL
TEMP_FILE=${SAVELOC}temp_shuffle$RUNLABEL
VERBOSE=0
MEMORY=12.0
VOCAB_MIN_COUNT=5
VECTOR_SIZE=300
MAX_ITER=80
WINDOW_SIZE=8
BINARY=0
MODEL=0
NUM_THREADS=20
X_MAX=50

echo "starting..."
$GLOVELOCATION$BUILDDIR/vocab_count -min-count $VOCAB_MIN_COUNT -verbose $VERBOSE < $CORPUS > $VOCAB_FILE
echo "finished building vocab"
if [[ $? -eq 0 ]]
  then
  $GLOVELOCATION$BUILDDIR/cooccur -memory $MEMORY -vocab-file $VOCAB_FILE -verbose $VERBOSE -overflow-file $OVERFLOW_FILE -window-size $WINDOW_SIZE < $CORPUS > $COOCCURRENCE_FILE
  echo "finished building cooccurrence file"
  if [[ $? -eq 0 ]]
  then
    $GLOVELOCATION$BUILDDIR/shuffle -memory $MEMORY -temp-file $TEMP_FILE -verbose $VERBOSE < $COOCCURRENCE_FILE > $COOCCURRENCE_SHUF_FILE
    echo "finished shuffling coeccurence"
    if [[ $? -eq 0 ]]
    then
       $GLOVELOCATION$BUILDDIR/glove -save-file $SAVE_FILE -threads $NUM_THREADS -input-file $COOCCURRENCE_SHUF_FILE -x-max $X_MAX -iter $MAX_ITER -vector-size $VECTOR_SIZE -binary $BINARY -model $MODEL -vocab-file $VOCAB_FILE -verbose $VERBOSE
    fi
  fi
fi
