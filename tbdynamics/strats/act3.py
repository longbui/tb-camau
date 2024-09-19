from summer2 import Stratification, Multiply
import numpy as np
from summer2.functions.time import get_sigmoidal_interpolation_function
from tbdynamics.constants import age_strata
from summer2.parameters import Parameter


def get_act3_strat(
    compartments,
    fixed_params,
) -> Stratification:

    # Extract the requested strata
    requested_strata = fixed_params["act3_stratification"]["strata"]
    proportions = fixed_params["act3_stratification"]["proportions"]
    prop_mixing_same_stratum = fixed_params["act3_stratification"]["prop_mixing_same_stratum"]
    # Create the stratification object
    strat = Stratification("act3", requested_strata, compartments)

    # Set the population proportions for each stratum
    strat.set_population_split(proportions)

    # Number of strata
    n_strata = len(requested_strata)

    # Initialize the mixing matrix
    mixing_matrix = np.zeros((n_strata, n_strata))

    # # Populate the mixing matrix based on within- and between-strata mixing
    for i in range(n_strata):
        for j in range(n_strata):
            if i == j:
                # If the individuals are in the same stratum, apply the within-stratum mixing proportion
                mixing_matrix[i, j] = prop_mixing_same_stratum
            else:
                # For between-strata mixing
                prop_pop_j = proportions[requested_strata[j]]
                prop_pop_non_i = sum(
                    [
                        proportions[requested_strata[k]]
                        for k in range(n_strata)
                        if k != i
                    ]
                )
                assert (
                    prop_pop_non_i > 0
                ), "Population proportions for non-i strata must be positive."
                mixing_matrix[i, j] = (
                    (1 - prop_mixing_same_stratum) * prop_pop_j / prop_pop_non_i
                )
    # Set the mixing matrix in the stratification object
    strat.set_mixing_matrix(mixing_matrix)
    adjustments = fixed_params["act3_stratification"]["adjustments"]
    adjustments["birth"] = proportions
    if "infection" in  adjustments:
        for stage in ["susceptible","late_latent", "recovered"]:
            flow_name = f"infection_from_{stage}"
            if flow_name not in adjustments:
                adjustments[flow_name] =  adjustments["infection"]
    # Apply the adjustments to flows (e.g., infection and detection)
    for flow_name, adjustment in adjustments.items():
        # Create the adjustment dictionary for each stratum
        if flow_name != "infection":
            adj = {stratum: Multiply(value) for stratum, value in adjustment.items()}
            strat.set_flow_adjustments(flow_name, adj)

  
    # adjust detection flow for act3 with active case finding, only for trial
    for age in age_strata:
        # Initialize adjustment for each age and strata
        intervention_adjustments = {stratum: 0.0 for stratum in requested_strata}

        if age not in [0, 5]:
            # Define intervention parameters
            intervention_stratum = "trial"
            times = [2014.25, 2014.26, 2018, 2018.2]
            vals = [
                0.0,  # Value for 2014
                1.9,  # Value for 2014.2
                1.9,  # Value for 2018
                0.0,  # Value for 2018.2
            ]

            # Generate interpolation function and set the adjustment
            intervention_adjustments[intervention_stratum] = get_sigmoidal_interpolation_function(times, vals)

        # Set the flow adjustments without needing to loop over interventions
        strat.set_flow_adjustments(
            "acf_detection", 
            {k: Multiply(v) for k, v in intervention_adjustments.items()},
            source_strata={"age": str(age)}
        )

    return strat
