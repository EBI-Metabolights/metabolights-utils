from typing import List, Union

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.isa.common import Comment, IsaAbstractModel, IsaTabConfig

module_name = __name__


class BaseSection(IsaAbstractModel):
    comments: List[Comment] = []


class OntologySourceReference(IsaAbstractModel):
    isatab_config: Annotated[IsaTabConfig, Field(exclude=True)] = IsaTabConfig(
        field_order=[
            "source_name",
            "source_file",
            "source_version",
            "source_description",
        ]
    )

    source_name: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Source Name",
                "source_description": True,
            },
        ),
    ] = ""

    source_file: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Source File"},
        ),
    ] = ""
    source_version: Annotated[
        Union[str, int],
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Source Version"},
        ),
    ] = ""
    source_description: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Source Description"},
        ),
    ] = ""


class OntologyAnnotation(IsaAbstractModel):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(exclude=True),
    ] = IsaTabConfig(field_order=["term", "term_accession_number", "term_source_ref"])

    term: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
            },
        ),
    ] = ""

    term_accession_number: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Term Accession Number",
            },
        ),
    ] = ""
    term_source_ref: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Term Source REF"},
        ),
    ] = ""


class ValueTypeAnnotation(IsaAbstractModel):
    isatab_config: Annotated[IsaTabConfig, Field(exclude=True)] = IsaTabConfig(
        field_order=[
            "name",
            "type",
            "term_accession_number",
            "term_source_ref",
        ]
    )

    name: Annotated[
        str,
        Field(
            description="", json_schema_extra={"auto_fill": True, "header_name": "Name"}
        ),
    ] = ""
    type: Annotated[
        str,
        Field(
            description="", json_schema_extra={"auto_fill": True, "header_name": "Type"}
        ),
    ] = ""
    term_accession_number: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Type Term Accession Number",
            },
        ),
    ] = ""
    term_source_ref: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Type Term Source REF",
            },
        ),
    ] = ""


class Publication(IsaAbstractModel):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=["pub_med_id", "doi", "author_list", "title", "status"]
    )

    pub_med_id: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "PubMed ID"},
        ),
    ] = ""
    doi: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Publication DOI"},
        ),
    ] = ""
    author_list: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Publication Author List",
            },
        ),
    ] = ""
    title: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Publication Title"},
        ),
    ] = ""
    status: Annotated[
        OntologyAnnotation,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Publication Status"},
        ),
    ] = OntologyAnnotation()


class Person(IsaAbstractModel):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
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
    )

    last_name: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Last Name"},
        ),
    ] = ""
    first_name: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "First Name"},
        ),
    ] = ""
    mid_initials: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Mid Initials"},
        ),
    ] = ""
    email: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Email"},
        ),
    ] = ""
    phone: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Phone"},
        ),
    ] = ""
    fax: Annotated[
        str,
        Field(
            description="", json_schema_extra={"auto_fill": True, "header_name": "Fax"}
        ),
    ] = ""
    address: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Address"},
        ),
    ] = ""
    affiliation: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Affiliation"},
        ),
    ] = ""
    roles: Annotated[
        List[OntologyAnnotation],
        Field(
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Roles",
                "text_multiple_value": True,
                "seperator": ";",
            },
        ),
    ] = []


class Factor(IsaAbstractModel):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(field_order=["name", "type"])

    name: Annotated[
        str,
        Field(
            description="", json_schema_extra={"auto_fill": True, "header_name": "Name"}
        ),
    ] = ""
    type: Annotated[
        OntologyAnnotation,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Type"},
        ),
    ] = OntologyAnnotation()


class Assay(IsaAbstractModel):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=[
            "file_name",
            "measurement_type",
            "technology_type",
            "technology_platform",
        ]
    )

    file_name: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "File Name"},
        ),
    ] = ""
    measurement_type: Annotated[
        OntologyAnnotation,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Measurement Type"},
        ),
    ] = OntologyAnnotation()
    technology_type: Annotated[
        OntologyAnnotation,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Technology Type"},
        ),
    ] = OntologyAnnotation()
    technology_platform: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Technology Platform"},
        ),
    ] = ""


class Protocol(IsaAbstractModel):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=[
            "name",
            "protocol_type",
            "description",
            "uri",
            "version",
            "parameters",
            "components",
        ]
    )

    name: Annotated[
        str,
        Field(
            description="", json_schema_extra={"auto_fill": True, "header_name": "Name"}
        ),
    ] = ""
    protocol_type: Annotated[
        OntologyAnnotation,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Type"},
        ),
    ] = OntologyAnnotation()
    description: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Description"},
        ),
    ] = ""
    uri: Annotated[
        str,
        Field(
            description="", json_schema_extra={"auto_fill": True, "header_name": "URI"}
        ),
    ] = ""
    version: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Version"},
        ),
    ] = ""
    parameters: Annotated[
        List[OntologyAnnotation],
        Field(
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Parameters Name",
                "text_multiple_value": True,
                "seperator": ";",
            },
        ),
    ] = []
    components: Annotated[
        List[ValueTypeAnnotation],
        Field(
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Components",
                "text_multiple_value": True,
                "seperator": ";",
            },
        ),
    ] = []


