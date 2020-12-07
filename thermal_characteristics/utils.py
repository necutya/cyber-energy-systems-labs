from . import calculations


def make_thermal_calculations(data: dict) -> tuple:
    """
    Make all required calculation and parsed data
    """
    if not data:
        return 0, 0
    q_shower = calculations.calc_water_consumption(data["N_Shower"], data["Q_shower_Normal"])
    q_t_shower = calculations.calc_cost_adjustment(q_shower, data["T_shower"], data["T_inWater"], data["T_endBak"])
    q_bath = calculations.calc_water_consumption(data["N_Bath"], data["Q_bath_Normal"])
    q_t_bath = calculations.calc_cost_adjustment(q_bath, data["T_Bath"], data["T_inWater"], data["T_endBak"])
    q_hot_water = calculations.calc_cost_main_adjustment(q_t_shower, q_t_bath)
    required_energy = calculations.cal_required_energy(q_hot_water, data['T_endBak'], data['T_inWater'])
    if data['t_heating']:
        return q_hot_water, data['t_heating'], calculations.calc_heater_power(required_energy, data['t_heating'])
    else:
        return q_hot_water, calculations.calc_heating_time(required_energy, data['p_of_heater']), data['p_of_heater'],
