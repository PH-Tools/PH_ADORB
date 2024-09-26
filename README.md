# PH-ADORB (WIP):
#### *NOTE: This package is for research and testing purposes only.*
### A Python Package for calculating building 'ADORB' costs:


> A.D.O.R.B. cost: Annualized De-carbonization Of Retrofitted Buildings cost - a “full-cost-accounted” 
annualized life-cycle cost metric for building projects. It includes the (annualized) direct costs of 
retrofit and maintenance, direct energy costs, a carbon cost for both operating and embodied/upfront 
greenhouse gas emissions, and a renewable-energy system-transition cost based on the required 
electrical service capacity.
[[Phius Revive 2024 Retrofit Standard for Buildings v24.1.00]](https://www.phius.org/phius-revive-2024-standard-document)

- - - 
The ADORB cost is used as part of the  [Phius-REVIVE](https://www.phius.org/phius-revive-2024) building retrofit program. [Phius Research Committee](https://github.com/Phius-ResearchComittee) has an example implementation of the ADORB calculation which can be found on the [Phius GitHub repository](https://github.com/Phius-ResearchComittee/REVIVE/tree/main/REVIVE2024).


This new PH-ADORB library is an adaptation of Phius's original code into an object-oriented version. This library is a work-in-progress and should NOT be used for any actual Phius compliance analysis or reporting. 

#### *Note: PH-Tools and this PH-ADORB library is in no way affiliated with Phius, and the library here is neither reviewed, nor approved by Phius for use in complying with the REVIVE program.*


# Installation:
This package is [hosted on PyPi](https://pypi.org/project/PH-ADORB/). To install the latests version of the package:

```python
>>> pip install ph-adorb
```

# Development:

### Development [Local]:
PH-ADORB is free and open-source. We welcome any and all thoughts, opinions, and contributions! To get setup for local development:
1. **Fork** this GitHub repository to your own GitHub account.
1. **Clone** the repository-fork onto your computer.
1. Setup a **virtual environment**.
1. Install the required **dependencies**.
1. Make your edits or changes.
1. Add tests to cover your changes.
1. Submit a **Pull-Request** to merge your changes into the main branch.

### Development [Tests]:
Note that PH-ADORB uses [`pytest`](https://docs.pytest.org/en/stable/#) to run all of the automated testing. Please be sure to include tests for any contributions or edits.

### Development [Deployment]:
This package is [published on PyPi](https://pypi.org/project/PH-ADORB/). To deploy a new version:
1. Update the [pyproject.toml version number](https://github.com/PH-Tools/PH_ADORB/blob/f3bbed034b91088bd240a36227ffb841afd51859/pyproject.toml#L3)
1. Publish a new release through the GitHub repository page:
![Screenshot 2024-09-26 at 10 05 14 AM](https://github.com/user-attachments/assets/8e831f39-03ee-4704-8a78-f3353960b3ea)
1. This is will trigger the [ci.yaml](https://github.com/PH-Tools/PH_ADORB/blob/main/.github/workflows/ci.yaml) GitHub Action, build, and deploy the package.



# More Information:
For more information on the use of these tools, check out the the Passive House Tools website:
[https://www.PassiveHouseTools.com](https://www.PassiveHouseTools.com)

### Contact:
For questions about PH-ADORB, feel free to reach out at: PHTools@bldgtyp.com


![Tests](https://github.com/PH-Tools/ph_adorb/actions/workflows/ci.yaml/badge.svg)