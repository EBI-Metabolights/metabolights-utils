from typing import List

from pydantic import Field

from metabolights_utils.models.isa.common import Comment, IsaAbstractModel

module_name = __name__


class BaseSection(IsaAbstractModel):
    section_header: str = Field("ONTOLOGY SOURCE REFERENCE", exclude=True)
    section_prefix: str = Field("", exclude=True)

    comments: List[Comment] = []

    class Config:
        field_order: List[str] = []


class OntologySourceReference(IsaAbstractModel):
    field_order: List[str] = [
        "source_name",
        "source_file",
        "source_version",
        "source_description",
    ]
    source_name: str = Field(
        "", source_description=True, auto_fill=True, header_name="Source Name"
    )
    source_file: str = Field("", auto_fill=True, header_name="Source File")
    source_version: str = Field("", auto_fill=True, header_name="Source Version")
    source_description: str = Field(
        "", auto_fill=True, header_name="Source Description"
    )


class OntologyAnnotation(IsaAbstractModel):
    field_order: List[str] = ["term", "term_accession_number", "term_source_ref"]

    term: str = Field("", auto_fill=True, header_name="")
    term_accession_number: str = Field(
        "", auto_fill=True, header_name="Term Accession Number"
    )
    term_source_ref: str = Field("", auto_fill=True, header_name="Term Source REF")


class ValueTypeAnnotation(IsaAbstractModel):
    field_order: List[str] = [
        "name",
        "type",
        "term_accession_number",
        "term_source_ref",
    ]
    name: str = Field("", auto_fill=True, header_name="Name")
    type: str = Field("", auto_fill=True, header_name="Type")
    term_accession_number: str = Field(
        "", auto_fill=True, header_name="Type Term Accession Number"
    )
    term_source_ref: str = Field("", auto_fill=True, header_name="Type Term Source REF")


class Publication(IsaAbstractModel):
    field_order: List[str] = ["pub_med_id", "doi", "author_list", "title", "status"]

    pub_med_id: str = Field("", auto_fill=True, header_name="PubMed ID")
    doi: str = Field("", auto_fill=True, header_name="Publication DOI")
    author_list: str = Field("", auto_fill=True, header_name="Publication Author List")
    title: str = Field("", auto_fill=True, header_name="Publication Title")
    status: OntologyAnnotation = Field(
        OntologyAnnotation(), auto_fill=True, header_name="Publication Status"
    )


