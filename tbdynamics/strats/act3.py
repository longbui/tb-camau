from summer2 import Stratification, Multiply
import numpy as np

def get_act3_strat(
    compartments: list,
    act3_stratification: dict
) -> Stratification:

    # Extract the requested strata
    requested_strata = act3_stratification['strata']

    # Create the stratification object
    strat = Stratification("act3", requested_strata, compartments)

    # Set the population proportions for each stratum
    strat.set_population_split(act3_stratification['proportions'])

    # # Number of strata
    # n_strata = len(requested_strata)

    # # Initialize the mixing matrix
    # mixing_matrix = np.zeros((n_strata, n_strata))

    # # Populate the mixing matrix based on within- and between-strata mixing
    # for i in range(n_strata):
    #     for j in range(n_strata):
    #         if i == j:
    #             # If the individuals are in the same stratum, apply the within-stratum mixing proportion
    #             mixing_matrix[i, j] = act3_stratification['prop_mixing_same_stratum']
    #         else:
    #             # For between-strata mixing
    #             prop_pop_j = act3_stratification["proportions"][requested_strata[j]]
    #             prop_pop_non_i = sum([act3_stratification["proportions"][requested_strata[k]] for k in range(n_strata) if k != i])
    #             assert prop_pop_non_i > 0, "Population proportions for non-i strata must be positive."
    #             mixing_matrix[i, j] = (1 - act3_stratification['prop_mixing_same_stratum']) * prop_pop_j / prop_pop_non_i

    # # Apply the adjustments to flows (e.g., infection and detection)
    # for flow_name, adjustment in act3_stratification["adjustments"].items():
    #     # Create the adjustment dictionary for each stratum
    #     adj = {stratum: Multiply(value) for stratum, value in adjustment.items()}
    #     strat.set_flow_adjustments(flow_name, adj)

    # # Set the mixing matrix in the stratification object
    # strat.set_mixing_matrix(mixing_matrix)

    return strat
