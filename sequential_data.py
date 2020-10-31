# -*- coding: utf-8 -*-
"""sequential-data.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ll1l5Ml0yqHMnqlv2JqcXqLbNgNpZsme

<details>
<summary>📓 &nbsp; Modeling Sequential Data Using Recurrent Neural Networks
</summary><br/>Github Links<br/>    
<a href="https://github.com/rasbt/python-machine-learning-book-3rd-edition/blob/master/ch16/ch16_part1.ipynb">Part 1</a><br/>
<a href="https://github.com/rasbt/python-machine-learning-book-3rd-edition/blob/master/ch16/ch16_part2.ipynb">Part 2</a><br/>
</details>
"""

from IPython.display import display,HTML
c1,c2,f1,f2,fs1,fs2=\
'#11ff66','#6611ff','Akronim','Smokum',30,15
def dhtml(string,fontcolor=c1,font=f1,fontsize=fs1):
    display(HTML("""<style>
    @import 'https://fonts.googleapis.com/css?family="""\
    +font+"""&effect=3d-float';</style>
    <h1 class='font-effect-3d-float' style='font-family:"""+\
    font+"""; color:"""+fontcolor+"""; font-size:"""+\
    str(fontsize)+"""px;'>%s</h1>"""%string))

dhtml('Code Modules, Setting, & Functions')

import numpy as np,pylab as pl
import tensorflow as tf
import tensorflow.keras.layers as tkl
import tensorflow_datasets as tfds
from collections import Counter
from tensorflow.keras.datasets import imdb
from tensorflow.keras.preprocessing \
import sequence as tksequence

def get_weights_shape(layer):
    w_xh,w_oo,b_h=layer.weights
    print('w_xh shape: %s'%w_xh.shape)
    print('w_oo shape: %s'%w_oo.shape)
    print('b_h shape: %s'%b_h.shape) 
def compare_calc(layer,x):
    n,inputs=x.shape[0],x.shape[1]
    w_xh,w_oo,b_h=layer.weights
    out_calc=[]
    output=layer(
        tf.reshape(x,shape=(1,n,inputs)))
    pl.figure(figsize=(10,5))
    for t in range(n):
        xt=tf.reshape(x_seq[t],(1,inputs))
        print('time step {} =>'.format(t))
        print(5*' '+'input'+13*' '+': '+
              str(xt.numpy()))
        ht=tf.matmul(xt,w_xh)+b_h 
        print(5*' '+'hidden'+11*' '+': '+   
              str(ht.numpy()))   
        if t>0:
            prev_o=out_calc[t-1]
        else:
            prev_o=tf.zeros(shape=(ht.shape))        
        ot=ht+tf.matmul(prev_o,w_oo)
        ot=tf.math.tanh(ot)
        out_calc.append(ot)
        print(5*' '+'calculated output: '+
              str(ot.numpy()))
        print(5*' '+'SimpleRNN output:   '.format(t)+
              str(output[0][t].numpy())+'\n')
        pl.plot(output[0][t].numpy(),'-o',
                label='time step %d'%t)
    pl.grid(); pl.legend(); pl.show()

def encode(text_tensor,label):
    text=text_tensor.numpy()
    encoded_text=encoder.encode(text)
    return encoded_text,label
def encode_fmap(text,label):
    return tf.py_function(encode,inp=[text,label], 
                          Tout=(tf.int64,tf.int64))

dhtml('Data Exploration')

# 25,000 movies reviews from IMDB, 
# labeled by sentiment (positive/negative)
num_words=10000; max_length=1000
embedding_vector_length=32
(x_train,y_train),(x_test,y_test)=\
imdb.load_data(path="imdb_full.pkl",
               num_words=num_words,
               skip_top=0,seed=113,
               maxlen=max_length,
               start_char=1,oov_char=2,
               index_from=3)

print(x_train.shape,x_test.shape)
print(y_train.shape,y_test.shape)
x=np.vstack([x_train.reshape(-1,1),
             x_test.reshape(-1,1)])
y=np.vstack([y_train.reshape(-1,1),
             y_test.reshape(-1,1)])
x=x.reshape(-1); y=y.reshape(-1)
print(x.shape,y.shape)

word_to_id=imdb.get_word_index()
word_to_id=\
{k:(v+3) for k,v in word_to_id.items()}
sw=["<PAD>","<START>","<UNK>","<UNUSED>"]
for i in range(4): word_to_id[sw[i]]=i
id_to_word=\
 {value:key for key,value in word_to_id.items()}
