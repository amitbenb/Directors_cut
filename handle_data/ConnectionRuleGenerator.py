import random as rn
import copy as cp
import time as t
import numpy as np

import handle_data.ConstantsAndUtil as ConstUtil
import handle_data.RuleGenerator as RuleGen
import handle_data.ListMembershipHashTable as HTable

# re.match(r'\d+[.]\d+','12.34')[0]=='12.34'
from handle_data.ConstantsAndUtil import _sample_size

_list_of_method_names = [
    {'name': 'member_in_common', 'types': [list], 'param_types': []},
    {'name': 'k_members_in_common', 'types': [list], 'param_types': [int]},
    {'name': 'same_as', 'types': [list, int, float, str, type(None)], 'param_types': []},
    # {'name': 'similar_to', 'types': [list, str], 'param_types': [int, float]},
    {'name': 'similar_number_to', 'types': [int, float], 'param_types': [float]},
    {'name': 'lesser_equal', 'types': [int, float], 'param_types': [int, float]},
    # {'name': 'greater_equal', 'types': [int, float], 'param_types': [int, float]},
    {'name': 'both_lesser_equal', 'types': [int, float], 'param_types': [float]},
    {'name': 'both_greater_equal', 'types': [int, float], 'param_types': [float]},
]
# _list_of_function_names = []


def random_sampler(generator, num_of_lines):
    return generator.sample_random_lines(num_of_lines)


def hash_same_sampler(generator, num_of_lines):
    return generator.sample_hash_shared_member_lines(num_of_lines)


