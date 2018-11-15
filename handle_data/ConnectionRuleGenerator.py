import random as rn
import copy as cp
import time as t
import numpy as np

import re

import handle_data.Data_File_Reader as DataReader
import handle_data.RuleGenerator as RuleGen

# re.match(r'\d+[.]\d+','12.34')[0]=='12.34'

_list_of_method_names = [
    {'name': 'member_in_common', 'types': [list], 'param_types': []},
    {'name': 'k_members_in_common', 'types': [list], 'param_types': [int]},
    {'name': 'same_as', 'types': [list, int, float, str, type(None)], 'param_types': []},
    # {'name': 'similar_to', 'types': [list, str], 'param_types': [int, float]},
    {'name': 'similar_number_to', 'types': [int, float], 'param_types': [float]},
    {'name': 'lesser_equal', 'types': [int, float], 'param_types': [int, float]},
    # {'name': 'greater_equal', 'types': [int, float], 'param_types': [int, float]},
]
# _list_of_function_names = []

_sample_size = 1000
# _mini_sample_size = 1000


class ConnectionRuleGenerator(RuleGen.RuleGenerator):
    def __init__(self, constraints=None):
        RuleGen.RuleGenerator.__init__(self, data_file_name=RuleGen._data_file_name)
        self.constraints = constraints
        pass

    def generate_random_rule(self):
        # print(len(self.data))
        # return self.generate_random_rule_for_lines(rn.sample(self.data, 2))
        return self.generate_random_rule_for_lines(self.sample_random_lines(2))

    def sample_random_lines(self, num_of_lines):
        while True:
            ret_val = [rn.choice(self.data)]

            while len(ret_val) < num_of_lines:
                ret_val += [i for i in [rn.choice(self.data)] if self.constraints_met(ret_val, i)]
                if rn.random() < 0.001:
                    # Avoid infinite loop due to no viable choice existing
                    break

            if len(ret_val) == num_of_lines:
                return ret_val

    def constraints_met(self, lines, new_line):
        if self.constraints is None:
            return True
        rule = cp.deepcopy(self.constraints)
        rule["lines"] = lines + [new_line]
        # print(rule)
        return self.is_relevant(rule)

    def generate_random_rule_for_lines(self, lines):
        # Assumption:
        #   Indexes are the same for all lines.
        #   Field names are the same for all lines.
        lengths = [len(i) for i in lines]
        indexes = list(range(lengths[0]))

        # hypothesis_indexes = [i for i in cp.deepcopy(indexes) if not (list(line.items())[i][0]).startswith('dam')]
        # conclusion_indexes = [i for i in cp.deepcopy(indexes) if (list(line.items())[i][0]).startswith('dam')]
        hypothesis_indexes = [i for i in cp.deepcopy(indexes) if
                              (list(lines[0].items())[i][0]) in RuleGen._hypothesis_field_list]
        conclusion_indexes = [i for i in cp.deepcopy(indexes) if
                              (list(lines[0].items())[i][0]) in RuleGen._conclusion_field_list]

        # print(hypothesis_indexes)
        # print(conclusion_indexes)


        # print(lines[0])
        self.last_rule = {"lines": lines, "hypothesis_idxes": rn.sample(hypothesis_indexes, rn.randint(3, 4)),
                          "conclusion_idxes": rn.sample(conclusion_indexes, rn.randint(1, 2)),
                          "hypothesis_functions": [], "conclusion_functions": [],
                          "hypothesis_operators": [], "conclusion_operators": []}

        # print(self.last_rule["hypothesis_idxes"])
        # print(self.last_rule["conclusion_idxes"])
        # Choose rule functions
        for idx, itm in enumerate(self.last_rule["hypothesis_idxes"]):
            self.last_rule["hypothesis_functions"].append(
                self.generate_rule_function(type(list(lines[0].values())[itm]),
                                            type(list(lines[1].values())[itm])))
            self.last_rule["hypothesis_operators"].append(rn.choice(['AND', 'OR', 'AND NOT', 'OR NOT']))
            pass

        for idx, itm in enumerate(self.last_rule["conclusion_idxes"]):
            self.last_rule["conclusion_functions"].append(
                self.generate_rule_function(type(list(lines[0].values())[itm]),
                                            type(list(lines[1].values())[itm])))
            self.last_rule["conclusion_operators"].append(rn.choice(['AND', 'OR', 'AND NOT']))
            pass

        # # Allow for list membership rules.
        # for idx, itm in enumerate(self.last_rule["hypothesis"]):
        #     actual_item = (list(line.items()))[itm][1]
        #     if type(actual_item) is list and len(actual_item) > 0:
        #         # rule element contains index, name of the list, and a member of the list to search for.
        #         self.last_rule["hypothesis"][idx] = {'index': self.last_rule["hypothesis"][idx],
        #                                              'list_name': (list(line.items()))[itm][0],
        #                                              'member': rn.choice(actual_item)}

        return cp.deepcopy(self.last_rule)

    def generate_rule_function(self, the_type1, the_type2):
        the_type = the_type1 if the_type1 == the_type2 else type(None)

        list_of_candidates = [i for i in _list_of_method_names if the_type in i['types']]
        chosen_func = rn.choice(list_of_candidates)
        ret_val = {"func_name": chosen_func["name"],
                   "extra_parameters": [self.generate_random_parameter_of_type(ty, chosen_func["name"]) for ty in
                                        chosen_func["param_types"]]}
        # ret_val = {"func_name": "same_as", "extra_parameters": []}
        # ret_val = {"func_name": rn.choice(_list_of_method_names)['name'], "extra_parameters": ()}
        return ret_val

    @staticmethod
    def generate_random_parameter_of_type(the_type, func_name):
        """

        :param the_type: type of number to return (int of float)
        :return: Random number of the_type. biased to return 0/1.0 'default_prob' of the time
        """
        default_prob = 0.5
        if func_name == "similar_number_to":
            return 1.0 + rn.random()/5
        else:
            if the_type is int:
                return 0 if rn.random() < default_prob else rn.randint(-100, 100)
            elif the_type is float:
                return 1.0 if rn.random() < default_prob else rn.random() * rn.choice([-2.0, 2.0])
            else:
                return None

        return None

    def rule_to_string(self, rule='last rule'):
        if rule == 'last rule':
            rule = self.last_rule
        if rule is None:
            string_rule = ''
        else:
            string_rule = ''
            # print(rule.keys())
            # print(rule['conclusion_functions'])
            # print(rule["lines"])
            rule_lines = list([i.items() for i in rule["lines"]])

            if self.constraints is not None:
                string_rule += 'Under ('
                if 'NOT' in self.constraints["hypothesis_operators"][0]:
                    string_rule += 'NOT '

                for idx, itm in enumerate(self.constraints["hypothesis_idxes"]):
                    if idx != 0:
                        # string_rule += ' and '
                        string_rule += ' ' + self.constraints['hypothesis_operators'][idx] + ' '
                    # print(itm)
                    if type(itm) is int:
                        self.constraints['lines'] = rule['lines']
                        string_rule += (self.rule_element_to_string(self.constraints, idx, part='hypothesis'))
                    else:
                        print("What?!? type of item is not an int!")
                        print("rule_to_string() constraint loop.")
                string_rule += ')\n'

            string_rule += 'If ('

            if 'NOT' in rule["hypothesis_operators"][0]:
                string_rule += 'NOT '

            for idx, itm in enumerate(rule["hypothesis_idxes"]):
                if idx != 0:
                    # string_rule += ' and '
                    string_rule += ' ' + rule['hypothesis_operators'][idx] + ' '
                # print(itm)
                if type(itm) is int:
                    string_rule += (self.rule_element_to_string(rule, idx, part='hypothesis'))
                else:
                    print("What?!? type of item is not an int!")
                    print("rule_to_string() hypothesis loop.")

            string_rule += ')\nThen ('
            if 'NOT' in rule["conclusion_operators"][0]:
                string_rule += 'NOT '

            # string_rule += (self.rule_element_to_string(rule_line[rule["conclusion"][0]]))

            for idx, itm in enumerate(rule["conclusion_idxes"]):
                if idx != 0:
                    # string_rule += ' and '
                    string_rule += ' ' + rule['conclusion_operators'][idx] + ' '
                if type(itm) is int:
                    string_rule += (self.rule_element_to_string(rule, idx, part='conclusion'))
                else:
                    print("What?!? type of item is not an int!")
                    print("rule_to_string() hypothesis loop.")

            # string_rule += ')\n'
            string_rule += ')'

        return cp.deepcopy(string_rule)

    def rule_element_to_string(self, rule, idx_in_lines, part):
        """

        :param rule:
        :param idx_in_lines:
        :param part: 'hypothesis' or 'conclusion'
        :return: A string representing the rule element.
        """
        ret_val = ''

        itm_key_in_rule = part + '_idxes'
        function_key_in_rule = part + '_functions'

        # print('***' + part)
        # print(rule[function_key_in_rule])
        # print(rule[itm_key_in_rule][idx_in_lines])
        ret_val += rule[function_key_in_rule][idx_in_lines]['func_name'] + '('
        # print(list(rule['lines'][0].keys())[0])
        ret_val += list(rule['lines'][0].keys())[rule[itm_key_in_rule][idx_in_lines]]
        for i in rule[function_key_in_rule][idx_in_lines]['extra_parameters']:
            ret_val += ', ' + str(i)
        ret_val += ')'

        return ret_val

    def calculate_correctness(self, rule='last rule'):
        if rule == 'last rule':
            rule = self.last_rule
        ret_val = {"correctness": 0.0, "relevance": 0.0, "conclusion_true": 0.0}
        sample_size = _sample_size
        # mini_sample_size = _mini_sample_size
        conclusion_true_count = relevance_count = correctness_count = 0.0

        for _ in range(sample_size):
            # rule["lines"] = rn.sample(self.data, 2)
            rule["lines"] = self.sample_random_lines(2)
            # print(line)
            # print(self.rule_to_string(rule))
            if self.is_relevant(rule):
                relevance_count += 1
                if self.is_correct(rule):
                    correctness_count += 1
                    conclusion_true_count += 1
            else:
                if self.is_correct(rule):
                    conclusion_true_count += 1

        ret_val["relevance"] = relevance_count / sample_size
        ret_val["correctness"] = correctness_count / max(relevance_count, 0.1)  # Do not divide by zero!
        ret_val["conclusion_true"] = conclusion_true_count / sample_size
        return ret_val

    # def is_relevant_old(self, rule):
    #     relevance = True
    #     for idx, itm in enumerate(rule["hypothesis_idxes"]):
    #         func_eval = self.calculate_function(rule["hypothesis_functions"][idx]["func_name"],
    #                                             list(rule["lines"][0].values())[itm],
    #                                             list(rule["lines"][1].values())[itm],
    #                                             rule["hypothesis_functions"][idx]["extra_parameters"])
    #         if func_eval is False:
    #             relevance = False
    #             break
    #
    #         # print(list(rule["line"].items())[h])
    #         # print(hypothesis_to_check)
    #     return relevance
    #
    # def is_correct_old(self, rule):
    #     # self.last_rule =
    #     # x ={"lines": lines, "hypothesis_idxes": rn.sample(hypothesis_indexes, rn.randint(1, 3)),
    #     #     "conclusion_idxes": rn.sample(conclusion_indexes, rn.randint(1, 3)),
    #     #  "hypothesis_functions": [], "conclusion_functions": []}
    #     #
    #     # y = {"func_name": chosen_func["name"],
    #     #      "extra_parameters": [self.generate_random_parameter_of_type(t) for t in chosen_func["param_types"]]}
    #     #
    #     # # def calculate_function(self, func_name, item1, item2, extra_parameters):
    #
    #     correctness = True
    #     for idx, itm in enumerate(rule["conclusion_idxes"]):
    #         func_eval = self.calculate_function(rule["conclusion_functions"][idx]["func_name"],
    #                                             list(rule["lines"][0].values())[itm],
    #                                             list(rule["lines"][1].values())[itm],
    #                                             rule["conclusion_functions"][idx]["extra_parameters"])
    #         if func_eval is False:
    #             correctness = False
    #             break
    #     return correctness

    def is_relevant(self, rule):
        """

        :param rule: Rule to check
        :return: True if relevant for rule["lines"][0:2]
        """
        # self.last_rule["hypothesis_operators"]
        relevance = False
        curr_idx = 0
        while curr_idx < len(rule["hypothesis_idxes"]):
            clause_relevance = True

            # AND clause loop.
            # print(rule["lines"])
            for idx, itm in list(enumerate(rule["hypothesis_idxes"]))[curr_idx:]:
                func_eval = self.calculate_function(rule["hypothesis_functions"][idx]["func_name"],
                                                    list(rule["lines"][0].values())[itm],
                                                    list(rule["lines"][1].values())[itm],
                                                    rule["hypothesis_functions"][idx]["extra_parameters"])

                curr_idx = idx+1

                if 'NOT' in rule["hypothesis_operators"][idx]:
                    func_eval = not func_eval

                if func_eval is False:
                    # clause failed. Advance to next clause (=next OR)
                    clause_relevance = False
                    while curr_idx < len(rule["hypothesis_idxes"]) \
                            and 'OR' not in rule["hypothesis_operators"][curr_idx]:
                        curr_idx += 1

                    break

                if idx + 1 == len(rule["hypothesis_idxes"]) or 'OR' in rule["hypothesis_operators"][idx + 1]:
                    # Here always: clause_relevance == True
                    break

            if clause_relevance:
                relevance = True
                break
            # print(list(rule["line"].items())[h])
            # print(hypothesis_to_check)
        return relevance

    def is_correct(self, rule):
        # self.last_rule["conclusion_operators"]
        correctness = False
        curr_idx = 0
        while curr_idx < len(rule["conclusion_idxes"]):
            clause_correctness = True

            # AND clause loop.
            for idx, itm in list(enumerate(rule["conclusion_idxes"]))[curr_idx:]:
                func_eval = self.calculate_function(rule["conclusion_functions"][idx]["func_name"],
                                                    list(rule["lines"][0].values())[itm],
                                                    list(rule["lines"][1].values())[itm],
                                                    rule["conclusion_functions"][idx]["extra_parameters"])

                curr_idx = idx+1

                if 'NOT' in rule["conclusion_operators"][idx]:
                    func_eval = not func_eval

                if func_eval is False:
                    # clause failed. Advance to next clause (=next OR)
                    clause_correctness = False
                    while curr_idx < len(rule["conclusion_idxes"]) \
                            and 'OR' not in rule["conclusion_operators"][curr_idx]:
                        curr_idx += 1
                    break

                if idx + 1 == len(rule["conclusion_idxes"]) or 'OR' in rule["conclusion_operators"][idx+1]:
                    # Here always: clause_relevance == True
                    break

            if clause_correctness:
                correctness = True
                break

        return correctness

    def calculate_function(self, func_name, item1, item2, extra_parameters):
        if func_name == 'same_as':
            return self.same_as(item1, item2)
        elif func_name == 'member_in_common':
            return self.k_members_in_common(item1, item2, 1)
        elif func_name == 'k_members_in_common':
            return self.k_members_in_common(item1, item2, extra_parameters[0])
        elif func_name == 'lesser_equal':
            return self.lesser_equal(item1, item2, extra_parameters[0], extra_parameters[1])
        elif func_name == 'similar_to':
            # TODO This is a patch. Need to fix this
            return self.similar_to(item1, item2, extra_parameters[0], extra_parameters[1])
        elif func_name == 'similar_number_to':
            # TODO This is a patch. Need to fix this
            return self.similar_number_to(item1, item2, extra_parameters[0])
        else:
            return "Method calculate_function could not identify function"

    @staticmethod
    def same_as(item1, item2):
        return item1 == item2

    @staticmethod
    def k_members_in_common(list1, list2, k):
        """

        :param list1:
        :param list2:
        :param k: at least ciel(abs(k)) members in common
        :return: True iff there are at least k members in common
        """
        return len(set(list1).intersection(set(list2))) >= np.ceil(abs(k))

    @staticmethod
    def lesser_equal(item1, item2, additive_factor, multiplicative_factor):
        # if type(item1) != type(item2):
        #     print("*", item1, "*", item2, "*")
        #     print(str(type(item1)), "*", str(type(item2)))
        if type(item1) not in [int, float] or type(item2) not in [int, float]:
            return item1 == item2
        return item1 <= multiplicative_factor * item2 + additive_factor

    @staticmethod
    def similar_to(item1, item2, additive_factor, multiplicative_factor):
        return item1 == item2

    @staticmethod
    def similar_number_to(item1, item2, multiplicative_factor):
        if item1 == item2:
            return True
        if set([int, float]) or set([item1, item2]) != set([int, float]):
            return False
        if 0 in [item1, item2] or item1*item2 < 0:
            return False
        # factor = (np.abs(multiplicative_factor) - int(np.abs(multiplicative_factor))) / 5  # Max of 0.2
        # return np.max(item1, item2) - np.min(item1, item2) < np.max(np.abs(item1), np.abs(item2)) * factor
        factor = multiplicative_factor
        item_max = max(np.abs(item1), np.abs(item2))
        item_min = min(np.abs(item1), np.abs(item2))
        return item_max < item_min * factor


