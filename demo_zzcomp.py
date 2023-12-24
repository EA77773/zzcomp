'''
Copyright (c) 2023 Egidijus Andriuskevicius

Licensed under the MIT license. See LICENSE file in the project root for full
license information.

Author: Egidijus Andriuskevicius
        (https://github.com/EA77773)

'''

import numpy as np
import matplotlib.pyplot as plt
import zzcomp as zzc
import time


# For this demo, timeseries is a list of datapoints [(index, value), ...]
DPIDX = 0   # Position of datapoint index in tulip
DPVAL = 1   # Position of datapoint value in tulip
# T[i][DPIDX] - index of i-th datapoint. Any sequential value such as number,
# datestamp, transaction id, etc
# T[i][DPVAL] - value of i-th datapoint. Price, number, etc
# T must be iterable and implement the "next" method called in the main
# compression function
T = []

# Comment out lines to turn off plotting for specific samples
SAMPLES_TO_PLOT = {
    'Sample 1',
    'Sample 2',
    'Sample 3a - Random Walk',
    'Sample 3b - Random Walk, concurrent compression',
    # 'Comment out like this',
    ''
}

fig_cnt = 0


def diff_sub(t1, t2):
    a, b = t1[DPVAL], t2[DPVAL]
    return b - a


def diff_pct2(t1, t2):
    a, b = t1[DPVAL], t2[DPVAL]
    return 200*(b - a)/(a + b)


def diff_pct(t1, t2):
    a, b = t1[DPVAL], t2[DPVAL]
    if a > b:
        return 100.0*(a/b - 1)
    elif a < b:
        return -100.0*(b/a - 1)
    return 0.0


def plot_zigzag(T, S, Z, deviation, title=''):
    global fig_cnt

    fig_cnt += 1
    plt.figure(f'{fig_cnt} ZigZag {title} deviation={deviation}')
    x = [dp[DPIDX] for dp in T]
    y = [dp[DPVAL] for dp in T]
    plt.plot(x, y, label='T', linestyle='dashed')

    x = [s[zzc.S_DP][DPIDX] for s in S]
    y = [s[zzc.S_DP][DPVAL] for s in S]
    plt.plot(x, y, label=f'Skeleton ({len(S)} points)', marker='o',
             linestyle='dotted')

    x = [z[zzc.S_DP][DPIDX] for z in Z]
    y = [z[zzc.S_DP][DPVAL] for z in Z]
    plt.plot(x, y, label=f'Deviation={round(deviation, 2)}')

    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('ZigZag ' + title)
    plt.legend()
    # plt.show()


def plot_zigzag_with_select(T, S, P, deviation, title=''):
    Z = zzc.select_zigzag_indicator(S, P, deviation, lambda t: t[DPIDX])

    plot_zigzag(T, S, Z, deviation, title)


def print_duration_ms(start_time_ns):
    print(f'Duration: {(time.time_ns() - start_time_ns)/1000000} ms')


# =============================================================================
sample = 'Sample 1'
print(f'=== {sample} ===')

T = [(i+1, t) for i, t in enumerate([
    1, 4, 2, 4, 3, 7, 4, 7, 7, 9, 8, 9, 4, 4, 8, 7, 1, 2, 2
    ])]

S, L = zzc.compress(iter(T), diff_sub)

print(f'Skeleton (S) len={len(S)}:\n{S}')
print(f'Importances:\n{L}')

Z = zzc.select_zigzag_indicator(S, L, 0, lambda t: t[DPIDX])
DIL = sorted(set([z[zzc.Z_IL] for z in Z]), reverse=True)
print(f'Distinct Importances:\n{DIL}')

# Select datapoints with importance at median importance
mil_idx = len(DIL) // 2
Z = [e for e in Z if e[zzc.S_DIFF] >= DIL[mil_idx]]

if sample in SAMPLES_TO_PLOT:
    plot_zigzag(T, S, Z, DIL[mil_idx], f'{sample} using subtraction function')

print('Recompressing using percentage function.')
S, L = zzc.recompress(diff_pct, S, L)
print(f'Skeleton (S) len={len(S)}:\n{S}')
print(f'Importances:\n{L}')

Z = zzc.select_zigzag_indicator(S, L, 0, lambda t: t[DPIDX])
DIL = sorted(set([z[zzc.Z_IL] for z in Z]), reverse=True)
print(f'Distinct Importances:\n{DIL}')

# Select datapoints with importance at top 3 levels
Z = [z for z in Z if z[zzc.Z_IL] >= DIL[mil_idx]]

if sample in SAMPLES_TO_PLOT:
    plot_zigzag(T, S, Z, DIL[mil_idx], f'{sample} using percentage function')

# Sample 2 ====================================================================
sample = 'Sample 2'
print(f'=== {sample} ===')

T = [(i+1, t) for i, t in enumerate([
    1, 1, 1, 1.01, 1.07, 1, 1.05, 1.11, 1.2, 0.8, 0.9, 0.95, 0.85,
    0.65, 0.75, 0.3, 0.6, 0.3, 0.6, 0.7, 0.7, 0.6, 0.61, 0.6, 0.25,
    0.25, 0.1, 0.2, 0.19, 0.15, 0.08, 0.1, 0.06, 0.06, 0.06
])]

