import numpy as np
import matplotlib.pyplot as plt

LINEWIDTH = 0.5
COLOR_AWAKE = "#d1c580"
COLOR_ASLEEP = "#264794"

R_MIN = 0.5
R_MAX = 1.0

NUM_SEGMENTS = 365
NUM_SAMPLES = 100

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

for idx in range(NUM_SEGMENTS):
    theta_lims = np.random.uniform(0, 2 * np.pi, (2,))
    theta = np.linspace(min(theta_lims), max(theta_lims), NUM_SAMPLES)

    r = [idx / NUM_SEGMENTS * (R_MAX - R_MIN) + R_MIN,] * len(theta)

    test = plt.polar(theta, r, lw=LINEWIDTH, color=COLOR_ASLEEP)

ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_rticks([])
ax.set_xticks([])
ax.tick_params('x', pad=2)
ax.grid(False)
ax.set_axis_off()

plt.show()
