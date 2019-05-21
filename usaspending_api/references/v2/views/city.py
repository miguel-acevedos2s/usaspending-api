from django.conf import settings
from rest_framework.response import Response
from collections import OrderedDict

from usaspending_api.common.cache_decorator import cache_response
from usaspending_api.common.views import APIDocumentationView

from usaspending_api.common.elasticsearch.client import es_client_query
from usaspending_api.search.v2.elasticsearch_helper import es_sanitize
from usaspending_api.common.validator.tinyshield import validate_post_request


models = [
    {
        "name": "filter|country_code",
        "key": "filter|country_code",
        "type": "text",
        "text_type": "search",
        "optional": False,
    },
    {
        "key": "filter|state_code",
        "name": "fitler|state_code",
        "type": "text",
        "text_type": "search",
        "optional": True,
        "default": None,
        "allow_nulls": True,
    },
    {
        "key": "filter|scope",
        "name": "filter|scope",
        "type": "enum",
        "enum_values": ("recipient_location", "primary_place_of_performance"),
        "optional": False,
    },
    {"key": "search_text", "name": "search_text", "type": "text", "text_type": "search", "optional": False},
    {"key": "limit", "name": "limit", "type": "integer", "max": 500, "optional": True, "default": 10},
]


@validate_post_request(models)
class CityAutocompleteViewSet(APIDocumentationView):
    """
    endpoint_doc: usaspending_api/api_contracts/autocomplete/City.md
    """

    @cache_response()
    def post(self, request, format=None):
        search_text, country, state = prepare_search_terms(request.data)
        scope = "recipient_location" if request.data["filter"]["scope"] == "recipient_location" else "pop"
        limit = request.data["limit"]
        return_fields = ["{}_city_name".format(scope), "{}_state_code".format(scope)]

        query_string = create_elasticsearch_query(return_fields, scope, search_text, country, state)
        sorted_results = query_elasticsearch(query_string, search_text)
        response = OrderedDict([("count", len(sorted_results)), ("results", sorted_results[:limit])])

        return Response(response)


def prepare_search_terms(request_data):
    fields = [request_data["search_text"], request_data["filter"]["country_code"], request_data["filter"]["state_code"]]

    return [es_sanitize(field).upper() if isinstance(field, str) else field for field in fields]


def create_elasticsearch_query(return_fields, scope, search_text, country, state):
    query_string = create_es_search("wildcard", scope, search_text, country, state)
    query = {
        "_source": return_fields,
        "size": 0,
        "query": {
            "bool": {
                "must": query_string,
                "filter": {
                    "wildcard": {
                        "{}_city_name.keyword".format(scope): search_text + "*"
                    }
                }
            }
        },
        "aggs": {
            "cities": {
                "terms": {
                    "field": "{}.keyword".format(return_fields[0]),
                    "size": 5000,
                },
                "aggs": {
                    "states": {"terms": {"field": return_fields[1], "size": 100}}
                },
            }
        }
    }
    return query


def create_es_search(method, scope, search_text, country=None, state=None):
    """
        Providing the parameters, create a value query sub-string for elasticsearch

        IF there is a need to perform a fuzzy search, there might be a need to set
            ["query_string"]["fuzzy_prefix_length"] to a value like 1
    """
    method_char = "~" if method == "fuzzy" else "*"
    if state:
        start_string = ("(({scope}_country_code:USA) OR ({scope}_country_code:UNITED STATES))"
                        " AND ({scope}_state_code:{state}) AND ")
        query_string = start_string.format(scope=scope, state=state)
    elif country == "FOREIGN":
        query_string = ("NOT (({scope}_country_code:USA) OR "
                        "({scope}_country_code:UNITED STATES)) AND ").format(scope=scope)
    elif country and country != "USA":
        query_string = "({scope}_country_code:{country}) AND ".format(scope=scope, country=country)
    else:
        query_string = "(({scope}_country_code:USA) OR ({scope}_country_code:UNITED STATES)) AND ".format(scope=scope)

    query_string += '({scope}_city_name:{text}{char})'.format(scope=scope, text=search_text, char=method_char)

    query = {"query_string": {"query": query_string, "allow_leading_wildcard": False}}
    return query


def query_elasticsearch(query, search_text):
    hits = es_client_query(index="{}*".format(settings.TRANSACTIONS_INDEX_ROOT), body=query)

    results = []
    if hits and hits["hits"]["total"] > 0:
        results = parse_elasticsearch_response(hits, search_text)
        results = sorted(results, key=lambda x: (x["city_name"], x["state_code"]))
    return results


def parse_elasticsearch_response(hits, search_text):
    results = []
    for city in hits["aggregations"]["cities"]["buckets"]:
        if city['key'].startswith(search_text):
            if len(city["states"]["buckets"]) > 0:
                for state_code in city["states"]["buckets"]:
                    results.append(OrderedDict([("city_name", city["key"]), ("state_code", state_code["key"])]))
            else:
                # for cities without states, useful for foreign country results
                results.append(OrderedDict([("city_name", city["key"]), ("state_code", None)]))
    return results