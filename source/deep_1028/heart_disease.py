import matplotlib.pyplot as plt
import numpy as np
# from sklearn.datasets import load_iris
import keras
from keras import layers, callbacks
from ucimlrepo import fetch_ucirepo

# fetch dataset
heart_disease = fetch_ucirepo(id=45)

keras.utils.set_random_seed(0)
save_path= "./model/ann_model.keras"
es = callbacks.EarlyStopping(monitor="val_loss", patience=10, verbose=1)
cp = callbacks.ModelCheckpoint(filepath=save_path, monitor="val_loss", save_best_only=True, verbose=1)
# data (as pandas dataframes)
x = heart_disease.data.features
y = heart_disease.data.targets

noise = np.random.normal(0,0.1, x.shape)
noisy_x = x + noise
x_ = np.concatenate((noisy_x, x), axis=0)
y_ = np.concatenate((y, y))
classes = len(np.unique(y_))
size = x_.shape


model = keras.Sequential([
    layers.Dense(units=4, input_shape=(size[1], ), activation='relu'),
    layers.Dense(units=32, activation='relu'),
    layers.Dense(units=64, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(units=classes, activation='softmax'),
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
history = model.fit(x_, y_, epochs=100, batch_size=32, validation_split=.2, validation_batch_size=32, callbacks=[es, cp], shuffle=True)

history_ = history.history
x_range = np.arange(1, len(history_["loss"]) +1)
plt.plot(x_range, history_['loss'], x_range, history_["val_loss"])
plt.show()

plt.plot(x_range, history_['accuracy'], x_range, history_["val_accuracy"])
plt.show()
# metadata
# print(heart_disease.metadata)
# variable information
# print(heart_disease.variables)