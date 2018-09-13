import random as rn
import copy as cp

import handle_data.Data_File_Reader as data_reader

_data_file_name = data_reader._main_dir + "data/merged_data.csv"


class Rule_Generator:

    def __init__(self, data_file_name=_data_file_name):
        self.data = []
        self.last_rule = {}
        data_reader.load_data_file(self.data, data_file_name)
        pass

    def generate_random_rule(self):
        return self.generate_random_rule_for_line(rn.choice(self.data))

    def generate_random_rule_for_line(self, line):
        length = len(line)
        indexes = list(range(length))

        self.last_rule = {}
        self.last_rule["line"] = line
        self.last_rule["hypothesis"] = rn.sample(indexes, rn.randint(1, 3))
        self.last_rule["conclusion"] = rn.sample(indexes, rn.randint(1, 3))

        return cp.deepcopy(self.last_rule)

    def rule_to_string(self, rule='last rule'):
        if rule == 'last rule':
            rule = self.last_rule
        if rule is None:
            string_rule = ''
        else:
            string_rule = ''
            rule_line = list(rule["line"].items())

            string_rule = 'If (%s = %s' % (rule_line[rule["hypothesis"][0]][0], rule_line[rule["hypothesis"][0]][1])
            # print(rule_line[rule["hypothesis"][0]])
            # print(rule["hypothesis"][1:])

            for i in rule["hypothesis"][1:]:
                # print("GGG")
                # print(i)
                # print(rule_line[i][0])
                # print(rule_line[i][1])
                string_rule += ' and ' + (str(rule_line[i][0]) + ' = ' + str(rule_line[i][1]))

            string_rule += ')\nThen (%s = %s' % (
                rule_line[rule["conclusion"][0]][0], rule_line[rule["conclusion"][0]][1])

            for i in rule["conclusion"][1:]:
                string_rule += ' and ' + (str(rule_line[i][0]) + ' = ' + str(rule_line[i][1]))

            string_rule += ')'

        return cp.deepcopy(string_rule)

    def calculate_correctness(self, rule='last rule'):
        if rule == 'last rule':
            rule = self.last_rule
        ret_val = {"correctness": 0.0, "relevance": 0.0}
        sample_size = 100
        relevance_count = correctness_count = 0.0

        for _ in range(sample_size):
            line = rn.choice(self.data)
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
            actual_value = list(rule["line"].items())[h]
            hypothesis_to_check = list(line.items())[h]
            if actual_value != hypothesis_to_check:
                relevance=False
                break
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

    _rule = _rg.generate_random_rule()

    # _rg.rule_to_string(_rule)
    print(_rg.rule_to_string(_rule))

    print(_rg.calculate_correctness(_rule))

    pass