from numpy import append, cumsum, delete, insert, shape


def running_mean(old_array, new_value):
    """Calculates a running mean from either a 1d numpy array of single
    measurements or a 2d numpy array of 1d numpy array measurements.

    :param old_array: Stored historical values either as a 1d numpy
        array or a 2d numpy array
    :param new_value: New value to add. For a 1d array this will be a
        single value. For a 2d Nxm numpy array, this will be a 1d numpy
        array that has m values, where N is the number of samples to
        average over.
    :return: tuple where index 0 is the new array and index 1 is the new
        mean.
    """

    def calculate_mean(x, N):
        cum_sum = cumsum(insert(x, 0, 0, axis=0), axis=0)
        return (cum_sum[N:] - cum_sum[:-N]) / float(N)

    array_shape = old_array.shape
    if old_array.ndim == 2:
        new_value = new_value.reshape(1, array_shape[1])
        new_array = append(delete(old_array, 0, axis=0), new_value, axis=0)
    else:
        new_array = append(delete(old_array, 0, axis=0), new_value)

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
        new_value = (
            ((old_value - old_min) * new_range_magnitude) / old_range_magnitude
        ) + new_min
    else:
        new_value = new_max - (
            ((old_value - old_min) * new_range_magnitude) / old_range_magnitude
        )

    return new_value
