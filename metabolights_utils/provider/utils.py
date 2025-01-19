import io
import json
import logging
import os
import re
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Union

import httpx

from metabolights_utils.models.isa.assay_file import AssayFile
from metabolights_utils.models.isa.common import AssayTechnique
from metabolights_utils.models.metabolights.model import MetabolightsStudyModel

logger = logging.getLogger(__name__)


def is_metadata_file(file_path: str):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        filename = os.path.basename(file_path)
        return is_metadata_filename_pattern(filename)
    return False


def is_metadata_filename_pattern(filename: str):
    if not filename:
        return False
    if len(filename) > 6:
        if filename[:2] in ("a_", "s_", "i_") and filename.endswith(".txt"):
            return True
        elif filename.startswith("m_") and filename.endswith(".tsv"):
            return True
    return False


def download_file_from_rest_api(
    url: str,
    local_file_path: str,
    timeout: Union[None, int] = None,
    headers: Union[None, Dict[str, Any]] = None,
    parameters: Union[None, Dict[str, Any]] = None,
    modification_time: Union[None, int, float] = None,
    is_zip_response: bool = False,
) -> Tuple[bool, str]:
    try:
        directory = os.path.dirname(local_file_path)
        Path(local_file_path).parent.mkdir(parents=True, exist_ok=True)
        data_bytes = io.BytesIO()

        with httpx.stream(
            "GET",
            url,
            timeout=timeout,
            headers=headers,
            params=parameters,
        ) as response:
            response.raise_for_status()

            for data in response.iter_bytes():
                data_bytes.write(data)

            if is_zip_response:
                with zipfile.ZipFile(data_bytes) as zip_file:
                    zip_file.extractall(directory)
            else:
                with open(local_file_path, "wb") as f:
                    f.write(data_bytes.read())

            if modification_time:
                if is_zip_response:
                    for file in os.listdir(directory):
                        file_path = os.path.join(directory, file)
                        os.utime(file_path, (modification_time, modification_time))
                else:
                    os.utime(local_file_path, (modification_time, modification_time))
            return True, None
    except Exception as ex:
        logger.exception(str(ex))
        return False, str(ex)


def rest_api_get(
    url: str,
    timeout: Union[None, int] = None,
    headers: Union[None, Dict[str, Any]] = None,
    parameters: Union[None, Dict[str, Any]] = None,
):
    try:
        response = httpx.get(
            url=url,
            timeout=timeout,
            headers=headers,
            params=parameters,
        )
        if response and response.status_code in (200, 201):
            data = json.loads(response.text)
            return data, None
        return None, response.text
    except Exception as ex:
        return None, str(ex)


def rest_api_post(
    url: str,
    timeout: Union[None, int] = None,
    headers: Union[None, Dict[str, Any]] = None,
    parameters: Union[None, Dict[str, Any]] = None,
    json_body: Union[None, Dict[str, Any]] = None,
):
    try:
        response = httpx.post(
            url=url, timeout=timeout, headers=headers, params=parameters, json=json_body
        )
        if response and response.status_code in (200, 201):
            data = json.loads(response.text)
            return data, None
        return None, response.text
    except Exception as ex:
        return None, str(ex)


def get_unique_file_extensions(
    files: Set[str], max_extension_length: int = 6
) -> Set[str]:
    extensions = set()

    for item in files:
        item_path = Path(item)
        suffixes = item_path.suffixes
        if len(suffixes) == 1:
            extensions.add(suffixes[0].lower())
        elif len(suffixes) > 1:
            if len(suffixes[-2]) <= max_extension_length:
                extensions.add(f"{suffixes[-2].lower()}{suffixes[-1].lower()}")
            else:
                extensions.add(suffixes[0].lower())
    return extensions


