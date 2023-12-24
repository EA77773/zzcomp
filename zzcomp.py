"""
Copyright (c) 2023 Egidijus Andriuskevicius

Licensed under the MIT license. See LICENSE file in the project root for full
license information.

Author: Egidijus Andriuskevicius
        (https://github.com/EA77773)

Implementation of ZigZag time series compression, which includes functions for
compression, recompression and generating ZigZag indicator from the compressed
time series.

"""

# Constants/globals
# Indexes of items within tulip stored in skeleton
S_DP = 0  # Datapoint
S_DIFF = 1  # Difference value

# Indexes of items within tulip stored in list of importance levels for
# datapoint pairs
L_DP1 = 0  # First datapoint of the pair
L_DP2 = 1  # Second datapoint of the pair
L_I = 2  # Numeric importance for the datapoint pair

# Indexes of items within tulip stored in ZigZag indicator
Z_DP = 0  # Datapoint
Z_IL = 1  # Numeric importance for the datapoint


def compress(iT, diff, S=None, L=None):
    """
    Compress time series iter(T) using difference function diff.

    Parameters
    ----------
    iT : iterator
        Iterator for time series T.
        If your time series is stored as a Python list T, pass iter(T)
        to this parameter
    diff : function diff(dp1, dp2) -> d
        A two argument function for two datapoints dp1 and dp2 from
        the time series. It must returns a number representing a difference
        value between the two points.
    S : list [(dp, d), ...], optional
        Skeleton. On the first call for a new time series it should be empty or
        None.
        On the subsequent calls, to continue compressing the same time series
        pass skeleton returned from the previous call to this function.
        dp: S[i][S_DP] i-th datapoint in skeleton
        d: S[i][S_DIFF] difference value returned from
        diff(S[i-1][S_DP], S[i][S_DP])
        S[0][S_DIFF] is always 0.

    L : list like object [(dp1, dp2, il), ...], optional
        Stores numeric importance (il) for datapoint pairs (dp1 and dp2).
        dp1: L[i][L_DP1] first datapoint in the pair
        dp2: L[i][L_DP2] second datapoint in the pair
        il:  L[i][L_I] numeric importance calculated as
        abs(diff(L[i][L_DP1], L[i][L_DP2]))
        It may be a custom list that implements its append method. It's
        the only method called in this function for this object.
        If not provided, a new python list [] will be created and returned
        Only datapoints with importance value greater than zero are stored in
        this list.

    Returns
    -------
    S : list
        See parameter S.
    L : list
        See parameter L.

    See Also
    --------
    recompress

    Notes
    -----
    This function does NOT rely on datapoint's internal structure therefore
    consumer applications are free to define their own. It operates purely on
    difference values returned by the provided diff function.

    Datapoints in this list may not be appended in the same order as
    datapoints received from the iterator.

    Examples
    --------
    >>> import zzcomp as zzc
    >>> T = [(i+1, t) for i, t in enumerate([
    ... 1, 4, 2, 4, 3, 7, 4, 7, 7, 9, 8, 9, 4, 4, 8, 7, 1, 2, 2
    ... ])]
    >>> S, L = zzc.compress(iter(T), lambda t1, t2: t2[1]-t1[0])
    >>> S
    [((1, 1), 0), ((10, 9), 8), ((19, 2), -8)]
    >>> L
    [((4, 4), (5, 3), 1), ((6, 7), (7, 4), 2)]

    """
    S, L = S or [], L or []
    try:
        # Initialise skeleton with at least two datapoints that are not equal
        if len(S) == 0:
            S.append((next(iT), 0))
        while len(S) == 1:
            t = next(iT)
            d = diff(S[0][S_DP], t)
            if d != 0:
                S.append((t, d))
    except StopIteration:
        return S, L

    for t in iT:
        d = diff(S[-1][S_DP], t)
        if d != 0:
            if (S[-1][S_DIFF] < 0) == (d < 0):
                S[-1] = (t, diff(S[-2][S_DP], t))
            else:
                S.append((t, d))
            # Identify and reduce Z formations
            while len(S) >= 4:
                il = abs(S[-2][S_DIFF])
                if abs(S[-3][S_DIFF]) >= il <= abs(S[-1][S_DIFF]):
                    L.append((S[-3][S_DP], S[-2][S_DP], il))
                    del S[-3:-1]
                    S[-1] = (S[-1][S_DP], diff(S[-2][S_DP], S[-1][S_DP]))
                else:
                    break

    return S, L


