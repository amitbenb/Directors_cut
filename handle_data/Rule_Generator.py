import random as rn
import copy as cp

import handle_data.Data_File_Reader as data_reader

_data_file_name = data_reader._main_dir + "data/merged_data.csv"
_hypothesis_field_list = ['fyear', 'log_ta', 'mtb', 'debtat', 'roa', 'sic', 'group_comp_id', 'list_of_dmcs', 'director_list']
_conclusion_field_list = ['dam_option_awards', 'dam_stock', 'dam_acc', 'dam_abs', 'dam_rel']
_sample_size = 100


class Rule_Generator:

    def __init__(self, data_file_name=_data_file_name):
        self.data = []
        self.last_rule = {}
        data_reader.load_data_file(self.data, data_file_name)
        pass

    def generate_random_rule(self):
        return self.generate_random_rule_for_line(rn.choice(self.data))

    def generate_rosit_rule(self):
        return self.generate_rosit_rule_for_line(rn.choice(self.data))

    def generate_rosit_rule_for_line(self, line):
        length = len(line)
        indexes = list(range(length))

        # hypothesis_indexes = [i for i in cp.deepcopy(indexes) if not (list(line.items())[i][0]).startswith('dam')]
        # conclusion_indexes = [i for i in cp.deepcopy(indexes) if (list(line.items())[i][0]).startswith('dam')]
        hypothesis_indexes = [i for i in cp.deepcopy(indexes) if (list(line.items())[i][0]) in _hypothesis_field_list]
        conclusion_indexes = [i for i in cp.deepcopy(indexes) if (list(line.items())[i][0]) in _conclusion_field_list]

        self.last_rule = {}
        self.last_rule["line"] = line
        self.last_rule["hypothesis"] = rn.sample(hypothesis_indexes, rn.randint(1, 3))
        self.last_rule["conclusion"] = rn.sample(conclusion_indexes, rn.randint(1, 3))
        # self.last_rule["hypothesis"] = [17]  # To get list_of_dmcs
        # self.last_rule["hypothesis"] = rn.sample(hypothesis_indexes, rn.randint(1, 1))
        # self.last_rule["conclusion"] = rn.sample(conclusion_indexes, rn.randint(1, 1))

        # Allow for list membership rules.
        for idx, itm in enumerate(self.last_rule["hypothesis"]):
            actual_item = (list(line.items()))[itm][1]
            if type(actual_item) is list and len(actual_item) > 0:
                # rule element contains index, name of the list, and a member of the list to search for.
                self.last_rule["hypothesis"][idx] = {'index': self.last_rule["hypothesis"][idx],
                                                     'list_name': (list(line.items()))[itm][0],
                                                     'member': rn.choice(actual_item)}

        return cp.deepcopy(self.last_rule)

    def generate_random_rule_for_line(self, line):
        length = len(line)
        indexes = list(range(length))

        self.last_rule = {}
        self.last_rule["line"] = line
        self.last_rule["hypothesis"] = rn.sample(indexes, rn.randint(1, 3))
        self.last_rule["conclusion"] = rn.sample(indexes, rn.randint(1, 3))
        # self.last_rule["hypothesis"] = rn.sample(indexes, rn.randint(1, 1))
        # self.last_rule["conclusion"] = rn.sample(indexes, rn.randint(1, 1))

        return cp.deepcopy(self.last_rule)

    def rule_to_string(self, rule='last rule'):
        if rule == 'last rule':
            rule = self.last_rule
        if rule is None:
            string_rule = ''
        else:
            string_rule = ''
            rule_line = list(rule["line"].items())

            string_rule = 'If ('
            # string_rule = '%s = %s' % (rule_line[rule["hypothesis"][0]][0], rule_line[rule["hypothesis"][0]][1])
            # print("Rule: ", rule)
            # print("Rule Line: ", rule_line)
            # print(rule["hypothesis"][0])
            # print(len(rule_line))
            # print("XXX ", rule_line)

            # itm = rule["hypothesis"][0]
            #
            # if type(itm) is int:
            #     # print("YYY")
            #     string_rule += (self.rule_element_to_string(rule_line[itm]))
            # else:  # type(rule["hypothesis"][0]) is dict
            #     # print(i)
            #     # print(type(rule_line[i['index']][1]))
            #     string_rule += (self.rule_element_to_string(rule_line[itm['index']], itm['member']))
            # # print(rule_line[rule["hypothesis"][0]])
            # # print(rule["hypothesis"][1:])

            for idx, itm in enumerate(rule["hypothesis"]):
                # print("GGG")
                # print(i)
                # print(rule_line[i][0])
                # print(rule_line[i][1])
                # string_rule += ' and ' + (str(rule_line[i][0]) + ' = ' + str(rule_line[i][1]))
                # string_rule += ' and ' + (self.rule_element_to_string(rule_line[i]))
                if idx != 0:
                    string_rule += ' and '
                if type(itm) is int:
                    string_rule += (self.rule_element_to_string(rule_line[itm]))
                else:  # type(i) is dict
                    # print(i)
                    # print(type(rule_line[i['index']][1]))
                    string_rule += (self.rule_element_to_string(rule_line[itm['index']], itm['member']))

            string_rule += ')\nThen '
            # string_rule += (self.rule_element_to_string(rule_line[rule["conclusion"][0]]))

            for idx, itm in enumerate(rule["conclusion"]):
                if idx != 0:
                    string_rule += ' and '
                string_rule += (self.rule_element_to_string(rule_line[itm]))

            string_rule += ')'

        return cp.deepcopy(string_rule)

    def rule_element_to_string(self, element, list_member=None):
        if type(element) is int:
            print("WHAT!?!")
            string_rule = '%s is in %s' % (element['member'], element['list_name'])
        elif type(element[1]) is str:
            string_rule = '%s = %s' % (element[0], element[1])
        elif type(element[1]) is list:
            if list_member is not None:
                string_rule = '%s is in %s' % (list_member, element[0])
            else:
                string_rule = '%s = %s' % (element[0], str(element[1]))
        else:
            print("Element: ", element)
        # if type(element[1]) is dict:
        #     print(element[1])
        #     print('fffff')


        return string_rule

    def calculate_correctness(self, rule='last rule'):
        if rule == 'last rule':
            rule = self.last_rule
        ret_val = {"correctness": 0.0, "relevance": 0.0}
        sample_size = _sample_size
        relevance_count = correctness_count = 0.0

        for _ in range(sample_size):
            line = rn.choice(self.data)
            # print(line)
            # print(self.rule_to_string(rule))
            if self.is_relevant(rule, line):
                relevance_count += 1
                if self.is_correct(rule, line):
                    correctness_count += 1

        ret_val["relevance"] = relevance_count / sample_size
        ret_val["correctness"] = correctness_count / max(relevance_count, 0.1)  # Do not divide by zero!
        return ret_val

    def is_relevant(self, rule, line):
        relevance = True
        for h in rule["hypothesis"]:
            if type(h) is int:
                actual_value = list(rule["line"].items())[h]
                hypothesis_to_check = list(line.items())[h]  # This is a tuple
                if actual_value != hypothesis_to_check:
                    relevance = False
                    break
            else:  # type(h) is dict
                # print("What now?")
                # actual_value = list(rule["line"].items())[h['index']]
                hypothesis_to_check = list(line.items())[h['index']]  # List to search in
                member = h['member']  # Possible member of list

                if member not in hypothesis_to_check[1]:
                    relevance = False
                    # print(hypothesis_to_check[1])
                    # print(member)
                    # input("Pause! Member not found for hypothesis")
                    break
                else:
                    # print(hypothesis_to_check[1])
                    # print(member)
                    # input("Pause! Member found for hypothesis")
                    pass

                # print(actual_value)
                # print(hypothesis_to_check)
                # print(member)
                # input("Pause!")

            # print(list(rule["line"].items())[h])
            # print(hypothesis_to_check)
        return relevance

    def is_correct(self, rule, line):
        correctness = True
        for c in rule["conclusion"]:
            actual_value = list(rule["line"].items())[c]
            conclusion_to_check = list(line.items())[c]
            if actual_value != conclusion_to_check:
                correctness=False
                break
            # print(list(rule["line"].items())[c])
            # print(conclusion_to_check)
        return correctness


if __name__ == "__main__":
    _rg = Rule_Generator()

    for _ in range(30):

        # _rule = _rg.generate_random_rule()
        _rule = _rg.generate_rosit_rule()

        # _rg.rule_to_string(_rule)
        print(_rg.rule_to_string(_rule))

        print(_rg.calculate_correctness(_rule))

    pass