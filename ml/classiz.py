from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn import cross_validation
import abc


class Classiz(object):

    def __init__(self, *args, **kwargs):
        self.__features = []
        self.__target   = []

    def dataload(self, path):
        for line in open(path):
            [instance, label] = line.strip().split('\t')
            self.__features.append(instance.split(','))
            self.__target.append(label)

    def getFeature(self):
        return self.__features

    def getTarget(self):
        return self.__target

    @abc.abstractmethod
    def train(self):
        raise NotImplementedError()


class SVM(Classiz):

    def __init__(self, *args, **kwargs):
        Classiz.__init__(self, *args, **kwargs)
        self.__clf = svm.SVC(gamma=0.001, C=100.)

    def train(self):
        pass

    def crossvalid(self, cv):
        data   = self.getFeature()
        target = self.getTarget()
        scores = cross_validation.cross_val_score(self.__clf, data, target, cv)
        print scores


class LR(Classiz):

    def __init__(self, *args, **kwargs):
        Classiz.__init__(self, *args, **kwargs)
        self.__clf = LogisticRegression(C=1., solver='lbfgs')

    def train(self):
        pass

    def crossvalid(self, cv):
        data   = self.getFeature()
        target = self.getTarget()
        scores = cross_validation.cross_val_score(self.__clf, data, target, cv)
        print scores

#
