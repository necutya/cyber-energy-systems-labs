def calc_water_consumption(n: int, q: float) -> float:
    """
	Обсяги споживання води
    """
    return n * q


def calc_cost_adjustment(q: float, t: float, t_vh: float, t_vih: float) -> float:
    """
    Корегування витрати гарячої води
    """
    return q * (t - t_vh) / (t_vih - t_vh)


def calc_cost_main_adjustment(q_d: float, q_v: float) -> float:
    ro = 998.23
    return (q_d + q_v) / ro


def cal_required_energy(q_gar_voda: float, t_bak: float, t_vh: float) -> float:
    """
    Енергія необхідна для нагріву води:
    """
    return 1.163 * q_gar_voda * (t_bak - t_vh)


def calc_heating_time(w_hot_water: float, heater_power: float) -> float:
    """
    Задаємо тривалість нагріву ємності і розраховуємо  потужність нагрівача
    """
    return w_hot_water / heater_power


def calc_heater_power(w_hot_water: float, heating_time: float) -> float:
    """
    Задаємо потужність нагрівача (для стандартного електробойлера) і розраховуємо  тривалість нагріву ємності
    """
    return w_hot_water / heating_time


def calc_heat_loss_capacity(t_count_in: float, area: float) -> float:
    """
    Потужність тепловтрат будівлі через огороджувальні конструкції для розрахункової температури
    """
    return t_count_in * area