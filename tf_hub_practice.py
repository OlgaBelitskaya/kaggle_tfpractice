# -*- coding: utf-8 -*-
"""tf-hub-practice.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1plIF6d0sK6eGLIQVrxWsOIi3b4tp3ijv

## Code Modules
"""

import numpy as np,pandas as pd
import h5py,pylab as pl
import tensorflow_hub as th,tensorflow as tf
from tensorflow import image as timage

"""## Data"""

fpath='../input/tf-cats-vs-dogs/'
f='CatDogImages.h5'
f=h5py.File(fpath+f,'r')
keys=list(f.keys()); print(keys)
x_test=np.array(f[keys[0]])
y_test=np.array(f[keys[1]],dtype='int8')
x_train=np.array(f[keys[2]])
y_train=np.array(f[keys[3]],dtype='int8')
N=len(y_train); shuffle_ids=np.arange(N)
np.random.RandomState(12).shuffle(shuffle_ids)
x_train,y_train=x_train[shuffle_ids],y_train[shuffle_ids]
N=len(y_test); shuffle_ids=np.arange(N)
np.random.RandomState(23).shuffle(shuffle_ids)
x_test,y_test=x_test[shuffle_ids],y_test[shuffle_ids]
n=int(len(x_test)/2)
x_valid,y_valid=x_test[:n],y_test[:n]
x_test,y_test=x_test[n:],y_test[n:]
pd.DataFrame([[x_train.shape,x_valid.shape,x_test.shape],
              [x_train.dtype,x_valid.dtype,x_test.dtype],
              [y_train.shape,y_valid.shape,y_test.shape],
              [y_train.dtype,y_valid.dtype,y_test.dtype]],
             columns=['train','valid','test'],
             index=['image shape','image type',
                    'label shape','label type'])

"""## TF Hub Models"""

fw='weights.best.hdf5'
def premodel(pix,den,mh,lbl,activ,loss):
    model=tf.keras.Sequential([
        tf.keras.layers.Input((pix,pix,3),
                              name='input'),
        th.KerasLayer(mh,trainable=True),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(den,activation='relu'),
        tf.keras.layers.Dropout(rate=.5),
        tf.keras.layers.Dense(lbl,activation=activ)])
    model.compile(optimizer='adam',
                  metrics=['accuracy'],loss=loss)
    display(model.summary())
    return model
def cb(fw):
    early_stopping=tf.keras.callbacks\
    .EarlyStopping(monitor='val_loss',patience=20,verbose=2)
    checkpointer=tf.keras.callbacks\
    .ModelCheckpoint(filepath=fw,save_best_only=True,verbose=2)
    lr_reduction=tf.keras.callbacks\
    .ReduceLROnPlateau(monitor='val_loss',verbose=2,
                       patience=5,factor=.8)
    return [checkpointer,early_stopping,lr_reduction]

[handle_base,pixels]=["mobilenet_v1_100_128",128]
mhandle="https://tfhub.dev/google/imagenet/{}/feature_vector/4"\
.format(handle_base)

model=premodel(pixels,3072,mhandle,1,
               'sigmoid','binary_crossentropy')
history=model.fit(x=x_train,y=y_train,batch_size=128,
                  epochs=3,callbacks=cb(fw),
                  validation_data=(x_valid,y_valid))

model.load_weights(fw)
model.evaluate(x_test,y_test)