import astral
from astral import LocationInfo
from astral.sun import sun
import datetime
import numpy as np
from scipy.interpolate import interp1d

import json
from astral import moon

lat = 17.7219
lon = 83.3057
city = LocationInfo('Vizag', 'India', 'Asia/Kolkata', lat, lon)

year = 2025
months = range(1, 13)
days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

sunrise_times = []
sunset_times = []
noon_times = []

moon_phases = []
civil_twilight = []
nautical_twilight = []
astronomical_twilight = []

day_of_year = 0
for m in months:
    for d in range(1, days_in_month[m - 1] + 1):
        date = datetime.date(year, m, d)
        try:
            s = sun(city.observer, date=date, tzinfo=city.tzinfo, dawn_dusk_depression=6)
            sunrise = s["sunrise"].hour + s["sunrise"].minute / 60
            sunset = s["sunset"].hour + s["sunset"].minute / 60
            noon = s["noon"].hour + s["noon"].minute / 60
            dawn = s["dawn"].hour + s["dawn"].minute / 60
            dusk = s["dusk"].hour + s["dusk"].minute / 60
            nautical = sun(city.observer, date=date, tzinfo=city.tzinfo, dawn_dusk_depression = 12)
            astro = sun(city.observer, date=date, tzinfo=city.tzinfo, dawn_dusk_depression = 18)
            dawn_nautical = nautical["dawn"].hour + nautical["dawn"].minute / 60
            dusk_nautical = nautical["dusk"].hour + nautical["dusk"].minute / 60
            dawn_astro = astro["dawn"].hour + astro["dawn"].minute / 60
            dusk_astro = astro["dusk"].hour + astro["dusk"].minute / 60
            # Moon phase calculation (approximate)
            # new moon = 0, full moon = 14, new moon = 28
            moon_phase =  astral.moon.phase(date)

        except Exception as e:
            print(f"Error calculating sunrise/sunset for {date}: {e}. Interpolating later")
            # library not converging - https://github.com/sffjunkie/astral/issues/86
            sunrise = sunset = moon_phase = noon = dawn = dusk = dawn_nautical = dusk_nautical = dawn_astro = dusk_astro = -1
        
        sunrise_times.append(sunrise)
        sunset_times.append(sunset)
        moon_phases.append(moon_phase)
        noon_times.append(noon)
        civil_twilight.append((dawn, dusk))
        nautical_twilight.append((dawn_nautical, dusk_nautical))
        astronomical_twilight.append((dawn_astro, dusk_astro))
        day_short_name = date.strftime('%a')
        day_of_year += 1

def interpolate_missing_values(times):
    if isinstance(times[0], tuple):
        first_values = np.array([t[0] for t in times])
        second_values = np.array([t[1] for t in times])
        first_values = interpolate_array(first_values)
        second_values = interpolate_array(second_values)
        interpolated_values = list(zip(first_values, second_values))
        return interpolated_values
    else:
        return interpolate_array(times)

def interpolate_array(times):    
    times = np.array(times, dtype=float)
    valid_indices = np.where(times != -1)[0]
    valid_values = times[valid_indices]

    interp_func = interp1d(valid_indices, valid_values, kind='linear', fill_value='extrapolate')
    invalid_indices = np.where(times == -1)[0]
    interpolated_values = interp_func(invalid_indices)
    times[invalid_indices] = interpolated_values
    return times.tolist()

def interpolate_circular(times, max_value=28):
    times = np.array(times, dtype=float)
    times[times != -1] /= max_value

    valid_indices = np.where(times != -1)[0]
    valid_values = times[valid_indices]

    interp_func = interp1d(valid_indices, valid_values, kind='linear', fill_value='extrapolate')
    invalid_indices = np.where(times == -1)[0]
    interpolated_values = interp_func(invalid_indices)
    interpolated_values *= max_value
    interpolated_values %= max_value

    times[invalid_indices] = interpolated_values
    return times.tolist()

sunrise_times = interpolate_missing_values(sunrise_times)
sunset_times = interpolate_missing_values(sunset_times)
noon_times = interpolate_missing_values(noon_times)
civil_twilight = interpolate_missing_values(civil_twilight)
nautical_twilight = interpolate_missing_values(nautical_twilight)
astronomical_twilight = interpolate_missing_values(astronomical_twilight)
moon_phases = interpolate_missing_values(moon_phases)

smoothed_sunrise = sunrise_times
smoothed_sunset = sunset_times

def round_values(data):
    def round_nested(value):
        if isinstance(value, list):
            return [round_nested(v) for v in value]
        elif isinstance(value, tuple):
            return tuple(round_nested(v) for v in value)
        elif isinstance(value, (int, float)):
            return round(value, 3)
        else:
            return value

    return {key: round_nested(value) for key, value in data.items()}

data = {
    "sunrise": smoothed_sunrise,
    "sunset": smoothed_sunset,
    "days_in_month": days_in_month,
    "moon_phases": moon_phases,
    "noon": noon_times,
    "civil": civil_twilight,
    "nautical": nautical_twilight,
    "astro": astronomical_twilight,
}
rounded_data = round_values(data)

with open("vizag_data.json", "w") as f:
    json.dump(rounded_data, f, indent=4)