def find_assay_technique(
    model: MetabolightsStudyModel,
    assay_file: AssayFile,
    assay_file_subset: AssayFile,
):
    nmr_assay_name = "NMR Assay Name"
    ms_assay_name = "MS Assay Name"
    # if nmr_assay_name and ms_assay_name are in the assay file, it is not well-structured assay
    # return empty
    if (
        nmr_assay_name in assay_file.table.columns
        and ms_assay_name in assay_file.table.columns
    ):
        return AssayTechnique()

    if nmr_assay_name in assay_file.table.columns:
        columns = get_assay_technique_search_columns("MRImaging")
        columns_in_assay_file = {x for x in assay_file.table.columns if x in columns}
        if len(columns) > 0 and len(columns_in_assay_file) == len(columns):
            return assay_techniques["MRImaging"]
    elif ms_assay_name in assay_file.table.columns:
        # search unique column names for each assay technique
        # return technique if assay has the relevant unique column names
        technique_names = [
            "DI-MS",
            "FIA-MS",
            "CE-MS",
            "SPE-IMS-MS",
            "TD-GC-MS",
            "LC-DAD",
            "MSImaging",
        ]
        for technique_name in technique_names:
            columns = get_assay_technique_search_columns(technique_name)
            columns_in_assay_file = {
                x for x in assay_file.table.columns if x in columns
            }
            if len(columns) > 0 and len(columns_in_assay_file) == len(columns):
                return assay_techniques[technique_name]
        # LC-MS or GC-MS difference
        column_type = "Parameter Value[Column type]"
        if column_type in assay_file_subset.table.columns:
            if assay_file_subset.table.data[column_type]:
                values = assay_file_subset.table.data[column_type]
                for i in range(len(values) if len(values) < 5 else 5):
                    if values[i]:
                        column_type = values[i].lower()
                        if "hilic" in column_type or "reverse" in column_type:
                            return assay_techniques["LC-MS"]
                        elif (
                            "low polarity" in column_type
                            or "high polarity" in column_type
                            or "medium polarity" in column_type
                        ):
                            return assay_techniques["GC-MS"]
    investigation_assay = None
    # check i_Investigation.txt file
    # Find the related assay and check technology platform
    # if technology platform contains assay technique name return the relavant assay technique
    for study in model.investigation.studies:
        for assay in study.study_assays.assays:
            if assay.file_name == assay_file.file_path:
                investigation_assay = assay
                for technique in assay_technique_keywords:
                    if technique in assay.technology_platform:
                        return assay_techniques[assay_technique_keywords[technique]]

    # try database curator tags to classify the assay
    if model.study_db_metadata and model.study_db_metadata.study_types:
        study_type_str = ",".join(model.study_db_metadata.study_types)
        if study_type_str:
            for pattern, technique_name in manual_assignments_patterns.items():
                result = re.search(pattern, study_type_str)
                if result:
                    return assay_techniques[technique_name]
    # if there is no match, use assay technology type and return generic assay technique
    if (
        investigation_assay
        and investigation_assay.technology_type
        and investigation_assay.technology_type.term
    ):
        if "mass spectrometry" in investigation_assay.technology_type.term:
            return assay_techniques["MS"]
        elif "NMR spectrometry" in investigation_assay.technology_type.term:
            return assay_techniques["NMR"]

    if nmr_assay_name in assay_file.table.columns:
        return assay_techniques["NMR"]
    return AssayTechnique()


