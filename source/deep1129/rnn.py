import keras
from keras import layers, callbacks, models, applications


keras.utils.set_random_seed(0)


fe_layer = applications.ResNet152V2(weights='imagenet', include_top=False, input_shape=(224,224,3))


fe_layer.summary()

fe_layer.trainable = False

fc_layer = layers.GlobalAveragePooling2D()(fe_layer.output)
fc_layer = layers.Dense(1000, activation='softmax')(fc_layer)

model = models.Model(inputs=fe_layer.input, outputs=fc_layer)

model.summary()