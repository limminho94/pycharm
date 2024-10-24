import numpy as np
import keras
from keras import layers, optimizers


keras.utils.set_random_seed(2)

inputs = np.array([[0,0], [0,1], [1,0], [1,1]], dtype = np.float32)
outputs = np.array([0,1,1,0], dtype = np.float32)


model = keras.Sequential([
    layers.Dense(units=16, input_shape=(2,), activation="relu"),
    layers.Dense(units=1, activation="sigmoid")
])

opt = optimizers.SGD(learning_rate=1.)

model.compile(optimizer=opt, loss="binary_crossentropy", metrics=["accuracy"])
model.fit(inputs, outputs, epochs=100)
result = model.predict(inputs)
print(result)
print(np.round(result).reshape(-1) == outputs)