assay_techniques = {
    "LC-MS": AssayTechnique(
        name="LC-MS",
        mainTechnique="MS",
        technique="LC-MS",
        subTechnique="LC",
    ),
    "LC-DAD": AssayTechnique(
        name="LC-DAD",
        mainTechnique="MS",
        technique="LC-MS",
        subTechnique="LC-DAD",
    ),
    "GC-MS": AssayTechnique(
        name="GC-MS",
        mainTechnique="MS",
        technique="GC-MS",
        subTechnique="GC",
    ),
    "GCxGC-MS": AssayTechnique(
        name="GCxGC-MS",
        mainTechnique="MS",
        technique="GC-MS",
        subTechnique="Tandem (GCxGC)",
    ),
    "GC-FID": AssayTechnique(
        name="GC-FID",
        mainTechnique="MS",
        technique="GC-MS",
        subTechnique="GC-FID",
    ),
    "MS": AssayTechnique(
        name="MS",
        mainTechnique="MS",
        technique="Direct Injection",
        subTechnique="MS",
    ),
    "DI-MS": AssayTechnique(
        name="DI-MS",
        mainTechnique="MS",
        technique="Direct Injection",
        subTechnique="Direct infusion (DI)",
    ),
    "FIA-MS": AssayTechnique(
        name="FIA-MS",
        mainTechnique="MS",
        technique="Direct Injection",
        subTechnique="Flow injection analysis (FIA)",
    ),
    "CE-MS": AssayTechnique(
        name="CE-MS",
        mainTechnique="MS",
        technique="Direct Injection",
        subTechnique="Capillary electrophoresis (CE)",
    ),
    "MALDI-MS": AssayTechnique(
        name="MALDI-MS",
        mainTechnique="MS",
        technique="Direct Injection",
        subTechnique="Matrix-assisted laser desorption-ionisation imaging mass spectrometry (MALDI)",
    ),
    "SPE-IMS-MS": AssayTechnique(
        name="SPE-IMS-MS",
        mainTechnique="MS",
        technique="Direct Injection",
        subTechnique="Solid-Phase Extraction Ion Mobility Spectrometry (SPE-IMS)",
    ),
    "MSImaging": AssayTechnique(
        name="MSImaging",
        mainTechnique="MS",
        technique="MS Imaging",
        subTechnique="MS Imaging",
    ),
    "NMR": AssayTechnique(
        name="NMR",
        mainTechnique="NMR",
        technique="NMR",
        subTechnique="Nuclear magnetic resonance",
    ),
    "MRImaging": AssayTechnique(
        name="MRImaging",
        mainTechnique="NMR",
        technique="MRI",
        subTechnique="Magnetic resonance imaging",
    ),
}


assay_technique_keywords: Dict[str, str] = {
    "Liquid Chromatography MS": "LC-MS",
    "Diode array detection MS": "LC-DAD",
    "Gas Chromatography MS": "GC-MS",
    "Tandem Gas Chromatography MS": "GCxGC-MS",
    "Flame ionisation detector MS": "GC-FID",
    "Mass spectrometry": "MS",
    "Direct infusion MS": "DI-MS",
    "Flow injection analysis MS": "FIA-MS",
    "Capillary electrophoresis MS": "CE-MS",
    "Matrix-assisted laser desorption-ionisation imaging MS": "MALDI-MS",
    "Solid-Phase Extraction Ion Mobility Spectrometry MS": "SPE-IMS-MS",
    "MS Imaging": "MSImaging",
    "Nuclear Magnetic Resonance (NMR)": "NMR",
    "Magnetic resonance imaging": "MRImaging",
}

assay_technique_labels: Dict[str, str] = {
    "LC-MS": "Liquid Chromatography MS",
    "LC-DAD": "Diode array detection MS",
    "GC-MS": "Gas Chromatography MS",
    "GCxGC-MS": "Tandem Gas Chromatography MS",
    "GC-FID": "Flame ionisation detector MS",
    "MS": "Mass spectrometry",
    "DI-MS": "Direct infusion MS",
    "FIA-MS": "Flow injection analysis MS",
    "CE-MS": "Capillary electrophoresis MS",
    "MALDI-MS": "Matrix-assisted laser desorption-ionisation imaging MS",
    "SPE-IMS-MS": "Solid-Phase Extraction Ion Mobility Spectrometry MS",
    "MSImaging": "MS Imaging",
    "NMR": "Nuclear Magnetic Resonance (NMR)",
    "MRImaging": "Magnetic resonance imaging",
}

manual_assignments_patterns = {
    r".*imaging.*MS.*": "MSImaging",
    r".*MS.*Imaging.*": "MSImaging",
    r".*CE-.*-MS.*": "CE-MS",
    r".*DI-.*-MS.*": "DI-MS",
    r".*FIA-.*-MS.*": "FIA-MS",
    r".*GC-.*-MS.*": "GC-MS",
    r".*LC-.*-MS.*": "LC-MS",
    r".*MALDI-.*-MS.*": "MALDI-MS",
}

