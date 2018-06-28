def parse_response(response):
    result = [{}]
    current_list_index = 0
    first_key = None
    for line in response.split("\n"):
        try:
            key, value = line.split(": ", 1)
        except ValueError as e:
            key = line.split(": ", 1)[0]
            value = ""
        if key is not "":
            if key == first_key:
                result.append({})
                current_list_index += 1
            if first_key is None:
                first_key = key
            result[current_list_index][key] = value
    return result
