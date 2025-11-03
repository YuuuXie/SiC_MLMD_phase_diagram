import scipy
import numpy as np
import os, glob
import matplotlib.pyplot as plt
#%matplotlib inline,
import matplotlib as mpl
import matplotlib.pylab as pl
import matplotlib.gridspec as gridspec
from matplotlib.markers import MarkerStyle
from scipy.optimize import fsolve
mpl.rcParams['figure.dpi'] = 200
plt.style.use('tableau-colorblind10')
#plt.rcParams['text.usetex'] = True,
plt.rcParams.update({
    'font.size': 13,
    'legend.fontsize': 13,
    'xtick.major.size': 5.0,
    'xtick.minor.size': 3.0,
    'xtick.major.width': 0.3,
    'xtick.minor.width': 0.3,
    'ytick.major.size': 5.0,
    'ytick.minor.size': 3.0,
    'ytick.major.width': 0.3,
    'ytick.minor.width': 0.3,
    'axes.linewidth': 0.3,
    'font.family': 'DejaVu Serif', #'DejaVu Serif', #'times new roman', #'latin modern roman', 'Liberation Serif'
    'mathtext.fontset': 'cm',
    'legend.frameon': False,
})

# T = 3000, 3200, 3400, 3600, 3800, 4000, 4200, 4400
# P = 0, 30, 60, 90, 120
plt.rcParams.update({'font.size': 10})
fig = plt.figure(figsize=(8, 5))

c_b3 = "dodgerblue"
c_b1 = "violet" # magenta lawngreen violet
c_decomp = "tab:orange" #"tab:olive" #"darkkhaki"
c_liquid = "tab:red" #"darkorange"
c_gas = "tab:brown" #"red"

shift_t = lambda x: x
shift_p = lambda x: x

inferred_boundary_T = np.linspace(0, 3000, 100)
inferred_boundary_P = np.zeros_like(inferred_boundary_T)
inferred_boundary_T = np.concatenate((inferred_boundary_T, np.array([4100, 4200])))
inferred_boundary_P = np.concatenate((inferred_boundary_P, np.array([3, 8])))
P_regress_gas = np.polyfit(inferred_boundary_T, inferred_boundary_P, 4)
T_range = np.linspace(0, 5000, 100)
P_range = np.polyval(P_regress_gas, T_range)
plt.plot(shift_t(T_range), shift_p(P_range), "--", color="black")

# Regression for phase boundary curve between B1 and other phases 
inferred_boundary_T = np.array([0, 300, 1000, 2000, 3000, 4000, 4415, 4701])
inferred_boundary_P = np.array([80, 80, 80, 80, 80, 80, 85, 100])
P_regress_b1 = scipy.interpolate.CubicSpline(inferred_boundary_T, inferred_boundary_P)
T_range_b1 = np.linspace(0, 3400, 100)
P_range_b1 = P_regress_b1(T_range_b1)
plt.plot(shift_t(T_range_b1), shift_p(P_range_b1), "-", color="black")
T_range_b1 = np.linspace(3200, 4200, 100)
P_range_b1 = P_regress_b1(T_range_b1)
plt.plot(shift_t(T_range_b1), shift_p(P_range_b1), "--", color="black")
T_range_b1 = np.linspace(4200, 5000, 100)
P_range_b1 = P_regress_b1(T_range_b1)
plt.plot(shift_t(T_range_b1), shift_p(P_range_b1), "-", color="black")
# inquire the temperature of the target pressure point
# target_P = 100
# print("At pressure", target_P, f"the temperature is {T_range_b1[np.argmin(np.abs(P_range_b1 - target_P))]:.0f}K on B1 boundary")

# Regression for phase boundary curve between B3 and other phases
inferred_boundary_T = np.array([2974, 3244, 3598, 3652, 3599, 3537, 3442])
inferred_boundary_P = np.array([10, 20, 30, 45, 60, 70, 80])
T_regress_b3 = np.polyfit(inferred_boundary_P, inferred_boundary_T, 2)
P_range_b3 = np.linspace(-2, 80, 100)
T_range_b3 = np.polyval(T_regress_b3, P_range_b3)
plt.plot(shift_t(T_range_b3), shift_p(P_range_b3), "-", color="black")

# Regression for phase boundary curve between liquid and other phases
inferred_boundary_T = np.array([4164, 3987, 3950, 3775]) # 4500
inferred_boundary_P = np.array([30, 45, 60, 70]) # np.polyval(P_regress_gas, 4500),
P_regress_liquid = np.polyfit(inferred_boundary_T, inferred_boundary_P, 2)

def find_liquid_b1_intersection():
    def equation(T):
        return np.polyval(P_regress_liquid, T) - P_regress_b1(T)
    # Initial guess around 3600K where they might intersect
    T_intersection = fsolve(equation, 3600)[0]
    P_intersection = np.polyval(P_regress_liquid, T_intersection)
    return T_intersection, P_intersection

