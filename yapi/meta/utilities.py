
def filter_response(data, **kwargs):
    filter_type = 'equals'
    
    for key, value in kwargs.items():
        if type(value) is tuple:
            filter_type, value = value
        if type(value) is list:
            filter_type, value = value[0], value[1]
            
        if filter_type == 'equals':
            data = [x for x in data if x[key] == value]
        elif filter_type == '!equals':
            data = [x for x in data if x[key] != value]
        elif filter_type == 'contains':
            data = [x for x in data if value in x[key]]
        elif filter_type == '!contains':
            data = [x for x in data if value not in x[key]]
        else:
            raise ValueError("Invalid filter type")
        
    return data