"""Bass diffusion model functions used in this homework.

    F(t) = (1 - e^{-(p+q)t}) / (1 + (q/p) e^{-(p+q)t})        cumulative share
    adopters in period k = M * (F(k) - F(k-1))                  discrete version
    peak time t* = ln(q/p) / (p + q)

Here I fit the model on adopters per period (the discrete version), so the
fitted yearly numbers always add up to the fitted cumulative total.
"""
import numpy as np
from scipy.optimize import curve_fit


def F(t, p, q):
    t = np.asarray(t, dtype=float)
    e = np.exp(-(p + q) * t)
    return (1 - e) / (1 + (q / p) * e)


def per_period(k, M, p, q):
    k = np.asarray(k, dtype=float)
    return M * (F(k, p, q) - F(k - 1, p, q))


def t_peak(p, q):
    return np.log(q / p) / (p + q)


def r_squared(y, yhat):
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    return 1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def fit_nls(y, start=(None, 0.01, 0.5)):
    """Non-linear least squares for M, p, q (same idea as nls() in R)."""
    y = np.asarray(y, dtype=float)
    k = np.arange(1, len(y) + 1)
    M0 = start[0] or 1.5 * y.sum()
    est, cov = curve_fit(per_period, k, y, p0=[M0, start[1], start[2]],
                         bounds=([y.sum(), 1e-7, 1e-3], [50 * y.sum(), 1.0, 3.0]),
                         maxfev=200000)
    return est, np.sqrt(np.diag(cov))


def fit_ols(y):
    """Bass (1969) regression: a(t) = b0 + b1 A(t-1) + b2 A(t-1)^2."""
    y = np.asarray(y, dtype=float)
    A = np.concatenate([[0.0], np.cumsum(y)[:-1]])
    X = np.column_stack([np.ones_like(A), A, A ** 2])
    b0, b1, b2 = np.linalg.lstsq(X, y, rcond=None)[0]
    roots = [r.real for r in np.roots([b2, b1, b0]) if abs(r.imag) < 1e-9 and r.real > 0]
    M = max(roots)
    p = b0 / M
    return np.array([M, p, p + b1])


def fit_p_and_M(y, q):
    """Keep q fixed (from the look-alike) and fit only M and p to early data."""
    y = np.asarray(y, dtype=float)
    k = np.arange(1, len(y) + 1)
    f = lambda kk, M, p: per_period(kk, M, p, q)
    est, cov = curve_fit(f, k, y, p0=[2 * y.sum(), 0.05],
                         bounds=([y.sum(), 1e-5], [100 * y.sum(), 0.99]), maxfev=200000)
    return est, np.sqrt(np.diag(cov))


def p_matching_first_period(first, M, q):
    """p such that M * F(1) equals the first-period adopters."""
    from scipy.optimize import brentq
    return brentq(lambda p: M * F(1, p, q) - first, 1e-6, 0.999)
