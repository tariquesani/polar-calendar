import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from matplotlib.font_manager import FontProperties

# City Information
city_name = "Nagpur"
city_coordinates = "21.1458° N, 79.0882° E"

with open("./results/nagpur_data.json", "r") as f:
    data = json.load(f)

# Load data
sunrise_times = data["sunrise"]
days_in_month = data["days_in_month"]
civil_twilight = data["civil"]
nautical_twilight = data["nautical"]
astronomical_twilight = data["astro"]
civil_twilight_dawn, civil_twilight_dusk = zip(*civil_twilight)
nautical_twilight_dawn, nautical_twilight_dusk = zip(*nautical_twilight)
astronomical_twilight_dawn, astronomical_twilight_dusk = zip(
    *astronomical_twilight)

# Plot Configuration
fig, ax = plt.subplots(figsize=(24, 24), subplot_kw=dict(polar=True), dpi=300)
fig.patch.set_facecolor('#faf0e6')

# Set the direction of the polar plot to be counter-clockwise (default is clockwise)
# and rotate the start of the plot by 90 degrees so that the right side of the plot
# corresponds to 12 AM/PM
ax.set_theta_direction(-1)
ax.set_theta_offset(np.pi / 2)

 
# Calculate the number of days in the year
num_days = len(sunrise_times)

# Convert the sunrise times from hours to a fraction of the day
# This will be used as the radial coordinate in the polar plot
sunrise_r = np.array(sunrise_times + [sunrise_times[0]]) / 24

# Convert the civil, nautical, and astronomical twilight times from hours to a fraction of the day
# These will be used as the radial coordinates in the polar plot
dawn_r = np.array(list(civil_twilight_dawn) + [civil_twilight_dawn[0]]) / 24
dawn_nautical_r = np.array(list(nautical_twilight_dawn) + [nautical_twilight_dawn[0]]) / 24
dawn_astro_r = np.array(list(astronomical_twilight_dawn) + [astronomical_twilight_dawn[0]]) / 24

# Generate angles from 0 to 2 pi with as many points as there are days in the year
# These angles will be used to plot the days of the year in a polar plot
theta = np.linspace(0, 2 * np.pi, len(sunrise_r), endpoint=True)

# Adjust radial limits to span only from 4:00 AM to 7:15 AM
start_time = 4 / 24
end_time = 7.25 / 24
ax.set_ylim(start_time, end_time)

# Night - our calendar doesn't show the night after sunset
ax.fill_between(theta, 0, sunrise_r, color='#011F26', zorder=2)

# Day
ax.fill_between(theta, sunrise_r, end_time-0.005, color='#fbba43', zorder=2)

# Twilight layers for dawn
ax.fill_between(theta, dawn_astro_r, dawn_nautical_r,
                color='#092A38', zorder=2, alpha=0.8)
ax.fill_between(theta, dawn_nautical_r, dawn_r,
                color='#0A3F4D', zorder=2, alpha=0.7)
ax.fill_between(theta, dawn_r, sunrise_r,
                color='#1C5C7C', zorder=2, alpha=0.85)


# Prepare month labels and their positions
months_labels = ['JAN', 'FEB', 'MAR', 'APR', 'MAY',
                 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
cumulative_days = np.cumsum(days_in_month)

# Calculate month tick positions
month_ticks = [(cumulative_days[i - 1] if i > 0 else 0) +
               days_in_month[i] / 2 for i in range(12)]
month_ticks_rad = [tick / num_days * 2 * np.pi for tick in month_ticks]

# Remove default tick labels
ax.set_xticks(month_ticks_rad)

# Remove default tick labels. The x-axis tick labels are the month labels, and
# the y-axis tick labels are the hour labels. The month labels and hour labels are
# added manually later in the code.
ax.set_xticklabels([])
ax.set_yticklabels([])

# Add month labels around the circle
label_height = end_time + 0.006
for angle, label in zip(month_ticks_rad, months_labels):
    ax.text(angle, label_height, label, horizontalalignment='center',
            fontsize=22, color="#2F4F4F", fontweight='bold')

# Draw vertical lines connecting the month labels
for i in range(12):
    angle = cumulative_days[i] / num_days * 2 * np.pi if i < 11 else 2 * np.pi
    ax.plot([angle, angle], [start_time, end_time],
            color='#02735E', linewidth=0.5, zorder=10)


# Sundays
first_sunday = 5 - 1  # Adjust for 0-based indexing
sundays = [(first_sunday + i * 7) for i in range(52)]

# Fixed radius for Sunday labels
fixed_label_radius = end_time - 0.008

for j, day_index in enumerate(sundays):
    if day_index >= num_days:
        continue  # Skip invalid days
    angle = day_index / num_days * 2 * np.pi

    # Determine the month and day
    cumulative_days = np.cumsum(days_in_month)
    month_index = next((i for i, total in enumerate(
        cumulative_days) if day_index < total), 11)
    days_before_month = cumulative_days[month_index -
                                        1] if month_index > 0 else 0
    month_day = day_index - days_before_month + 1

    # Use a fixed radius for consistent placement
    rotation = -np.degrees(angle)
    # Normalize rotation for proper alignment
    rotation = (rotation + 180) % 360 - 180
    ha = 'center'

    # Add Sunday labels
    ax.text(
        angle, fixed_label_radius, str(month_day),
        ha=ha, va='center', fontsize=14, color='#696969',
        rotation=rotation, zorder=5, fontweight='bold'
    )


hour_labels_to_display = [
    '4:00AM', '4:15AM', '4:30AM', '4:45AM', '5:00AM', '5:15AM', 
    '5:30AM', '5:45AM', '6:00AM', '6:15AM', '6:30AM', '6:45AM'
]

hour_ticks_to_display = [
    4 / 24, 4.25 / 24, 4.5 / 24, 4.75 / 24, 5 / 24, 5.25 / 24, 5.5 /
    24, 5.75 / 24, 6 / 24, 6.25 / 24, 6.5 / 24, 6.75 / 24, 7 / 24
]

# Add radial tick labels
for i, label in enumerate(hour_labels_to_display):
    radius = hour_ticks_to_display[i]
    ax.text(np.pi / 2, radius, label, ha='left', va='center',
            fontsize=9, color='#e7fdeb', zorder=10)

# Draw hour tick marks
for tick in hour_ticks_to_display:
    ax.fill_between(theta, tick - 0.0001, tick + 0.0001,
                    color='gray', alpha=0.4, zorder=3, linewidth=0)

# Add city name
font_system = FontProperties(fname='Arvo-Bold.ttf', weight='bold', size=64)
ax.text(0.5, 1.18, city_name, ha='center', va='center',
        fontproperties=font_system, transform=ax.transAxes)

# Add city coordinates
font_system = FontProperties(fname='Arvo-Regular.ttf', size=20)
ax.text(0.5, 1.14, city_coordinates, ha='center', va='center',
        fontproperties=font_system, transform=ax.transAxes)

# Add year
font_system = FontProperties(fname='Arvo-Regular.ttf', size=48)
ax.text(0.5, 1.23, "2025", ha='center', va='center',
        fontproperties=font_system, transform=ax.transAxes)


# Move the top of the plot down to make room for the title and labels
plt.subplots_adjust(top=0.9)

# Save the plot
plt.savefig(f'{city_name}_dawn.png', bbox_inches='tight', pad_inches=1)
plt.savefig(f'{city_name}_dawn.pdf', bbox_inches='tight', pad_inches=1)
