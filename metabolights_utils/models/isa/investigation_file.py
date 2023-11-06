from typing import List

from pydantic import Field

from metabolights_utils.models.isa.common import Comment, IsaAbstractModel, IsaTabConfig

module_name = __name__


class BaseSection(IsaAbstractModel):
    comments: List[Comment] = []


class OntologySourceReference(IsaAbstractModel):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=[
                "source_name",
                "source_file",
                "source_version",
                "source_description",
            ]
        ),
        exclude=True,
    )

    source_name: str = Field(
        "",
        json_schema_extra={
            "auto_fill": True,
            "header_name": "Source Name",
            "source_description": True,
        },
    )
    source_file: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Source File"}
    )
    source_version: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Source Version"}
    )
    source_description: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Source Description"}
    )


class OntologyAnnotation(IsaAbstractModel):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(field_order=["term", "term_accession_number", "term_source_ref"]),
        exclude=True,
    )

    term: str = Field("", json_schema_extra={"auto_fill": True, "header_name": ""})
    term_accession_number: str = Field(
        "",
        json_schema_extra={"auto_fill": True, "header_name": "Term Accession Number"},
    )
    term_source_ref: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Term Source REF"}
    )


class ValueTypeAnnotation(IsaAbstractModel):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=[
                "name",
                "type",
                "term_accession_number",
                "term_source_ref",
            ]
        ),
        exclude=True,
    )

    name: str = Field("", json_schema_extra={"auto_fill": True, "header_name": "Name"})
    type: str = Field("", json_schema_extra={"auto_fill": True, "header_name": "Type"})
    term_accession_number: str = Field(
        "",
        json_schema_extra={
            "auto_fill": True,
            "header_name": "Type Term Accession Number",
        },
    )
    term_source_ref: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Type Term Source REF"}
    )


class Publication(IsaAbstractModel):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=["pub_med_id", "doi", "author_list", "title", "status"]
        ),
        exclude=True,
    )

    pub_med_id: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "PubMed ID"}
    )
    doi: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Publication DOI"}
    )
    author_list: str = Field(
        "",
        json_schema_extra={"auto_fill": True, "header_name": "Publication Author List"},
    )
    title: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Publication Title"}
    )
    status: OntologyAnnotation = Field(
        OntologyAnnotation(),
        json_schema_extra={"auto_fill": True, "header_name": "Publication Status"},
    )


class Person(IsaAbstractModel):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=[
                "last_name",
                "first_name",
                "mid_initials",
                "email",
                "phone",
                "fax",
                "address",
                "affiliation",
                "roles",
            ]
        ),
        exclude=True,
    )

    last_name: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Last Name"}
    )
    first_name: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "First Name"}
    )
    mid_initials: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Mid Initials"}
    )
    email: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Email"}
    )
    phone: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Phone"}
    )
    fax: str = Field("", json_schema_extra={"auto_fill": True, "header_name": "Fax"})
    address: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Address"}
    )
    affiliation: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Affiliation"}
    )
    roles: List[OntologyAnnotation] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "Roles",
            "text_multiple_value": True,
            "seperator": ";",
        },
    )


class Factor(IsaAbstractModel):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(field_order=["name", "type"]),
        exclude=True,
    )

    name: str = Field("", json_schema_extra={"auto_fill": True, "header_name": "Name"})
    type: OntologyAnnotation = Field(
        OntologyAnnotation(),
        json_schema_extra={"auto_fill": True, "header_name": "Type"},
    )


class Assay(IsaAbstractModel):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=[
                "file_name",
                "measurement_type",
                "technology_type",
                "technology_platform",
            ]
        ),
        exclude=True,
    )

    file_name: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "File Name"}
    )
    measurement_type: OntologyAnnotation = Field(
        OntologyAnnotation(),
        json_schema_extra={"auto_fill": True, "header_name": "Measurement Type"},
    )
    technology_type: OntologyAnnotation = Field(
        OntologyAnnotation(),
        json_schema_extra={"auto_fill": True, "header_name": "Technology Type"},
    )
    technology_platform: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Technology Platform"}
    )


class Protocol(IsaAbstractModel):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=[
                "name",
                "protocol_type",
                "description",
                "uri",
                "version",
                "parameters",
                "components",
            ]
        ),
        exclude=True,
    )

    name: str = Field("", json_schema_extra={"auto_fill": True, "header_name": "Name"})
    protocol_type: OntologyAnnotation = Field(
        OntologyAnnotation(),
        json_schema_extra={"auto_fill": True, "header_name": "Type"},
    )
    description: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Description"}
    )
    uri: str = Field("", json_schema_extra={"auto_fill": True, "header_name": "URI"})
    version: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Version"}
    )
    parameters: List[OntologyAnnotation] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "Parameters Name",
            "text_multiple_value": True,
            "seperator": ";",
        },
    )
    components: List[ValueTypeAnnotation] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "Components",
            "text_multiple_value": True,
            "seperator": ";",
        },
    )


######################################################################################################
# ISA TAB FILE SECTIONS
######################################################################################################


