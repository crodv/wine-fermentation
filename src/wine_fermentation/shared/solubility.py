
"""Provisional inherited wine-like correlation, explicitly not a verified Henry correlation."""
import numpy as np
STATUS='provisional_inherited_correlation'
def saturation(T,E,G,F):
    return 1.69*np.exp(-.032*(np.asarray(T)-20))*np.exp(.0016*np.asarray(E)) * np.exp(-.0012*(np.asarray(G)+np.asarray(F)))
