## Support Vector Machine
import numpy as np

from svm_3 import *

train_f1 = x_train[:, 0]
train_f2 = x_train[:, 1]

train_f1 = train_f1.reshape(90, 1)
train_f2 = train_f2.reshape(90, 1)

w1 = np.zeros((90, 1))
w2 = np.zeros((90, 1))

epochs = 1
alpha = 0.0001

while (epochs < 10000):
    y = w1 * train_f1 + w2 * train_f2
    prod = y * y_train
    # print(epochs)
    # count = 0
    # for val in prod:
    for count, val in enumerate(prod):
        if (val >= 1):
            cost = 0
            w1 = w1 - alpha * (2 * 1 / epochs * w1)
            w2 = w2 - alpha * (2 * 1 / epochs * w2)

        else:
            cost = 1 - val
            w1 = w1 + alpha * (train_f1[count] * y_train[count] - 2 * 1 / epochs * w1)
            w2 = w2 + alpha * (train_f2[count] * y_train[count] - 2 * 1 / epochs * w2)
        # count += 1
    epochs += 1