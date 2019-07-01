from typing import Union
from SPARQLWrapper import SPARQLWrapper, JSON
import string
from Code.property_type_map import property_type_map


def get_column_letter(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


def get_excel_column_index(column: str) -> int:
    """
    This function converts an excel column to its respective column index as used by pyexcel package.
    viz. 'A' to 0
    'AZ' to 51
    :param column:
    :return: column index of type int
    """
    index = 0
    column = column.upper()
    column = column[::-1]
    for i in range(len(column)):
        index += ((ord(column[i]) % 65 + 1)*(26**i))
    return index-1


def get_excel_row_index(row: Union[str, int]) -> int:
    """
    This function converts an excel row to its respective row index as used by pyexcel package.
    viz. '5' to 1
    10 to 9
    :param row:
    :return: row index of type int
    """
    return int(row)-1


def get_actual_cell_index(cell_index):
    col = get_column_letter(cell_index[0]+1)
    row = str(cell_index[1] + 1)
    return col+row


def get_property_type(wikidata_property: str) -> str:
    try:
        type = property_type_map[wikidata_property]
    except KeyError:
        query = """SELECT ?type WHERE {
          wd:"""+wikidata_property+""" rdf:type wikibase:Property ;
            wikibase:propertyType ?type .  
        }"""

        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        try:
            type = results["results"]["bindings"][0]["type"]["value"].split("#")[1]
        except IndexError:
            type = "Property Not Found"
    return type


def excel_to_json(file_path):
    print("in excel 2 json")
    import pyexcel as p
    import json
    book_dict = p.get_book_dict(file_name=file_path)
    result = {"columnDefs": [{"headerName": "", "field": "^", "pinned": "left"}], "rowData": []}
    column_index_map = {}
    for key, item in book_dict.items():
        for i in range(len(item[0])):
            column = get_column_letter(i+1)
            column_index_map[i+1] = column
            result["columnDefs"].append({"headerName": column_index_map[i + 1], "field": column_index_map[i + 1]})
        for row in range(len(item)):
            r = {"^": str(row + 1)}
            for col in range(len(item[row])):
                r[column_index_map[col+1]] = item[row][col]
            result["rowData"].append(r)
        # break here for accessing only the first sheet in the workbook
        break
    return json.dumps(result)


def read_file(file_path):
    with open(file_path, "r") as f:
        return f.read()


def write_file(filepath, data):
    with open(filepath, "w") as f:
        f.write(data)
        f.close()


def check_special_characters(text) -> bool:
    """
    This funtion checks if the text is made up of only special characters
    :param text:
    :return:
    """
    return all(char in string.punctuation for char in text)


def check_if_empty(text: str) -> bool:
    """
    This function checks if the text is empty or has only special characters
    :param text:
    :return:
    """
    text = text.strip()
    if text is None or text == "" or check_special_characters(text):
        return True
    return False