class Person(IsaAbstractModel):
    field_order: List[str] = [
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
    last_name: str = Field("", auto_fill=True, header_name="Last Name")
    first_name: str = Field("", auto_fill=True, header_name="First Name")
    mid_initials: str = Field("", auto_fill=True, header_name="Mid Initials")
    email: str = Field("", auto_fill=True, header_name="Email")
    phone: str = Field("", auto_fill=True, header_name="Phone")
    fax: str = Field("", auto_fill=True, header_name="Fax")
    address: str = Field("", auto_fill=True, header_name="Address")
    affiliation: str = Field("", auto_fill=True, header_name="Affiliation")
    roles: List[OntologyAnnotation] = Field(
        [],
        auto_fill=True,
        header_name="Roles",
        text_multiple_value=True,
        seperator=";",
    )


class Factor(IsaAbstractModel):
    field_order: List[str] = ["name", "type"]
    name: str = Field("", auto_fill=True, header_name="Name")
    type: OntologyAnnotation = Field(
        OntologyAnnotation(), auto_fill=True, header_name="Type"
    )


class Assay(IsaAbstractModel):
    field_order: List[str] = [
        "file_name",
        "measurement_type",
        "technology_type",
        "technology_platform",
    ]
    file_name: str = Field("", auto_fill=True, header_name="File Name")
    measurement_type: OntologyAnnotation = Field(
        OntologyAnnotation(), auto_fill=True, header_name="Measurement Type"
    )
    technology_type: OntologyAnnotation = Field(
        OntologyAnnotation(), auto_fill=True, header_name="Technology Type"
    )
    technology_platform: str = Field(
        "", auto_fill=True, header_name="Technology Platform"
    )


class Protocol(IsaAbstractModel):
    field_order: List[str] = [
        "name",
        "protocol_type",
        "description",
        "uri",
        "version",
        "parameters",
        "components",
    ]
    name: str = Field("", auto_fill=True, header_name="Name")
    protocol_type: OntologyAnnotation = Field(
        OntologyAnnotation(), auto_fill=True, header_name="Type"
    )
    description: str = Field("", auto_fill=True, header_name="Description")
    uri: str = Field("", auto_fill=True, header_name="URI")
    version: str = Field("", auto_fill=True, header_name="Version")
    parameters: List[OntologyAnnotation] = Field(
        [],
        auto_fill=True,
        header_name="Parameters Name",
        text_multiple_value=True,
        seperator=";",
    )
    components: List[ValueTypeAnnotation] = Field(
        [],
        auto_fill=True,
        header_name="Components",
        text_multiple_value=True,
        seperator=";",
    )


######################################################################################################
# ISA TAB FILE SECTIONS
######################################################################################################


class OntologySourceReferences(BaseSection):
    field_order: List[str] = ["references"]

    section_header: str = Field("ONTOLOGY SOURCE REFERENCE", exclude=True)
    section_prefix: str = Field("Term", exclude=True)
    references: List[OntologySourceReference] = Field(
        [], auto_fill=True, header_name="", search_header="Source Name"
    )


class InvestigationPublications(BaseSection):
    section_header: str = Field("INVESTIGATION PUBLICATIONS", exclude=True)
    section_prefix: str = Field("", exclude=True)
    field_order: List[str] = ["publications"]
    publications: List[Publication] = Field(
        [], auto_fill=True, header_name="", search_header="Publication Title"
    )


class InvestigationContacts(BaseSection):
    section_header: str = Field("INVESTIGATION CONTACTS", exclude=True)
    section_prefix: str = Field("Person", exclude=True)

    field_order: List[str] = ["people"]
    people: List[Person] = Field(
        [], auto_fill=True, header_name="", search_header="Last Name"
    )


class StudyDesignDescriptors(BaseSection):
    field_order: List[str] = ["design_types"]
    section_header: str = Field("STUDY DESIGN DESCRIPTORS", exclude=True)
    section_prefix: str = Field("Design", exclude=True)
    design_types: List[OntologyAnnotation] = Field(
        [], auto_fill=True, header_name="Type"
    )


class StudyPublications(BaseSection):
    field_order: List[str] = ["publications"]
    section_header: str = Field("STUDY PUBLICATIONS", exclude=True)
    section_prefix: str = Field("", exclude=True)
    publications: List[Publication] = Field(
        [], auto_fill=True, header_name="", search_header="Publication Title"
    )


class StudyFactors(BaseSection):
    field_order: List[str] = ["factors"]
    section_header: str = Field("STUDY FACTORS", exclude=True)
    section_prefix: str = Field("Factor", exclude=True)
    factors: List[Factor] = Field(
        [], auto_fill=True, header_name="", search_header="Name"
    )


class StudyAssays(BaseSection):
    field_order: List[str] = ["assays"]
    section_header: str = Field("STUDY ASSAYS", exclude=True)
    section_prefix: str = Field("Assay", exclude=True)
    assays: List[Assay] = Field(
        [], auto_fill=True, header_name="", search_header="File Name"
    )


class StudyProtocols(BaseSection):
    field_order: List[str] = ["protocols"]
    section_header: str = Field("STUDY PROTOCOLS", exclude=True)
    section_prefix: str = Field("Protocol", exclude=True)
    protocols: List[Protocol] = Field(
        [], auto_fill=True, header_name="", search_header="Name"
    )


class StudyContacts(BaseSection):
    field_order: List[str] = ["people"]
    section_header: str = Field("STUDY CONTACTS", exclude=True)
    section_prefix: str = Field("Person", exclude=True)
    people: List[Person] = Field(
        [], auto_fill=True, header_name="", search_header="Last Name"
    )


class Study(BaseSection):
    field_order: List[str] = [
        "identifier",
        "title",
        "description",
        "submission_date",
        "public_release_date",
        "file_name",
    ]
    section_header: str = Field("STUDY", exclude=True)
    section_prefix: str = Field("Study", exclude=True)
    identifier: str = Field("", auto_fill=True, header_name="Identifier")
    title: str = Field("", auto_fill=True, header_name="Title")
    description: str = Field("", auto_fill=True, header_name="Description")
    submission_date: str = Field("", auto_fill=True, header_name="Submission Date")
    public_release_date: str = Field(
        "", auto_fill=True, header_name="Public Release Date"
    )
    file_name: str = Field("", auto_fill=True, header_name="File Name")

    study_design_descriptors: StudyDesignDescriptors = Field(
        StudyDesignDescriptors(), auto_fill=True, header_name=""
    )
    study_publications: StudyPublications = Field(
        StudyPublications(), auto_fill=True, header_name=""
    )
    study_factors: StudyFactors = Field(StudyFactors(), auto_fill=True, header_name="")
    study_assays: StudyAssays = Field(StudyAssays(), auto_fill=True, header_name="")
    study_protocols: StudyProtocols = Field(
        StudyProtocols(), auto_fill=True, header_name=""
    )
    study_contacts: StudyContacts = Field(
        StudyContacts(), auto_fill=True, header_name=""
    )


class Investigation(BaseSection):
    section_header: str = Field("INVESTIGATION", exclude=True)
    section_prefix: str = Field("Investigation", exclude=True)
    field_order: List[str] = [
        "identifier",
        "title",
        "description",
        "submission_date",
        "public_release_date",
    ]
    specification_version: str = Field("1.0")
    specification_date: str = Field("2016-10-28")

    identifier: str = Field("", auto_fill=True, header_name="Identifier")
    title: str = Field("", auto_fill=True, header_name="Title")
    description: str = Field("", auto_fill=True, header_name="Description")
    submission_date: str = Field("", auto_fill=True, header_name="Submission Date")
    public_release_date: str = Field(
        "", auto_fill=True, header_name="Public Release Date"
    )

    ontology_source_references: OntologySourceReferences = Field(
        OntologySourceReferences(), auto_fill=True, header_name="", inherit_prefix=False
    )
    investigation_publications: InvestigationPublications = Field(
        InvestigationPublications(), auto_fill=True, header_name=""
    )
    investigation_contacts: InvestigationContacts = Field(
        InvestigationContacts(), auto_fill=True, header_name=""
    )
    studies: List[Study] = []
