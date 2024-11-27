#!/usr/bin/python3

import math

E24 = [
    1,
    1.1,
    1.2,
    1.3,
    1.5,
    1.6,
    1.8,
    2,
    2.2,
    2.4,
    2.7,
    3,
    3.3,
    3.6,
    3.9,
    4.3,
    4.7,
    5.1,
    5.6,
    6.2,
    6.8,
    7.5,
    8.2,
    9.1,
]

E96 = [
    1.00,
    1.02,
    1.05,
    1.07,
    1.10,
    1.13,
    1.15,
    1.18,
    1.21,
    1.24,
    1.27,
    1.30,
    1.33,
    1.37,
    1.40,
    1.43,
    1.47,
    1.50,
    1.54,
    1.58,
    1.62,
    1.65,
    1.69,
    1.74,
    1.78,
    1.82,
    1.87,
    1.91,
    1.96,
    2.00,
    2.05,
    2.10,
    2.15,
    2.21,
    2.26,
    2.32,
    2.37,
    2.43,
    2.49,
    2.55,
    2.61,
    2.67,
    2.74,
    2.80,
    2.87,
    2.94,
    3.01,
    3.09,
    3.16,
    3.24,
    3.32,
    3.40,
    3.48,
    3.57,
    3.65,
    3.74,
    3.83,
    3.92,
    4.02,
    4.12,
    4.22,
    4.32,
    4.42,
    4.53,
    4.64,
    4.75,
    4.87,
    4.99,
    5.11,
    5.23,
    5.36,
    5.49,
    5.62,
    5.76,
    5.90,
    6.04,
    6.19,
    6.34,
    6.49,
    6.65,
    6.81,
    6.98,
    7.15,
    7.32,
    7.50,
    7.68,
    7.87,
    8.06,
    8.25,
    8.45,
    8.66,
    8.87,
    9.09,
    9.31,
    9.53,
    9.76,
]


def find_closest_e(r, e_series=E24):
    decade = 10 ** math.floor(math.log(r, 10))
    closest = 0
    last = decade * 10
    for i in e_series:
        current = decade * i
        if abs(current - r) < last:
            last = abs(current - r)
            closest = current
    return closest

def find_next_e(r, e_series=E24):
    decade = 10 ** math.floor(math.log(r, 10))
    closest = 0
    last = decade * 10
    for i in e_series:
        current = decade * i
        if (current - r) >= 0 and (current - r) < last:
            last = current - r
            closest = current
    return closest


# Frequency < 500kHz
# Vin between 8 and 11 V
# Vout 5 volts
# Need to filter input as audio uses input
# output ripple needs to be < 5mV pk-pk
# 1.3A max current, usual current is around 600mA

# Calculations

V_out = 5
V_in = 9
I_out_max = 1.3
I_out_load = .600
#I_out_load = I_out_max
output_ripple = 0.005
t_ss = 0.005
fsw = 300 #kHz

print("Requirements")
print(f"V_in: {V_in} V")
print(f"V_out: {V_out} V")
print(f"I_out_max: {I_out_max} A")
print(f"I_out_load: {I_out_load} A")
print(f"output_ripple: {output_ripple}")
print(f"startup time: {t_ss}")
print("--")
# R_FBT = (V_out - V_ref) / V_ref * R_FBB

R_fbb = 12_000  # recommended by datasheet
V_ref = 0.8  # provided by datasheet
R_fbt = (5 - V_ref) / V_ref * R_fbb
# = 52500

print("Resistor divider to set output voltage")
print(f"R_fbb: {R_fbb} Ω, R_fbt: {R_fbt} Ω")
R_fbb = find_closest_e(R_fbb)
R_fbt = find_closest_e(R_fbt, E96)
print(f"E series values R_fbb: {R_fbb} Ω, R_fbt: {R_fbt} Ω")
print("Actual setpoint: {}".format(R_fbt / R_fbb * V_ref + V_ref))

print()

print("Resistor to set switching frequency")
# fsw(kHz) = 17293 * RT(in kOhm) ^ -0.942
R_t = math.e ** (math.log(fsw / 17293) / -0.942) * 1000
# fsw = 17293 * R_t ** -0.942
print(f"fsw: {fsw} kHz")
print(f"R_t: {R_t} Ω")
R_t = find_closest_e(R_t)
print(f"E series value R_t: {R_t}")
print(f"Actual fsw: {17293 * (R_t / 1000) ** -0.942}")
print()

# Css = 33nF (check if we want to tweak, here it's 5ms startup)

