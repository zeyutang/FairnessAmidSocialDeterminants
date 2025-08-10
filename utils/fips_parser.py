def parse_fips(fips_code, data_source):
    """
    Parse FIPS codes from different data sources into standardized components.

    Parameters:
    -----------
    fips_code : str
        The FIPS code to parse
    data_source : str
        The source of the FIPS code, either "neighborhood_atlas" or "social_vulnerability_index"

    Returns:
    --------
    geocorr_format : dict[str, str]
        A dictionary containing the parsed components according to geocorr_2022 format
    target_fips_str : str
        The FIPS code formatted as a string with leading zeros
    """
    # Ensure the FIPS code is a string
    fips_code = str(fips_code).strip()

    # Handle different data sources
    if data_source == "neighborhood_atlas":
        # Should be 12-digit FIPS, but might have leading zeros omitted
        # Format: SSCCCTTTTTTG

        # Pad to ensure 12 digits
        fips_code = fips_code.zfill(12)

        # Extract components
        state_code = fips_code[:2]
        county_code = fips_code[2:5]
        tract_code = fips_code[5:11]
        block_group = fips_code[11]

    elif data_source == "social_vulnerability_index":
        # Should be 11-digit FIPS, but might have leading zeros omitted
        # Format: SSCCCTTTTTT

        # Pad to ensure 11 digits
        fips_code = fips_code.zfill(11)

        # Extract components
        state_code = fips_code[:2]
        county_code = fips_code[2:5]
        tract_code = fips_code[5:11]
        block_group = "0"  # Not provided in this format

    else:
        raise ValueError(f"Unsupported data source: {data_source}")

    # Format tract code with decimal point (TTTT.TT)
    formatted_tract = tract_code[:4] + "." + tract_code[4:]

    # Prepare output in geocorr_2022 format
    geocorr_format = {
        "state": state_code,
        "county": state_code + county_code,
        "census_tract": formatted_tract,
        "census_block_group": block_group,
    }

    target_fips_str = fips_code

    return geocorr_format, target_fips_str