def get_string(x,i):
    return ' '.join(id_to_word[id] for id in x[i] if id>3)

features=[get_string(x,i) 
          for i in range(x.shape[0])]
features=np.array(features)
targets=y
dhtml(features[0],c2,f2,fs2)

dhtml('Data Building')

ds=tf.data.Dataset.\
from_tensor_slices((features,targets))
for ex in ds.take(3):
    tf.print(ex[0].numpy()[:60],ex[1])

tf.random.set_seed(123)
ds=ds.shuffle(50000,reshuffle_each_iteration=False)
ds_test=ds.take(10000)
ds_train_valid=ds.skip(10000)
ds_valid=ds_train_valid.take(10000)
ds_train=ds_train_valid.skip(10000)

tokenizer=tfds.features.text.Tokenizer()
token_counts=Counter()
for example in ds_train:
    tokens=tokenizer.tokenize(example[0].numpy())
    token_counts.update(tokens)
print('vocabulary size:',len(token_counts))

encoder=tfds.features.text\
.TokenTextEncoder(token_counts)
example_str='hi this is an example of sentences'
encoder.encode(example_str)

tf.random.set_seed(123)
train=ds_train.map(encode_fmap)
valid=ds_valid.map(encode_fmap)
test=ds_test.map(encode_fmap)

tf.random.set_seed(1)
for example in train.shuffle(1000).take(3):
    print('sequence length:',example[0].shape)
    print(example[0].numpy())

ds_example=train.take(20)
print('individual sizes:')
for example in ds_example:
    print(example[0].shape)
ds_batched_example=ds_example\
.padded_batch(4,padded_shapes=([-1],[]))
print('batch dimensions:')
for batch in ds_batched_example:
    print(batch[0].shape)

train_data=train.padded_batch(
    32,padded_shapes=([-1],[]))
valid_data=valid.padded_batch(
    32,padded_shapes=([-1],[]))
test_data=test.padded_batch(
    32,padded_shapes=([-1],[]))

for example in train_data.take(1):
    print(example[0].numpy()[0],'\n',
          example[1].numpy())

dhtml('Embedding, RNN, LSTM, & GRU Layers')

model=tf.keras.Sequential(
    name='embedding_structure')
model.add(tkl.Embedding(
    input_dim=256,output_dim=5,
    input_length=32,name='embedding_1'))
model.summary()

def rnn_layer(inputs,units):
    rnn_layer=tkl.SimpleRNN(
        units=units,use_bias=True,
        return_sequences=True)
    rnn_layer.build(
        input_shape=(None,None,inputs))
    return rnn_layer

m=5; inputs=7; units=4
tf.random.set_seed(123)
rnn_layer74=rnn_layer(inputs,units)    
get_weights_shape(rnn_layer74)

x_seq=tf.convert_to_tensor(
    [[1.*(i+1)]*inputs for i in range(m)],
    dtype=tf.float32)
compare_calc(rnn_layer74,x_seq)

model=tf.keras.Sequential(
    name='simple_rnn_structure')
model.add(tkl.Embedding(1000,32))
model.add(
    tkl.SimpleRNN(32,return_sequences=True))
model.add(tkl.SimpleRNN(32))
model.add(tkl.Dense(1))
model.summary()

model=tf.keras.Sequential(
    name='lstm_structure')
model.add(tkl.Embedding(10000,32))
model.add(
    tkl.LSTM(32,return_sequences=True))
model.add(tkl.LSTM(32))
model.add(tkl.Dense(1))
model.summary()

model=tf.keras.Sequential(
    name='gru_structure')
model.add(tkl.Embedding(10000,32))
model.add(
    tkl.GRU(32,return_sequences=True))
model.add(tkl.GRU(32))
model.add(tkl.Dense(1))
model.summary()

dhtml('Predicting Sentiments')

dhtml(' '.join(
    [list(token_counts)[i]
     for i in range(32)]),c2,f2,fs2)

embedding_dim=32
vocabulary_size=len(token_counts)+2
model=tf.keras.Sequential(
    name='bi_lstm_model')
model.add(tkl.Embedding(
    input_dim=vocabulary_size,
    output_dim=embedding_dim,
    name='embedding_layer'))
model.add(tkl.Bidirectional(
    tkl.LSTM(64,name='lstm_layer'),
    name='bidirect_lstm_layer'))
