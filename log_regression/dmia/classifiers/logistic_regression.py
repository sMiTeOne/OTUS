import numpy as np
from scipy import sparse
from scipy.special import expit


class LogisticRegression:
    def __init__(self):
        self.w = None
        self.loss_history = None

    def train(self, x, y, learning_rate=1e-3, reg=1e-5, num_iters=100, batch_size=200, verbose=False):
        """
        Train this classifier using stochastic gradient descent.

        Inputs:
        - x: N x D array of training data. Each training point is a D-dimensional
             column.
        - y: 1-dimensional array of length N with labels 0-1, for 2 classes.
        - learning_rate: (float) learning rate for optimization.
        - reg: (float) regularization strength.
        - num_iters: (integer) number of steps to take when optimizing
        - batch_size: (integer) number of training examples to use at each step.
        - verbose: (boolean) If true, print progress during optimization.

        Outputs:
        A list containing the value of the loss function at each training iteration.
        """
        # Add a column of ones to X for the bias sake.
        x = LogisticRegression.append_biases(x)
        num_train, dim = x.shape
        if self.w is None:
            # lazily initialize weights
            self.w = np.random.randn(dim) * 0.01

        # Run stochastic gradient descent to optimize W
        self.loss_history = []
        for i in range(num_iters):
            random_idx = np.random.choice(num_train, batch_size)
            x_batch = x[random_idx]
            y_batch = y[random_idx]

            # evaluate loss and gradient
            loss, grad_weight = self.loss(x_batch, y_batch, reg)
            self.loss_history.append(loss)
            # perform parameter update
            self.w -= learning_rate * grad_weight

            if verbose and i % 100 == 0:
                print(f'iteration {i} / {num_iters}: loss {loss}')

        return self

    def predict_proba(self, x, append_bias=False):
        """
        Use the trained weights of this linear classifier to predict probabilities for
        data points.

        Inputs:
        - X: N x D array of data. Each row is a D-dimensional point.
        - append_bias: bool. Whether to append bias before predicting or not.

        Returns:
        - y_proba: Probabilities of classes for the data in X. y_pred is a 2-dimensional
          array with a shape (N, 2), and each row is a distribution of classes [prob_class_0, prob_class_1].
        """
        if append_bias:
            x = LogisticRegression.append_biases(x)

        x_dot_w = x.dot(self.w)
        proba = expit(x_dot_w)
        y_proba = np.vstack((1 - proba, proba)).T

        return y_proba

    def predict(self, x):
        """
        Use the ```predict_proba``` method to predict labels for data points.

        Inputs:
        - x: N x D array of training data. Each column is a D-dimensional point.

        Returns:
        - y_pred: Predicted labels for the data in X. y_pred is a 1-dimensional
          array of length N, and each element is an integer giving the predicted
          class.
        """
        y_proba = self.predict_proba(x, append_bias=True)
        y_pred = np.argmax(y_proba, axis=1)

        return y_pred

    def loss(self, x_batch, y_batch, reg):
        """Logistic Regression loss function
        Inputs:
        - x: N x D array of data. Data are D-dimensional rows
        - y: 1-dimensional array of length N with labels 0-1, for 2 classes
        Returns:
        a tuple of:
        - loss as single float
        - gradient with respect to weights w; an array of same shape as w
        """
        y_proba = self.predict_proba(x_batch)
        sigmoid = y_proba[:, 1]

        left_part = y_batch * np.log(sigmoid)
        right_part = (1 - y_batch) * np.log(1 - sigmoid)

        loss = -np.sum(left_part + right_part) / y_batch.shape
        dw = x_batch.T.dot(sigmoid - y_batch) / x_batch.shape[0]

        loss += reg * np.sum(self.w[:-1] ** 2) / 2
        dw[:-1] += self.w[:-1] * reg

        return loss, dw

    @staticmethod
    def append_biases(x):
        return sparse.hstack((x, np.ones(x.shape[0])[:, np.newaxis])).tocsr()
