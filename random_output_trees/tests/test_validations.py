"""Tests for input validation functions"""

import numpy as np
import scipy.sparse as sp
from nose.tools import assert_raises, assert_true, assert_false, assert_equal
from itertools import product


# from sklearn.utils.estimator_checks import NotAnArray


from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

from random_output_trees._utils import has_fit_parameter
from random_output_trees._utils import check_array


def test_ordering():
    """Check that ordering is enforced correctly by validation utilities.

    We need to check each validation utility, because a 'copy' without
    'order=K' will kill the ordering.
    """
    X = np.ones((10, 5))
    for A in X, X.T:
        for copy in (True, False):
            B = check_array(A, order='C', copy=copy)
            assert_true(B.flags['C_CONTIGUOUS'])
            B = check_array(A, order='F', copy=copy)
            assert_true(B.flags['F_CONTIGUOUS'])
            if copy:
                assert_false(A is B)

    X = sp.csr_matrix(X)
    X.data = X.data[::-1]
    assert_false(X.data.flags['C_CONTIGUOUS'])

    for copy in (True, False):
        Y = check_array(X, accept_sparse='csr', copy=copy, order='C')
        assert_true(Y.data.flags['C_CONTIGUOUS'])


def test_check_array():
    # accept_sparse == None
    # raise error on sparse inputs
    X = [[1, 2], [3, 4]]
    X_csr = sp.csr_matrix(X)
    assert_raises(TypeError, check_array, X_csr)
    # ensure_2d
    X_array = check_array([0, 1, 2])
    assert_equal(X_array.ndim, 2)
    X_array = check_array([0, 1, 2], ensure_2d=False)
    assert_equal(X_array.ndim, 1)
    # don't allow ndim > 3
    X_ndim = np.arange(8).reshape(2, 2, 2)
    assert_raises(ValueError, check_array, X_ndim)
    check_array(X_ndim, allow_nd=True)  # doesn't raise
    # force_all_finite
    X_inf = np.arange(4).reshape(2, 2).astype(np.float)
    X_inf[0, 0] = np.inf
    assert_raises(ValueError, check_array, X_inf)
    check_array(X_inf, force_all_finite=False)  # no raise
    # nan check
    X_nan = np.arange(4).reshape(2, 2).astype(np.float)
    X_nan[0, 0] = np.nan
    assert_raises(ValueError, check_array, X_nan)
    check_array(X_inf, force_all_finite=False)  # no raise

    # dtype and order enforcement.
    X_C = np.arange(4).reshape(2, 2).copy("C")
    X_F = X_C.copy("F")
    X_int = X_C.astype(np.int)
    X_float = X_C.astype(np.float)
    Xs = [X_C, X_F, X_int, X_float]
    dtypes = [np.int32, np.int, np.float, np.float32, None, np.bool, object]
    orders = ['C', 'F', None]
    copys = [True, False]

    for X, dtype, order, copy in product(Xs, dtypes, orders, copys):
        X_checked = check_array(X, dtype=dtype, order=order, copy=copy)
        if dtype is not None:
            assert_equal(X_checked.dtype, dtype)
        else:
            assert_equal(X_checked.dtype, X.dtype)
        if order == 'C':
            assert_true(X_checked.flags['C_CONTIGUOUS'])
            assert_false(X_checked.flags['F_CONTIGUOUS'])
        elif order == 'F':
            assert_true(X_checked.flags['F_CONTIGUOUS'])
            assert_false(X_checked.flags['C_CONTIGUOUS'])
        if copy:
            assert_false(X is X_checked)
        else:
            # doesn't copy if it was already good
            if (X.dtype == X_checked.dtype and
                    X_checked.flags['C_CONTIGUOUS'] == X.flags['C_CONTIGUOUS']
                    and X_checked.flags['F_CONTIGUOUS'] == X.flags['F_CONTIGUOUS']):
                assert_true(X is X_checked)

    # allowed sparse != None
    X_csc = sp.csc_matrix(X_C)
    X_coo = X_csc.tocoo()
    X_dok = X_csc.todok()
    X_int = X_csc.astype(np.int)
    X_float = X_csc.astype(np.float)

    Xs = [X_csc, X_coo, X_dok, X_int, X_float]
    accept_sparses = [['csr', 'coo'], ['coo', 'dok']]
    for X, dtype, accept_sparse, copy in product(Xs, dtypes, accept_sparses,
                                                  copys):
        X_checked = check_array(X, dtype=dtype, accept_sparse=accept_sparse,
                                copy=copy)
        if dtype is not None:
            assert_equal(X_checked.dtype, dtype)
        else:
            assert_equal(X_checked.dtype, X.dtype)
        if X.format in accept_sparse:
            # no change if allowed
            assert_equal(X.format, X_checked.format)
        else:
            # got converted
            assert_equal(X_checked.format, accept_sparse[0])
        if copy:
            assert_false(X is X_checked)
        else:
            # doesn't copy if it was already good
            if (X.dtype == X_checked.dtype and X.format == X_checked.format):
                assert_true(X is X_checked)

    # other input formats
    # convert lists to arrays
    X_dense = check_array([[1, 2], [3, 4]])
    assert_true(isinstance(X_dense, np.ndarray))
    # raise on too deep lists
    assert_raises(ValueError, check_array, X_ndim.tolist())
    check_array(X_ndim.tolist(), allow_nd=True)  # doesn't raise
    # convert weird stuff to arrays
    # X_no_array = NotAnArray(X_dense)
    # result = check_array(X_no_array)
    # assert_true(isinstance(result, np.ndarray))

def test_has_fit_parameter():
    assert_false(has_fit_parameter(KNeighborsClassifier, "sample_weight"))
    assert_true(has_fit_parameter(RandomForestRegressor, "sample_weight"))
    assert_true(has_fit_parameter(SVR, "sample_weight"))
    assert_true(has_fit_parameter(SVR(), "sample_weight"))