assay_technique_non_protocol_search_columns = {
    "TD-GC-MS": ["Thermal Desorption unit", "Cryogenic Trap"],
    "MRImaging": [
        "Parameter Value[Tomography]",
        "Parameter Value[Spatial resolution]",
    ],
    "DI-MS": [
        "Parameter Value[DI Instrument]",
    ],
    "FIA-MS": [
        "Parameter Value[FIA Instrument]",
    ],
    "CE-MS": [
        "Parameter Value[CE Instrument]",
    ],
    "GCxGC-MS": [
        "Parameter Value[Column model 1]",
        "Parameter Value[Column model 2]",
        "Parameter Value[Column type 1]Parameter Value[Column type 2]",
    ],
    "SPE-IMS-MS": [
        "Parameter Value[SPE-IMS Instrument",
    ],
    "MSImaging": [
        "Parameter Value[Sectioning instrument]",
        "Parameter Value[Instrument manufacturer]",
    ],
    "LC-DAD": [
        "Parameter Value[Signal range]",
        "Parameter Value[Resolution]",
        "Parameter Value[Detector]",
    ],
}


def get_assay_technique_search_columns(technique_name: str) -> List[str]:
    if technique_name in assay_technique_non_protocol_search_columns:
        return assay_technique_non_protocol_search_columns[technique_name]
    return []


