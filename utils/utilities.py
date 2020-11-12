def pop_from_data(pop_list, data):
    for _ in pop_list:
        if _ in data:
            data.pop(_)
    return data