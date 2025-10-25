def compute_suitability(weather, crop_params):
    temp = weather["temperature"]
    tmin, tmax = crop_params["TMIN"], crop_params["TMAX"]

    if not all([tmin, tmax]):
        return None

    if temp < tmin or temp > tmax:
        score = 0.0
    elif tmin <= temp <= tmax:
        score = 1.0
    else:
        score = 0.5

    return round(score, 2)
