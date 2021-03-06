def parse_response(response):
    result = [{}]
    current_list_index = 0
    first_key = None
    for line in response.split("\n"):
        key, value = _extract_key_value(line)
        if _value_is_valid(value):
            if key == first_key:
                result.append({})
                current_list_index += 1
            if first_key is None:
                first_key = key
            result[current_list_index][key] = value
    return result


def _value_is_valid(value):
    return value is not ""


def _extract_key_value(line):
    # try:
    key = line.split(":", 1)[0].lstrip().lower()
    value = ":".join(line.split(":", 1)[1:]).lstrip()
    # except ValueError as e:
    #     key = ""  # line.split(":", 1)[0].lstrip().lower
    #     value = ""
    return key, value

