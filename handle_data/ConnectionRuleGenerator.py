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
_mini_sample_size = 1000


class ConnectionRuleGenerator(RuleGen.RuleGenerator):
    def __init__(self):
        RuleGen.RuleGenerator.__init__(self, data_file_name=RuleGen._data_file_name)
        pass

    def generate_random_rule(self):
        # print(len(self.data))
        return self.generate_random_rule_for_lines(rn.sample(self.data, 2))

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
        self.last_rule = {"lines": lines, "hypothesis_idxes": rn.sample(hypothesis_indexes, rn.randint(1, 3)),
                          "conclusion_idxes": rn.sample(conclusion_indexes, rn.randint(1, 3)),
                          "hypothesis_functions": [], "conclusion_functions": []}

        # print(self.last_rule["hypothesis_idxes"])
        # print(self.last_rule["conclusion_idxes"])
        # Choose rule functions
        for idx, itm in enumerate(self.last_rule["hypothesis_idxes"]):
            self.last_rule["hypothesis_functions"].append(
                self.generate_rule_function(type(list(lines[0].values())[itm]),
                                            type(list(lines[1].values())[itm])))
            pass

        for idx, itm in enumerate(self.last_rule["conclusion_idxes"]):
            self.last_rule["conclusion_functions"].append(
                self.generate_rule_function(type(list(lines[0].values())[itm]),
                                            type(list(lines[1].values())[itm])))
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
                   "extra_parameters": [self.generate_random_parameter_of_type(t) for t in chosen_func["param_types"]]}
        # ret_val = {"func_name": "same_as", "extra_parameters": []}
        # ret_val = {"func_name": rn.choice(_list_of_method_names)['name'], "extra_parameters": ()}
        return ret_val

    @staticmethod
    def generate_random_parameter_of_type(the_type):
        """

        :param the_type: type of number to return (int of float)
        :return: Random number of the_type. biased to return 0/1.0 'default_prob' of the time
        """
        default_prob = 0.5
        if the_type is int:
            return 0 if rn.random() < default_prob else rn.randint(-100, 100)
        elif the_type is float:
            return 1.0 if rn.random() < default_prob else rn.random() * rn.choice([-2.0, 2.0])
        else:
            return None
        return ret_val

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

            string_rule = 'If ('

            for idx, itm in enumerate(rule["hypothesis_idxes"]):
                if idx != 0:
                    string_rule += ' and '
                # print(itm)
                if type(itm) is int:
                    string_rule += (self.rule_element_to_string(rule, idx, part='hypothesis'))
                else:
                    print("What?!? type of item is not an int!")
                    print("rule_to_string() hypothesis loop.")

            string_rule += ')\nThen ('
            # string_rule += (self.rule_element_to_string(rule_line[rule["conclusion"][0]]))

            for idx, itm in enumerate(rule["conclusion_idxes"]):
                if idx != 0:
                    string_rule += ' and '
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
        :return: A string represtenting the rule element.
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
            rule["lines"] = rn.sample(self.data, 2)
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

    def is_relevant(self, rule):
        relevance = True
        for idx, itm in enumerate(rule["hypothesis_idxes"]):
            func_eval = self.calculate_function(rule["hypothesis_functions"][idx]["func_name"],
                                                list(rule["lines"][0].values())[itm],
                                                list(rule["lines"][1].values())[itm],
                                                rule["hypothesis_functions"][idx]["extra_parameters"])
            if func_eval is False:
                relevance = False
                break

            # print(list(rule["line"].items())[h])
            # print(hypothesis_to_check)
        return relevance

    def is_correct(self, rule):
        # self.last_rule =
        # x ={"lines": lines, "hypothesis_idxes": rn.sample(hypothesis_indexes, rn.randint(1, 3)),
        #     "conclusion_idxes": rn.sample(conclusion_indexes, rn.randint(1, 3)),
        #  "hypothesis_functions": [], "conclusion_functions": []}
        #
        # y = {"func_name": chosen_func["name"],
        #      "extra_parameters": [self.generate_random_parameter_of_type(t) for t in chosen_func["param_types"]]}
        #
        # # def calculate_function(self, func_name, item1, item2, extra_parameters):

        correctness = True
        for idx, itm in enumerate(rule["conclusion_idxes"]):
            func_eval = self.calculate_function(rule["conclusion_functions"][idx]["func_name"],
                                                list(rule["lines"][0].values())[itm],
                                                list(rule["lines"][1].values())[itm],
                                                rule["conclusion_functions"][idx]["extra_parameters"])
            if func_eval is False:
                correctness = False
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
        if 0 in [item1, item2]:
            return False
        factor = (np.abs(multiplicative_factor) - int(np.abs(multiplicative_factor))) / 5  # Max of 0.2
        return np.max(item1, item2) - np.min(item1, item2) < np.max(np.abs(item1), np.abs(item2)) * factor


if __name__ == "__main__":
    _rg = ConnectionRuleGenerator()

    _t0 = t.time()

    for _ in range(1000):

        _rule = _rg.generate_random_rule()

        rule_as_string = _rg.rule_to_string(_rule)
        # print(rule_as_string)
        rule_score = _rg.calculate_correctness(_rule)

        # print(rule_as_string)
        # print(rule_score)
        # print()

        # if rule_score['relevance'] > 0:
        # if 0 < rule_score['relevance'] < 1:
        # if rule_score['correctness'] > 0:
        # if rule_score['relevance'] > 0 and rule_score['correctness'] == rule_score['conclusion_true']:
        if 0.1 < rule_score['relevance'] < 0.9 and rule_score['correctness'] > rule_score['conclusion_true'] + 0.1:
            print(rule_as_string)
            print(rule_score)
            print()

    _t1 = t.time()

    print("Runtime: %.3f" % (_t1 - _t0))

    pass

    # print(_list_of_method_names)