class ConnectionRuleGenerator(RuleGen.RuleGenerator):
    def __init__(self, data_file_path=ConstUtil._data_file_path, constraints=None, unchanging_rule=None,
                 line_sampler=None, hash_key=None):
        RuleGen.RuleGenerator.__init__(self, data_file_name=data_file_path)
        # if hash_key is not None:
        #     print(self.data[0][hash_key])
        #     input()
        self.constraints = constraints
        self.unchanging_rule = unchanging_rule
        self.line_sampler = line_sampler if line_sampler is not None else random_sampler
        self.hash_key = hash_key
        self.hash_table = None if hash_key is None else HTable.ListMembershipHashTable()
        self.data_neighbors = [None for _ in self.data]
        if self.hash_table is not None:
            self.fill_up_table()
        self.hyp_gen_min = self.conc_gen_min = 0
        self.hyp_gen_max = self.conc_gen_max = 3
        pass

    def generate_random_rule(self):
        # print(len(self.data))
        # return self.generate_random_rule_for_lines(rn.sample(self.data, 2))
        # return self.generate_random_rule_for_lines(self.sample_random_lines(2))
        return self.generate_random_rule_for_lines(self.line_sampler(self, 2))

    def sample_random_lines(self, num_of_lines):
        # print("sample_random_lines")
        while True:
            # ret_val = [rn.choice(self.data)]
            line_indexes = [rn.choice(range(len(self.data)))]

            while len(line_indexes) < num_of_lines:
                # ret_val += [i for i in [rn.choice(self.data)] if self.constraints_met(ret_val, i)]
                # ret_val += [i for i in [rn.choice(self.data)] if
                #             self.constraints_met(ret_val, i) and i not in ret_val]
                line_indexes += [i for i in [rn.choice(range(len(self.data)))] if
                                 self.constraints_met(
                                     [self.data[j] for j in line_indexes], self.data[i]) and i not in line_indexes]
                if rn.random() < 0.001:
                    # Avoid infinite loop due to no viable choice existing
                    break

            if len(line_indexes) == num_of_lines:
                return [self.data[i] for i in line_indexes]

    def fill_up_table(self):
        """
        This method assumes line[self.hash_key] contains a list of keys for hash table and proceeds to insert the line
        into the hash table for each of these keys

        """
        # for line in self.data:
        #     my_list_of_keys = line[self.hash_key]
        #     for key in my_list_of_keys:
        #         self.hash_table.insert(line, key)
        for line_idx, line in enumerate(self.data):
            my_list_of_keys = line[self.hash_key]
            for key in my_list_of_keys:
                self.hash_table.insert(line_idx, key)

    def sample_hash_shared_member_lines(self, num_of_lines):
        while True:
            # ret_val = [rn.choice(self.data)]
            line_indexes = [rn.choice(range(len(self.data)))]
            keys = self.data[line_indexes[0]][self.hash_key]  # These are the keys one of which must be shared.

            while len(line_indexes) < num_of_lines:
                # All lines that share a key with first line.
                # candidate_lines = [line for key in keys for [_, line] in self.hash_table.find_all(key)]
                # candidate_lines = [line for key in keys for [_, line] in self.hash_table.find_all(key) if
                #                    line not in ret_val]
                # candidate_lines = [line for key in keys for line in self.hash_table.find_all(key) if
                #                    line not in ret_val]
                # candidate_lines = [line_idx for key in keys for line_idx in self.hash_table.find_all(key) if
                #                    line_idx not in line_indexes]
                # candidate_lines = list(set(candidate_lines))

                if self.data_neighbors[line_indexes[-1]] is None:
                    self.data_neighbors[line_indexes[-1]] = list(set(
                        [line_idx for key in keys for line_idx in self.hash_table.find_all(key) if
                         line_idx not in line_indexes and self.constraints_met([self.data[j] for j in line_indexes],
                                                                               self.data[line_idx])]))

                candidate_lines = self.data_neighbors[line_indexes[-1]]
                if len(candidate_lines) == 0:
                    break

                # print(keys[0])
                # print(self.hash_table.search(keys[0]))

                # ret_val += [i for i in [rn.choice(candidate_lines)]
                #             if self.constraints_met(ret_val, i)]
                # line_indexes += [i for i in [rn.choice(candidate_lines)]
                #                  if self.constraints_met([self.data[j] for j in line_indexes], self.data[i])]
                line_indexes += [rn.choice(candidate_lines)]
                if rn.random() < 0.001:
                    # Avoid infinite loop due to no viable choice existing
                    break

            if len(line_indexes) == num_of_lines:
                return [self.data[i] for i in line_indexes]

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
        # indexes = self.get_lengths_indexes_from_lines(lines)
        hypothesis_indexes, conclusion_indexes = self.get_lists_of_indexes_from_lines(lines)

        # hypothesis_indexes = [i for i in cp.deepcopy(indexes) if
        #                       (list(lines[0].items())[i][0]) in RuleGen._hypothesis_field_list]
        # conclusion_indexes = [i for i in cp.deepcopy(indexes) if
        #                       (list(lines[0].items())[i][0]) in RuleGen._conclusion_field_list]

        # print(hypothesis_indexes)
        # print(conclusion_indexes)

        # print(lines[0])
        self.last_rule = {"lines": lines, "hypothesis_idxes": rn.sample(hypothesis_indexes,
                                                                        rn.randint(self.hyp_gen_min, self.hyp_gen_max)),
                          "conclusion_idxes": rn.sample(conclusion_indexes,
                                                        rn.randint(self.conc_gen_min, self.conc_gen_max)),
                          "hypothesis_functions": [], "conclusion_functions": [],
                          "hypothesis_operators": [], "conclusion_operators": []}

        # print(self.last_rule["hypothesis_idxes"])
        # print(self.last_rule["conclusion_idxes"])
        # Choose rule functions
        for idx, itm in enumerate(self.last_rule["hypothesis_idxes"]):
            self.last_rule["hypothesis_functions"].append(
                self.generate_rule_function(list(lines[0].values())[itm],
                                            list(lines[1].values())[itm]))
            self.last_rule["hypothesis_operators"].append(rn.choice(['AND', 'OR', 'AND NOT', 'OR NOT']))

        for idx, itm in enumerate(self.last_rule["conclusion_idxes"]):
            self.last_rule["conclusion_functions"].append(
                self.generate_rule_function(list(lines[0].values())[itm],
                                            list(lines[1].values())[itm]))
            self.last_rule["conclusion_operators"].append(rn.choice(['AND', 'OR', 'AND NOT']))

        # # Allow for list membership rules.
        # for idx, itm in enumerate(self.last_rule["hypothesis"]):
        #     actual_item = (list(line.items()))[itm][1]
        #     if type(actual_item) is list and len(actual_item) > 0:
        #         # rule element contains index, name of the list, and a member of the list to search for.
        #         self.last_rule["hypothesis"][idx] = {'index': self.last_rule["hypothesis"][idx],
        #                                              'list_name': (list(line.items()))[itm][0],
        #                                              'member': rn.choice(actual_item)}

        return cp.deepcopy(self.last_rule)

    # @staticmethod
    # def get_lengths_indexes_from_lines(lines):
    #     lengths = [len(i) for i in lines]
    #     indexes = list(range(lengths[0]))
    #     return indexes

    @staticmethod
    def get_lists_of_indexes_from_lines(lines):
        lengths = [len(i) for i in lines]
        indexes = list(range(lengths[0]))
        hypothesis_indexes = [i for i in cp.deepcopy(indexes) if
                              (list(lines[0].items())[i][0]) in ConstUtil._hypothesis_field_list]
        conclusion_indexes = [i for i in cp.deepcopy(indexes) if
                              (list(lines[0].items())[i][0]) in ConstUtil._conclusion_field_list]
        return hypothesis_indexes, conclusion_indexes

    def add_element_to_rule(self, lines, hyp_or_conc, rule=None):
        """
        Currently for external use. Although can be used by generate_random_rule_for_lines after fixing (hopefully)

        :param lines: Data lines
        :param hyp_or_conc: Where in the rule to add the element: either 'hypothesis' or 'conclusion'
        :param rule:
        :return:
        """
        if rule is None:
            rule = self.last_rule
        # indexes = self.get_lengths_indexes_from_lines(lines)
        hypothesis_indexes, conclusion_indexes = self.get_lists_of_indexes_from_lines(lines)

        my_indexes = hypothesis_indexes if hyp_or_conc == 'hypothesis' else conclusion_indexes

        rule[hyp_or_conc + '_idxes'].append(rn.choice(my_indexes))
        rule[hyp_or_conc + "_functions"].append(
            self.generate_rule_function(list(lines[0].values())[rule[hyp_or_conc + '_idxes'][-1]],
                                        list(lines[1].values())[rule[hyp_or_conc + '_idxes'][-1]]))
        rule[hyp_or_conc + "_operators"].append(rn.choice(['AND', 'OR', 'AND NOT', 'OR NOT']))

    def swap_element_in_rule(self, lines, hyp_or_conc, element_idx, rule=None):
        """
        Currently for external use. Although can be used by generate_random_rule_for_lines after fixing (hopefully)

        :param lines: Data lines.
        :param hyp_or_conc: Where to in the rule swap the element: either 'hypothesis' or 'conclusion'.
        :param element_idx: Index of element to be swapped.
        :param rule:
        :return:
        """
        # indexes = self.get_lengths_indexes_from_lines(lines)
        hypothesis_indexes, conclusion_indexes = self.get_lists_of_indexes_from_lines(lines)
        my_indexes = hypothesis_indexes if hyp_or_conc == 'hypothesis' else conclusion_indexes

        rule[hyp_or_conc + '_idxes'][element_idx] = rn.choice(my_indexes)
        rule[hyp_or_conc + "_functions"][element_idx] = self.generate_rule_function(
            list(lines[0].values())[rule[hyp_or_conc + '_idxes'][element_idx]],
            list(lines[1].values())[rule[hyp_or_conc + '_idxes'][element_idx]])
        # Should I swap operator as well when swapping rule?
        # rule[hyp_or_conc + "_operators"][element_idx] = rn.choice(['AND', 'OR', 'AND NOT', 'OR NOT'])

    def swap_operator_in_rule(self, lines, hyp_or_conc, operator_idx, rule=None):
        """
        Currently for external use. Although can be used by generate_random_rule_for_lines after fixing (hopefully)

        :param lines: Data lines.
        :param hyp_or_conc: Where in the rule swap in the operator: either 'hypothesis' or 'conclusion'.
        :param operator_idx: Index of operator to be swapped.
        :param rule:
        :return:
        """
        # indexes = self.get_lengths_indexes_from_lines(lines)
        hypothesis_indexes, conclusion_indexes = self.get_lists_of_indexes_from_lines(lines)
        my_indexes = hypothesis_indexes if hyp_or_conc == 'hypothesis' else conclusion_indexes

        rule[hyp_or_conc + "_operators"][operator_idx] = rn.choice(['AND', 'OR', 'AND NOT', 'OR NOT'])

    def tweak_element_in_rule(self, lines, hyp_or_conc, element_idx, rule=None):
        """
        Currently for external use. Although can be used by generate_random_rule_for_lines after fixing (hopefully)

        :param lines: Data lines.
        :param hyp_or_conc: Where to in the rule tweak in the element: either 'hypothesis' or 'conclusion'.
        :param element_idx: Index of element to be swapped.
        :param rule:
        :return:
        """
        # indexes = self.get_lengths_indexes_from_lines(lines)
        hypothesis_indexes, conclusion_indexes = self.get_lists_of_indexes_from_lines(lines)
        my_indexes = hypothesis_indexes if hyp_or_conc == 'hypothesis' else conclusion_indexes

        # {"func_name": chosen_func["name"],
        #  "extra_parameters": [self.generate_random_parameter_of_type(ty, chosen_func["name"]) for ty in
        #                       chosen_func["param_types"]]}
        func_arguments = rule[hyp_or_conc + "_functions"][element_idx]["extra_parameters"]
        if len(func_arguments) > 0:
            chosen_param_idx = rn.choice(range(len(func_arguments)))
            func_arguments[chosen_param_idx] = self.minor_change_in_value(func_arguments[chosen_param_idx])

    @staticmethod
    def minor_change_in_value(val):
        factor = rn.random()/5 + 0.9  #  in [0.9, 1.1)
        ret_val = val * factor
        if type(float):
            pass
        elif type(int):
            ret_val = int(ret_val)
            if ret_val == val:
                ret_val += rn.choice([-1, 1])
        else:
            print("Something bad has happened in ConnectionRuleGenerator.minor_change_in_value")
            raise RuntimeError
        return ret_val

    def generate_rule_function(self, item1, item2):
        the_type1, the_type2 = type(item1), type(item2)
        the_type = the_type1 if the_type1 == the_type2 else type(None)

        list_of_candidates = [i for i in _list_of_method_names if the_type in i['types']]
        chosen_func = rn.choice(list_of_candidates)
        ret_val = {"func_name": chosen_func["name"],
                   "extra_parameters": [self.generate_random_parameter_of_type(ty, [item1, item2], chosen_func["name"])
                                        for ty in chosen_func["param_types"]]}
        # ret_val = {"func_name": "same_as", "extra_parameters": []}
        # ret_val = {"func_name": rn.choice(_list_of_method_names)['name'], "extra_parameters": ()}
        return ret_val

    @staticmethod
    def generate_random_parameter_of_type(the_type, items, func_name):
        """

        :param the_type: type of number to return (int of float)
        :param items: In some cases we need item values
        :param func_name:
        :return: Random number of the_type. biased to return 0/1.0 'default_prob' of the time
        """
        """

        """
        default_prob = 0.5
        if func_name == "similar_number_to":
            return 1.0 + rn.random()/5
        elif func_name == "both_lesser_equal":
            return float(min(items))
        elif func_name == "both_greater_equal":
            return float(max(items))
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

            # Ugly but necessary to have lines there:
            if self.unchanging_rule is not None:
                self.unchanging_rule["lines"] = rule["lines"]

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

            if self.unchanging_rule is not None and len(self.unchanging_rule["hypothesis_idxes"]) != 0:
                if 'NOT' in self.unchanging_rule["hypothesis_operators"][0]:
                    string_rule += 'NOT '

                for idx, itm in enumerate(self.unchanging_rule["hypothesis_idxes"]):
                    if idx != 0:
                        # string_rule += ' and '
                        string_rule += ' ' + self.unchanging_rule['hypothesis_operators'][idx] + ' '
                    # print(itm)
                    if type(itm) is int:
                        string_rule += (self.rule_element_to_string(self.unchanging_rule, idx, part='hypothesis'))
                    else:
                        print("What?!? type of item is not an int!")
                        print("rule_to_string() const hypothesis loop.")

                    if len(rule["hypothesis_idxes"]) != 0:
                        string_rule += ')\nAND if also ('

            if len(rule["hypothesis_idxes"]) != 0:
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

            if self.unchanging_rule is not None and len(self.unchanging_rule["conclusion_idxes"]) != 0:
                if 'NOT' in self.unchanging_rule["conclusion_operators"][0]:
                    string_rule += 'NOT '

                for idx, itm in enumerate(self.unchanging_rule["conclusion_idxes"]):
                    if idx != 0:
                        # string_rule += ' and '
                        string_rule += ' ' + self.unchanging_rule['conclusion_operators'][idx] + ' '
                    if type(itm) is int:
                        string_rule += (self.rule_element_to_string(self.unchanging_rule, idx, part='conclusion'))
                    else:
                        print("What?!? type of item is not an int!")
                        print("rule_to_string() hypothesis loop.")

                if len(rule["conclusion_idxes"]) != 0:
                    string_rule += ')\nAND also ('

            if len(rule["conclusion_idxes"]) != 0:
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

    def calculate_correctness(self, rule='last rule', factor=1.0):
        if rule == 'last rule':
            rule = self.last_rule
        ret_val = {"correctness": 0.0, "relevance": 0.0, "conclusion_true": 0.0}
        sample_size = int(_sample_size * factor)
        # mini_sample_size = _mini_sample_size
        conclusion_true_count = relevance_count = correctness_count = 0.0

        for _ in range(sample_size):
            # rule["lines"] = rn.sample(self.data, 2)
            # rule["lines"] = self.sample_random_lines(2)
            rule["lines"] = self.line_sampler(self, 2)

            # Ugly but necessary to have lines there:
            if self.unchanging_rule is not None:
                self.unchanging_rule["lines"] = rule["lines"]

            # print(line)
            # print(self.rule_to_string(rule))
            if self.is_relevant(rule) and (self.unchanging_rule is None or self.is_relevant(self.unchanging_rule)):
                relevance_count += 1
                if self.is_correct(rule) and (self.unchanging_rule is None or self.is_correct(self.unchanging_rule)):
                    correctness_count += 1
                    conclusion_true_count += 1
            else:
                if self.is_correct(rule) and (self.unchanging_rule is None or self.is_correct(self.unchanging_rule)):
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
        # if rule == self.unchanging_rule:
        #     print("Unchanging")
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

                # if rule == self.unchanging_rule:
                #     print(func_eval)
                if not func_eval:
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

        if len(rule["hypothesis_idxes"]) == 0:
            # Empty hypothesis rules are always relevant
            relevance = True

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

        if len(rule["conclusion_idxes"]) == 0:
            # Empty conclusion rules are always correct
            correctness = True

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
        elif func_name == 'both_lesser_equal':
            return self.both_lesser_equal(item1, item2, extra_parameters[0])
        elif func_name == 'both_greater_equal':
            return self.both_greater_equal(item1, item2, extra_parameters[0])
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
        # print(list1)
        # print(list2)
        # print(list(set(list1).intersection(set(list2))))
        # print(len(set(list1).intersection(set(list2))), np.ceil(abs(k)))
        # print(len(set(list1).intersection(set(list2))) >= np.ceil(abs(k)))
        # input()

        if type(list1) is not list or type(list2) is not list:
            print(type(list1), type(list2))
            print(list1)
            print(list2)
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

    @staticmethod
    def both_lesser_equal(item1, item2, lower_bound):
        if type(item1) not in [int, float] or type(item2) not in [int, float]:
            return False
        return item1 <= lower_bound and item2 <= lower_bound

    @staticmethod
    def both_greater_equal(item1, item2, lower_bound):
        if type(item1) not in [int, float] or type(item2) not in [int, float]:
            return False
        return item1 >= lower_bound and item2 >= lower_bound

    def get_indexes_for_keys(self, keys):
        rule = self.generate_random_rule()
        return [list(rule['lines'][0].keys()).index(key) for key in keys]


