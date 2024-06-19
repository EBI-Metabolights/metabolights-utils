from typing import List, Union

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
            description="The name of the source of a term; i.e. the source controlled vocabulary or ontology."
            " These names will be used in all corresponding Term Source REF fields that occur elsewhere.",
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
            description="The version number of the Term Source to support terms tracking.",
            json_schema_extra={"auto_fill": True, "header_name": "Source Version"},
        ),
    ] = ""
    source_description: Annotated[
        str,
        Field(
            description="Description of source. Use for disambiguating resources when homologous prefixes have been used.",
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
            description="The accession number from the Term Source associated with the term.",
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
            "Ontology source reference names should be defined in ontology source references section in i_Investigation.txt file",
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
            description="The PubMed IDs of the publication.",
            json_schema_extra={"auto_fill": True, "header_name": "PubMed ID"},
        ),
    ] = ""
    doi: Annotated[
        str,
        Field(
            description="A Digital Object Identifier (DOI) for the publication.",
            json_schema_extra={"auto_fill": True, "header_name": "Publication DOI"},
        ),
    ] = ""
    author_list: Annotated[
        str,
        Field(
            description="The list of authors associated with the publication. Comma (,) is recommended to define multiple authors.",
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
            description="A term describing the status of that publication (i.e. EFO:submitted, EFO:in preparation, EFO:published).",
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
            description="Last name of a person associated with the investigation or study.",
            json_schema_extra={"auto_fill": True, "header_name": "Last Name"},
        ),
    ] = ""
    first_name: Annotated[
        str,
        Field(
            description="First name of person associated with the investigation or study.",
            json_schema_extra={"auto_fill": True, "header_name": "First Name"},
        ),
    ] = ""
    mid_initials: Annotated[
        str,
        Field(
            description="Middle name initials (if exists) of person associated with the investigation or study",
            json_schema_extra={"auto_fill": True, "header_name": "Mid Initials"},
        ),
    ] = ""
    email: Annotated[
        str,
        Field(
            description="Email address of person associated with the investigation or study",
            json_schema_extra={"auto_fill": True, "header_name": "Email"},
        ),
    ] = ""
    phone: Annotated[
        str,
        Field(
            description="Phone number of person associated with the investigation or study",
            json_schema_extra={"auto_fill": True, "header_name": "Phone"},
        ),
    ] = ""
    fax: Annotated[
        str,
        Field(
            description="Fax number of person associated with the investigation or study",
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
            description="Affiliation of person associated with the investigation or study",
            json_schema_extra={"auto_fill": True, "header_name": "Affiliation"},
        ),
    ] = ""
    roles: Annotated[
        List[OntologyAnnotation],
        Field(
            description="Roles of person associated with the investigation or study. "
            "Multiple role can be defined for each person. Role is defined as an ontology term. "
            "e.g., NCIT:Investigator, NCIT:Author",
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
            description="The name of one factor used in the Study files. "
            "A factor corresponds to an independent variable manipulated by the experimentalist "
            "with the intention to affect biological systems in a way that can be measured by an assay.",
            json_schema_extra={"auto_fill": True, "header_name": "Name"},
        ),
    ] = ""
    type: Annotated[
        OntologyAnnotation,
        Field(
            description="A term allowing the classification of the factor into categories. The term is a controlled vocabulary or an ontology",
            json_schema_extra={"auto_fill": True, "header_name": "Type"},
        ),
    ] = OntologyAnnotation()

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
            description="A term to qualify what is being measured (e.g. metabolite identification).",
            json_schema_extra={"auto_fill": True, "header_name": "Measurement Type"},
        ),
    ] = OntologyAnnotation()
    technology_type: Annotated[
        OntologyAnnotation,
        Field(
            description="Term to identify the technology used to perform the measurement, e.g. NMR spectrometry assay, mass spectrometry assay",
            json_schema_extra={"auto_fill": True, "header_name": "Technology Type"},
        ),
    ] = OntologyAnnotation()
    technology_platform: Annotated[
        str,
        Field(
            description="Platform information such as assay technique name, polarity, column model, manufacturer, platform name.",
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
            description="Pointer to external protocol resources that can be accessed by their Uniform Resource Identifier (URI).",
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
        List[OntologyAnnotation],
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
        List[ValueTypeAnnotation],
        Field(
            description="Protocol’s components; e.g. instrument names, software names, and reagents names.",
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
        List[OntologyAnnotation],
        Field(
            description="Design descriptors defined in study design descriptors section.",
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
            description="A unique identifier, either a temporary identifier generated by MetaboLights repository.",
            json_schema_extra={"auto_fill": True, "header_name": "Identifier"},
        ),
    ] = ""
    title: Annotated[
        str,
        Field(
            description="A concise phrase used to encapsulate the purpose and goal of the study.",
            json_schema_extra={"auto_fill": True, "header_name": "Title"},
        ),
    ] = ""
    description: Annotated[
        str,
        Field(
            description="A textual description of the study, with components such as objective or goals.",
            json_schema_extra={"auto_fill": True, "header_name": "Description"},
        ),
    ] = ""
    submission_date: Annotated[
        str,
        Field(
            description="The date on which the study is submitted to an archive. String formatted as ISO8601 date YYYY-MM-DD",
            json_schema_extra={"auto_fill": True, "header_name": "Submission Date"},
        ),
    ] = ""
    public_release_date: Annotated[
        str,
        Field(
            description="The date on which the study SHOULD be released publicly. String formatted as ISO8601 date YYYY-MM-DD",
            json_schema_extra={"auto_fill": True, "header_name": "Public Release Date"},
        ),
    ] = ""
    file_name: Annotated[
        str,
        Field(
            description="Name of the Sample Table file corresponding the definition of that Study.",
            json_schema_extra={"auto_fill": True, "header_name": "File Name"},
        ),
    ] = ""

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
            description="Study assay section of i_Investigation.txt file. This section contains study assays and comments.",
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
            description="The date on which the investigation was reported to the MetaboLights repository. String formatted as ISO8601 date YYYY-MM-DD",
            json_schema_extra={"auto_fill": True, "header_name": "Submission Date"},
        ),
    ] = ""
    public_release_date: Annotated[
        str,
        Field(
            description="The date on which the investigation was released publicly. String formatted as ISO8601 date YYYY-MM-DD",
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
            description="All publications prepared to report results of the investigation.",
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
