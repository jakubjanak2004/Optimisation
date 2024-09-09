import numpy as np
import matplotlib.pyplot as plt


class PolynomialRegression:
    def __init__(self, n=1):
        self.n = n
        self.a = None
        self.x = None
        self.y = None

    def train(self, x: np.array, y: np.array):
        self.x = x
        self.y = y
        X = np.array([1 for e in range(len(x))]).reshape(-1, 1)
        for column in range(1, self.n + 1):
            X = np.column_stack((X, x ** column))

        self.a = np.linalg.inv(X.T @ X) @ X.T @ y

    def plot_trained_model(self):
        def model(X):
            polynom = 0
            for c in range(len(self.a)):
                polynom += self.a[c] * X ** c
            return polynom

        X = np.linspace(np.min(self.x) - 1, np.max(self.x) + 1, 100)
        f = model(X)

        plt.scatter(self.x, self.y, color='blue')
        plt.plot(X, f, color='red')

        plt.title('Polynomial Regression')

        plt.show()