def replace_process_name(process_name, replace, replace_to):
    for i in range(len(replace)):
        if process_name == replace[i]:
            process_name = replace_to[i]
            break
    return process_name
