import re

import handle_data.Data_File_Reader as DataReader
import handle_data.RuleGenerator as RuleGen

# re.match(r'\d+[.]\d+','12.34')[0]=='12.34'

_list_of_method_names = [
    {'name': 'member_in_common', 'types': [list]},
    {'name': 'k_members_in_common', 'types': [list]},
    {'name': 'same_as', 'types': [list, int, float, str]},
    {'name': 'lesser_equal', 'types': [list]},
    {'name': 'member_in_common', 'types': [list]},
]
# _list_of_function_names = []


class ConnectionRuleGenerator(RuleGen.RuleGenerator):
    pass


if __name__ == "__main__":
    _rg = ConnectionRuleGenerator()

    print(_list_of_function_names)

