import pandas as pd
import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
from matplotlib.widgets import Button, Slider
import os
import sys

# --- CONFIG ---

MONSTER_TYPES = ["Angler", "Blitz", "Frogger", "Pinkie", "Chainsmoker", "Pande", "Mirage", "A60"]
ANGLER_GROUP  = ["Angler", "Blitz", "Frogger", "Pinkie", "Chainsmoker"]
SOLO_TYPES    = ["Pande", "Mirage", "A60"]

PLOT_ROWS = ["GENERAL", "ANGLER GROUP", "PANDE", "MIRAGE", "A60"]
PLOT_COLORS = {
    "GENERAL":      "green",
    "ANGLER GROUP": "blue",
    "PANDE":        "cyan",
    "MIRAGE":       "magenta",
    "A60":          "gray",
}

# --- FILE LOADING ---

def read_event_data_from_txt(filename="events.txt"):
    try:
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        full_path = os.path.join(script_dir, filename)
        df_file = pd.read_csv(full_path, delimiter=' ', header=None)
        if df_file.shape[1] == 2:
            df_file.columns = ["TIME", "DOOR"]
            df_file["MONSTER_TYPE"] = "Unknown"
        else:
            df_file.columns = ["TIME", "DOOR", "MONSTER_TYPE"]
        return df_file
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# --- SESSION / DT ---

def split_sessions(df):
    df_orig = df.reset_index(drop=True).copy()
    session_id = (df_orig["TIME"].diff().fillna(1) < 0).cumsum()
    df_orig["session"] = session_id
    return df_orig

def compute_dt_angler(df):
    df_s = split_sessions(df)
    all_dts = []
    for _, session in df_s.groupby("session"):
        sub = session[session["MONSTER_TYPE"].isin(ANGLER_GROUP)].copy()
        sub["dt"] = sub["TIME"].diff()
        sub = sub.dropna(subset=["dt"])
        all_dts.extend(sub["dt"].values)
    return np.array(all_dts)

def compute_dt_since_any(df, group):
    df_s = split_sessions(df)
    all_dts = []
    for _, session in df_s.groupby("session"):
        session = session.copy()
        session["dt"] = session["TIME"].diff()
        sub = session[session["MONSTER_TYPE"].isin(group)].dropna(subset=["dt"])
        all_dts.extend(sub["dt"].values)
    return np.array(all_dts)

# --- INITIAL DATA ---
df = read_event_data_from_txt("events.txt")
if df is None:
    df = pd.DataFrame(columns=["TIME", "DOOR", "MONSTER_TYPE"])

# --- PLOT SETUP ---
fig, axes = plt.subplots(5, 2, figsize=(16, 13))
fig.canvas.manager.set_window_title("Pandepande DA")
plt.subplots_adjust(bottom=0.2, top=0.93, hspace=0.6)

lines = {}
for i, label in enumerate(PLOT_ROWS):
    color = PLOT_COLORS[label]
    pdf_line, = axes[i][0].plot([], [], color=color)
    cdf_line, = axes[i][1].plot([], [], color=color)
    lines[label] = (pdf_line, cdf_line)
    axes[i][0].set_ylabel(label, fontsize=8)
    axes[i][0].grid(True)
    axes[i][1].grid(True)

axes[0][0].set_title("PDF — Time Between Events")
axes[0][1].set_title("CDF — P(next event within t seconds)")
axes[4][0].set_xlabel("Seconds since last event")
axes[4][1].set_xlabel("Seconds since last event")

# --- BUTTON & SLIDER ---
ax_btn_file  = plt.axes([0.42, 0.10, 0.15, 0.04])
ax_slider_bw = plt.axes([0.15, 0.955, 0.70, 0.025])
button_file  = Button(ax_btn_file, 'Load From File', color='lightgreen', hovercolor='green')
slider_bw    = Slider(ax_slider_bw, 'Smoothing (bw)', 0.005, 1.0, valinit=0.04, valstep=0.005)

# --- UPDATE ---

def get_group_dts(df):
    return {
        "GENERAL":      compute_dt_since_any(df, MONSTER_TYPES),
        "ANGLER GROUP": compute_dt_angler(df),
        "PANDE":        compute_dt_since_any(df, ["Pande"]),
        "MIRAGE":       compute_dt_since_any(df, ["Mirage"]),
        "A60":          compute_dt_since_any(df, ["A60"]),
    }

def update_bottom_text(group_dts):
    fig.texts = []

    parts = []
    for label, dts in group_dts.items():
        if len(dts) > 0:
            parts.append(f"{label}  min={dts.min():.1f}s  max={dts.max():.1f}s  n={len(dts)}")
    fig.text(0.01, 0.08, "   |   ".join(parts), ha='left', va='bottom', fontsize=8, color='black')

    known = df[~df["MONSTER_TYPE"].isin(["N/A", "Unknown"])]
    angler_total = known[known["MONSTER_TYPE"].isin(ANGLER_GROUP)].shape[0]
    all_total    = known.shape[0]

    angler_parts = []
    if angler_total > 0:
        for m in ANGLER_GROUP:
            n = (known["MONSTER_TYPE"] == m).sum()
            angler_parts.append(f"{m}: {100*n/angler_total:.1f}%")
    angler_str = "ANGLER BREAKDOWN (% of angler spawns):  " + "  |  ".join(angler_parts) if angler_parts else ""

    solo_parts = []
    if all_total > 0:
        for m in SOLO_TYPES:
            n = (known["MONSTER_TYPE"] == m).sum()
            solo_parts.append(f"{m}: {100*n/all_total:.1f}%")
    solo_str = "SOLO SPAWN RATE (% of all spawns):  " + "  |  ".join(solo_parts) if solo_parts else ""

    fig.text(0.01, 0.045, angler_str, ha='left', va='bottom', fontsize=8, color='steelblue')
    fig.text(0.01, 0.015, solo_str,   ha='left', va='bottom', fontsize=8, color='darkgreen')

def plot_data():
    global df
    group_dts = get_group_dts(df)
    for label, (pdf_line, cdf_line) in lines.items():
        dts = group_dts[label]
        if len(dts) > 1:
            kde    = gaussian_kde(dts, bw_method=slider_bw.val)
            t_grid = np.linspace(0, dts.max() + 20, 500)
            pdf    = kde(t_grid)
            cdf    = np.cumsum(pdf) * (t_grid[1] - t_grid[0])
            cdf   /= cdf[-1]
            pdf_line.set_data(t_grid, pdf)
            cdf_line.set_data(t_grid, cdf)
        else:
            pdf_line.set_data([], [])
            cdf_line.set_data([], [])
    for i in range(5):
        for j in range(2):
            axes[i][j].relim()
            axes[i][j].autoscale_view()
    update_bottom_text(group_dts)
    fig.canvas.draw_idle()

# --- BUTTON CALLBACK ---

def load_file(event):
    global df
    df_new = read_event_data_from_txt("events.txt")
    if df_new is not None:
        df = df_new
        plot_data()
        print(df)
    else:
        print("No data found.")

button_file.on_clicked(load_file)
slider_bw.on_changed(lambda val: plot_data())

# --- INITIAL PLOT ---
plot_data()
plt.show()