class OntologySourceReferences(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=["references"],
            section_header="ONTOLOGY SOURCE REFERENCE",
            section_prefix="Term",
        ),
        exclude=True,
    )

    references: List[OntologySourceReference] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "",
            "search_header": "Source Name",
        },
    )


class InvestigationPublications(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=["publications"],
            section_header="INVESTIGATION PUBLICATIONS",
            section_prefix=None,
        ),
        exclude=True,
    )

    publications: List[Publication] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "",
            "search_header": "Publication Title",
        },
    )


class InvestigationContacts(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=["people"],
            section_header="INVESTIGATION CONTACTS",
            section_prefix="Person",
        ),
        exclude=True,
    )

    people: List[Person] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "",
            "search_header": "Last Name",
        },
    )


class StudyDesignDescriptors(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=["design_types"],
            section_header="STUDY DESIGN DESCRIPTORS",
            section_prefix="Design",
        ),
        exclude=True,
    )

    design_types: List[OntologyAnnotation] = Field(
        [], json_schema_extra={"auto_fill": True, "header_name": "Type"}
    )


class StudyPublications(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=["publications"],
            section_header="STUDY PUBLICATIONS",
            section_prefix=None,
        ),
        exclude=True,
    )

    publications: List[Publication] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "",
            "search_header": "Publication Title",
        },
    )


class StudyFactors(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=["factors"],
            section_header="STUDY FACTORS",
            section_prefix="Factor",
        ),
        exclude=True,
    )

    factors: List[Factor] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "",
            "search_header": "Name",
        },
    )


class StudyAssays(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=["assays"],
            section_header="STUDY ASSAYS",
            section_prefix="Assay",
        ),
        exclude=True,
    )

    assays: List[Assay] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "",
            "search_header": "File Name",
        },
    )


class StudyProtocols(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=["protocols"],
            section_header="STUDY PROTOCOLS",
            section_prefix="Protocol",
        ),
        exclude=True,
    )

    protocols: List[Protocol] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "",
            "search_header": "Name",
        },
    )


class StudyContacts(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=["people"],
            section_header="STUDY CONTACTS",
            section_prefix="Person",
        ),
        exclude=True,
    )

    people: List[Person] = Field(
        [],
        json_schema_extra={
            "auto_fill": True,
            "header_name": "",
            "search_header": "Last Name",
        },
    )


class Study(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=[
                "identifier",
                "title",
                "description",
                "submission_date",
                "public_release_date",
                "file_name",
            ],
            section_header="STUDY",
            section_prefix="Study",
        ),
        exclude=True,
    )

    identifier: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Identifier"}
    )
    title: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Title"}
    )
    description: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Description"}
    )
    submission_date: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Submission Date"}
    )
    public_release_date: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Public Release Date"}
    )
    file_name: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "File Name"}
    )

    study_design_descriptors: StudyDesignDescriptors = Field(
        StudyDesignDescriptors(),
        json_schema_extra={"auto_fill": True, "header_name": ""},
    )
    study_publications: StudyPublications = Field(
        StudyPublications(), json_schema_extra={"auto_fill": True, "header_name": ""}
    )
    study_factors: StudyFactors = Field(
        StudyFactors(), json_schema_extra={"auto_fill": True, "header_name": ""}
    )
    study_assays: StudyAssays = Field(
        StudyAssays(), json_schema_extra={"auto_fill": True, "header_name": ""}
    )
    study_protocols: StudyProtocols = Field(
        StudyProtocols(), json_schema_extra={"auto_fill": True, "header_name": ""}
    )
    study_contacts: StudyContacts = Field(
        StudyContacts(), json_schema_extra={"auto_fill": True, "header_name": ""}
    )


class Investigation(BaseSection):
    isatab_config: IsaTabConfig = Field(
        IsaTabConfig(
            field_order=[
                "identifier",
                "title",
                "description",
                "submission_date",
                "public_release_date",
            ],
            section_header="INVESTIGATION",
            section_prefix="Investigation",
            specification_version="1.0",
            specification_date="2016-10-28",
        ),
        exclude=True,
    )

    identifier: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Identifier"}
    )
    title: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Title"}
    )
    description: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Description"}
    )
    submission_date: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Submission Date"}
    )
    public_release_date: str = Field(
        "", json_schema_extra={"auto_fill": True, "header_name": "Public Release Date"}
    )

    ontology_source_references: OntologySourceReferences = Field(
        OntologySourceReferences(),
        description="Ontology sources used in the investigation ffile",
        json_schema_extra={
            "auto_fill": True,
            "header_name": "",
            "inherit_prefix": False,
        },
    )
    investigation_publications: InvestigationPublications = Field(
        InvestigationPublications(),
        description="All publications prepared to report results of the investigation",
        json_schema_extra={"auto_fill": True, "header_name": ""},
    )
    investigation_contacts: InvestigationContacts = Field(
        InvestigationContacts(),
        description="People details of the investigation.",
        json_schema_extra={"auto_fill": True, "header_name": ""},
    )
    studies: List[Study] = Field(
        [], description="Studies carried out in the investigation."
    )
