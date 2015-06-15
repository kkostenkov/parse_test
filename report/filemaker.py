def list_to_file(dict_data, total_size):
    # для красоты тэги можно сделать через декоратор
    html_code = "<!DOCTYPE html>\n\
<html>\n\
<head>\n\
<title>Found executable files</title>\n\
</head>\n\
<body>"
    html_code += ("\n<li>name of list\n")
    field_deparator = " "
    for item in dict_data:
        list_item_text = "<li>"
        field_deparator = " "
        html_code += "<li>"
        html_code += str(item).strip('{}')
        html_code += "</li>\n"
    html_code += "</li>\n"
    html_code += "<p>Total size: " + str(total_size) + " bytes</p>\n"
    html_code += "</body>\n</html>\n"
    print (html_code)
    return html_code

if __name__ == "__main__":
    test_list = [["a","b"], ["c", "d", "e"]]
    total_size = "100000b"
    list_to_file(test_list, total_size)