if __name__ == "__main__":

    # {"lines": lines, "hypothesis_idxes": rn.sample(hypothesis_indexes, rn.randint(3, 4)),
    #  "conclusion_idxes": rn.sample(conclusion_indexes, rn.randint(1, 2)),
    #  "hypothesis_functions": [], "conclusion_functions": [],
    #  "hypothesis_operators": [], "conclusion_operators": []}

    # {"func_name": chosen_func["name"],
    #  "extra_parameters": [self.generate_random_parameter_of_type(ty, chosen_func["name"]) for ty in
    #                       chosen_func["param_types"]]}

    # Same company different year.
    constraints1 = {"hypothesis_idxes": [16, 0],
                    "hypothesis_functions": [{"func_name": 'same_as', "extra_parameters": []},
                                             {"func_name": 'same_as', "extra_parameters": []}],
                    "hypothesis_operators": ['AND', 'AND NOT']}
    constraints2 = {"hypothesis_idxes": [6],
                    "hypothesis_functions": [{"func_name": 'lesser_equal', "extra_parameters": [0, 1.0]}],
                    "hypothesis_operators": ['AND']}
    constraints3 = {"hypothesis_idxes": [20],
                    "hypothesis_functions": [{"func_name": 'member_in_common', "extra_parameters": []}],
                    "hypothesis_operators": ['AND']}
    _rg = ConnectionRuleGenerator(constraints=constraints3)
    # _rg = ConnectionRuleGenerator(constraints=None)

    _t0 = t.time()

    for _ in range(1000):

        _rule = _rg.generate_random_rule()
        # print(_rule)
        # print(list(_rule['lines'][0].keys()))
        # print(list(_rule['lines'][0].keys()).index('director_list'))

        _rule_as_string = _rg.rule_to_string(_rule)
        # print(rule_as_string)

        _rule_score = _rg.calculate_correctness(_rule)

        # print(_rule_as_string)
        # # print(_rule["hypothesis_operators"])
        # # print(_rule["conclusion_operators"])
        # print(_rule_score)
        # print()

        # if _rule_score['relevance'] > 0:
        # if 0 < _rule_score['relevance'] < 1:
        # if _rule_score['correctness'] > 0:
        # _if _rule_score['relevance'] > 0 and _rule_score['correctness'] > _rule_score['conclusion_true']:
        if 0.1 < _rule_score['relevance'] < 0.9 and _rule_score['correctness'] > _rule_score['conclusion_true'] + 0.2:
            print(_rule_as_string)
            print(_rule_score)
            print()

    _t1 = t.time()

    print("Runtime: %.3f" % (_t1 - _t0))

    pass

    # print(_list_of_method_names)