# Compressing in two batches
split_at = len(T) // 2

S, L = zzc.compress(iter(T[:split_at]), diff_sub)
S, L = zzc.compress(iter(T[split_at:]), diff_sub, S, L)

print(f'Skeleton (S) len={len(S)}:\n{S}')
print(f'Importances:\n{L}')

if sample in SAMPLES_TO_PLOT:
    plot_zigzag_with_select(T, S, L, 0.2, f'{sample} using subtraction function')

print('Recompressing using percentage function.')

# Recompressing in two batches, can be done concurrently
split_at = len(L) // 2
_, L0 = zzc.recompress(diff_pct, None, L[:split_at])
S, L1 = zzc.recompress(diff_pct, S, L[split_at:])
L = L0 + L1

print(f'Skeleton (S) len={len(S)}:\n{S}')
print(f'Importances:\n{L}')

if sample in SAMPLES_TO_PLOT:
    plot_zigzag_with_select(T, S, L, 20, f'{sample} using percentage function')

# Sample 3a ===================================================================
sample = 'Sample 3a - Random Walk'
print(f'=== {sample} ===')

# Generate random walk time series of 500 datapoints
# T = np.random.normal(0.0, scale=0.10, size=500)
T = np.random.normal(0.0, scale=0.02, size=500)
# print(f'min={min(T)} max={max(T)}')
seed = 10.0
T[0] = seed + max(-0.999, T[0]) * seed
# T[0] = seed + T[0]
for i in range(1, len(T)):
    T[i] = T[i-1] + max(-0.999, T[i]) * T[i-1]
    # T[i] = T[i-1] + T[i]
T = [(i+1, round(t, 2)) for i, t in enumerate(T)]

start_time = time.time_ns()
S, L = zzc.compress(iter(T), diff_sub)
print_duration_ms(start_time)
print(f'Skeleton (S) len={len(S)}:\n{S}')

#
dev1 = max([abs(s[zzc.S_DIFF]) for s in S]) / 11
dev2 = 2 * dev1

Z = zzc.select_zigzag_indicator(S, L, dev1, lambda t: t[DPIDX])
if sample in SAMPLES_TO_PLOT:
    plot_zigzag(T, S, Z, dev1, f'{sample} using subtraction function')
# Filter values from the previous select with lower deviation
Z = [z for z in Z if z[zzc.Z_IL] >= dev2]
if sample in SAMPLES_TO_PLOT:
    plot_zigzag(T, S, Z, dev2, f'{sample} using subtraction function')

print('Recompressing using percentage function.')

start_time = time.time_ns()
S, L = zzc.recompress(diff_pct, S, L)
print_duration_ms(start_time)

print(f'Skeleton (S) len={len(S)}:\n{S}')

# il1 = max([abs(s[zzc.S_DIFF]) for s in S]) / 11
dev1 = 5
dev2 = 2 * dev1

Z = zzc.select_zigzag_indicator(S, L, dev1, lambda t: t[DPIDX])
if sample in SAMPLES_TO_PLOT:
    plot_zigzag(T, S, Z, dev1, f'{sample} using percentage function')
# Filter values from the previous select with lower deviation
Z = [z for z in Z if z[zzc.Z_IL] >= dev2]
if sample in SAMPLES_TO_PLOT:
    plot_zigzag(T, S, Z, dev2, f'{sample} using percentage function')

# Sample 3b ===================================================================
sample = 'Sample 3b - Random Walk, concurrent compression'
print(f'=== {sample} ===')

# Reuse the same timeseries from the previous sample
# Compressing in three batches concurrently
b1 = len(T) // 3
b2 = 2 * b1

start_time = time.time_ns()

# Thread 1 (imaginary)
S1, L1 = zzc.compress(iter(T[:b1]), diff_pct)
# Thread 2 (imaginary)
S2, L2 = zzc.compress(iter(T[b1:b2]), diff_pct)
# Thread 3 (imaginary)
S3, L3 = zzc.compress(iter(T[b2:]), diff_pct)

# Combine importances for pairs
L = L1 + L2 + L3
# To combine skeletons we need to pick one and then
#  compress subsequent ones as time series.
# Depending on which completes first, valid option are:
#  S1 with S2 and then with S3
#  S2 with S3 and then S1 with the combined S2 and S3
# Combining S1 with S3 is not valid, we can only combine
# adjacent skeletons
T1 = [s[zzc.S_DP] for s in S2] + [s[zzc.S_DP] for s in S3]
S, L = zzc.compress(iter(T1), diff_pct, S1, L)
print_duration_ms(start_time)
print(f'Skeleton (S) len={len(S)}:\n{S}')

if sample in SAMPLES_TO_PLOT:
    dev1 = max([abs(s[zzc.S_DIFF]) for s in S]) / 7
    dev2 = 2 * dev1

    Z = zzc.select_zigzag_indicator(S, L, dev1, lambda t: t[DPIDX])
    plot_zigzag(T, S, Z, dev1, f'{sample} using percentage function')
    # Filter values from the previous select with lower deviation
    Z = [z for z in Z if z[zzc.Z_IL] >= dev2]
    plot_zigzag(T, S, Z, dev2, f'{sample} using percentage function')

"""
"""

if fig_cnt > 0:
    plt.show()
