from variables import db
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
import numpy as np
import matplotlib.pyplot as plt

def NBAccuracy(features_train, labels_train, features_test, labels_test):
    """ compute the accuracy of your Naive Bayes classifier """
    ### import the sklearn module for GaussianNB
    from sklearn.naive_bayes import GaussianNB

    ### create classifier
    clf = GaussianNB()

    ### fit the classifier on the training features and labels
    clf.fit(features_train.reshape(-1, 1), labels_train)

    ### use the trained classifier to predict labels for the test features
    pred = clf.predict(features_test.reshape(-1,1))
    print(pred)

    ### calculate and return the accuracy on the test data
    ### this is slightly different than the example,
    ### where we just print the accuracy
    ### you might need to import an sklearn module
    accuracy = clf.score(features_test.reshape(-1, 1), labels_test)
    return accuracy

ml_classifier = LinearRegression()

#Get all the entries from mrally
mrally_data_cursor = db.ashioto_data.find({"eventCode" : "mnm16", "gateID": 2}, {"outcount": 1, "timestamp": 1})
mrally_data_cursor_count = mrally_data_cursor.count()
mrally_data_timestamps = []
mrally_data_counts = []

# for datapoint in mrally_data_cursor:
#     mrally_data_timestamps.append(datapoint['timestamp'])
#     mrally_data_counts.append(datapoint['outcount'])

for i in range(0, mrally_data_cursor_count):
    mrally_data_counts.append(mrally_data_cursor[i]['outcount'])
    mrally_data_timestamps.append(mrally_data_cursor[i]['timestamp'])

mrally_data_counts = np.asarray(mrally_data_counts)
mrally_data_timestamps = np.asarray(mrally_data_timestamps)

#print(mrally_data_counts)
#print(mrally_data_timestamps)
ml_classifier.fit(mrally_data_timestamps.reshape(-1, 1), mrally_data_counts)
print(int(ml_classifier.predict(np.array([1474694435]).reshape(-1,1))))
plt.plot(mrally_data_timestamps, mrally_data_counts, 'bo')
plt.show()
#print(NBAccuracy(features_train=mrally_data_timestamps, labels_train=mrally_data_counts, features_test=np.array([1474705930]), labels_test=np.array([79925])))
