def calculate_suitability(temp, humidity, crop_data):
    tmin, tmax = crop_data["TMIN"], crop_data["TMAX"]
    ropmn, ropmx = crop_data["ROPMN"], crop_data["ROPMX"]

    def score(value, minv, maxv):
        if value < minv: return max(0, 1 - (minv - value)/10)
        if value > maxv: return max(0, 1 - (value - maxv)/10)
        return 1

    t_score = score(temp, tmin, tmax)
    h_score = score(humidity * 10, ropmn, ropmx)  # примерная нормализация
    return round((t_score + h_score) / 2, 2)
