import numpy as np
import re
import itertools
from collections import Counter
import os
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

### Data preprocessing functions
def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()


def load_data_and_labels(positive_data_file, negative_data_file):
    """
    Loads MR polarity data from files, splits the data into words and generates labels.
    Returns split sentences and labels.
    """
    # Load data from files
    positive_examples = list(open(positive_data_file, "r",encoding='utf-8',errors='ignore').readlines())
    positive_examples = [s.strip() for s in positive_examples]
    negative_examples = list(open(negative_data_file, "r",encoding='utf-8',errors='ignore').readlines())
    negative_examples = [s.strip() for s in negative_examples]
    # Split by words
    x_text = positive_examples + negative_examples
    x_text = [clean_str(sent) for sent in x_text]
    # Generate labels
    positive_labels = [1 for _ in positive_examples]
    negative_labels = [0 for _ in negative_examples]
    y = np.concatenate([positive_labels, negative_labels], 0)
    return [x_text, y]


# Data Preparation
# ==================================================
DATA_DIR = '/Users/mandeepsingh/kaggle_competitions/data/rt-polaritydata/rt-polaritydata/'

# Load data
print("Loading data...")
x_text, y = load_data_and_labels(os.path.join(DATA_DIR,'rt-polarity.pos'), os.path.join(DATA_DIR,'rt-polarity.neg'))

# Build vocabulary
max_document_length = max([len(x.split(" ")) for x in x_text])

tokenizer = Tokenizer()
tokenizer.fit_on_texts(x_text)
sequences = tokenizer.texts_to_sequences(x_text)

word_index = tokenizer.word_index
print('Found %s unique tokens.', len(word_index))

data = pad_sequences(sequences, maxlen=max_document_length)

VALIDATION_SPLIT=0.01
indices = np.arange(data.shape[0])
np.random.shuffle(indices)
data = data[indices]
y = y[indices]
nb_validation_samples = int(VALIDATION_SPLIT * data.shape[0])

x_train = data[:-nb_validation_samples]
y_train = y[:-nb_validation_samples]
x_val = data[-nb_validation_samples:]
y_val = y[-nb_validation_samples:]

from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation , Flatten, LSTM, BatchNormalization
from keras.layers import Embedding
from keras.layers import Conv1D, MaxPooling1D, GlobalMaxPooling1D
from keras import regularizers


print('Build model...')
batch_size = 32
embedding_dims = 128
filters = 125
kernel_size = 5
hidden_dims = 8
epochs = 20
model = Sequential()

# we start off with an efficient embedding layer which maps
# our vocab indices into embedding_dims dimensions
model.add(Embedding(len(word_index)+1,
                    embedding_dims,
                    input_length=max_document_length))


# we add a Convolution1D, which will learn filters
# word group filters of size filter_length:
#model.add(Conv1D(filters,kernel_size,padding='valid',activation='relu',strides=1 ))
# we use max pooling:


model.add(Dropout(0.5))

model.add(LSTM(70,dropout=.7, recurrent_dropout=.7))



# We add a vanilla hidden layer:
model.add(Dense(hidden_dims,activity_regularizer=regularizers.l1(.0001),kernel_regularizer=regularizers.l1(.0001)) )
model.add(Dropout(0.2))
model.add(Activation('relu'))
model.add(BatchNormalization())

# model.add(Dense(hidden_dims,activity_regularizer=regularizers.l1(.0001),kernel_regularizer=regularizers.l1(.0001)) )
# model.add(Dropout(0.2))
# model.add(Activation('relu'))
# model.add(BatchNormalization())

# model.add(Dense(hidden_dims,activity_regularizer=regularizers.l1(0.0001),kernel_regularizer=regularizers.l1(.0001)) )
# model.add(Dropout(0.2))
# model.add(Activation('relu'))
# model.add(BatchNormalization())



# We project onto a single unit output layer, and squash it with a sigmoid:
model.add(Dense(1))
model.add(Activation('sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])
model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          validation_split=0.2, shuffle=True,verbose=2)











