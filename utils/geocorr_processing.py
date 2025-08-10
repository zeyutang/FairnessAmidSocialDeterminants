import csv
import json
import pickle
from collections import defaultdict


# ... Process Geocorr 2022 file (CensusBlockGroup to PUMA)
def generate_geocorr_dictionary(
    csv_file_path, save_dict_path=None, save_format="pickle"
):
    """
    Generate a dictionary from geocorr2022 CSV file.

    Parameters:
    -----------
    csv_file_path : str
        Path to the geocorr2022 CSV file
    save_dict_path : str
        Path where the dictionary will be saved
    save_format : str
        Format to save the dictionary ('pickle' or 'json')
        Default is 'pickle' for better performance with large datasets

    Returns:
    --------
    dict
        The generated dictionary with PUMA keys and tract/block group data
    """

    # Initialize the dictionary with defaultdict for automatic list initialization
    geocorr_dict = defaultdict(
        lambda: {
            "state_county": [],
            "census_tract": [],
            "census_block_group": [],
            "population_2020": [],
            "cbg_to_puma_alloc_factor": [],
        }
    )

    with open(csv_file_path, "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)

        # Skip the explanation row (second row)
        # The DictReader automatically uses the first row as headers
        next(csv_reader)  # skip the explanation row

        for row in csv_reader:
            # Extract required fields
            state_code = row["state"].zfill(2)  # Ensure 2-digit format
            puma_code = row["puma22"].zfill(5)  # Ensure 5-digit format

            # Create 7-digit key
            puma_key = str(state_code) + str(puma_code)

            # Extract data fields
            state_county = row["county"]  # 5-digit SSCCC
            census_tract = row["tract"]
            census_block_group = row["blockgroup"]
            population_2020 = row["pop20"]
            alloc_factor = row["afact"]

            # Append to the appropriate lists
            geocorr_dict[puma_key]["state_county"].append(state_county)
            geocorr_dict[puma_key]["census_tract"].append(census_tract)
            geocorr_dict[puma_key]["census_block_group"].append(census_block_group)
            geocorr_dict[puma_key]["population_2020"].append(population_2020)
            geocorr_dict[puma_key]["cbg_to_puma_alloc_factor"].append(alloc_factor)

    # Convert defaultdict to regular dict for saving
    geocorr_dict = dict(geocorr_dict)

    # Save the dictionary
    if None is not save_dict_path:
        if save_format.lower() == "json":
            with open(save_dict_path, "w", encoding="utf-8") as f:
                json.dump(geocorr_dict, f, indent=2)
        elif save_format.lower() == "pickle":
            with open(save_dict_path, "wb") as f:
                pickle.dump(geocorr_dict, f)
        else:
            raise ValueError("save_format must be either 'json' or 'pickle'")

    print(f"Dictionary generated with {len(geocorr_dict)} PUMA keys")
    print(f"Saved to: {save_dict_path}")

    return geocorr_dict


def load_geocorr_dictionary(dict_path, load_format="pickle"):
    """
    Load a previously saved geocorr dictionary.

    Parameters:
    -----------
    dict_path : str
        Path to the saved dictionary file
    load_format : str
        Format of the saved dictionary ('pickle' or 'json')

    Returns:
    --------
    dict
        The loaded dictionary
    """
    if load_format.lower() == "json":
        with open(dict_path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif load_format.lower() == "pickle":
        with open(dict_path, "rb") as f:
            return pickle.load(f)
    else:
        raise ValueError("load_format must be either 'json' or 'pickle'")


def get_puma_info(geocorr_dict, state_code, puma_code):
    """
    Retrieve information for a specific PUMA.

    Parameters:
    -----------
    geocorr_dict : dict
        The geocorr dictionary
    state_code : str
        2-digit state code
    puma_code : str
        5-digit PUMA code

    Returns:
    --------
    dict or None
        Dictionary with tract and block group information, or None if not found
    """
    puma_key = str(state_code).zfill(2) + str(puma_code).zfill(5)
    return geocorr_dict.get(puma_key)


def print_puma_summary(geocorr_dict, state_code, puma_code):
    """
    Print a summary of data for a specific PUMA.

    Parameters:
    -----------
    geocorr_dict : dict
        The geocorr dictionary
    state_code : str
        2-digit state code
    puma_code : str
        5-digit PUMA code
    """
    puma_key = str(state_code).zfill(2) + str(puma_code).zfill(5)
    if puma_key in geocorr_dict:
        data = geocorr_dict[puma_key]
        print(f"PUMA {puma_key} Summary:")
        print(f"  Number of census tracts: {len(data['census_tract'])}")
        print(f"  Number of census block groups: {len(data['census_block_group'])}")
        print(f"  Total entries: {len(data['population_2020'])}")

        # Calculate total population if numeric
        try:
            total_pop = sum(float(pop) for pop in data["population_2020"] if pop)
            print(f"  Total population (2020): {total_pop:,.0f}")
        except (ValueError, TypeError):
            print("  Population data contains non-numeric values")
    else:
        print(f"PUMA {puma_key} not found in dictionary")


# ... Weighted population calculation
def calculate_weights(geocorr_dict, mode):
    """
    Calculate population weights for census tracts or block groups.

    Parameters:
    -----------
    geocorr_dict : dict
        Dictionary with 7-digit PUMA keys containing lists of geographic and population data
    mode : str
        Either "census_tract_level" or "census_block_group_level"

    Returns:
    --------
    dict
        Dictionary with 7-digit PUMA keys and weighted population data
    """

    if mode not in ["census_tract_level", "census_block_group_level"]:
        raise ValueError(
            "Mode must be either 'census_tract_level' or 'census_block_group_level'"
        )

    result_dict = {}

    for puma_key, puma_data in geocorr_dict.items():
        if mode == "census_tract_level":
            result_dict[puma_key] = _calculate_tract_level_weights(puma_data)
        elif mode == "census_block_group_level":
            result_dict[puma_key] = _calculate_block_group_level_weights(puma_data)

    return result_dict


def _calculate_tract_level_weights(puma_data):
    """
    Calculate weights at census tract level by summing products for each unique tract.

    Parameters:
    -----------
    puma_data : dict
        Dictionary containing lists of geographic and population data

    Returns:
    --------
    dict
        Dictionary with 11-digit FIPS codes as keys and weighted populations as values
    """
    # Dictionary to accumulate weights for each unique tract
    tract_weights = defaultdict(float)

    # Iterate through all entries
    for i in range(len(puma_data["census_tract"])):
        state_county = puma_data["state_county"][i]
        tract = puma_data["census_tract"][i]
        population = (
            float(puma_data["population_2020"][i])
            if puma_data["population_2020"][i]
            else 0.0
        )
        alloc_factor = (
            float(puma_data["cbg_to_puma_alloc_factor"][i])
            if puma_data["cbg_to_puma_alloc_factor"][i]
            else 0.0
        )

        # Construct 11-digit FIPS code (SSCCCTTTTTT)
        # state_county should be SSCCC (5 digits)
        # tract should be TTTTTT (6 digits)
        fips_11_digit = state_county + tract.replace(".", "").zfill(6)

        # Calculate weighted population and add to tract total
        weighted_population = population * alloc_factor
        tract_weights[fips_11_digit] += weighted_population

    return dict(tract_weights)


def _calculate_block_group_level_weights(puma_data):
    """
    Calculate weights at census block group level.

    Parameters:
    -----------
    puma_data : dict
        Dictionary containing lists of geographic and population data

    Returns:
    --------
    dict
        Dictionary with 12-digit FIPS codes as keys and weighted populations as values
    """
    block_group_weights = {}

    # Iterate through all entries
    for i in range(len(puma_data["census_tract"])):
        state_county = puma_data["state_county"][i]
        tract = puma_data["census_tract"][i]
        block_group = puma_data["census_block_group"][i]
        population = (
            float(puma_data["population_2020"][i])
            if puma_data["population_2020"][i]
            else 0.0
        )
        alloc_factor = (
            float(puma_data["cbg_to_puma_alloc_factor"][i])
            if puma_data["cbg_to_puma_alloc_factor"][i]
            else 0.0
        )

        # Construct 12-digit FIPS code (SSCCCTTTTTTG)
        # state_county should be SSCCC (5 digits)
        # tract should be TTTTTT (6 digits)
        # block_group should be G (1 digit)
        tract_formatted = tract.replace(".", "").zfill(6)
        fips_12_digit = state_county + tract_formatted + str(block_group)

        # Calculate weighted population
        weighted_population = population * alloc_factor
        block_group_weights[fips_12_digit] = weighted_population

    return block_group_weights


def print_weight_summary(weight_dict, mode, top_n=5):
    """
    Print a summary of the calculated weights.

    Parameters:
    -----------
    weight_dict : dict
        Result from calculate_weights function
    mode : str
        The mode used for calculation
    top_n : int
        Number of top entries to display per PUMA
    """
    print(f"Weight Calculation Summary ({mode})")
    print("=" * 50)

    for puma_key, weights in weight_dict.items():
        print(f"\nPUMA {puma_key}:")
        print(f"  Total entries: {len(weights)}")

        if weights:
            total_weight = sum(weights.values())
            print(f"  Total weighted population: {total_weight:,.2f}")

            # Show top entries
            top_entries = sorted(weights.items(), key=lambda x: x[1], reverse=True)[
                :top_n
            ]
            print(f"  Top {min(top_n, len(top_entries))} entries:")
            for fips, weight in top_entries:
                if mode == "census_tract_level":
                    print(f"    Tract {fips}: {weight:,.2f}")
                else:
                    print(f"    Block Group {fips}: {weight:,.2f}")


def validate_geocorr_dict_structure(geocorr_dict):
    """
    Validate that the geocorr dictionary has the expected structure.

    Parameters:
    -----------
    geocorr_dict : dict
        Dictionary to validate

    Returns:
    --------
    bool
        True if structure is valid, raises exception otherwise
    """
    required_keys = [
        "state_county",
        "census_tract",
        "census_block_group",
        "population_2020",
        "cbg_to_puma_alloc_factor",
    ]

    for puma_key, data in geocorr_dict.items():
        if not isinstance(data, dict):
            raise ValueError(f"Data for PUMA {puma_key} is not a dictionary")

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key '{key}' in PUMA {puma_key}")

            if not isinstance(data[key], list):
                raise ValueError(f"Key '{key}' in PUMA {puma_key} is not a list")

        # Check that all lists have the same length
        list_lengths = [len(data[key]) for key in required_keys]
        if len(set(list_lengths)) > 1:
            raise ValueError(
                f"Lists in PUMA {puma_key} have different lengths: {list_lengths}"
            )

    return True
