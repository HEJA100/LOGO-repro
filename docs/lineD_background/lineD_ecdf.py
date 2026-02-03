import numpy as np

class DummyECDF:
    def __call__(self, x):
        x = np.asarray(x)
        return np.zeros_like(x, dtype=float)
