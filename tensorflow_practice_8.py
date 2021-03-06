# -*- coding: utf-8 -*-
"""tensorflow-practice-8.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KFMSV_vvxnf-eRlJ2C0QH-pBplSl1258

Reading classics [Python Machine Learning 3rd Edition](https://github.com/rasbt/python-machine-learning-book-3rd-edition/blob/master/ch15/ch15_part1.ipynb)
"""

# Commented out IPython magic to ensure Python compatibility.
from IPython.display import display,HTML

c1,c2,f1,f2,fs1,fs2=\
'#11ff66','#6611ff','Wallpoet','Orbitron',20,10
def dhtml(string,fontcolor=c1,font=f1,fontsize=fs1):
    display(HTML("""<style>
    @import 'https://fonts.googleapis.com/css?family="""\
    +font+"""&effect=3d-float';</style>
    <h1 class='font-effect-3d-float' 
    style='font-family:"""+font+\
    """; color:"""+fontcolor+\
    """; font-size:"""+str(fontsize)+"""px;'>
#     %s</h1>"""%string))

dhtml('Code Modules, Setting, & Functions')

!python3 -m pip install --upgrade pip \
--user --quiet --no-warn-script-location
!python3 -m pip install --upgrade tensorflow==2.3.0 \
--user --quiet --no-warn-script-location
!pip install mplcyberpunk --user --quiet

import warnings; warnings.filterwarnings('ignore')
import mplcyberpunk,numpy as np
import tensorflow as tf,pylab as pl
from IPython.core.magic import register_line_magic
from sklearn.metrics import \
classification_report,confusion_matrix
pl.style.use('cyberpunk')

