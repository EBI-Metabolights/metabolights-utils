# Overview

## MetaboLights Utilities
<!-- <img src="https://www.ebi.ac.uk/metabolights/img/MetaboLightsLogo.png" width="50" height="50" alt="Metabolights">  -->
<a href="https:/www.ebi.ac.uk/metabolights" target="_blank">
    <img src="https://img.shields.io/badge/Homepage-MetaboLights-blue" alt="MetaboLights">
</a>
<a href="https://github.com/EBI-Metabolights/metabolights-utils" target="_blank">
    <img src="https://img.shields.io/badge/Github-MetaboLights-blue" alt="MetaboLights Github">
</a>
<a href="https://isa-specs.readthedocs.io/en/latest/isatab.html" target="_blank">
    <img src="https://img.shields.io/badge/ISA--Tab-v1.0-blue" alt="ISA-Tab version">
</a>
<a href="https://github.com/EBI-Metabolights/metabolights-utils/blob/master/LICENCE" target="_blank">
    <img src="https://img.shields.io/badge/Licence-Apache%20v2.0-blue" alt="License">
</a>

![Python](https://img.shields.io/badge/Python-3.8%7C3.9%7C3.10%7C3.11%7C3.12-dark_blue)
![Coverage](https://img.shields.io/badge/Coverage-85%25-dark_blue)
![Lint](https://img.shields.io/badge/Lint-Ruff-dark_blue)


---
The `metaboligts-utils` is a *lightweight API* and *command line interface* (CLI) to use or search MetaboLights public studies, update your [ISA-Tab](https://isa-specs.readthedocs.io/en/latest/isatab.html) metadata files. 

---

## CLI Features
* Download and list MetaboLights public study metadata files.
* Search MetaboLights public studies [beta release].
* Download, upload and validate MetaboLights submitted studies
* Create assay file templates.

## API Features
* `Read and update ISA files` with minimum pyhton package dependency.
* Read MetaboLights study metadata files
* Calculate hash value of each ISA metadata file or study ISA metadata folder
* Read ISA table files (s_\*.txt, a_\*.txt, m_\*.txt) with **pagination support**.
* `Multi-column filters and sort options` on ISA table files.
* `Json serializable` models with [pydantic](https://github.com/pydantic/pydantic) library.

///

```Python hl_lines="1 4-6" title="test_assay_file.py"
--8<-- "metabolights_utils/isatab/test_assay_file.py:1:20"
```

///