import datetime
import json
import pytest


class Helpers:
    @staticmethod
    def post_for_count_endpoint(client, url, def_codes=None):
        if def_codes:
            request_body = json.dumps({"filter": {"def_codes": def_codes}})
        else:
            request_body = json.dumps({"filter": {}})
        resp = client.post(url, content_type="application/json", data=request_body)
        return resp

    @staticmethod
    def patch_date_today(monkeypatch, year, month, day):
        class PatchedDate(datetime.date):
            @classmethod
            def today(cls):
                return datetime.date(year, month, day)

        monkeypatch.setattr(datetime, "date", PatchedDate)


@pytest.fixture
def helpers():
    return Helpers
