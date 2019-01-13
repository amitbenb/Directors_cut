import time as t
import random as rn
import copy as cp
import numpy as np

from evo_core import Evolution
from evo_core.Population_Containers import Individual

import handle_data.ConnectionRuleGenerator as CRGen
import handle_data.RuleGenerator as RGen


class RuleIndividual(Individual):
    generator: CRGen.ConnectionRuleGenerator
    rule: dict

    def __init__(self, rule, generator, hypothesis_mutable=True, conclusion_mutable=True):
        self.rule = rule
        # print(rule)
        # input()
        self.generator = generator
        self.hypothesis_mutable = hypothesis_mutable
        self.conclusion_mutable = conclusion_mutable
        self.scores = None
        self.fitness = 0.0

    def self_replicate(self):
        rule = {i: cp.deepcopy(self.rule[i]) for i in self.rule if i != 'lines'}
        rule['lines'] = self.rule['lines']  # Deep copying this monstrosity takes too long.
        r = RuleIndividual(self.rule, self.generator, self.hypothesis_mutable, self.conclusion_mutable)
        r.scores = self.scores
        r.set_fitness(self.get_fitness())
        # return RuleIndividual(cp.deepcopy(self.rule), self.generator)
        return r

    def mutate(self):
        self.mutate_rule()
        # pass
        # print(self.rule)

    def rule_to_string(self):
        return self.generator.rule_to_string(self.rule)

    def mutate_rule(self):
        choice = rn.random()
        # if choice < 1.0:
        if choice < 1.0 / 5.0:
            self.drop_random_element_from_rule()
        elif choice < 2.0 / 5.0:
            self.add_random_element_to_rule()
        elif choice < 3.0 / 5.0:
            self.swap_random_element_in_rule()
        elif choice < 4.0 / 5.0:
            self.swap_rule_operator()
        else:
            self.tweak_rule_element()
            pass
        pass

    def drop_random_element_from_rule(self):
        hypothesis_flag = True if len(self.rule['hypothesis_idxes']) > 0 and not self.hypothesis_mutable else False
        conclusion_flag = True if len(self.rule['conclusion_idxes']) > 0 and not self.conclusion_mutable else False
        choice = None if not (hypothesis_flag or conclusion_flag) else ('conclusion' if not hypothesis_flag else (
            'hypothesis' if not conclusion_flag else rn.choice(['hypothesis', 'conclusion'])))
        if choice is not None:
            del_idx = rn.randint(0, len(self.rule[choice + '_idxes']) - 1)
            self.rule[choice + '_idxes'].__delitem__(del_idx)
            self.rule[choice + '_functions'].__delitem__(del_idx)
            self.rule[choice + '_operators'].__delitem__(del_idx)

    def add_random_element_to_rule(self):
        section_choices = []
        section_choices += ['conclusion'] if self.conclusion_mutable else []
        section_choices += ['hypothesis'] if self.hypothesis_mutable else []
        section_choices += [None] if section_choices == [] else []
        choice = rn.choice(section_choices)
        if choice is not None:
            lines = self.generator.sample_random_lines(2)

            self.generator.add_element_to_rule(lines, choice, self.rule)

    def swap_random_element_in_rule(self):
        hypothesis_flag = True if len(self.rule['hypothesis_idxes']) > 0 and not self.hypothesis_mutable else False
        conclusion_flag = True if len(self.rule['conclusion_idxes']) > 0 and not self.conclusion_mutable else False
        choice = None if not (hypothesis_flag or conclusion_flag) else ('conclusion' if not hypothesis_flag else (
            'hypothesis' if not conclusion_flag else ('conclusion' if rn.random() < 0.5 else 'hypothesis')))
        if choice is not None:
            lines = self.generator.sample_random_lines(2)
            element_idx = rn.randint(0, len(self.rule[choice + '_idxes']) - 1)
            self.generator.swap_element_in_rule(lines, choice, element_idx, self.rule)

    def swap_rule_operator(self):
        hypothesis_flag = True if len(self.rule['hypothesis_idxes']) > 0 and not self.hypothesis_mutable else False
        conclusion_flag = True if len(self.rule['conclusion_idxes']) > 0 and not self.conclusion_mutable else False
        choice = None if not (hypothesis_flag or conclusion_flag) else ('conclusion' if not hypothesis_flag else (
            'hypothesis' if not conclusion_flag else ('conclusion' if rn.random() < 0.5 else 'hypothesis')))
        if choice is not None:
            lines = self.generator.sample_random_lines(2)
            operator_idx = rn.randint(0, len(self.rule[choice + '_idxes']) - 1)
            self.generator.swap_operator_in_rule(lines, choice, operator_idx, self.rule)

    def tweak_rule_element(self):
        hypothesis_flag = True if len(self.rule['hypothesis_idxes']) > 0 and not self.hypothesis_mutable else False
        conclusion_flag = True if len(self.rule['conclusion_idxes']) > 0 and not self.conclusion_mutable else False
        choice = None if not (hypothesis_flag or conclusion_flag) else ('conclusion' if not hypothesis_flag else (
            'hypothesis' if not conclusion_flag else ('conclusion' if rn.random() < 0.5 else 'hypothesis')))
        if choice is not None:
            lines = self.generator.sample_random_lines(2)
            element_idx = rn.randint(0, len(self.rule[choice + '_idxes']) - 1)
            self.generator.tweak_element_in_rule(lines, choice, element_idx, self.rule)

    def calculate_fitness(self):
        # print("fitness")
        if self.get_fitness() == 0.0:
            self.scores = self.generator.calculate_correctness(self.rule)
        else:
            self.scores = self.generator.calculate_correctness(self.rule, factor=0.1)
        relevance, correctness, conclusion_true = self.scores['relevance'], self.scores['correctness'], self.scores[
            'conclusion_true']
        # fitness = 0 if conclusion_true == 0 else correctness / conclusion_true
        # fitness = 1 + (correctness - conclusion_true) * relevance * (1 - relevance)
        # fitness = 1 + (correctness - conclusion_true) * 2 * min(relevance, (1 - relevance))
        fitness = 1 + (correctness - conclusion_true) * 7 * min(1.0 / 7.0, relevance, (1 - relevance))
        # fitness = 1 + rn.random()

        self.set_fitness(fitness if self.get_fitness() == 0.0 else 0.9 * self.fitness + 0.1 * fitness)
        return self.fitness

    def get_fitness(self):
        return self.fitness

    def set_fitness(self, fitness):
        self.fitness = fitness
        return self.fitness


class MutationPhase(Evolution.EvoPhase):

    def __init__(self, probability=0.1):
        self.probability = probability

    def run(self, population):
        for ind in population:
            if rn.random() < self.probability:
                ind.mutate()

        return population


class FitnessEvaluationPhase(Evolution.EvoPhase):

    def __init__(self, fitness_calc_function, fitness_getter_function=None):
        self.fitness_calc_function = fitness_calc_function
        self.fitness_getter_function = fitness_getter_function \
            if fitness_getter_function is not None \
            else self.fitness_calc_function

    def run(self, population):
        for ind in population:
            # ind.calculate_fitness()
            self.fitness_calc_function(ind)
            # if rn.random() < 1:
            #     print("%s %.0f" % (str(ind.genome), ind.get_fitness()))

        print("Average fitness: %f" % (np.average([self.fitness_getter_function(ind) for ind in population])))
        print("Best fitness: %f" % (np.max([self.fitness_getter_function(ind) for ind in population])))
        print("Best individual in generation:")
        best_ind = max([ind for ind in population], key=lambda x: self.fitness_getter_function(x))
        print(best_ind.rule_to_string())
        print(best_ind.scores)

        return population
