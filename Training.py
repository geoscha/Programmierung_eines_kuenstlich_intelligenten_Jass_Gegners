# Grundmanipulationen mit Keras:
# https://machinelearningmastery.com/tutorial-first-neural-network-python-keras/
#
# Bestimmen der Batch Grössen:
# https://vitalflux.com/python-keras-learning-validation-curve-classification-model/
#
# https://www.youtube.com/watch?v=d3-j-hq5AD8&t=998s
#
# 2. Modell graph aufzeigen
# https://machinelearningmastery.com/display-deep-learning-model-training-history-in-keras/
#
# Modell bewerten anhand loss
# https://machinelearningmastery.com/learning-curves-for-diagnosing-machine-learning-model-performance/
#
# Model loss spike wegkriegen
# https://stats.stackexchange.com/questions/498584/extremely-large-spike-in-training-loss-that-destroys-training-progress
#
# Opttimieren d. Netzes
# https://machinelearningmastery.com/better-deep-learning-neural-networks-crash-course/
#
# Relu/Leaky Relu
# https://artemoppermann.com/de/aktivierungsfunktionen/

# Batchsize Normalization:
# 0: A: 88, R:87%
# 1: A: 83, R: 86%
# 2: A: 86, R: 86%
# 3: A: 84, R: 87%
# 4: A: 86, R: 86%
# 5: A: 83, R: 89%

import numpy as np
import copy
import pickle
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from keras.layers import BatchNormalization
from keras.layers import GaussianNoise  # Verhindert Overfitting nach 2 Epochs mit Batch Size 5
from keras.callbacks import EarlyStopping

modus = 0
ansagen = True
# Ansage bestimmung

def create_model():

    print("Warten...")
    global model, X_size, Y_size, accuracy, history

    X_size = len(X[0].tolist())
    print("X_size", X_size)

    model = Sequential()                                                # Modell definieren

    model.add(Dense(X_size, input_shape=(X_size,), activation='relu'))  # Input Layer
    model.add(GaussianNoise(0.3))                                       # extrapolieren der Daten, mildert Overfitting
    model.add(Dense(X_size, activation='relu'))                         # Hidden Layer 1
    model.add(BatchNormalization())                                     # Stabilisator
    model.add(Dense(X_size, activation='relu'))                         # Hidden Layer 2
    model.add(BatchNormalization())                                     # Stabilisator
    model.add(Dense(X_size, activation='relu'))                         # Hidden Layer 3
    model.add(BatchNormalization())                                     # Stabilisator
    model.add(Dense(1, activation='relu'))                              # Output Layer

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    history = model.fit(X, Y, validation_split=0.1, epochs=100, batch_size=10, verbose=1)

    _, accuracy = model.evaluate(X, Y)
    print('Accuracy: %.2f' % (accuracy * 100))
    scores = model.evaluate(X, Y)
    print("%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))

    model.save(s_name+".h5") # Nicht die korrekte Speicher bezeichnung, Modell soll nicht geändert werden

print("Daten laden...")

mod_name = ["OA", "UU", "HE", "SC", "KA", "KR"]
               
if ansagen:
    s_name = "Data/108_A-" + mod_name[modus] + "_data"
else:
    s_name = "Data/108_R-" + mod_name[modus] + "_data"

X = np.array(pickle.load(open(s_name, "rb"))[0])  # Dateien laden
Y = np.array(pickle.load(open(s_name, "rb"))[1])  # Dateien laden

print("LEN_X:", len(copy.deepcopy(X.tolist())), "/LEN_Y", len(copy.deepcopy(X.tolist())))

create_model()

# Loss Darstellen
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
if ansagen:
    plt.title('model loss - Ansagen: ' + s_name)
else:
    plt.title('model loss - Reagieren: ' + s_name)
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# Accuracy darstellen
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
