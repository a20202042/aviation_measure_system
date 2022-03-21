
def measure_go_nogo_calculate(upper, lower, value):
    gonogo = bool
    print(float(value))
    print(float(upper))
    print(float(lower))
    if float(value) <= float(upper):
        if float(lower) <= float(value):
            gonogo = True
    else:
        gonogo = False
    return gonogo


def measure_Yield(upper, lower, values):
    excellent = []
    inferior = []
    all = []
    for value in values:
        value = float(value)
        if value <= upper:
            if lower <= value:
                excellent.append(value)
        else:
            inferior.append(value)
        all.append(value)

    return (
     len(excellent), len(inferior), len(all))


def draw_measure(data):
    measure_data = []
    upper_data = []
    lower_data = []
    for item in data:
        measure_data.append(float(item[0]))
        upper_data.append(float(item[3]))
        lower_data.append(float(item[4]))

    print(measure_data, upper_data, lower_data)
    return (measure_data, upper_data, lower_data)
# okay decompiling measure.pyc
