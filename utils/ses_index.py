import warnings
import pandas as pd
from utils.fips_parser import parse_fips


# ... Neighborhood Atlas (Updated ADI)
def calculate_puma_adi_rankings(
    puma_block_group_population_weights, adi_df, specific_index="ADI_NATRANK"
):
    """
    Calculate PUMA ADI national rankings as weighted averages of block group ADI rankings,
    where weights are based on block group populations.

    Parameters:
    -----------
    puma_block_group_population_weights : dict
        Dictionary mapping PUMA codes to dictionaries of {fips: population}
    adi_df : pd.DataFrame
        DataFrame mapping FIPS codes to ADI
    specific_index : str
        The column in adi_df to use for ADI rankings (default is "ADI_NATRANK")

    Returns:
    --------
    puma_adi_rankings : dict
        Dictionary mapping PUMA codes to their calculated ADI
    """
    puma_adi_rankings = {}

    adi_df[specific_index] = pd.to_numeric(adi_df[specific_index], errors="coerce")

    if specific_index == "ADI_NATRANK":
        UPPER_ADI_RANK = 100
    elif specific_index == "ADI_STATERNK":
        UPPER_ADI_RANK = 10
    else:
        raise ValueError(
            f"Unsupported specific_index: {specific_index}. Supported values are 'ADI_NATRANK' or 'ADI_STATERNK'."
        )

    adi_df_filtered = adi_df[
        (adi_df[specific_index] >= 1) & (adi_df[specific_index] <= UPPER_ADI_RANK)
    ]
    adi_df_filtered = adi_df_filtered.astype({specific_index: "int"})
    adi_dict = dict(
        zip(
            [
                parse_fips(_fips, data_source="neighborhood_atlas")[1]
                for _fips in adi_df_filtered["FIPS"]
            ],
            adi_df_filtered[specific_index],
        )
    )

    for puma_key, fips_population_dict in puma_block_group_population_weights.items():
        total_population = 0
        weighted_adi_sum = 0

        for fips, population in fips_population_dict.items():
            # Skip if FIPS not in ADI dictionary or population is zero/negative
            if fips not in adi_dict or population <= 0:
                # warnings.warn(
                #     f"FIPS {fips} not found in ADI dictionary or has zero population or corresponds to PH/GQ."
                # )
                continue

            adi_value = adi_dict[fips]
            weighted_adi_sum += adi_value * population
            total_population += population

        # Calculate weighted average if there's valid population data
        if total_population > 0:
            puma_adi_rankings[puma_key] = weighted_adi_sum / total_population
        # Handle the case where no valid population data exists for this PUMA
        # else:
        #     puma_adi_rankings[puma_key] = None

    return puma_adi_rankings


# ... Social Vulnerability Index (SVI)
def calculate_puma_svi_quantiles(
    puma_tract_population_weights, svi_df, specific_index="RPL_THEMES"
):
    """
    Calculate PUMA SVI quantiles as weighted averages of tract SVI quantiles, RPL_THEMES,
    where weights are based on tract populations.

    Parameters:
    -----------
    puma_tract_population_weights : dict
        Dictionary mapping PUMA codes to dictionaries of {fips: population}
    svi_df : pd.DataFrame
        DataFrame mapping FIPS codes to SVI quantile values
    specific_index : str
        The column in svi_df to use for SVI quantiles (default is "RPL_THEMES")

    Returns:
    --------
    puma_svi_quantiles : dict
        Dictionary mapping PUMA codes to their calculated SVI quantile values
    """
    puma_svi_quantiles = {}

    svi_df_filtered = svi_df[
        (svi_df[specific_index] >= 0) & (svi_df[specific_index] <= 1)
    ]
    svi_dict = dict(
        zip(
            [
                parse_fips(_fips, data_source="social_vulnerability_index")[1]
                for _fips in svi_df_filtered["FIPS"]
            ],
            svi_df_filtered[specific_index],
        )
    )

    for puma_key, fips_population_dict in puma_tract_population_weights.items():
        total_population = 0
        weighted_svi_sum = 0

        for fips, population in fips_population_dict.items():
            # Skip if FIPS not in SVI dictionary or population is zero
            if fips not in svi_dict or population <= 0:
                # warnings.warn(
                #     f"FIPS {fips} not found in SVI dictionary or has zero population."
                # )
                continue

            svi_value = svi_dict[fips]
            weighted_svi_sum += svi_value * population
            total_population += population

        # Calculate weighted average if there's population data
        if total_population > 0:
            puma_svi_quantiles[puma_key] = weighted_svi_sum / total_population
        # Handle the case where no valid population data exists for this PUMA
        # else:
        #     puma_svi_quantiles[puma_key] = None

    return puma_svi_quantiles
