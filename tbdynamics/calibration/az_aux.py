import arviz as az
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from .utils import convert_prior_to_numpyro


def tabulate_calib_results(
    idata: az.InferenceData, params_name
) -> pd.DataFrame:
    """
    Get tabular outputs from calibration inference object,
    except for the dispersion parameters, and standardize formatting.

    Args:
        idata: InferenceData object from ArviZ containing calibration outputs.
        priors: List of parameter names as strings.

    Returns:
        Calibration results table in standard format.
    """
    # Generate summary table
    table = az.summary(idata)

    # Filter out dispersion parameters
    table = table[~table.index.str.contains("_dispersion")]

    # Round and format the relevant columns
    for col_to_round in [
        "mean",
        "sd",
        "hdi_3%",
        "hdi_97%",
        "ess_bulk",
        "ess_tail",
        "r_hat",
    ]:
        table[col_to_round] = table.apply(
            lambda x: str(round(x[col_to_round], 3)), axis=1
        )

    # Create the HDI column
    table["hdi"] = table.apply(lambda x: f'{x["hdi_3%"]} to {x["hdi_97%"]}', axis=1)

    # Drop unnecessary columns
    table = table.drop(["mcse_mean", "mcse_sd", "hdi_3%", "hdi_97%"], axis=1)

    # Rename columns for standardized format
    table.columns = [
        "Mean",
        "Standard deviation",
        "ESS bulk",
        "ESS tail",
        "\\textit{\^{R}}",
        "High-density interval",
    ]
    table.index = table.index.map(lambda x: params_name.get(x, x))
    table.index.name = "Parameter"
    return table

def plot_post_prior_comparison(idata, priors, params_name):
    """
    Plot comparison of model posterior outputs against priors.

    Args:
        idata: Arviz inference data from calibration.
        priors: Dictionary of custom prior objects.
        params_name: Dictionary mapping parameter names to descriptive titles.

    Returns:
        The figure object.
    """
    # Filter priors to exclude those containing '_dispersion'
    req_vars = [var for var in priors.keys() if "_dispersion" not in var]
    num_vars = len(req_vars)
    num_rows = (num_vars + 1) // 2  # Ensure even distribution across two columns

    # Set figure size to match A4 page width (8.27 inches) in portrait mode and adjust height based on rows
    fig, axs = plt.subplots(num_rows, 2, figsize=(8.27, 2.3 * num_rows), gridspec_kw={'width_ratios': [1.5, 1.5]})  # A4 width in portrait mode
    axs = axs.ravel()

    for i_ax, ax in enumerate(axs):
        if i_ax < num_vars:
            var_name = req_vars[i_ax]
            posterior_samples = idata.posterior[var_name].values.flatten()
            low_post = np.min(posterior_samples)
            high_post = np.max(posterior_samples)
            x_vals_posterior = np.linspace(low_post, high_post, 100)

            numpyro_prior, prior_bounds = convert_prior_to_numpyro(priors[var_name])
            if prior_bounds:
                low_prior, high_prior = prior_bounds
                x_vals_prior = np.linspace(low_prior, high_prior, 100)
            else:
                x_vals_prior = (
                    x_vals_posterior  # Fallback if no specific prior bounds are given
                )

            # Compute the original prior density using NumPy's exp function
            prior_density = np.exp(numpyro_prior.log_prob(x_vals_prior))

            # Compute the posterior density using a kernel density estimate
            posterior_density = np.histogram(posterior_samples, bins=100, density=True)[
                0
            ]
            x_vals_posterior = np.linspace(low_post, high_post, len(posterior_density))

            ax.fill_between(
                x_vals_prior,
                prior_density,
                color="k",
                alpha=0.2,
                linewidth=2,
                label="Prior",
            )
            ax.plot(
                x_vals_posterior,
                posterior_density,
                color="b",
                linewidth=1,
                linestyle="solid",
                label="Posterior",
            )

            # Set the title using the descriptive name from params_name
            title = params_name.get(var_name, var_name)  # Use var_name if not in params_name
            ax.set_title(title, fontsize=12, fontname='Arial')  # Set title to Arial 12
            
            # Show legend only for the first plot
            if i_ax == 0:
                ax.legend()
        else:
            ax.axis("off")  # Turn off empty subplots if the number of req_vars is odd

    # Adjust padding and spacing
    plt.tight_layout(h_pad=1.0, w_pad=5)  # Increase padding between plots for better fit
    return fig


def plot_trace(idata: az.InferenceData, params_name: dict):
    """
    Plot trace plots for the InferenceData object, excluding parameters containing '_dispersion'.
    Adds descriptive titles from params_name.

    Args:
        idata: InferenceData object from ArviZ containing calibration outputs.
        params_name: Dictionary mapping parameter names to descriptive titles.

    Returns:
        trace_fig: The figure object containing trace plots.
    """
    plt.rcParams['font.family'] = 'Arial'
    # Filter out parameters containing '_dispersion'
    filtered_posterior = idata.posterior.drop_vars(
        [var for var in idata.posterior.data_vars if "_dispersion" in var]
    )

    # Plot trace plots with the filtered parameters
    az.plot_trace(
        filtered_posterior, figsize=(28, 3.1 * len(filtered_posterior.data_vars))
    )

    # Get the current figure
    trace_fig = plt.gcf()

    # Set titles for each row of plots
    var_names = list(filtered_posterior.data_vars)  # Get the list of variable names
    for i, var_name in enumerate(var_names):
        row_axes = trace_fig.axes[i * 2:i * 2 + 2]  # Get the axes in the current row (each param has 2 columns)
        title = params_name.get(var_name, var_name)  # Get the title from params_name or default to var_name
        row_axes[0].set_title(title, fontsize=34,loc="center")  # Set title for the first column
        row_axes[1].set_title("")  # Clear the title for the second column
        # Set tick label size for both x and y axis in the first plot (trace plot)
        row_axes[0].tick_params(axis='both', which='major', labelsize=24)

        # Set tick label size for the second plot (density plot)
        row_axes[1].tick_params(axis='both', which='major', labelsize=24)

    plt.tight_layout()

    return trace_fig 
