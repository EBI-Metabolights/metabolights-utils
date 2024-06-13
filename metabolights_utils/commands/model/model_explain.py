import os
from typing import Any, Dict, Union

import click
from pydantic.alias_generators import to_camel, to_snake

from metabolights_utils.commands.utils import split_to_lines
from metabolights_utils.models.metabolights.model import MetabolightsStudyModel


@click.command(name="explain")
@click.argument("model_pattern", required=False)
def model_explain(
    model_pattern: Union[None, str] = None,
):
    """Expain properties and sub-properties of MetaboLights study model. It lists root properties of the model, If it is not specified

    Examples:
    investigation -> explains properties of Investigation property of MetaboLights study model.
    investigation.studies -> explains properties of Study model
    investigation.studies.study_assays.assays -> explains properties of Assay model
    investigation.studies.study_assays.comments -> explains properties of Comment model of assay

    assays.assay_technique -> explains Assay Technique model

    """
    search_pattern = model_pattern
    schema = MetabolightsStudyModel.model_json_schema(
        by_alias=True, mode="serialization"
    )
    model_name = None
    title = None
    description = None
    if not search_pattern:
        model = schema
        model_name = "object"
        title = "MetaboLights Study Model"
        description = ""
    else:
        model, model_name, title, description = find_property(schema, search_pattern)

    click.echo(f"\nExplain '{search_pattern}'")
    if title:
        print_properties(schema, model_name, title, description, model)
    else:
        click.echo(f"Not valid search object '{search_pattern}'")


def print_properties(
    schema: Dict[str, Any],
    model_name: str,
    title: str,
    description: str,
    model: Dict[str, Any],
):
    required_properties = set()
    if model and "required" in model:
        required_properties = {x for x in model["required"]}
    properties = {}
    _type = None
    if model and "properties" in model:
        _type = define_type(schema, model["properties"])
        properties = model["properties"]
    enums = ""
    click.echo(f"\nDefinition: {title} [{model_name}]")

    if model and "enum" in model:
        enum = f", ".join([str(x) for x in model["enum"]])
        enums = "Valid values: " + "\n\t ".join(split_to_lines(enum))
    if description:
        dec = split_to_lines(description)
        click.echo("\t" + f"\n\t".join(dec) + (f" {enums}" if enums else ""))
    elif enums:
        click.echo(f"\t{enums}")
    property_names = list([x for x in properties.keys()])
    if property_names:
        property_names.sort()

        click.echo("\nProperties:")
        for property in property_names:
            target = properties[property]
            required_properties = set()
            if "" in target:
                required_properties = {x for x in target["required"]}

            property_name = to_snake(property)
            if "isatab_config" in property_name:
                continue
            required = f"{'***required***' if property in required_properties else ''}"

            _type = define_type(schema, target)

            click.echo(
                "  " + property_name + f" [{_type}] {required if required else ''}"
            )
            if "description" in target:
                dec = split_to_lines(target["description"])

            click.echo("\t" + f"\n\t".join(dec).strip() + "\n")


def define_type(schema: Dict[str, Any], desc: Dict[str, Any]):
    _type = ""
    if "type" in desc:
        _type = desc["type"]
    if not _type:
        if "allOf" in desc:
            types = []
            for item in desc["allOf"]:
                definition = item
                if "$ref" in definition:
                    types.append(definition["$ref"].split("/")[-1])
                else:
                    if "type" in item:
                        types.append(item["type"])
            _type = ", ".join(types)
            if len(types) > 1:
                _type = f"All of {_type}"
        elif "anyOf" in desc:
            types = []
            for item in desc["anyOf"]:
                definition = item
                if "$ref" in definition:
                    types.append(definition["$ref"].split("/")[-1])
                else:
                    if "type" in item:
                        types.append(item["type"])
            _type = ", ".join(types)
            if len(types) > 1:
                _type = f"Any of {_type}"

    else:

        if _type == "object" and "properties" not in desc:
            _type = "dictionary of"
        elif _type == "array":
            _type = "array of"

        if "additionalProperties" in desc and isinstance(
            desc["additionalProperties"], dict
        ):
            additional = desc["additionalProperties"]
            types = []
            if "$ref" in additional:
                child = additional["$ref"].split("/")[-1]
                if child in schema["$defs"]:
                    _type = f"{_type} {child}".strip()
                else:
                    sub_type = define_type(schema, schema["$defs"][child])
                    _type = f"{_type} {sub_type}".strip()
            else:
                child = None
                prefix = ""
                if "items" in additional:
                    items = additional["items"]
                    child_name = ""
                    if "$ref" in items:
                        child_name = items["$ref"].split("/")[-1]
                    if child_name in schema["$defs"]:
                        items = schema["$defs"][child_name]
                    if "properties" in items:
                        if "type" in items and items["type"] == "object":
                            return f"array of {child_name}"
                        else:
                            child = define_type(schema, items)
                    elif "type" in items:
                        child = items["type"]

                    prefix = "array of"
                    _type = f"{_type} {prefix} {child}".strip()
                elif "$ref" in additional:

                    child_name = additional["$ref"].split("/")[-1]
                    child = define_type(schema, schema["$defs"][child_name])
                    prefix = "dictionary of"
                    _type = f"{_type} {prefix} {child}".strip()

        elif "items" in desc:
            if "$ref" in desc["items"]:
                child = ""
                child = desc["items"]["$ref"].split("/")[-1]
            else:
                if "type" in desc["items"]:
                    child = desc["items"]["type"]
            if child:
                # if child in schema["$defs"]:
                #     _type = f"dictionary of {child}"
                # else:
                _type = f"array of {child}"

    return _type


def find_property(schema: Dict[str, Any], search_str: str):
    if "properties" not in schema:
        return None, None, None, None
    values = search_str.split(".")
    if not values:
        return None, None, None, None
    current_description = None
    current_model = schema

    current_properties = []
    if to_camel(search_str) in schema["$defs"]:
        current_model = schema["$defs"][to_camel(search_str)]
    if "properties" in current_model:
        current_properties = current_model["properties"]

    model_title_terms = []
    model_name = None
    not_matched = False
    if not values or "properties" not in current_model:
        return None, None, None, None
    for value in values:
        found = False
        property_name = to_camel(value)
        if "isatab_config" in property_name:
            continue
        if property_name in current_properties:

            definition = current_properties[property_name]
            _type = define_type(schema, definition)
            if _type and _type.split()[-1]:
                model = _type.split()[-1]
                if model in schema["$defs"]:
                    if "properties" in schema["$defs"][model]:
                        current_model = schema["$defs"][model]
                        current_properties = current_model["properties"]
                    elif "enum" in schema["$defs"][model]:
                        current_model = schema["$defs"][model]
                        current_properties = schema["$defs"][model]
                    else:
                        current_model = None
                        current_properties = None

                else:
                    current_model = None
                    current_properties = None

                if "description" in definition:
                    current_description = definition["description"]
                # if current_model and "enum" in current_model:
                #     enum = f", ".join([str(x) for x in current_model["enum"]])
                #     enums = "Valid values: " + "\n\t ".join(split_to_lines(enum))
                #     if current_description:
                #         current_description += f" {enums}"

                model_name = _type if _type else to_snake(property_name)
                model_title_terms.append(to_snake(property_name))

                found = True

            if not found:
                not_matched = True
                break
        else:
            not_matched = True
            break
    if not_matched:
        return None, None, None, current_description
    return (
        current_model,
        model_name,
        " -> ".join(model_title_terms),
        current_description,
    )


if __name__ == "__main__":
    model_explain()