if __name__ == "__main__":

    # {"lines": lines, "hypothesis_idxes": rn.sample(hypothesis_indexes, rn.randint(3, 4)),
    #  "conclusion_idxes": rn.sample(conclusion_indexes, rn.randint(1, 2)),
    #  "hypothesis_functions": [], "conclusion_functions": [],
    #  "hypothesis_operators": [], "conclusion_operators": []}

    # {"func_name": chosen_func["name"],
    #  "extra_parameters": [self.generate_random_parameter_of_type(ty, chosen_func["name"]) for ty in
    #                       chosen_func["param_types"]]}

    # Same company different year.
    # _rg = ConnectionRuleGenerator(constraints=CRC.constraints3, unchanging_rule=CRC.unchanging_rule1)
    # _rg = ConnectionRuleGenerator(constraints=None, unchanging_rule=CRC.unchanging_rule2)
    # _rg = ConnectionRuleGenerator(constraints=CRC.constraints3, unchanging_rule=CRC.unchanging_rule3,
    #                               hash_key=None)
    # _rg = ConnectionRuleGenerator(constraints=CRC.constraints3, unchanging_rule=CRC.unchanging_rule3,
    #                               hash_key="director_list")
    # _rg = ConnectionRuleGenerator(constraints=CRC.constraints3, unchanging_rule=CRC.unchanging_rule3,
    #                               line_sampler=hash_same_sampler, hash_key="director_list")

    _rg = ConnectionRuleGenerator(constraints=None)

    _t0 = t.time()

    for _ in range(100):

        _rule = _rg.generate_random_rule()

        # print(_rule.keys())
        # print(list(_rule['lines'][0].keys()))
        # print(list(_rule['lines'][0].keys()).index('director_list'))
        # print(list(_rule['lines'][0].keys())[16])

        _rule_as_string = _rg.rule_to_string(_rule)
        # print(rule_as_string)

        _rule_score = _rg.calculate_correctness(_rule)

        # print(_rule["hypothesis_operators"])
        # print(_rule["conclusion_operators"])
        # print(_rule_as_string)
        # print(_rule_score)
        # print()

        # if _rule_score['relevance'] > 0:
        # if 0.0 < _rule_score['relevance'] < 1.0:
        # if _rule_score['correctness'] > 0:
        # _if _rule_score['relevance'] > 0 and _rule_score['correctness'] > _rule_score['conclusion_true']:
        if 0.1 < _rule_score['relevance'] < 0.9 and _rule_score['correctness'] > _rule_score['conclusion_true'] + 0.2:
            print(_rule)
            print([i for i in _rule])
            print(_rule_as_string)
            print(_rule_score)
            print()

    _t1 = t.time()

    print("Runtime: %.3f" % (_t1 - _t0))

    pass

    # print(_list_of_method_names)

