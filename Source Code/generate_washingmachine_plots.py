import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

base = Path('CLEAN_REFIT_081116')
selected = {3: 6, 7: 5, 8: 4, 10: 5, 13: 3, 16: 5}


def detect_cycles(series, thresh=100, min_run=10):
    active = series > thresh
    runs = []
    start = None
    prev = False
    for ts, val in active.items():
        if val and not prev:
            start = ts
        elif (not val) and prev and start is not None:
            runs.append((start, ts - pd.Timedelta(minutes=1)))
            start = None
        prev = val
    if start is not None:
        runs.append((start, series.index[-1]))

    cycles = []
    for s, e in runs:
        seg = series.loc[s:e]
        if len(seg) >= min_run and seg.max() > thresh:
            cycles.append(seg)
    return cycles

# Plot 1: representative aggregate + appliance trace
house = 7
app = f'Appliance{selected[house]}'
df = pd.read_csv(base / f'CLEAN_House{house}.csv', parse_dates=['Time'])
df = df[df['Issues'] == 0].sort_values('Time').copy()
minute = df.set_index('Time')[app].resample('1min').mean().fillna(0).astype(float)
active_days = minute[minute > 100].resample('D').count()
sample_day = active_days.idxmax().date() if not active_days.empty else minute.index[0].date()
aggregate = df.set_index('Time')['Aggregate'].resample('1min').mean().fillna(0)
wm = df.set_index('Time')[app].resample('1min').mean().fillna(0)
fig, axes = plt.subplots(2, 1, figsize=(16, 7), sharex=True)
axes[0].plot(aggregate.loc[str(sample_day)].index, aggregate.loc[str(sample_day)].values, color='black', linewidth=1.2)
axes[0].set_title(f'House {house}: representative 24-hour aggregate load')
axes[0].set_ylabel('Aggregate power (W)')
axes[1].plot(wm.loc[str(sample_day)].index, wm.loc[str(sample_day)].values, color='tab:blue', linewidth=1.5)
axes[1].axhline(100, color='red', linestyle='--', linewidth=1.0, label='100 W threshold')
axes[1].set_title(f'House {house}: washing-machine trace on {sample_day}')
axes[1].set_ylabel('Washing-machine power (W)')
axes[1].legend(loc='upper right')
fig.tight_layout()
fig.savefig('washingmachine_24h_trace.png', dpi=200)
plt.close(fig)

# Plot 2: detected cycles
house = 8
app = f'Appliance{selected[house]}'
df = pd.read_csv(base / f'CLEAN_House{house}.csv', parse_dates=['Time'])
df = df[df['Issues'] == 0].sort_values('Time').copy()
minute = df.set_index('Time')[app].resample('1min').mean().fillna(0).astype(float)
cycles = detect_cycles(minute)
fig, axes = plt.subplots(max(1, min(3, len(cycles))), 1, figsize=(14, 6), sharex=True)
if not isinstance(axes, np.ndarray):
    axes = [axes]
for i, c in enumerate(cycles[:3]):
    axes[i].plot(c.index, c.values, color='tab:green', linewidth=2)
    axes[i].axhline(100, color='red', linestyle='--', linewidth=1.0)
    axes[i].set_title(f'House {house} cycle {i+1}: {c.index[0]} to {c.index[-1]}')
    axes[i].set_ylabel('Power (W)')
for ax in axes:
    ax.set_xlabel('Time')
fig.tight_layout()
fig.savefig('washingmachine_cycles.png', dpi=200)
plt.close(fig)

# Plot 3: cross-house cycle duration comparison
cross_rows = []
for house, app_idx in selected.items():
    df = pd.read_csv(base / f'CLEAN_House{house}.csv', parse_dates=['Time'])
    df = df[df['Issues'] == 0].sort_values('Time').copy()
    app = f'Appliance{app_idx}'
    minute = df.set_index('Time')[app].resample('1min').mean().fillna(0).astype(float)
    for c in detect_cycles(minute):
        cross_rows.append({'house': house, 'cycle_duration_min': len(c)})

cross_df = pd.DataFrame(cross_rows)
fig, ax = plt.subplots(figsize=(10, 5))
cross_df.boxplot(column='cycle_duration_min', by='house', ax=ax)
ax.set_title('Detected washing-machine cycle duration by household')
ax.set_xlabel('Household')
ax.set_ylabel('Duration (minutes)')
fig.tight_layout()
fig.savefig('washingmachine_crosshouse_boxplot.png', dpi=200)
plt.close(fig)

print('Created plot files: washingmachine_24h_trace.png, washingmachine_cycles.png, washingmachine_crosshouse_boxplot.png')