default_assay_protocols = {
    "CE-MS": {
        "name": "CE-MS",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {
                "name": "Capillary Electrophoresis",
                "parameters": ["CE Instrument", "Column model", "Column type"],
            },
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Ion source",
                    "Mass analyzer",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Capillary electrophoresis MS",
        "technology_type": "mass spectrometry",
    },
    "DI-MS": {
        "name": "DI-MS",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {"name": "Direct infusion", "parameters": ["DI Instrument"]},
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Ion source",
                    "Mass analyzer",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Direct infusion MS",
        "technology_type": "mass spectrometry",
    },
    "FIA-MS": {
        "name": "FIA-MS",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {"name": "Flow Injection Analysis", "parameters": ["FIA Instrument"]},
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Ion source",
                    "Mass analyzer",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Flow injection analysis MS",
        "technology_type": "mass spectrometry",
    },
    "GC-FID": {
        "name": "GC-FID",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {
                "name": "Chromatography",
                "parameters": [
                    "Chromatography Instrument",
                    "Autosampler model",
                    "Column model",
                    "Column type",
                    "Guard column",
                    "Detector",
                    "Temperature",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Flame ionisation detector MS",
        "technology_type": "mass spectrometry",
    },
    "GC-MS": {
        "name": "GC-MS",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {
                "name": "Chromatography",
                "parameters": [
                    "Chromatography Instrument",
                    "Autosampler model",
                    "Column model",
                    "Column type",
                    "Guard column",
                ],
            },
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Ion source",
                    "Mass analyzer",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Gas Chromatography MS",
        "technology_type": "mass spectrometry",
    },
    "GCxGC-MS": {
        "name": "GCxGC-MS",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {
                "name": "Chromatography",
                "parameters": [
                    "Chromatography Instrument",
                    "Autosampler model",
                    "Column model 1",
                    "Column type 1",
                    "Guard column",
                    "Column model 2",
                    "Column type 2",
                ],
            },
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Ion source",
                    "Mass analyzer",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Tandem Gas Chromatography MS",
        "technology_type": "mass spectrometry",
    },
    "LC-DAD": {
        "name": "LC-DAD",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {
                "name": "Chromatography",
                "parameters": [
                    "Chromatography Instrument",
                    "Autosampler model",
                    "Column model",
                    "Column type",
                    "Guard column",
                    "Detector",
                    "Signal range",
                    "Resolution",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Diode array detection MS",
        "technology_type": "mass spectrometry",
    },
    "LC-MS": {
        "name": "LC-MS",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {
                "name": "Chromatography",
                "parameters": [
                    "Chromatography Instrument",
                    "Autosampler model",
                    "Column model",
                    "Column type",
                    "Guard column",
                ],
            },
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Ion source",
                    "Mass analyzer",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Liquid Chromatography MS",
        "technology_type": "mass spectrometry",
    },
    "MALDI-MS": {
        "name": "MALDI-MS",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Ion source",
                    "Mass analyzer",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": [
            "Matrix-assisted laser desorption-ionisation imaging MS"
        ],
        "technology_type": "mass spectrometry",
    },
    "MRImaging": {
        "name": "MRImaging",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {
                "name": "Magnetic resonance imaging",
                "parameters": ["Instrument", "Tomography", "Temperature"],
            },
            {
                "name": "In vivo magnetic resonance spectroscopy",
                "parameters": [
                    "Spatial resolution",
                    "Field of view",
                    "Matrix",
                    "Magnetic pulse sequence name",
                    "Voxel size",
                    "Localisation pulse sequence name",
                    "Number of transients",
                    "Water inhibition pulse sequence name",
                    "Magnetic field strength",
                ],
            },
            {
                "name": "In vivo magnetic resonance assay",
                "parameters": ["NMR tube type", "Solvent", "Sample pH", "Temperature"],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Magnetic resonance imaging",
        "technology_type": ["NMR spectroscopy"],
    },
    "MS": {
        "name": "MS",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Ion source",
                    "Mass analyzer",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Mass spectrometry",
        "technology_type": "mass spectrometry",
    },
    "MSImaging": {
        "name": "MSImaging",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {
                "name": "Preparation",
                "parameters": [
                    "Sample mounting",
                    "Sample preservation",
                    "Tissue modification",
                    "Sectioning instrument",
                    "Section thickness",
                    "Matrix",
                    "Matrix application",
                ],
            },
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Instrument manufacturer",
                    "Ion source",
                    "Mass analyzer",
                    "Solvent",
                    "Target material",
                    "Spatial resolution",
                    "Pixel size x",
                    "Pixel size y",
                    "Max count of pixel x",
                    "Max count of pixel y",
                    "Max dimension x",
                    "Max dimension y",
                    "Inlet type",
                    "Detector",
                    "Detector mode",
                    "Resolving power",
                    "Resolving power m/z",
                    "Native spectrum identifier format",
                    "Data file content",
                    "Spectrum representation",
                    "Raw data file format",
                    "Instrument software",
                    "Instrument software version",
                    "Line scan direction",
                    "Linescan sequence",
                    "Scan pattern",
                    "Scan type",
                    "Number of scans",
                ],
            },
            {
                "name": "Histology",
                "parameters": ["Stain", "High-res image", "Low-res image"],
            },
            {
                "name": "Data transformation",
                "parameters": [
                    "Data Transformation software",
                    "Data Transformation software version",
                ],
            },
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "MS Imaging",
        "technology_type": "mass spectrometry",
    },
    "NMR": {
        "name": "NMR",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Extraction Method"]},
            {
                "name": "NMR sample",
                "parameters": ["NMR tube type", "Solvent", "Sample pH", "Temperature"],
            },
            {
                "name": "NMR spectroscopy",
                "parameters": [
                    "Instrument",
                    "NMR Probe",
                    "Number of transients",
                    "Pulse sequence name",
                    "Magnetic field strength",
                ],
            },
            {"name": "NMR assay", "parameters": []},
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Nuclear Magnetic Resonance (NMR)",
        "technology_type": ["NMR spectroscopy"],
    },
    "SPE-IMS-MS": {
        "name": "SPE-IMS-MS",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {
                "name": "Solid-Phase Extraction Ion Mobility Spectrometry",
                "parameters": ["SPE-IMS Instrument", "Cartridge type"],
            },
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Ion source",
                    "Mass analyzer",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": ["Solid-Phase Extraction Ion Mobility Spectrometry MS"],
        "technology_type": "mass spectrometry",
    },
    "TD-GC-MS": {
        "name": "TD-GC-MS",
        "protocols": [
            {"name": "Sample collection", "parameters": []},
            {"name": "Extraction", "parameters": ["Post Extraction", "Derivatization"]},
            {
                "name": "Chromatography",
                "parameters": [
                    "Chromatography Instrument",
                    "Autosampler model",
                    "Column model",
                    "Column type",
                ],
            },
            {
                "name": "Mass spectrometry",
                "parameters": [
                    "Scan polarity",
                    "Scan m/z range",
                    "Instrument",
                    "Ion source",
                    "Mass analyzer",
                ],
            },
            {"name": "Data transformation", "parameters": []},
            {"name": "Metabolite identification", "parameters": []},
        ],
        "technology_platform": "Thermal Desorption-Gas Chromatography MS",
        "technology_type": "mass spectrometry",
    },
}
