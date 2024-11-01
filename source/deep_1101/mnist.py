import os

import keras
from keras import layers, callbacks, datasets
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

np.set_printoptions(threshold=None, linewidth=np.inf, suppress=True, precision=3)
keras.utils.set_random_seed(0)

(x_train, y_train), (x_test, y_test) = datasets.fashion_mnist.load_data()

norm = layers.Normalization()
norm.adapt(x_train)
x_train_, x_test_ = norm(x_train), norm(x_test)
# print(x_train_[0])
# print(x_train.shape)
# print(x_test.shape)
# print(y_train.shape)
# print(y_test.shape)
# print(np.unique(y_train))
# print(x_train[2])
# print(y_train[2])
# plt.imshow(x_train[0], cmap='gray')
# plt.show()
x_train_, x_test_ = tf.expand_dims(x_train_, axis=-1), tf.expand_dims(x_test_, axis=-1)

# model= keras.Sequential([
#     layers.Flatten(input_shape=x_train[0].shape),
#     layers.Dense(512, activation='relu'),
#     layers.Dense(10, activation='softmax')
# ])

model = keras.Sequential([
    layers.Conv2D(8, input_shape=x_train_[0].shape, kernel_size=(3,3), padding="same", strides=(1,1), activation="relu"),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(16,kernel_size=3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.BatchNormalization(),
    layers.Flatten(),
    layers.Dense(512, activation="relu"),
    layers.Dense(len(np.unique(y_train)), activation="softmax")
])

model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

if not os.path.exists("./model"):
    os.mkdir("./model")

save_path = "./model/mnist_model.keras"
es = callbacks.EarlyStopping(monitor="val_loss", patience=10, verbose=1)
cp = callbacks.ModelCheckpoint(filepath=save_path, monitor="val_loss", save_best_only=True, verbose=1)

history = model.fit(x_train_, y_train, epochs=30, batch_size=256, validation_split=0.2, validation_batch_size=256, callbacks=[es, cp], shuffle=True)

loss = history.history["loss"]
val_loss = history.history["val_loss"]
accuracy = history.history["accuracy"]
val_accuracy = history.history["val_accuracy"]

x_len = np.arange(len(loss))
plt.plot(x_len, loss, marker=".", c="blue", label="train_loss")
plt.plot(x_len, val_loss, marker=".", c="red", label="validation_loss")
plt.legend(loc="upper right")
plt.grid()
plt.xlabel("epoch")
plt.ylabel("loss")
plt.show()

plt.plot(x_len, val_accuracy, marker=".", c="blue", label="train_accuracy")
plt.plot(x_len, accuracy, marker=".", c="red", label="validation_accuracy")
plt.legend(loc="upper right")
plt.grid()
plt.xlabel("epoch")
plt.ylabel("accuracy")
plt.show()

predict = model.predict(x_test_)
# print(np.mean(np.argmax(predict, axis=1) == y_test))

# model.summary()