@register_line_magic
def display_examples(pars):
    pars=pars.split()
    data,n=pars[0],int(pars[1])
    if data=='mnist': data=mnist_test
    if data=='cifar': data=cifar_test
    batch=next(iter(data.batch(n)))
    images=batch[0].numpy()
    labels=batch[1].numpy() 
    fig=pl.figure(figsize=(2*n//3,4.5))
    for i in range(n):
        ax=fig.add_subplot(3,n//3,i+1)
        ax.set_xticks([]); ax.set_yticks([])
        ax.imshow(np.squeeze(images[i]),
                  cmap='bone')
        ax.text(.85,.15,'{}'.format(labels[i]), 
                fontdict={'color':c1,'fontsize':30},
                horizontalalignment='center',
                verticalalignment='center', 
                transform=ax.transAxes)
    pl.tight_layout(); pl.show()
    
@register_line_magic
def history_plot(yes):
    global history
    pl.figure(figsize=(10,10)); pl.subplot(211)
    keys=list(history.history.keys())[0:4]
    pl.plot(history.history[keys[0]],
            color=c1,label=keys[0])
    pl.plot(history.history[keys[2]],
            color=c2,label=keys[2])
    pl.xlabel('Epochs'); pl.ylabel('Loss')
    pl.legend(); pl.grid(); pl.title('Loss Function')     
    pl.subplot(212)
    pl.plot(history.history[keys[1]],
            color=c1,label=keys[1])
    pl.plot(history.history[keys[3]],
            color=c2,label=keys[3])
    pl.xlabel('Epochs'); pl.ylabel('Accuracy')    
    pl.legend(); pl.grid(); pl.title('Accuracy')
    mplcyberpunk.add_glow_effects()
    pl.tight_layout(); pl.show()
    
@register_line_magic
def display_reports(data):
    global model,model_weights,buffer_size,c2,f2,fs2
    model.load_weights(model_weights)
    if data=='mnist': data=mnist_test
    if data=='cifar': data=cifar_test
    test_results=model.evaluate(
        data.batch(buffer_size),verbose=0)
    dhtml('\ntest accuracy: {:.2f}%'\
          .format(test_results[1]*100),c2,f2,fs2)
    batch=next(iter(data.batch(buffer_size)))
    y_test=batch[1].numpy()
    py_test=np.argmax(
        model.predict(data.batch(buffer_size)),axis=-1)
    dhtml('Classification Report',c2,f2,fs2)
    print(classification_report(y_test,py_test))
    dhtml('Confusion Matrix',c2,f2,fs2)
    print(confusion_matrix(y_test,py_test))

dhtml('Data Processing')

# Commented out IPython magic to ensure Python compatibility.
# %%writefile tfpreprocess_mnist.py
# import warnings; warnings.filterwarnings('ignore')
# import tensorflow as tf,numpy as np,pandas as pd
# import tensorflow_datasets as tfds
# from IPython.display import display,HTML
# pd.set_option('precision',3)
# tf.keras.backend.set_floatx('float64')
# tfds.disable_progress_bar()
# img_size=32
# buffer_size,batch_size=10000,64
# 
# c1,c2,f1,f2,fs1,fs2=\
# '#11ff66','#6611ff','Wallpoet','Orbitron',20,10
# 
# def dhtml(string,fontcolor=c1,font=f1,fontsize=fs1):
#     display(HTML("""<style>
#     @import 'https://fonts.googleapis.com/css?family="""\
#     +font+"""&effect=3d-float';</style>
#     <h1 class='font-effect-3d-float' 
#     style='font-family:"""+font+\
#     """; color:"""+fontcolor+\
#     """; font-size:"""+str(fontsize)+"""px;'>
#     %s</h1>"""%string))
# 
# def load_mnist():
#     mnist=tfds.builder('mnist')
#     mnist.download_and_prepare()
#     ds=mnist.as_dataset(shuffle_files=False,
#                         split=['train','test'])
#     mnist_train,mnist_test=ds[0],ds[1]
#     dhtml(mnist.info.features['image'],c2,f2,fs2)
#     dhtml(mnist.info.features['label'],c2,f2,fs2)
#     mnist_train=mnist_train.map(
#         lambda item:(tf.image.resize(
#             tf.cast(item['image'],tf.float32),
#             [img_size,img_size])/255., 
#                      tf.cast(item['label'],tf.int32)))
#     mnist_test=mnist_test.map(
#         lambda item:(tf.image.resize(
#             tf.cast(item['image'],tf.float32),
#             [img_size,img_size])/255., 
#                      tf.cast(item['label'],tf.int32)))
#     tf.random.set_seed(123)
#     mnist_train=mnist_train.shuffle(
#         buffer_size=buffer_size,
#         reshuffle_each_iteration=False)
#     mnist_valid=mnist_train.take(buffer_size).batch(batch_size)
#     mnist_train=mnist_train.skip(buffer_size).batch(batch_size)
#     return mnist_train,mnist_valid,mnist_test

# Commented out IPython magic to ensure Python compatibility.
# %run tfpreprocess_mnist.py
mnist_train,mnist_valid,mnist_test=load_mnist()
# %display_examples mnist 9

# Commented out IPython magic to ensure Python compatibility.
# %%writefile tfpreprocess_cifar.py
# import warnings; warnings.filterwarnings('ignore')
# import tensorflow as tf,numpy as np,pandas as pd
# import tensorflow_datasets as tfds
# from IPython.display import display,HTML
# pd.set_option('precision',3)
# tf.keras.backend.set_floatx('float64')
# tfds.disable_progress_bar()
# img_size=32
# buffer_size,batch_size=10000,64
# 
# c1,c2,f1,f2,fs1,fs2=\
# '#11ff66','#6611ff','Wallpoet','Orbitron',20,10
# 
# def dhtml(string,fontcolor=c1,font=f1,fontsize=fs1):
#     display(HTML("""<style>
#     @import 'https://fonts.googleapis.com/css?family="""\
#     +font+"""&effect=3d-float';</style>
#     <h1 class='font-effect-3d-float' 
#     style='font-family:"""+font+\
#     """; color:"""+fontcolor+\
#     """; font-size:"""+str(fontsize)+"""px;'>
#     %s</h1>"""%string))
# 
# def load_cifar():
#     cifar=tfds.builder('cifar10')
#     cifar.download_and_prepare()
#     ds=cifar.as_dataset(shuffle_files=False,
#                         split=['train','test'])
#     cifar_train,cifar_test=ds[0],ds[1]
#     dhtml(cifar.info.features['image'],c2,f2,fs2)
#     dhtml(cifar.info.features['label'],c2,f2,fs2)
#     cifar_train=cifar_train.map(
#         lambda item:(tf.cast(item['image'],tf.float32)/255., 
#                      tf.cast(item['label'],tf.int32)))
#     cifar_test=cifar_test.map(
#         lambda item:(tf.cast(item['image'],tf.float32)/255., 
#                       tf.cast(item['label'],tf.int32)))
#     tf.random.set_seed(123)
#     cifar_train=cifar_train.shuffle(
#         buffer_size=buffer_size,
#         reshuffle_each_iteration=False)
#     cifar_valid=cifar_train.take(buffer_size).batch(batch_size)
#     cifar_train=cifar_train.skip(buffer_size).batch(batch_size)
#     return cifar_train,cifar_valid,cifar_test

# Commented out IPython magic to ensure Python compatibility.
# %run tfpreprocess_cifar.py
cifar_train,cifar_valid,cifar_test=load_cifar()
# %display_examples cifar 12

dhtml('CNN Construction. One Channel')

# Commented out IPython magic to ensure Python compatibility.
# %%writefile cnn_classify.py
# import warnings; warnings.filterwarnings('ignore')
# from IPython.display import display
# import tensorflow as tf,numpy as np
# import tensorflow.keras.layers as tkl
# import tensorflow.keras.utils as tku
# import tensorflow.keras.callbacks as tkc
# tf.keras.backend.set_floatx('float64')
# 
# def cb(mw):
#     early_stopping=tkc.EarlyStopping(
#         monitor='val_loss',patience=20,verbose=2)
#     checkpointer=tkc.ModelCheckpoint(
#         filepath=mw,save_best_only=True,verbose=2,
#         save_weights_only=True,monitor='val_accuracy',mode='max')
#     lr_reduction=tkc.ReduceLROnPlateau(
#         monitor='val_loss',verbose=2,patience=10,factor=.8)
#     return [checkpointer,early_stopping,lr_reduction]
# 
# def main_block_cnn(channels,img_size=32,filters=32):
#     model=tf.keras.Sequential()
#     model.add(tkl.Input(
#         (img_size,img_size,channels),name='input'))
#     model.add(tkl.Conv2D(
#         filters=filters,kernel_size=(7,7),
#         strides=(1,1),padding='same',name='conv_1'))
#     model.add(tkl.LeakyReLU(alpha=.02,name='lrelu_1'))
#     model.add(tf.keras.layers.MaxPool2D(
#         pool_size=(2,2),name='pool_1'))
#     model.add(tkl.Dropout(.25,name='drop_1'))
#     model.add(tkl.Conv2D(
#         filters=3*channels*filters,kernel_size=(7,7),
#         strides=(1,1),padding='same',name='conv_2'))
#     model.add(tkl.LeakyReLU(alpha=.02,name='lrelu_2'))
#     model.add(tf.keras.layers.MaxPool2D(
#         pool_size=(2,2),name='pool_2'))
#     model.add(tkl.Dropout(.25,name='drop_2'))
#     model.add(tkl.Conv2D(
#         filters=filters,kernel_size=(7,7),
#         strides=(1,1),padding='same',name='conv_3'))
#     model.add(tkl.LeakyReLU(alpha=.02,name='lrelu_3'))
#     model.add(tf.keras.layers.MaxPool2D(
#         pool_size=(2,2),name='pool_3'))
#     model.add(tkl.Dropout(.25,name='drop_3'))
#     return model
# 
# def out_block_cnn(model,dense,num_classes,plot=True):
#     model.add(tkl.GlobalMaxPooling2D(name='gmpool'))   
#     model.add(tkl.Dense(dense,name='dense_1'))
#     model.add(tkl.LeakyReLU(alpha=.02,name='lrelu_4'))
#     model.add(tkl.Dropout(.5,name='drop_4'))
#     model.add(tkl.Dense(num_classes,name='out',
#                         activation='softmax'))
#     if plot:
#         display(tku.plot_model(model,show_shapes=True))
#     return model
# 
# def compile_model(model):
#     return model.compile(
#         optimizer=tf.keras.optimizers.Adam(),
#         loss=tf.keras.losses\
#         .SparseCategoricalCrossentropy(),
#         metrics=['accuracy'])

# Commented out IPython magic to ensure Python compatibility.
# %run cnn_classify.py
model=main_block_cnn(1)
model.compute_output_shape(
    input_shape=(batch_size,img_size,img_size,1))

model=out_block_cnn(model,512,10)
compile_model(model)

model_weights='/checkpoints'
history=model.fit(mnist_train,epochs=50,shuffle=True, 
                  validation_data=mnist_valid,
                  callbacks=cb(model_weights))

# Commented out IPython magic to ensure Python compatibility.
# %history_plot yes

# Commented out IPython magic to ensure Python compatibility.
# %display_reports mnist

dhtml('CNN Construction. Three Channels')

model=main_block_cnn(3)
model.compute_output_shape(
    input_shape=(batch_size,img_size,img_size,3))

model=out_block_cnn(model,1024,10)
compile_model(model)

history=model.fit(cifar_train,epochs=70,shuffle=True, 
                  validation_data=cifar_valid,
                  callbacks=cb(model_weights))

# Commented out IPython magic to ensure Python compatibility.
# %history_plot yes

# Commented out IPython magic to ensure Python compatibility.
# %display_reports cifar