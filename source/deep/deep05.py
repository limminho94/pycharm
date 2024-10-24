import keras
from keras import layers


model = keras.Sequential([
    layers.Dense(units=16, input_shape=(16,), activation="relu"),
    layers.Dense(units=128, activation="relu"),
    layers.Dense(units=512, activation="relu"),
    layers.Dense(units=10, activation="softmax"),
])


model.summary()