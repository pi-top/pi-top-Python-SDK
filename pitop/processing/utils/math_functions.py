from numpy import cumsum, insert, append, shape, delete


def running_mean(old_array, new_value):
    def calculate_mean(x, N):
        cum_sum = cumsum(insert(x, 0, 0))
        return (cum_sum[N:] - cum_sum[:-N]) / float(N)

    new_array = append(delete(old_array, 0), new_value)
    new_mean = calculate_mean(new_array, shape(new_array)[0])[0]
    return new_array, new_mean


def remap_range(old_value, old_range, new_range, invert_direction=False):
    old_min = old_range[0]
    old_max = old_range[1]
    old_range_magnitude = abs(old_max - old_min)
    new_min = new_range[0]
    new_max = new_range[1]
    new_range_magnitude = abs(new_max - new_min)

    if not invert_direction:
        new_value = (((old_value - old_min) * new_range_magnitude) / old_range_magnitude) + new_min
    else:
        new_value = new_max - (((old_value - old_min) * new_range_magnitude) / old_range_magnitude)

    return new_value