print("Resistors to control when to turn on buck converter")
I_p = 0.0000007  # from datasheet
I_h = 0.0000014  # from datasheet
V_en_fall = 1.17  # from datasheet
V_en_rise = 1.21  # from datasheet
V_start = 7.7  # Don't enable until V_in is at least 7.5V
V_stop = 6.5  # Stop if voltage drops below 6.5V (Audio subsystem may not work well below here)
print(f"Desired V_start: {V_start}, V_stop: {V_stop}")
R_1 = (V_start * (V_en_fall / V_en_rise) - V_stop) / (
    I_p * (1 - V_en_fall / V_en_rise) + I_h
)
R_2 = (R_1 * V_en_fall) / (V_stop - V_en_fall + R_1 * (I_p + I_h))
V_en = (R_2 * V_in + R_1 * R_2 * (I_p + I_h)) / (R_1 + R_2)

print("R_1: {} Ω, R_2: {} Ω, V_en: {} V".format(R_1, R_2, V_en))
R_1 = find_closest_e(R_1)
R_2 = find_closest_e(R_2)
V_en = (R_2 * V_in + R_1 * R_2 * (I_p + I_h)) / (R_1 + R_2)
print("E series values R_1: {} Ω, R_2: {} Ω, V_en: {} V".format(R_1, R_2, V_en))
V_start = (R_1 * (I_p * (1 - V_en_fall / V_en_rise) + I_h) + V_stop) / (V_en_fall / V_en_rise)
V_stop = R_1 * V_en_fall / R_2 + V_en_fall - R_1 * (I_p + I_h)
print(f"Effective V_start: {V_start},  V_stop: {V_stop}")
print()

# 100nF bootstrap cap between BST and SW (good quality), 16V or higher rating. Small resistance below 10Ohm to reduce spike voltage in series with boostrap cap.

print("Inductor, and inductor current ripple")
K = 0.4  # suggested by datasheet
L = (V_in - V_out) / (fsw * 1000 * K * I_out_max) * V_out / V_in
delta_I_l = V_out / V_in * (V_in - V_out) / (L * fsw * 1000)
I_l_peak = I_out_load + delta_I_l / 2
I_l_min = I_out_load - delta_I_l / 2
I_l_rms = math.sqrt(I_out_load**2 + (delta_I_l**2) / 12)
print(f"L: {L} H")
print(f"delta_I_l: {delta_I_l} A")
print(f"I_l_peak: {I_l_peak} A")
print(f"I_l_min: {I_l_min} A")
print(f"I_l_rms: {I_l_rms} A")
L = find_closest_e(L)
print(f"E series value L: {L}")
delta_I_l = V_out / V_in * (V_in - V_out) / (L * fsw * 1000)
I_l_peak = I_out_load + delta_I_l / 2
I_l_min = I_out_load - delta_I_l / 2
I_l_rms = math.sqrt(I_out_load**2 + (delta_I_l**2) / 12)
print(f"actual delta_I_l: {delta_I_l} A")
print(f"actual I_l_peak: {I_l_peak} A")
print(f"actual I_l_min: {I_l_min} A")
print(f"actual I_l_rms: {I_l_rms} A")
print(f"actual K: {delta_I_l / I_out_max}")
print()

print("Output capacitor selection")
delta_V_out_esr = output_ripple
delta_V_out_c = output_ripple
max_ESR = delta_V_out_esr / (K * I_out_load)
min_C_out = (K * I_out_load) / (delta_V_out_c * 8 * fsw * 1000)

delta_I_step = 1.3
delta_V_out_step = V_out * 0.005

min_C_out2 = (
    delta_I_step
    / (fsw * 1000 * delta_V_out_step * K)
    * ((1 - V_out / V_in) * (1 + K) + (K**2) / 12 * (2 - V_out / V_in))
)
C_out = max(min_C_out, min_C_out2)
print(f"Maximum ESR: {max_ESR}, Minimum C_out: {C_out}")

C_out = find_next_e(C_out)
print(f"Series E C_out: {C_out}")
delta_V_out_c = (K * I_out_load) / (C_out * 8 * fsw * 1000)
print(f"Actual delta_V_out_c: {delta_V_out_c}")
print()

print("Input capacitor selection")
I_cin_rms = I_out_load * math.sqrt(V_out / V_in * (V_in - V_out) / V_in)
print(f"I_cin_rms: {I_cin_rms}")

C_in = 0.00330 * 2
R_esr_max = 0.015 / 2
delta_V_in = (I_out_max * 0.25) / (C_in * fsw * 1000) + (I_out_max * R_esr_max)
print(f"C_in: {C_in}, R_esr_max: {R_esr_max}")
print(f"input ripple current: {delta_V_in}")
print()

print("Startup time capacitor selection")
I_ss = 0.0000055 # From datasheet
C_ss = t_ss * I_ss / V_ref
print(f"C_ss: {C_ss}")
C_ss = find_closest_e(C_ss)
print(f"Series E C_ss {C_ss}")
t_ss = C_ss * V_ref / I_ss
print(f"Actual startup time: {t_ss}")