def find_liquid_gas_intersection():
    def equation(T):
        return np.polyval(P_regress_liquid, T) - np.polyval(P_regress_gas, T)
    # Initial guess around 4500K where they might intersect
    T_intersection = fsolve(equation, 4500)[0]
    P_intersection = np.polyval(P_regress_liquid, T_intersection)
    return T_intersection, P_intersection

T_liquid_b1, P_liquid_b1 = find_liquid_b1_intersection()
T_liquid_gas, P_liquid_gas = find_liquid_gas_intersection()
T_range_liquid = np.linspace(T_liquid_b1, T_liquid_gas, 100)
P_range_liquid = np.polyval(P_regress_liquid, T_range_liquid)
plt.plot(shift_t(T_range_liquid), shift_p(P_range_liquid), "-", color="black")

# Annotation
plt.annotate(text="B3 (Zinc blende)", xy=(shift_t(500), shift_p(30)), color=c_b3, weight="bold")
plt.annotate(text="B1 (Rock salt)", xy=(shift_t(1000), shift_p(100)), color=c_b1, weight="bold")
plt.annotate(text="Decomposed\nSi + C", xy=(shift_t(3730), shift_p(12)), color="chocolate", weight="bold", ha='center')
plt.annotate(text="Liquid", xy=(shift_t(4400), shift_p(50)), color=c_liquid, weight="bold")
plt.annotate(text="Gas", xy=(shift_t(4500), shift_p(1)), color=c_gas, weight="bold")

# Fill color between phases
# Fill B1 phase
y_lim = [-1e-9, 122]
T_fill = np.linspace(0, 5000, 100)
P_fill_b1 = P_regress_b1(T_fill)
plt.fill_between(shift_t(T_fill), shift_p(P_fill_b1), y_lim[1], color=c_b1, alpha=0.2)

# Fill B3 phase
T_fill_bottom = np.linspace(0, T_range_b3[0], 100)
T_fill_top = np.linspace(T_range_b3[-1], 0, 100)
T_bound = np.concatenate([T_fill_bottom, T_range_b3, T_fill_top])
P_bound = np.concatenate([np.full_like(T_fill_bottom, -5), P_range_b3, P_regress_b1(T_fill_top)])
plt.fill(shift_t(T_bound), shift_p(P_bound), color=c_b3, alpha=0.2)

# Fill liquid phase
T_fill = np.linspace(T_liquid_b1, 5000, 100)
P_fill_liquid = np.polyval(P_regress_liquid, T_fill)
P_fill_gas = np.polyval(P_regress_gas, T_fill)
P_bottom = np.max(np.array([P_fill_liquid, P_fill_gas]), axis=0)
P_top = P_regress_b1(T_fill)
plt.fill_between(shift_t(T_fill), shift_p(P_bottom), shift_p(P_top), color=c_liquid, alpha=0.2)

# Fill for decomposed phase
T_fill_left = T_range_b3
P_left = P_range_b3
T_fill_top = np.linspace(T_fill_left[-1], T_liquid_gas, 100)
P_top = np.min(np.array([P_regress_b1(T_fill_top), np.polyval(P_regress_liquid, T_fill_top)]), axis=0)
T_fill_bottom = np.linspace(T_liquid_gas, T_fill_left[0], 100)
P_bottom = np.polyval(P_regress_gas, T_fill_bottom)
plt.fill(shift_t(np.concatenate([T_fill_left, T_fill_top, T_fill_bottom])), 
         shift_p(np.concatenate([P_left, P_top, P_bottom])), color=c_decomp, alpha=0.3)

# Fill color for gas phase
T_fill = np.linspace(0, 5000, 100)
P_fill_b1 = P_regress_b1(T_fill)
P_fill_gas = np.polyval(P_regress_gas, T_fill)
plt.fill_between(shift_t(T_fill), y_lim[0], shift_p(P_fill_gas), color=c_gas, alpha=0.4)

# B3 <--> Si + C
# Add 20, 45, 70, 80 data
LT_bound = np.array([(2974, 10), (3244, 20), (3598, 30), (3652, 45), (3599, 60), (3537, 70), (3442, 80)])
plt.scatter(shift_t(LT_bound[:, 0]), shift_p(LT_bound[:, 1]), marker=MarkerStyle("s", fillstyle="left"), s=100, color=c_b3) 
plt.scatter(shift_t(LT_bound[:, 0]), shift_p(LT_bound[:, 1]), marker=MarkerStyle("s", fillstyle="right"), s=100, color=c_decomp) 

# Si + C <--> liquid
HT_bound = np.array([(4164, 30), (3987, 45), (3950, 60), (3775, 70)])
plt.scatter(shift_t(HT_bound[:, 0]), shift_p(HT_bound[:, 1]), marker=MarkerStyle("s", fillstyle="left"), s=100, color=c_decomp) #, edgewidth=0)
plt.scatter(shift_t(HT_bound[:, 0]), shift_p(HT_bound[:, 1]), marker=MarkerStyle("s", fillstyle="right"), s=100, color=c_liquid) #, edgewidth=0)