model.add(tkl.Dense(64,activation='relu',
                    name='dense_64'))
model.add(tkl.Dense(1,activation='sigmoid',
                    name='out'))
optimizer=tf.keras.optimizers.Adam(1e-3)
loss_fun=tf.keras.losses\
.BinaryCrossentropy(from_logits=False)
model.compile(
    optimizer=optimizer,loss=loss_fun,
    metrics=['accuracy'])

history=model.fit(
    train_data,epochs=5,
    validation_data=valid_data)

model.evaluate(test_data)

dhtml('Functions in Construction Process')

def preprocess_datasets(
    ds_train,ds_valid,ds_test,
    max_seq_len=None,batch_size=32):
    tokenizer=tfds.features.text.Tokenizer()
    token_counts=Counter()
    for ds in [ds_train,ds_valid,ds_test]:
        for example in ds:
            tokens=tokenizer.tokenize(
                example[0].numpy())
            if max_seq_len is not None:
                tokens=tokens[-max_seq_len:]
            token_counts.update(tokens)
    print('vocabulary size: ',len(token_counts))
    encoder=tfds.features.text\
    .TokenTextEncoder(token_counts)
    def encode(text_tensor,label):
        text=text_tensor.numpy()
        encoded_text=encoder.encode(text)
        if max_seq_len is not None:
            encoded_text=encoded_text[-max_seq_len:]
        return encoded_text,label
    def encode_fmap(text,label):
        return tf.py_function(
            encode,inp=[text,label], 
            Tout=(tf.int64,tf.int64))
    train=ds_train.map(encode_fmap)
    valid=ds_valid.map(encode_fmap)
    test=ds_test.map(encode_fmap)
    train_data=train.padded_batch(
        batch_size,padded_shapes=([-1],[]))
    valid_data=valid.padded_batch(
        batch_size,padded_shapes=([-1],[]))
    test_data=test.padded_batch(
        batch_size,padded_shapes=([-1],[]))
    return (train_data,valid_data,test_data,
            len(token_counts))

def build_rnn_model(
    embedding_dim,vocabulary_size,
    recurrent_type='SimpleRNN',
    n_rnn_units=64,n_rnn_layers=1,
    bidirect=True):
    tf.random.set_seed(123)
    model=tf.keras.Sequential()
    model.add(tkl.Embedding(
        input_dim=vocabulary_size,
        output_dim=embedding_dim,
        name='embedding_layer'))
    for i in range(n_rnn_layers):
        return_sequences=(i<n_rnn_layers-1)    
        if recurrent_type=='SimpleRNN':
            recurrent_layer=tkl.SimpleRNN(
                units=n_rnn_units, 
                return_sequences=return_sequences,
                name='simple_rnn_layer{}'.format(i))
        elif recurrent_type=='LSTM':
            recurrent_layer=tkl.LSTM(
                units=n_rnn_units, 
                return_sequences=return_sequences,
                name='lstm_layer{}'.format(i))
        elif recurrent_type=='GRU':
            recurrent_layer=tkl.GRU(
                units=n_rnn_units, 
                return_seq=return_sequences,
                name='gru_layer{}'.format(i))     
        if bidirect:
            recurrent_layer=tkl.Bidirectional(
                recurrent_layer,
                name='bidirect_'+recurrent_layer.name)       
        model.add(recurrent_layer)
    model.add(tkl.Dense(64,activation='relu'))
    model.add(tkl.Dense(1,activation='sigmoid'))
    return model

batch_size=32
max_seq_len=100
train_data,valid_data,test_data,n=\
preprocess_datasets(
    ds_train,ds_valid,ds_test,
    max_seq_len=max_seq_len,
    batch_size=batch_size)

vocabulary_size=n+2
embedding_dim=32
rnn_model=build_rnn_model(
    embedding_dim,vocabulary_size,
    recurrent_type='SimpleRNN', 
    n_rnn_units=64,n_rnn_layers=3,
    bidirect=True)
rnn_model.summary()

optimizer=tf.keras.optimizers.Adam(1e-3)
loss_fun=tf.keras.losses\
.BinaryCrossentropy(from_logits=False)
rnn_model.compile(
    optimizer=optimizer,loss=loss_fun,
    metrics=['accuracy'])
history=rnn_model.fit(
    train_data,epochs=10,
    validation_data=valid_data)

rnn_model.evaluate(test_data)