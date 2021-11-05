import warnings

import numpy as np
from scipy.stats import multivariate_normal

# Older versions of scipy do not support the allow_singular keyword. I could
# check the version number explicily, but perhaps this is clearer
_support_singular = True
try:
    multivariate_normal.logpdf(1, 1, 1, allow_singular=True)
except TypeError:
    warnings.warn(
        "You are using a version of SciPy that does not support the "
        "allow_singular parameter in scipy.stats.multivariate_normal.logpdf(). "
        "Future versions of FilterPy will require a version of SciPy that "
        "implements this keyword",
        DeprecationWarning,
    )
    _support_singular = False


def logpdf(x, mean=None, cov=1, allow_singular=True):
    """Computes the log of the probability density function of the normal
    N(mean, cov) for the data x.

    The normal may be univariate or multivariate. Wrapper for older
    versions of scipy.multivariate_normal.logpdf which don't support
    support the allow_singular keyword prior to verion 0.15.0. If it is
    not supported, and cov is singular or not PSD you may get an
    exception. `x` and `mean` may be column vectors, row vectors, or
    lists.
    """

    if mean is not None:
        flat_mean = np.asarray(mean).flatten()
    else:
        flat_mean = None

    flat_x = np.asarray(x).flatten()

    if _support_singular:
        return multivariate_normal.logpdf(flat_x, flat_mean, cov, allow_singular)
    return multivariate_normal.logpdf(flat_x, flat_mean, cov)
