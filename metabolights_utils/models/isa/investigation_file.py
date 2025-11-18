from typing import List, Literal, OrderedDict, Union

from pydantic import Field
from typing_extensions import Annotated

from metabolights_utils.models.isa.common import Comment, IsaAbstractModel, IsaTabConfig

module_name = __name__


class BaseSection(IsaAbstractModel):
    comments: Annotated[
        List[Comment],
        Field(
            description="List of comments linked to the related section",
        ),
    ] = []


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
            description="The name of the source of a term; "
            "i.e. the source controlled vocabulary or ontology."
            " These names will be used in all corresponding Term Source REF fields "
            "that occur elsewhere.",
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
            description="A file name or a URI of an official resource.",
            json_schema_extra={"auto_fill": True, "header_name": "Source File"},
        ),
    ] = ""
    source_version: Annotated[
        Union[str, int],
        Field(
            description="The version number of the Term Source "
            "to support terms tracking.",
            json_schema_extra={"auto_fill": True, "header_name": "Source Version"},
        ),
    ] = ""
    source_description: Annotated[
        str,
        Field(
            description="Description of source. "
            "Use for disambiguating resources when homologous prefixes have been used.",
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
            description="Ontology term",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
            },
        ),
    ] = ""

    term_accession_number: Annotated[
        str,
        Field(
            description="The accession number from the Term Source "
            "associated with the term.",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Term Accession Number",
            },
        ),
    ] = ""
    term_source_ref: Annotated[
        str,
        Field(
            description="Source reference name of ontology term. e.g., EFO, OBO, NCIT. "
            "Ontology source reference names should be defined "
            "in ontology source references section in i_Investigation.txt file",
            json_schema_extra={"auto_fill": True, "header_name": "Term Source REF"},
        ),
    ] = ""

    def __str__(self) -> str:
        if self.term:
            if self.term_source_ref or self.term_accession_number:
                return (
                    f"{self.term} [{self.term_source_ref}:{self.term_accession_number}]"
                )
            else:
                return self.term
        return ""


