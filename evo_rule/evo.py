import time as t

from evo_core import Population_Containers as PopContainers
from evo_core import Evolution
from evo_core.evo_tools import Selection
from evo_core.evo_tools import MiscPhases
from evo_rule.RuleIndividual import MutationPhase, FitnessEvaluationPhase

from handle_data import ConnectionRuleGenerator as CRGen
import evo_rule.RuleIndividual as RuleInd

if __name__ == "__main__":
    Evolution._debug_output_flag = True
    num_of_generations = 30
    pop_size = 30
    # genome_len = 20
    rg = CRGen.ConnectionRuleGenerator()
    inds = [RuleInd.RuleIndividual(rg.generate_random_rule(), rg) for _ in range(pop_size)]
    pop = PopContainers.SimplePopulationWithElite(inds)
    # pop.update_pop(inds)

    calc_fitness = RuleInd.RuleIndividual.calculate_fitness
    get_fitness = RuleInd.RuleIndividual.get_fitness

    init_p = MiscPhases.SimpleInitPhase(num_of_generations)
    elite_e_p = Selection.SimpleExtractElitePhase(get_fitness, elite_size=3)
    elite_m_p = Selection.SimpleMergeElitePhase()
    select_p = Selection.TournamentSelectionPhase(get_fitness, tour_size=2)
    mut_p = MutationPhase(probability=0.2)
    eval_p = FitnessEvaluationPhase(fitness_calc_function=calc_fitness,
                                    fitness_getter_function=get_fitness)
    record_p = MiscPhases.MaintainBestsPhase(get_fitness)

    cyc = Evolution.Cycle([select_p, mut_p, eval_p, record_p])
    # cyc = Evolution.Cycle([elite_e_p, select_p, mut_p, elite_m_p, eval_p, record_p])
    ebody = Evolution.EpochBasicBody(cyc, init_p.check_gen_limit)
    epo = Evolution.Epoch(ebody, init_cycle=Evolution.Cycle([init_p, eval_p, record_p]))
    evo = Evolution.Evolution(epo)

    _t0 = t.time()
    evo.run(pop)
    _t1 = t.time()

    print("\nRuntime: %.3f" % (_t1 - _t0))
    print("Best ever individual")
    print(record_p.best_ever_ind.rule_to_string())
    print(record_p.best_ever_ind.scores)
    print("Fitness: %.5f" % record_p.best_ever_ind.fitness)

    pass