# B1 <--> liquid
B1_liquid_t = np.array([4415, 4517, 4701])
B1_liquid_p = np.array([85, 90, 100])
plt.scatter(shift_t(B1_liquid_t), shift_p(B1_liquid_p), marker=MarkerStyle("s", fillstyle="top"), s=100, color=c_b1)
plt.scatter(shift_t(B1_liquid_t), shift_p(B1_liquid_p), marker=MarkerStyle("s", fillstyle="bottom"), s=100, color=c_liquid)

# B3 <--> B1
zb_rs_t = np.array([300, 1000, 2000, 3000])
zb_rs_p = np.array([80, 77.5, 86, 80]) 
plt.scatter(shift_t(zb_rs_t), shift_p(zb_rs_p), marker=MarkerStyle("s", fillstyle="top"), s=100, color=c_b1) #, edgewidth=0)
plt.scatter(shift_t(zb_rs_t), shift_p(zb_rs_p), marker=MarkerStyle("s", fillstyle="bottom"), s=100, color=c_b3) #, edgewidth=0)

# Gas
gas_t = np.array([4000, 4100, 4200])
gas_p = np.array([0, 1, 5]) 
plt.scatter(shift_t(gas_t), shift_p(gas_p), marker="s", s=100, color=c_gas)

# Experiment
def plot_exp_half(name, marker, color):
    data = np.loadtxt(f"Experiment/{name}.csv", delimiter=",")
    if len(data.shape) == 1:
        x = shift_t(data[0])
        y = shift_p(data[1]) 
        n_points = 1
    else:
        x = shift_t(data[:, 0])
        y = shift_p(data[:, 1])
        n_points = len(data)

    # Scale the marker size inversely to the number of points
    base_size = 55  # Base marker size
    min_size = 25   # Minimum marker size
    size = max(base_size / np.sqrt(n_points), min_size)

    base_alpha = 1.0  # Base transparency
    min_alpha = 0.6   # Minimum transparency 
    alpha = max(base_alpha / np.sqrt(n_points), min_alpha)

    if name.split('/')[-1].endswith('B1') or name.split('/')[-1].endswith('B3'):
        myplt = plt.scatter(x, y, 
                          marker=marker, 
                          s=size, 
                          color=color,
                          alpha=alpha,
                          linewidth=0,
                          zorder=15,
                          clip_on=False)
    else:
        myplt = plt.scatter(x, y, 
                          marker=marker, 
                          s=size, 
                          color=color,
                          alpha=alpha,
                          edgecolor='black',
                          linewidth=0.2,
                          zorder=15,
                          clip_on=False)
    return myplt

def plot_exp(name, markershape, colors, fillstyle="lr"):
    if fillstyle == "lr":
        f1, f2 = "left", "right"
    elif fillstyle == "tb":
        f1, f2 = "top", "bottom" 
    m1 = plot_exp_half(name, MarkerStyle(markershape, fillstyle=f1), colors[0])
    m2 = plot_exp_half(name, MarkerStyle(markershape, fillstyle=f2), colors[1])
    handle_list.append((m1, m2))
    label = name.split("/")[-1].replace("_", " ")
    label_list.append(label)

handle_list = []
label_list = []

plot_exp("Congruent/Hall", "H", [c_b3, c_liquid])
plot_exp("Congruent/Sokolov", "h", [c_b3, c_liquid])

plot_exp("Decomposition/Bhaumik1996", "d", [c_b3, c_decomp])
plot_exp("Decomposition/Bhaumik2000", "^", [c_b3, c_decomp])
plot_exp("Decomposition/Dolloff", "P", [c_b3, c_decomp])
plot_exp("Decomposition/Ekimov", "X", [c_b3, c_decomp])
plot_exp("Decomposition/Togaya", ">", [c_b3, c_decomp])
plot_exp("Decomposition/Daviau2017Decomposition", "o", [c_b3, c_decomp])

plot_exp("B3_to_B1/Daviau2017Zinc_B1", "^", [c_b1, c_b1])
plot_exp("B3_to_B1/Daviau2017Zinc_B3", "^", [c_b3, c_b3])
plot_exp("B3_to_B1/Kidokoro_B1", "X", [c_b1, c_b1])
plot_exp("B3_to_B1/Kidokoro_B3", "X", [c_b3, c_b3])

plot_exp("B3_to_B1/Miozzi", "d", [c_b1, c_b3], "tb")
plot_exp("B3_to_B1/Sekine", "o", [c_b1, c_b3], "tb")
plot_exp("B3_to_B1/Tracy", "P", [c_b1, c_b3], "tb")
plot_exp("B3_to_B1/Yoshida", "v", [c_b1, c_b3], "tb")

plt.legend(handle_list, label_list, numpoints=1, bbox_to_anchor=(1.0, 1.0), fontsize=8)

# plt.xticks([0, 5, 10, 15, 20, 25], labels=[0, 1000, 2000, 3000, 4000, 5000])
plt.xlabel("Temperature (K)")
# plt.yticks([0, 1, 2, 3, 4], labels=[120, 90, 60, 30, 0])
plt.xlim([0, 5000])
plt.ylim(y_lim)
plt.ylabel("Pressure (GPa)")
plt.tight_layout()
plt.savefig("phase_diagram/SiC_phase_diagram.png", dpi=500)