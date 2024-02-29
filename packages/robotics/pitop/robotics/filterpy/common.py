import numpy as np


def pretty_str(label, arr):
    """Generates a pretty printed NumPy array with an assignment. Optionally
    transposes column vectors so they are drawn on one line. Strictly speaking
    arr can be any time convertible by `str(arr)`, but the output may not be
    what you want if the type of the variable is not a scalar or an ndarray.

    Examples
    --------
    >>> pprint('cov', np.array([[4., .1], [.1, 5]]))
    cov = [[4.  0.1]
           [0.1 5. ]]
    >>> print(pretty_str('x', np.array([[1], [2], [3]])))
    x = [[1 2 3]].T
    """

    def is_col(a):
        """Return true if a is a column vector."""
        try:
            return a.shape[0] > 1 and a.shape[1] == 1
        except (AttributeError, IndexError):
            return False

    if label is None:
        label = ""

    if label:
        label += " = "

    if is_col(arr):
        return label + str(arr.T).replace("\n", "") + ".T"

    rows = str(arr).split("\n")
    if not rows:
        return ""

    s = label + rows[0]
    pad = " " * len(label)
    for line in rows[1:]:
        s = s + "\n" + pad + line

    return s


def reshape_z(z, dim_z, ndim):
    """Ensure z is a (dim_z, 1) shaped vector."""

    z = np.atleast_2d(z)
    if z.shape[1] == dim_z:
        z = z.T

    if z.shape != (dim_z, 1):
        raise ValueError(
            "z (shape {}) must be convertible to shape ({}, 1)".format(z.shape, dim_z)
        )

    if ndim == 1:
        z = z[:, 0]

    if ndim == 0:
        z = z[0, 0]

    return z