class ExtendedOntologyAnnotation(OntologyAnnotation):
    category: Annotated[
        str,
        Field(description="Category of descriptor annotation"),
    ] = ""
    source: Annotated[
        str,
        Field(description="Source of ontology annotation"),
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


class CharacteristicDefinition(ValueTypeAnnotation):
    value_format: Annotated[
        Literal["", "text", "ontology", "numeric"],
        Field(
            description="Format of characteristic value, "
            "empty value is used for undefined value."
            "text (one column), "
            "ontology ( one column+ term source ref and accession number), "
            "numeric (one column + unit, unit term source ref and accession number)",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""


class ParameterDefinition(OntologyAnnotation):
    value_format: Annotated[
        Literal["", "text", "ontology", "numeric"],
        Field(
            description="Format of parameter value, "
            "empty value is used for undefined value."
            "text (one column), "
            "ontology ( one column+ term source ref and accession number), "
            "numeric (one column + unit, unit term source ref and accession number)",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""


class ProtocolComponent(ValueTypeAnnotation): ...


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
            description="The PubMed IDs of the publication.",
            json_schema_extra={"auto_fill": True, "header_name": "PubMed ID"},
            title="PubMed Id",
        ),
    ] = ""
    doi: Annotated[
        str,
        Field(
            description="A Digital Object Identifier (DOI) for the publication.",
            json_schema_extra={"auto_fill": True, "header_name": "Publication DOI"},
            title="DOI",
        ),
    ] = ""
    author_list: Annotated[
        str,
        Field(
            description="The list of authors associated with the publication. "
            "Comma (,) is recommended to define multiple authors.",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Publication Author List",
            },
        ),
    ] = ""
    title: Annotated[
        str,
        Field(
            description="The title of publication associated with the investigation.",
            json_schema_extra={"auto_fill": True, "header_name": "Publication Title"},
        ),
    ] = ""
    status: Annotated[
        OntologyAnnotation,
        Field(
            description="A term describing the status of that publication "
            "(i.e. EFO:submitted, EFO:in preparation, EFO:published).",
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
            description="Last name of a person "
            "associated with the investigation or study.",
            json_schema_extra={"auto_fill": True, "header_name": "Last Name"},
        ),
    ] = ""
    first_name: Annotated[
        str,
        Field(
            description="First name of person "
            "associated with the investigation or study.",
            json_schema_extra={"auto_fill": True, "header_name": "First Name"},
        ),
    ] = ""
    mid_initials: Annotated[
        str,
        Field(
            description="Middle name initials (if exists) of person "
            "associated with the investigation or study",
            json_schema_extra={"auto_fill": True, "header_name": "Mid Initials"},
        ),
    ] = ""
    email: Annotated[
        str,
        Field(
            description="Email address of person "
            "associated with the investigation or study",
            json_schema_extra={"auto_fill": True, "header_name": "Email"},
        ),
    ] = ""
    phone: Annotated[
        str,
        Field(
            description="Phone number of person "
            "associated with the investigation or study",
            json_schema_extra={"auto_fill": True, "header_name": "Phone"},
        ),
    ] = ""
    fax: Annotated[
        str,
        Field(
            description="Fax number of person "
            "associated with the investigation or study",
            json_schema_extra={"auto_fill": True, "header_name": "Fax"},
        ),
    ] = ""
    address: Annotated[
        str,
        Field(
            description="Address of person associated with the investigation or study",
            json_schema_extra={"auto_fill": True, "header_name": "Address"},
        ),
    ] = ""
    affiliation: Annotated[
        str,
        Field(
            description="Affiliation of person associated "
            "with the investigation or study",
            json_schema_extra={"auto_fill": True, "header_name": "Affiliation"},
        ),
    ] = ""
    roles: Annotated[
        List[OntologyAnnotation],
        Field(
            description="Roles of person associated with the investigation or study. "
            "Multiple role can be defined for each person. "
            "Role is defined as an ontology term. "
            "e.g., NCIT:Investigator, NCIT:Author",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Roles",
                "text_multiple_value": True,
                "seperator": ";",
            },
        ),
    ] = []
    orcid: Annotated[
        str,
        Field(
            description="ORCID of person associated with the investigation or study",
            json_schema_extra={"auto_fill": False},
            title="ORCID",
        ),
    ] = ""
    additional_emails: Annotated[
        list[str],
        Field(
            description="Additional email addresses of person associated "
            "with the investigation or study",
            json_schema_extra={"auto_fill": False},
        ),
    ] = []
    affiliation_ror_id: Annotated[
        str,
        Field(
            description="ROR Id of the person's affiliation",
            json_schema_extra={"auto_fill": False},
            title="Affiliation ROR Id",
        ),
    ] = ""


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
            description="The name of one factor used in the Study files. "
            "A factor corresponds to an independent variable "
            "manipulated by the experimentalist "
            "with the intention to affect biological systems in a way "
            "that can be measured by an assay.",
            json_schema_extra={"auto_fill": True, "header_name": "Name"},
        ),
    ] = ""
    type: Annotated[
        OntologyAnnotation,
        Field(
            description="A term allowing the classification of the factor "
            "into categories. "
            "The term is a controlled vocabulary or an ontology",
            json_schema_extra={"auto_fill": True, "header_name": "Type"},
        ),
    ] = OntologyAnnotation()

    value_format: Annotated[
        Literal["", "text", "ontology", "numeric"],
        Field(
            description="Format of factor value, "
            "empty value is used for undefined value."
            "text (one column), "
            "ontology ( one column+ term source ref and accession number), "
            "numeric (one column + unit, unit term source ref and accession number)",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""

    def __str__(self):
        return f"{self.name if self.name else ''} ({str(self.type)})"


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
            description="Assay file name. Expected filename pattern is a_*.txt",
            json_schema_extra={"auto_fill": True, "header_name": "File Name"},
        ),
    ] = ""
    measurement_type: Annotated[
        OntologyAnnotation,
        Field(
            description="A term to qualify what is being measured "
            "(e.g. metabolite identification).",
            json_schema_extra={"auto_fill": True, "header_name": "Measurement Type"},
        ),
    ] = OntologyAnnotation()
    technology_type: Annotated[
        OntologyAnnotation,
        Field(
            description="Term to identify the technology "
            "used to perform the measurement, "
            "e.g. NMR spectrometry assay, mass spectrometry assay",
            json_schema_extra={"auto_fill": True, "header_name": "Technology Type"},
        ),
    ] = OntologyAnnotation()
    technology_platform: Annotated[
        str,
        Field(
            description="Platform information such as assay technique name, "
            "polarity, column model, manufacturer, platform name.",
            json_schema_extra={"auto_fill": True, "header_name": "Technology Platform"},
        ),
    ] = ""

    assay_identifier: Annotated[
        str,
        Field(description="Assay identifier.", json_schema_extra={"auto_fill": False}),
    ] = ""
    assay_type: Annotated[
        OntologyAnnotation,
        Field(description="Assay type.", json_schema_extra={"auto_fill": False}),
    ] = OntologyAnnotation()
    omics_type: Annotated[
        OntologyAnnotation,
        Field(description="Assay type.", json_schema_extra={"auto_fill": False}),
    ] = OntologyAnnotation()
    assay_descriptors: Annotated[
        list[ExtendedOntologyAnnotation],
        Field(description="Assay descriptors.", json_schema_extra={"auto_fill": False}),
    ] = []
    result_file_format: Annotated[
        str,
        Field(
            description="result file format. e.g., MAF v2.0, mzTab-M v2.1, etc.",
            json_schema_extra={"auto_fill": False},
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
            description="Protocol name.",
            json_schema_extra={"auto_fill": True, "header_name": "Name"},
        ),
    ] = ""
    protocol_type: Annotated[
        OntologyAnnotation,
        Field(
            description="Term to classify the protocol.",
            json_schema_extra={"auto_fill": True, "header_name": "Type"},
        ),
    ] = OntologyAnnotation()
    description: Annotated[
        str,
        Field(
            description="Protocol description.",
            json_schema_extra={"auto_fill": True, "header_name": "Description"},
        ),
    ] = ""
    uri: Annotated[
        str,
        Field(
            description="Pointer to external protocol resources "
            "that can be accessed by their Uniform Resource Identifier (URI).",
            json_schema_extra={"auto_fill": True, "header_name": "URI"},
        ),
    ] = ""
    version: Annotated[
        str,
        Field(
            description="An identifier for the version to ensure protocol tracking..",
            json_schema_extra={"auto_fill": True, "header_name": "Version"},
        ),
    ] = ""
    parameters: Annotated[
        List[ParameterDefinition],
        Field(
            description="Protocol's parameters.",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "Parameters Name",
                "text_multiple_value": True,
                "seperator": ";",
            },
        ),
    ] = []
    components: Annotated[
        List[ProtocolComponent],
        Field(
            description="Protocol’s components; e.g. instrument names, "
            "software names, and reagents names.",
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
            description="List of ontology sources used in ISA metadata files.",
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
            description="Investigation publications.",
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
            description="Investigation contact list.",
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
        List[ExtendedOntologyAnnotation],
        Field(
            description="Design descriptors "
            "defined in study design descriptors section.",
            json_schema_extra={"auto_fill": True, "header_name": "Type"},
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
            description="Publications defined in study publications section.",
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
            description="Factors defined in study factors section.",
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
        Field(exclude=True),
    ] = IsaTabConfig(
        field_order=["assays"],
        section_header="STUDY ASSAYS",
        section_prefix="Assay",
    )

    assays: Annotated[
        List[Assay],
        Field(
            description="List of assays defined in study assay section.",
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
            description="Protocols defined in study protocol section.",
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
            description="Contacts defined in study contacts section",
            json_schema_extra={
                "auto_fill": True,
                "header_name": "",
                "search_header": "Last Name",
            },
        ),
    ] = []


class Funder(IsaAbstractModel):
    funder_name: Annotated[str, Field(description="Funder organization full name.")] = (
        ""
    )
    funder_id: Annotated[str, Field(description="Funder ID.")] = ""
    grant_ids: Annotated[list[str], Field(description="Grant ID.")] = []


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
            description="A unique identifier, either a temporary identifier "
            "generated by MetaboLights repository.",
            json_schema_extra={"auto_fill": True, "header_name": "Identifier"},
        ),
    ] = ""
    title: Annotated[
        str,
        Field(
            description="A concise phrase used to encapsulate "
            "the purpose and goal of the study.",
            json_schema_extra={"auto_fill": True, "header_name": "Title"},
        ),
    ] = ""
    description: Annotated[
        str,
        Field(
            description="A textual description of the study "
            "with components such as objective or goals.",
            json_schema_extra={"auto_fill": True, "header_name": "Description"},
        ),
    ] = ""
    submission_date: Annotated[
        str,
        Field(
            description="The date on which the study is submitted to an archive. "
            "String formatted as ISO8601 date YYYY-MM-DD",
            json_schema_extra={"auto_fill": True, "header_name": "Submission Date"},
        ),
    ] = ""
    public_release_date: Annotated[
        str,
        Field(
            description="The date on which the study SHOULD be released publicly. "
            "String formatted as ISO8601 date YYYY-MM-DD",
            json_schema_extra={"auto_fill": True, "header_name": "Public Release Date"},
        ),
    ] = ""
    file_name: Annotated[
        str,
        Field(
            description="Name of the Sample Table file "
            "corresponding the definition of that Study.",
            json_schema_extra={"auto_fill": True, "header_name": "File Name"},
        ),
    ] = ""
    study_category: Annotated[
        str,
        Field(description="Study category", json_schema_extra={"auto_fill": False}),
    ] = ""
    template_version: Annotated[
        str,
        Field(description="Template version", json_schema_extra={"auto_fill": False}),
    ] = ""
    sample_template: Annotated[
        str,
        Field(
            description="Study sample file template",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""
    mhd_accession: Annotated[
        str,
        Field(
            description="MetabolomicsHub accession number of the study",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""
    mhd_model_version: Annotated[
        str,
        Field(
            description="MetabolomicsHub model version of the study",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""
    created_at: Annotated[
        str,
        Field(
            description="Study creation time",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""
    revision_number: Annotated[
        str,
        Field(
            description="Revision number of the study",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""
    revision_date: Annotated[
        str,
        Field(
            description="Revision date of the study",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""
    revision_comment: Annotated[
        str,
        Field(
            description="Revision comment of the study",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""
    dataset_license: Annotated[
        str,
        Field(
            description="Data license of the study",
            json_schema_extra={"auto_fill": False},
        ),
    ] = ""
    funders: Annotated[
        list[Funder],
        Field(
            description="Study funders.",
            json_schema_extra={"auto_fill": False},
        ),
    ] = []
    characteristic_types: Annotated[
        list[CharacteristicDefinition],
        Field(
            description="Study characteristic types.",
            json_schema_extra={"auto_fill": False},
        ),
    ] = []
    study_design_descriptors: Annotated[
        StudyDesignDescriptors,
        Field(
            description="Content of study design descriptors section.",
            json_schema_extra={"auto_fill": True, "header_name": ""},
        ),
    ] = StudyDesignDescriptors()
    study_publications: Annotated[
        StudyPublications,
        Field(
            description="Content of study publications section.",
            json_schema_extra={"auto_fill": True, "header_name": ""},
        ),
    ] = StudyPublications()
    study_factors: Annotated[
        StudyFactors,
        Field(
            description="Content of study factors section.",
            json_schema_extra={"auto_fill": True, "header_name": ""},
        ),
    ] = StudyFactors()
    study_assays: Annotated[
        StudyAssays,
        Field(
            description="Study assay section of i_Investigation.txt file. "
            "This section contains study assays and comments.",
            json_schema_extra={"auto_fill": True, "header_name": ""},
        ),
    ] = StudyAssays()
    study_protocols: Annotated[
        StudyProtocols,
        Field(
            description="Content of study protocols section.",
            json_schema_extra={"auto_fill": True, "header_name": ""},
        ),
    ] = StudyProtocols()
    study_contacts: Annotated[
        StudyContacts,
        Field(
            description="Content of study contacts section.",
            json_schema_extra={"auto_fill": True, "header_name": ""},
        ),
    ] = StudyContacts()


class Investigation(BaseSection):
    isatab_config: Annotated[
        IsaTabConfig,
        Field(exclude=True),
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
            description="Investigation identifier.",
            json_schema_extra={"auto_fill": True, "header_name": "Identifier"},
        ),
    ] = ""
    title: Annotated[
        str,
        Field(
            description="A concise name given to the investigation.",
            json_schema_extra={"auto_fill": True, "header_name": "Title"},
        ),
    ] = ""
    description: Annotated[
        str,
        Field(
            description="A textual description of the investigation.",
            json_schema_extra={"auto_fill": True, "header_name": "Description"},
        ),
    ] = ""
    submission_date: Annotated[
        str,
        Field(
            description="The date on which the investigation was reported "
            "to the MetaboLights repository. "
            "String formatted as ISO8601 date YYYY-MM-DD",
            json_schema_extra={"auto_fill": True, "header_name": "Submission Date"},
        ),
    ] = ""
    public_release_date: Annotated[
        str,
        Field(
            description="The date on which the investigation was released publicly. "
            "String formatted as ISO8601 date YYYY-MM-DD",
            json_schema_extra={"auto_fill": True, "header_name": "Public Release Date"},
        ),
    ] = ""

    ontology_source_references: Annotated[
        OntologySourceReferences,
        Field(
            description="Ontology sources used in the i_Investigation.txt file",
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
            description="All publications "
            "prepared to report results of the investigation.",
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

    def sync_study_comments_from_fields(self):
        if not self.studies:
            return

        study_comment_field_map = OrderedDict(
            [
                ("Revision", "revision_number"),
                ("Revision Date", "revision_date"),
                ("Revision Log", "revision_comment"),
                ("License", "dataset_license"),
                ("MHD Accession", "mhd_accession"),
                ("MHD Model Version", "mhd_model_version"),
                ("Study Category", "study_category"),
                ("Template Version", "template_version"),
                ("Sample Template", "sample_template"),
                ("Created At", "created_at"),
            ]
        )
        for study in self.studies:
            comment_values = OrderedDict()
            comment_names = set()
            for comment_name, field_name in study_comment_field_map.items():
                val = getattr(study, field_name or "")
                if val:
                    comment_values[comment_name] = val
                    comment_names.add(comment_name.lower())
            old_study_comments = study.comments
            study.comments = [
                Comment(name=x, value=[y]) for x, y in comment_values.items()
            ]

            funder_comments = OrderedDict(
                [("Funder", []), ("Funder ROR Id", []), ("Grant Identifier", [])]
            )

            if study.funders:
                for funder in study.funders:
                    if (
                        funder.funder_name
                        or funder.funder_id
                        or ";".join(funder.grant_ids)
                    ):
                        funder_comments["Funder"].append(funder.funder_name)
                        funder_comments["Funder ROR Id"].append(funder.funder_id)
                        funder_comments["Grant Identifier"].append(
                            ";".join(funder.grant_ids)
                        )
            self.add_non_empty_comments(study.comments, funder_comments, comment_names)

            characteristic_comments = OrderedDict(
                [
                    ("Study Characteristics Name", []),
                    ("Study Characteristics Type", []),
                    ("Study Characteristics Type Term Source REF", []),
                    ("Study Characteristics Type Term Accession Number", []),
                    ("Study Characteristics Value Format", []),
                ]
            )
            if study.characteristic_types:
                for characteristic in study.characteristic_types:
                    characteristic_comments["Study Characteristics Name"].append(
                        characteristic.name
                    )
                    characteristic_comments["Study Characteristics Type"].append(
                        characteristic.type
                    )
                    characteristic_comments[
                        "Study Characteristics Type Term Accession Number"
                    ].append(characteristic.term_accession_number)
                    characteristic_comments[
                        "Study Characteristics Type Term Source REF"
                    ].append(characteristic.term_source_ref)
                    characteristic_comments[
                        "Study Characteristics Value Format"
                    ].append(characteristic.value_format)

            self.add_non_empty_comments(
                study.comments,
                characteristic_comments,
                comment_names,
                old_study_comments,
            )

    def sync_study_design_descriptor_comments_from_fields(self):
        if not self.studies:
            return
        for study in self.studies:
            descriptor_comments = OrderedDict(
                [("Study Design Category", []), ("Study Design Source", [])]
            )
            old_comments = study.study_design_descriptors.comments
            comment_names = set()
            if study.study_design_descriptors.design_types:
                study.study_design_descriptors.comments = []
                for characteristic in study.study_design_descriptors.design_types:
                    descriptor_comments["Study Design Category"].append(
                        characteristic.category
                    )
                    descriptor_comments["Study Design Source"].append(
                        characteristic.source
                    )
            self.add_non_empty_comments(
                study.study_design_descriptors.comments,
                descriptor_comments,
                comment_names,
                old_comments,
            )

    def sync_study_factor_comments_from_fields(self):
        if not self.studies:
            return
        for study in self.studies:
            factor_comments = OrderedDict([("Study Factor Value Format", [])])
            old_comments = study.study_factors.comments
            comment_names = set()

            if study.study_factors.factors:
                study.study_factors.comments = []
                comment_names = set([x.lower() for x in factor_comments])
                for characteristic in study.study_factors.factors:
                    factor_comments["Study Factor Value Format"].append(
                        characteristic.value_format or ""
                    )
            self.add_non_empty_comments(
                study.study_factors.comments,
                factor_comments,
                comment_names,
                old_comments,
            )

    def sync_protocol_parameter_comments_from_fields(self):
        if not self.studies:
            return
        for study in self.studies:
            protocol_param_comments = OrderedDict(
                [("Study Protocol Parameters Value Format", [])]
            )
            old_comments = study.study_protocols.comments
            comment_names = set()
            protocols = study.study_protocols.protocols
            if protocols:
                study.study_protocols.comments = []
                comment_names = set([x.lower() for x in protocol_param_comments])
                for protocol in protocols:
                    values = [
                        x.value_format or ""
                        for x in protocol.parameters
                        if x.value_format and x.value_format.strip()
                    ]
                    param_value_formats = ""
                    if values:
                        param_value_formats = ";".join(
                            [x.value_format or "" for x in protocol.parameters]
                        )
                    protocol_param_comments[
                        "Study Protocol Parameters Value Format"
                    ].append(param_value_formats or "")

            self.add_non_empty_comments(
                study.study_protocols.comments,
                protocol_param_comments,
                comment_names,
                old_comments,
            )

    def sync_study_contact_comments_from_fields(self):
        if not self.studies:
            return
        for study in self.studies:
            old_comments = study.study_contacts.comments
            comment_names = set()
            study.study_contacts.comments = []

            for comment_name, field_name in [
                ("Study Person ORCID", "orcid"),
                ("Study Person Additional Email", "additional_emails"),
                ("Study Person Affiliation ROR Id", "affiliation_ror_id"),
            ]:
                contact_comments = OrderedDict([(comment_name, [])])
                if study.study_contacts.people:
                    for person in study.study_contacts.people:
                        val = getattr(person, field_name) or ""
                        if isinstance(val, list):
                            val = ";".join(val)
                        contact_comments[comment_name].append(val)

                self.add_non_empty_comments(
                    study.study_contacts.comments, contact_comments, comment_names
                )

            self.add_non_empty_comments(
                study.study_contacts.comments, {}, comment_names, old_comments
            )

    def sync_assay_comments_from_fields(self):
        if not self.studies:
            return
        for study in self.studies:
            assay_comments = OrderedDict([("Assay Identifier", [])])
            result_file_format_comments = OrderedDict(
                [("Assay Result File Format", [])]
            )
            assay_type_comments = OrderedDict(
                [
                    ("Assay Type", []),
                    ("Assay Type Term Accession Number", []),
                    ("Assay Type Term Source REF", []),
                ]
            )
            assay_omics_comments = OrderedDict(
                [
                    ("Omics Type", []),
                    ("Omics Type Term Accession Number", []),
                    ("Omics Type Term Source REF", []),
                ]
            )
            assay_descriptor_comments = OrderedDict(
                [
                    ("Assay Descriptor", []),
                    ("Assay Descriptor Term Accession Number", []),
                    ("Assay Descriptor Term Source REF", []),
                    ("Assay Descriptor Category", []),
                    ("Assay Descriptor Source", []),
                ]
            )
            old_comments = study.study_assays.comments
            comment_names = set()
            if study.study_assays:
                study.study_assays.comments = []

                for assay in study.study_assays.assays:
                    assay_comments["Assay Identifier"].append(
                        assay.assay_identifier or ""
                    )
                    result_file_format_comments["Assay Result File Format"].append(
                        assay.result_file_format or ""
                    )
                    assay_type_comments["Assay Type"].append(
                        assay.assay_type.term or ""
                    )
                    assay_type_comments["Assay Type Term Accession Number"].append(
                        assay.assay_type.term_accession_number
                        if assay.assay_type
                        else ""
                    )
                    assay_type_comments["Assay Type Term Source REF"].append(
                        assay.assay_type.term_source_ref if assay.assay_type else ""
                    )
                    assay_omics_comments["Omics Type"].append(
                        assay.omics_type.term if assay.omics_type else ""
                    )
                    assay_omics_comments["Omics Type Term Accession Number"].append(
                        assay.omics_type.term_accession_number
                        if assay.omics_type
                        else ""
                    )
                    assay_omics_comments["Omics Type Term Source REF"].append(
                        assay.omics_type.term_source_ref if assay.omics_type else ""
                    )

                    for term, field_name in [
                        ("Assay Descriptor", "term"),
                        (
                            "Assay Descriptor Term Accession Number",
                            "term_accession_number",
                        ),
                        ("Assay Descriptor Term Source REF", "term_source_ref"),
                        ("Assay Descriptor Category", "category"),
                        ("Assay Descriptor Source", "source"),
                    ]:
                        assay_descriptor_comments[term].append(
                            ";".join(
                                [
                                    getattr(x, field_name)
                                    for x in assay.assay_descriptors
                                    if x and x.term
                                ]
                            )
                        )
            self.add_non_empty_comments(
                study.study_assays.comments, assay_comments, comment_names
            )
            self.add_non_empty_comments(
                study.study_assays.comments, assay_type_comments, comment_names
            )
            self.add_non_empty_comments(
                study.study_assays.comments, assay_omics_comments, comment_names
            )
            self.add_non_empty_comments(
                study.study_assays.comments,
                assay_descriptor_comments,
                comment_names,
            )
            self.add_non_empty_comments(
                study.study_assays.comments,
                result_file_format_comments,
                comment_names,
                old_comments,
            )

    def add_non_empty_comments(
        self,
        new_comment_list: list[Comment],
        field_comments_map: OrderedDict[str, list[str]],
        new_comment_names: set[str],
        old_comment_list: None | list[Comment] = None,
    ):
        empty = True
        for v in field_comments_map.values():
            non_empty_vals = [x for x in v if str(x)]
            if non_empty_vals:
                empty = False
                break

        if not empty:
            new_comment_names.update([x.lower() for x in field_comments_map.keys()])

            new_comment_list.extend(
                [Comment(name=x, value=y) for x, y in field_comments_map.items()]
            )
        if old_comment_list:
            for old_comment in old_comment_list:
                if old_comment.name.lower() not in new_comment_names:
                    new_comment_list.append(old_comment)

    def sync_comments_from_fields(self):
        self.sync_study_comments_from_fields()
        self.sync_study_design_descriptor_comments_from_fields()
        self.sync_study_contact_comments_from_fields()
        self.sync_assay_comments_from_fields()
        self.sync_study_factor_comments_from_fields()
        self.sync_protocol_parameter_comments_from_fields()

    def sync_fields_from_comments(self):
        self.sync_study_design_descriptors_from_comments()
        self.sync_contact_fields_from_comments()
        self.sync_assay_fields_from_comments()
        self.sync_study_fields_from_comments()
        self.sync_factors_from_comments()
        self.sync_protocols_from_comments()

    def sync_study_design_descriptors_from_comments(self):
        if not self.studies:
            return
        design_descriptor_comment_field_map = {
            "study design category": "category",
            "study design source": "source",
        }
        for study in self.studies:
            if not study.study_design_descriptors.comments:
                continue
            comments_dict: dict[str, list[str]] = {}
            for comment in study.study_design_descriptors.comments:
                if comment.name:
                    comments_dict[comment.name.lower()] = comment.value

            for comment_name, field_name in design_descriptor_comment_field_map.items():
                val = comments_dict.get(comment_name, [])
                if not val:
                    continue
                for idx, comment_item in enumerate(val):
                    types = study.study_design_descriptors.design_types
                    if len(types) > idx:
                        setattr(types[idx], field_name, comment_item or "")

    def sync_factors_from_comments(self):
        if not self.studies:
            return
        factor_comment_field_map = {"study factor value format": "value_format"}
        for study in self.studies:
            if not study.study_factors.comments:
                continue
            comments_dict: dict[str, list[str]] = {}
            for comment in study.study_factors.comments:
                if comment.name:
                    comments_dict[comment.name.lower()] = comment.value

            for comment_name, field_name in factor_comment_field_map.items():
                val = comments_dict.get(comment_name, [])
                if not val:
                    continue
                for idx, comment_item in enumerate(val):
                    factors = study.study_factors.factors
                    if len(factors) > idx:
                        setattr(factors[idx], field_name, comment_item or "")

    def sync_protocols_from_comments(self):
        if not self.studies:
            return
        protocol_comment_field_map = {
            "study protocol parameters value format": "value_format"
        }
        for study in self.studies:
            if not study.study_protocols.comments:
                continue
            comments_dict: dict[str, list[str]] = {}
            for comment in study.study_protocols.comments:
                if comment.name:
                    comments_dict[comment.name.lower()] = comment.value

            for comment_name, field_name in protocol_comment_field_map.items():
                val = comments_dict.get(comment_name, [])
                if not val:
                    continue
                for idx, comment_item in enumerate(val):
                    protocols = study.study_protocols.protocols
                    if len(protocols) > idx:
                        parameter_comments = comment_item.split(";")
                        for param_ind, param in enumerate(parameter_comments):
                            if len(protocols[idx].parameters) > param_ind:
                                setattr(
                                    protocols[idx].parameters[param_ind],
                                    field_name,
                                    param or "",
                                )

    def sync_contact_fields_from_comments(self):
        if not self.studies:
            return
        for study in self.studies:
            if not study.study_contacts.comments:
                continue
            comments_dict: dict[str, list[str]] = {}
            for comment in study.study_contacts.comments:
                if comment.name:
                    comments_dict[comment.name.lower()] = comment.value

            orcid = comments_dict.get("study person orcid", [])
            additional_emails = comments_dict.get("study person additional email", [])
            affiliation_ror_id = comments_dict.get(
                "study person affiliation ror id", []
            )

            for idx, contact in enumerate(study.study_contacts.people):
                if len(orcid) > idx:
                    contact.orcid = orcid[idx] or ""
                if len(affiliation_ror_id) > idx:
                    contact.affiliation_ror_id = affiliation_ror_id[idx] or ""
                if len(additional_emails) > idx:
                    additional_email = additional_emails[idx] or ""
                    additional_email = additional_email.replace(",", ";")
                    additional_email = additional_email.replace(" ", "")
                    contact.additional_emails = [
                        x for x in additional_email.split(";") if x
                    ]

    def sync_assay_fields_from_comments(self):
        if not self.studies:
            return
        for study in self.studies:
            if not study.study_assays.comments:
                continue
            comments_dict: dict[str, list[str]] = {}
            for comment in study.study_assays.comments:
                if comment.name:
                    comments_dict[comment.name.lower()] = comment.value

            identifier = comments_dict.get("assay identifier", [])
            assay_type = comments_dict.get("assay type", [])
            assay_type_term_accession = comments_dict.get(
                "assay type term accession number", []
            )
            assay_type_term_source = comments_dict.get("assay type term source ref", [])

            omics_type = comments_dict.get("omics type", [])
            omics_type_term_accession = comments_dict.get(
                "omics type term accession number", []
            )
            omics_type_term_source = comments_dict.get("omics type term source ref", [])

            assay_descriptor = comments_dict.get("assay descriptor", [])
            assay_descriptor_term_accession = comments_dict.get(
                "assay descriptor term accession number", []
            )
            assay_descriptor_term_source = comments_dict.get(
                "assay descriptor term source ref", []
            )
            assay_descriptor_category = comments_dict.get(
                "assay descriptor category", []
            )
            assay_descriptor_source = comments_dict.get("assay descriptor source", [])
            result_file_format = comments_dict.get("assay result file format", [])

            for idx, assay in enumerate(study.study_assays.assays):
                if len(identifier) > idx:
                    assay.assay_identifier = identifier[idx].strip()
                if len(result_file_format) > idx:
                    assay.result_file_format = result_file_format[idx].strip()
                if len(assay_type) > idx:
                    assay.assay_type.term = assay_type[idx].strip()
                if len(assay_type_term_source) > idx:
                    assay.assay_type.term_source_ref = assay_type_term_source[
                        idx
                    ].strip()
                if len(assay_type_term_accession) > idx:
                    assay.assay_type.term_accession_number = assay_type_term_accession[
                        idx
                    ].strip()

                if len(omics_type) > idx:
                    assay.omics_type.term = omics_type[idx].strip()
                if len(omics_type_term_source) > idx:
                    assay.omics_type.term_source_ref = omics_type_term_source[
                        idx
                    ].strip()
                if len(omics_type_term_accession) > idx:
                    assay.omics_type.term_accession_number = omics_type_term_accession[
                        idx
                    ].strip()
                desc = assay_descriptor[idx] if len(assay_descriptor) > idx else ""
                desc_term_accession = (
                    assay_descriptor_term_accession[idx]
                    if len(assay_descriptor_term_accession) > idx
                    else ""
                )
                desc_term_source = (
                    assay_descriptor_term_source[idx].strip()
                    if len(assay_descriptor_term_source) > idx
                    else ""
                )
                desc_category = (
                    assay_descriptor_category[idx].strip()
                    if len(assay_descriptor_category) > idx
                    else ""
                )
                desc_source = (
                    assay_descriptor_source[idx].strip()
                    if len(assay_descriptor_source) > idx
                    else ""
                )
                if len(desc.split(";")) > 1:
                    desc_parts = desc.split(";")
                    desc_term_accession_parts = desc_term_accession.split(";")
                    desc_term_source_parts = desc_term_source.split(";")
                    desc_category_parts = desc_category.split(";")
                    desc_source_parts = desc_source.split(";")
                    for sub_index, desc in enumerate(desc_parts):
                        assay.assay_descriptors.append(
                            ExtendedOntologyAnnotation(
                                term=desc,
                                term_accession_number=desc_term_accession_parts[
                                    sub_index
                                ]
                                if len(desc_term_accession_parts) > sub_index
                                else "",
                                term_source_ref=desc_term_source_parts[sub_index]
                                if len(desc_term_source_parts) > sub_index
                                else "",
                                category=desc_category_parts[sub_index]
                                if len(desc_category_parts) > sub_index
                                else "",
                                source=desc_source_parts[sub_index]
                                if len(desc_source_parts) > sub_index
                                else "",
                            )
                        )
                else:
                    assay.assay_descriptors.append(
                        ExtendedOntologyAnnotation(
                            term=desc,
                            term_accession_number=desc_term_accession,
                            term_source_ref=desc_term_source,
                            category=desc_category,
                            source=desc_source,
                        )
                    )

    def sync_study_fields_from_comments(self):
        if not self.studies:
            return
        study_comment_field_map = {
            "revision": "revision_number",
            "revision date": "revision_date",
            "revision log": "revision_comment",
            "license": "dataset_license",
            "mhd accession": "mhd_accession",
            "mhd model version": "mhd_model_version",
            "study category": "study_category",
            "template version": "template_version",
            "sample template": "sample_template",
            "created at": "created_at",
        }
        for study in self.studies:
            if not study.comments:
                continue
            comments_dict: dict[str, list[str]] = {}
            for comment in study.comments:
                if comment.name:
                    comments_dict[comment.name.lower()] = comment.value

            for comment_name, field_name in study_comment_field_map.items():
                val = comments_dict.get(comment_name, [])
                if val:
                    setattr(study, field_name, val[0] if val else "")

            funders = comments_dict.get("funder", [])
            funder_ids = comments_dict.get("funder ror id", [])
            grant_ids = comments_dict.get("grant identifier", [])
            counts = [len(x) for x in (funders, funder_ids, grant_ids) if x and x[0]]

            if counts and len(counts) > 0:
                study.funders = []
                for idx in range(max(counts)):
                    study.funders.append(
                        Funder(
                            funder_name=funders[idx] if len(funders) > idx else "",
                            funder_id=funder_ids[idx] if len(funder_ids) > idx else "",
                            grant_ids=grant_ids[idx].split(";")
                            if len(grant_ids) > idx
                            else "",
                        )
                    )
            characteristic_names = comments_dict.get("study characteristics name", [])
            characteristic_types = comments_dict.get("study characteristics type", [])
            characteristic_type_accessions = comments_dict.get(
                "study characteristics type term accession number", []
            )
            characteristic_type_sources = comments_dict.get(
                "study characteristics type term source ref", []
            )
            characteristic_value_formats = comments_dict.get(
                "study characteristics value format", []
            )
            counts = [
                len(x)
                for x in (
                    characteristic_names,
                    characteristic_types,
                    characteristic_type_accessions,
                    characteristic_type_sources,
                    characteristic_value_formats,
                )
                if x and x[0]
            ]
            if counts and len(counts) > 0:
                study.characteristic_types = []
                for idx in range(max(counts)):
                    study.characteristic_types.append(
                        CharacteristicDefinition(
                            name=characteristic_names[idx]
                            if len(characteristic_names) > idx
                            else "",
                            type=characteristic_types[idx]
                            if len(characteristic_types) > idx
                            else "",
                            term_accession_number=characteristic_type_accessions[idx]
                            if len(characteristic_type_accessions) > idx
                            else "",
                            term_source_ref=characteristic_type_sources[idx]
                            if len(characteristic_type_sources) > idx
                            else "",
                            value_format=characteristic_value_formats[idx]
                            if len(characteristic_value_formats) > idx
                            else "",
                        )
                    )
