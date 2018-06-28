def parse_response(response):
    result = [{}]
    current_list_index = 0
    for line in response.split("\n"):
        try:
            key, value = line.split(": ", 1)
        except ValueError as e:
            key = line.split(": ", 1)[0]
            value = ""
        if key is not "":
            if key in result[current_list_index]:
                result.append({})
                current_list_index += 1
            result[current_list_index][key] = value
    return result