def recompress(diff, S, L):
    """
    Compress already compressed time series using a different difference
    function.

    Parameters
    ----------
    diff : function diff(dp1, dp2) -> d
        Refer to compress function.
    S : list [(dp, d), ...], optional
        Refer to compress function.

    L : list-like object [(dp1, dp2, il), ...], optional
        Refer to compress function.

    Returns
    -------
    S : list
        See parameter S.
    L : list
        See parameter L.

    See Also
    --------
    compress

    Notes
    -----
    None.

    Examples
    --------
    Continued from the example for compress function

    >>> S, L = zzc.recompress(
    ...     lambda t1, t2: 200*(t2[1] - t1[0])/(t1[0] + t2[1]),
    ...     S, L)
    >>> print(S)
    [((1, 1), 0), ((10, 9), 160.0), ((19, 2), -133.33333333333334)]
    >>> print(L)
    [((4, 4), (5, 3), 28.571428571428573), ((6, 7), (7, 4), 40.0)]

    """
    for i, e in enumerate(L):
        il = abs(diff(e[L_DP1], e[L_DP2]))
        L[i] = (e[L_DP1], e[L_DP2], il)
    if S and len(S) > 1:
        for i in range(1, len(S)):
            S[i] = (S[i][S_DP], diff(S[i-1][S_DP], S[i][S_DP]))
    return S, L


def select_zzi_from_skeleton(S, deviation):
    """
    Utility function to select datapoints from skeleton and calculate their
    importance for ZigZag indicator.

    Parameters
    ----------
    S : list [(dp, d), ...], optional
        Refer to compress function.

    deviation : Positive real number.

    Returns
    -------
    Z : list

    See Also
    --------
    select_zigzag_indicator

    Notes
    -----
    Called from select_zigzag_indicator.

    Examples
    --------
    None.

    """
    # Identify all segments in S longer than min_il
    # The length of segmets in S is always either
    #   * only strictly increasing, or
    #   * only strictly decreasing, or
    #   * strictly increasing and then strictly decreasing
    Z = []
    n = len(S)
    if n < 2:
        return Z

    # abs(S[i][DIFF]) is segment length between the two endpoints
    #   S[i-1][DPOINT] and S[i][DPOINT]
    # S[0][DIFF] is always 0
    d1 = abs(S[1][S_DIFF])
    i = 1
    # Find first segment with length >= deviation
    while d1 < deviation:
        d0 = d1
        i += 1
        if i == n:
            return Z
        d1 = abs(S[i][S_DIFF])
        if d0 > d1:
            # Decreasing already
            return Z
    # i is pointing to the first segment in S with length >= min_il
    Z.append((S[i-1][S_DP], d1))
    i += 1
    if i == n:
        Z.append((S[i-1][S_DP], d1))
    else:
        d0 = d1
        d1 = abs(S[i][S_DIFF])
        while d0 < d1:
            Z.append((S[i-1][S_DP], d1))
            i += 1
            if i == n:
                Z.append((S[i-1][S_DP], d1))
                break
            d0 = d1
            d1 = abs(S[i][S_DIFF])
        else:
            Z.append((S[i-1][S_DP], d0))
            while d1 >= deviation:
                Z.append((S[i][S_DP], d1))
                i += 1
                if i == n:
                    break
                d1 = abs(S[i][S_DIFF])

    return Z


def select_zigzag_indicator(S, L, deviation, index_key):
    """
    Selects ZigZag indicator from compressed time series.

    Parameters
    ----------
    S : list [(dp, d), ...]
        Skeleton returned from the [re]compress function.
        Refer to compress function.

    L : list-like object [(dp1, dp2, il), ...]
        Importances returned from the [re]compress function.
        Refer to compress function.

    deviation : Positive real number.
        The meaning is specific to the difference function used in compression,
        such as price change in percentage or price change in $.

    index_key : function.
        Accessor function that returns unique and sortable index value for
        datapoints in time series. The index values define the order in which
        datapoints will be sorted and returned.
        For a datapoint dp=(5, 200) where its sequence number is 5 and
        value 200, index_key may be defined as lambda dp: dp[0],
        which retuns 5 for dp.

    Returns
    -------
    Z : list [(dp, il), ...]
        dp: Z[i][Z_DP] i-th datapoint in ZigZag indicator
        il: Z[i][Z_IL] numeric importance for the datapoint

    See Also
    --------
    compress

    Notes
    -----
    If L is a custom list, this function may require modifications to achieve
    optimal filtering.

    If you need to select multiple ZigZag indicators with deviation values
    d0 < d1 < d2 < ... then you may call this function once with d0 and then
    filter on the previously returned indicator for the subsequent di values:
    >>> Z0 = zzc.select_zigzag_indicator(S, L, d0, index_func)
    >>> Z1 = [z for z in Z0 if z[zzc.Z_IL] >= d1]
    >>> Z2 = [z for z in Z1 if z[zzc.Z_IL] >= d2]
    ...

    Examples
    --------
    Continued from the example for recompress function

    >>> zzc.select_zigzag_indicator(S, L, 30, lambda dp: dp[0])
    [((1, 1), 160.0), ((6, 7), 40.0), ((7, 4), 40.0), ((10, 9), 160.0),
     ((19, 2), 133.33333333333334)]

    """
    Z = select_zzi_from_skeleton(S, deviation)
    if len(Z) == 0:
        # Skeleton always contains the max value of importance
        # If deviation is greater than any abs(s[i][S_DIFF]) then
        #   L contains no elemets such that il >= deviation
        return Z
    Z += [(dp, el[L_I])
          for el in L if el[L_I] >= deviation
              for dp in (el[L_DP1], el[L_DP2])]
    Z.sort(key=lambda z: index_key(z[S_DP]))

    return Z
