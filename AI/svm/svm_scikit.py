
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

from svm_3 import *

clf = SVC(kernel='linear')
clf.fit(x_train,y_train)
y_pred = clf.predict(x_test)
print(accuracy_score(y_test,y_pred))