from handle_data.ConnectionRuleGenerator import  ConnectionRuleGenerator

_rg = ConnectionRuleGenerator(constraints=None)

constraints1 = {"hypothesis_idxes": _rg.get_indexes_for_keys(['group_comp_id', 'fyear']),
                "hypothesis_functions": [{"func_name": 'same_as', "extra_parameters": []},
                                         {"func_name": 'same_as', "extra_parameters": []}],
                "hypothesis_operators": ['AND', 'AND NOT']}
constraints2 = {"hypothesis_idxes": _rg.get_indexes_for_keys(['debtat']),
                "hypothesis_functions": [{"func_name": 'lesser_equal', "extra_parameters": [0, 1.0]}],
                "hypothesis_operators": ['AND']}
constraints3 = {"hypothesis_idxes": _rg.get_indexes_for_keys(['director_list']),
                "hypothesis_functions": [{"func_name": 'member_in_common', "extra_parameters": []}],
                "hypothesis_operators": ['AND']}

