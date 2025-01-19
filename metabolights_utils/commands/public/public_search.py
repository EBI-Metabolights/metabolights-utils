import json
from typing import Any, Callable, Dict, Literal, Union

import click

from metabolights_utils.commands.utils import convert_html_to_plain_text, split_to_lines
from metabolights_utils.provider import definitions
from metabolights_utils.provider.utils import rest_api_post

JoinOperator = Literal["and", "or"]


@click.command(no_args_is_help=True, name="search")
@click.option(
    "--search_rest_api_url",
    "-u",
    default=definitions.default_study_search_rest_api_url,
    help="MetaboLights search API URL.",
)
@click.option(
    "--skip",
    "-s",
    default=0,
    type=int,
    help="Skip n items from the matched items.",
)
@click.option(
    "--limit",
    "-l",
    default=10,
    type=int,
    help="Maximum number items in response. Maximum return size is 100 items.",
)
@click.option(
    "--query_join_operator",
    "-j",
    default="and",
    type=str,
    help="If multiple keywords are defined and there is no join operator (+, |) in query, One of the 'and' (default) or 'or' operator will be used.",
)
@click.option(
    "--body",
    "-b",
    default=None,
    type=str,
    help="Advanced filter options in json format. Please read the API documentation.",
)
@click.option(
    "--study_ids",
    "--id",
    is_flag=True,
    default=False,
    help="Shows only MetaboLights accession numbers.",
)
@click.option(
    "--raw",
    is_flag=True,
    default=False,
    help="Shows raw result in json format.",
)
@click.argument("query", required=False)
def public_search(
    search_rest_api_url: str = "",
    skip: int = 0,
    limit: int = 10,
    query_join_operator: JoinOperator = "and",
    body: Union[None, str] = None,
    query: Union[None, str] = None,
    study_ids: bool = False,
    raw: bool = False,
):
    """
    Search public studies with query keywords. If there are multiple search keywords and no join operator (+, |) defined, results are merged with the selected query join operator (and, or)

    query: query terms that will be in search. e.g. cancer, (mus musculus)
    """

    sub_path = "/public/search/studies/_search"
    parameters = {
        "limit": limit,
        "skip": skip,
        "query_join_operator": query_join_operator,
    }
    if query:
        parameters["query"] = query.strip()
    else:
        query = ""
    try:
        body = json.loads(body) if body else {}
    except Exception as ex:
        click.echo(str(ex))
        exit(1)
    headers = {}
    url = f"{search_rest_api_url.rstrip('/')}/{sub_path.lstrip('/')}"
    response, error = rest_api_post(
        url=url,
        headers=headers,
        parameters=parameters,
        json_body=body,
    )
    if response and not error:
        if raw and "content" in response:
            str_response = json.dumps(response["content"], indent=4)
            click.echo(str_response)
        else:
            print_search_response(study_ids, query, response, click.echo)
    else:
        click.echo(error)
        exit(1)


def print_search_response(
    show_only_study_ids: bool, query: str, response: Dict[str, Any], log: Callable
):
    if "status" in response and response["status"].lower() == "success":
        log(f"MetaboLights public study search results for query: {query}")
    else:
        log(f"Failure of MetaboLights public study search for query: {query}")
        exit(1)

    if (
        "content" not in response
        or not response["content"]
        or "page" not in response["content"]
        or "total" not in response["content"]
        or "pageSize" not in response["content"]
    ):
        log("Invalid response.")
        exit(1)

    content = response["content"]
    page = content["page"]
    total = content["total"]
    page_size = content["pageSize"]

    if total > 0:
        if show_only_study_ids:
            id_list = [x["studyId"] for x in page if "studyId" in x]
            log(f"[{', '.join(id_list)}]")
            exit(0)
        else:
            log(f"{page_size} of total {total} results")
    else:
        if show_only_study_ids:
            log("[]")
        else:
            log("No results found.")
        exit(0)

    for item in page:
        if "studyId" in item and "title" in item:
            log(f"  - {item['studyId']}: {item['title']}")
        if "contacts" in item:
            names = [f"{x['firstName']} {x['lastName']}" for x in item["contacts"]]
            log(f"\t* Submitters: {', '.join(names)}")

        if "description" in item:
            log("\t* Description:")
            lines = split_to_lines(convert_html_to_plain_text(item["description"]))
            for line in lines:
                log(f"\t  {line}")
        if "assayTechniques" in item:
            names = [
                x["name"] for x in item["assayTechniques"] if "name" in x and x["name"]
            ]
            log(f"\t* Techniques: {', '.join(names).strip(',').strip().strip(',')}")
        for terms in [
            ("designDescriptors", "Design descriptors"),
            ("factors", "Factors"),
            ("organisms", "Organisms"),
            ("organismParts", "Organism parts"),
        ]:
            if terms[0] in item:
                log(f"\t* {terms[1]}:")
                for descriptor in item[terms[0]]:
                    parts = [
                        descriptor["termSourceRef"],
                        descriptor["term"],
                        descriptor["termAccessionNumber"],
                    ]

                    log(f"\t  - {', '.join(parts).strip(',').strip().strip(',')}")


if __name__ == "__main__":
    public_search(
        [
            "(chicken | turkey)",
            "--body",
            '{"assayTechniqueNameFilter": {"joinOperator": "and", "values": ["NMR"]}}',
        ]
    )
