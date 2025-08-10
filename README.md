# Algorithmic Fairness amid Social Determinants: Reflection, Characterization, and Approach

> This repository contains the implementation accompanying our paper "Algorithmic Fairness amid Social Determinants: Reflection, Characterization, and Approach."

### Abstract

_Social determinants_ are variables that, while not directly pertaining to any specific individual, capture key aspects of contexts and environments that have direct causal influences on certain attributes of an individual. Previous algorithmic fairness literature has primarily focused on sensitive attributes, often overlooking the role of social determinants. Our paper addresses this gap by introducing formal and quantitative rigor into a space that has been shaped largely by qualitative proposals regarding the use of social determinants. To demonstrate theoretical perspectives and practical applicability, we examine a concrete setting of college admissions, using region as a proxy for social determinants. Our approach leverages a region-based analysis with Gamma distribution parameterization to model how social determinants impact individual outcomes. Despite its simplicity, our method quantitatively recovers findings that resonate with nuanced insights in previous qualitative debates, that are often missed by existing algorithmic fairness approaches. Our findings suggest that mitigation strategies centering solely around sensitive attributes may introduce new structural injustice when addressing existing discrimination. Considering both sensitive attributes and social determinants facilitates a more comprehensive explication of benefits and burdens experienced by individuals from diverse demographic backgrounds as well as contextual environments, which is essential for understanding and achieving fairness effectively and transparently.

---

### Requirements

- `python >= 3.9.6`
- `numpy >= 1.22.0`
- `scikit-learn >= 1.0.0`

### To run the code

- Open `pipeline.ipynb` and click `Run All` to run the Jupyter Notebook containing the implementation of our constrained optimization (based on UC summary statistics).

- Open `PUMS_enhanced.ipynb` and click `Run All` to run our implementation of PUMA-based data enhancement (connecting [Public-Use Microdata Sample](https://www.census.gov/programs-surveys/acs/microdata/access.html) to [Neighborhood Atlas](https://www.neighborhoodatlas.medicine.wisc.edu/) and [Social Vulnerability Index](https://www.atsdr.cdc.gov/place-health/php/svi/svi-data-documentation-download.html)).
