# -*- coding: utf-8 -*-
"""tf-flowers.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uAxj_ToyWZ-CZDBWP8zy5WQV0jl39Ehs

## Code Modules
"""

!pip install --upgrade neural_structured_learning --user

import pandas as pd,numpy as np,pylab as pl
import os,h5py,cv2,tensorflow as tf
import tensorflow_hub as th
import neural_structured_learning as nsl
from sklearn.model_selection import train_test_split
fpath='../input/image-classification-for-biospecies-2/'
fw='weights.best.hdf5'

"""## Data"""

f=h5py.File(fpath+'TfFlowerImages.h5','r')
keys=list(f.keys()); print(keys)
x_test=np.array(f[keys[0]]); y_test=np.array(f[keys[1]])
x_train=np.array(f[keys[2]]); y_train=np.array(f[keys[3]])
fig=pl.figure(figsize=(11,4))
n=np.random.randint(1,50); n_classes=120
for i in range(n,n+5):
    ax=fig.add_subplot(1,5,i-n+1,\
    xticks=[],yticks=[],title=y_test[i][0])
    ax.imshow((x_test[i]))
cy_train=np.array(tf.keras.utils\
.to_categorical(y_train,n_classes),dtype='int32')
cy_test=np.array(tf.keras.utils\
.to_categorical(y_test,n_classes),dtype='int32')
n=int(len(x_test)/2)
x_valid,y_valid,cy_valid=x_test[:n],y_test[:n],cy_test[:n]
x_test,y_test,cy_test=x_test[n:],y_test[n:],cy_test[n:]
df=pd.DataFrame([[x_train.shape,x_valid.shape,x_test.shape],
                 [x_train.dtype,x_valid.dtype,x_test.dtype],
                 [y_train.shape,y_valid.shape,y_test.shape],
                 [y_train.dtype,y_valid.dtype,y_test.dtype],
                 [cy_train.shape,cy_valid.shape,cy_test.shape],
                 [cy_train.dtype,cy_valid.dtype,cy_test.dtype]],
                 columns=['train','valid','test'],
                 index=['image shape','image type',
                        'label shape','label type',
                        'shape of encoded label',
                        'type of encoded label'])
display(df)

"""## NN Examples
CNN Based Models with Adversarial Regularization
"""

batch_size=64; img_size=128; n_class=5; epochs=7
base_model=tf.keras.Sequential([
    tf.keras.Input((img_size,img_size,3),name='input'),
    tf.keras.layers.Conv2D(32,(5,5),padding='same'),
    tf.keras.layers.Activation('relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2,2)),
    tf.keras.layers.Dropout(.25),
    tf.keras.layers.Conv2D(196,(5,5)),
    tf.keras.layers.Activation('relu'),    
    tf.keras.layers.MaxPooling2D(pool_size=(2,2)),
    tf.keras.layers.Dropout(.25),
    tf.keras.layers.GlobalMaxPooling2D(),    
    tf.keras.layers.Dense(512),
    tf.keras.layers.Activation('relu'),
    tf.keras.layers.Dropout(.25),
    tf.keras.layers.Dense(128),
    tf.keras.layers.Activation('relu'),
    tf.keras.layers.Dropout(.25),
    tf.keras.layers.Dense(10,activation='softmax')
])
adv_config=nsl.configs\
.make_adv_reg_config(multiplier=.2,adv_step_size=.05)
adv_model=nsl.keras\
.AdversarialRegularization(base_model,adv_config=adv_config)
adv_model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

train=tf.data.Dataset.from_tensor_slices(
    {'input':x_train,'label':y_train}).batch(batch_size)
valid=tf.data.Dataset.from_tensor_slices(
    {'input':x_valid,'label':y_valid}).batch(batch_size)
valid_steps=x_valid.shape[0]//batch_size
adv_model.fit(train,validation_data=valid,verbose=2,
              validation_steps=valid_steps,epochs=epochs)

adv_model.evaluate({'input':x_test,'label':y_test})

"""## Pretrained Models"""

def premodel(pix,den,mh,lbl):
    model=tf.keras.Sequential([
        tf.keras.layers.Input((pix,pix,3),
                              name='input'),
        th.KerasLayer(mh,trainable=True),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(den,activation='relu'),
        tf.keras.layers.Dropout(rate=.5),
        tf.keras.layers.Dense(lbl,activation='softmax')])
    model.compile(optimizer='adam',metrics=['accuracy'],
                  loss='sparse_categorical_crossentropy')
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

[handle_base,pixels]=["mobilenet_v2_100_128",128]
mhandle="https://tfhub.dev/google/imagenet/{}/feature_vector/4"\
.format(handle_base)

model=premodel(pixels,512,mhandle,10)
history=model.fit(x=x_train,y=y_train,batch_size=64,
                  epochs=10,callbacks=cb(fw),
                  validation_data=(x_valid,y_valid))

model.load_weights(fw)
model.evaluate(x_test,y_test)