######################################################################################################
# ISA TAB FILE SECTIONS
######################################################################################################


class OntologySourceReferences(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=["references"],
        section_header="ONTOLOGY SOURCE REFERENCE",
        section_prefix="Term",
    )

    references: Annotated[
        List[OntologySourceReference],
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
                "search_header": "Source Name",
            },
        ),
    ] = []


class InvestigationPublications(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=["publications"],
        section_header="INVESTIGATION PUBLICATIONS",
        section_prefix=None,
    )

    publications: Annotated[
        List[Publication],
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
                "search_header": "Publication Title",
            },
        ),
    ] = []


class InvestigationContacts(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=["people"],
        section_header="INVESTIGATION CONTACTS",
        section_prefix="Person",
    )

    people: Annotated[
        List[Person],
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
                "search_header": "Last Name",
            },
        ),
    ] = []


class StudyDesignDescriptors(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=["design_types"],
        section_header="STUDY DESIGN DESCRIPTORS",
        section_prefix="Design",
    )

    design_types: Annotated[
        List[OntologyAnnotation],
        Field(
            description="", json_schema_extra={"auto_fill": True, "header_name": "Type"}
        ),
    ] = []


class StudyPublications(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=["publications"],
        section_header="STUDY PUBLICATIONS",
        section_prefix=None,
    )

    publications: Annotated[
        List[Publication],
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
                "search_header": "Publication Title",
            },
        ),
    ] = []


class StudyFactors(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=["factors"],
        section_header="STUDY FACTORS",
        section_prefix="Factor",
    )

    factors: Annotated[
        List[Factor],
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
                "search_header": "Name",
            },
        ),
    ] = []


class StudyAssays(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=["assays"],
        section_header="STUDY ASSAYS",
        section_prefix="Assay",
    )

    assays: Annotated[
        List[Assay],
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
                "search_header": "File Name",
            },
        ),
    ] = []


class StudyProtocols(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=["protocols"],
        section_header="STUDY PROTOCOLS",
        section_prefix="Protocol",
    )

    protocols: Annotated[
        List[Protocol],
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
                "search_header": "Name",
            },
        ),
    ] = []


class StudyContacts(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
        field_order=["people"],
        section_header="STUDY CONTACTS",
        section_prefix="Person",
    )

    people: Annotated[
        List[Person],
        Field(
            description="",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
                "search_header": "Last Name",
            },
        ),
    ] = []


class Study(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
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
    )

    identifier: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Identifier"},
        ),
    ] = ""
    title: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Title"},
        ),
    ] = ""
    description: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Description"},
        ),
    ] = ""
    submission_date: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Submission Date"},
        ),
    ] = ""
    public_release_date: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Public Release Date"},
        ),
    ] = ""
    file_name: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "File Name"},
        ),
    ] = ""

    study_design_descriptors: Annotated[
        StudyDesignDescriptors,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": ""},
        ),
    ] = StudyDesignDescriptors()
    study_publications: Annotated[
        StudyPublications,
        Field(description="", json_schema_extra={"auto_fill": True, "header_name": ""}),
    ] = StudyPublications()
    study_factors: Annotated[
        StudyFactors,
        Field(description="", json_schema_extra={"auto_fill": True, "header_name": ""}),
    ] = StudyFactors()
    study_assays: Annotated[
        StudyAssays,
        Field(description="", json_schema_extra={"auto_fill": True, "header_name": ""}),
    ] = StudyAssays()
    study_protocols: Annotated[
        StudyProtocols,
        Field(description="", json_schema_extra={"auto_fill": True, "header_name": ""}),
    ] = StudyProtocols()
    study_contacts: Annotated[
        StudyContacts,
        Field(description="", json_schema_extra={"auto_fill": True, "header_name": ""}),
    ] = StudyContacts()


class Investigation(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(
            exclude=True,
        ),
    ] = IsaTabConfig(
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
    )

    identifier: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Identifier"},
        ),
    ] = ""
    title: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Title"},
        ),
    ] = ""
    description: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Description"},
        ),
    ] = ""
    submission_date: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Submission Date"},
        ),
    ] = ""
    public_release_date: Annotated[
        str,
        Field(
            description="",
            json_schema_extra={"auto_fill": True, "header_name": "Public Release Date"},
        ),
    ] = ""

    ontology_source_references: Annotated[
        OntologySourceReferences,
        Field(
            description="Ontology sources used in the investigation file",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
                "inherit_prefix": False,
            },
        ),
    ] = OntologySourceReferences()

    investigation_publications: Annotated[
        InvestigationPublications,
        Field(
            description="All publications prepared to report results of the investigation",
            json_schema_extra={"auto_fill": True, "header_name": ""},
        ),
    ] = InvestigationPublications()

    investigation_contacts: Annotated[
        InvestigationContacts,
        Field(
            description="People details of the investigation.",
            json_schema_extra={"auto_fill": True, "header_name": ""},
        ),
    ] = InvestigationContacts()

    studies: Annotated[
        List[Study], Field(description="Studies carried out in the investigation.")
    ] = []
