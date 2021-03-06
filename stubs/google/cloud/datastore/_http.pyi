from google.cloud import exceptions as exceptions
from google.rpc import status_pb2 as status_pb2
from typing import Any, Optional

DATASTORE_API_HOST: str
API_BASE_URL: Any
API_VERSION: str
API_URL_TEMPLATE: str

def _request(
    http: Any, project: Any, method: Any, data: Any, base_url: Any, client_info: Any
): ...
def _rpc(
    http: Any,
    project: Any,
    method: Any,
    base_url: Any,
    client_info: Any,
    request_pb: Any,
    response_pb_cls: Any,
): ...
def build_api_url(project: Any, method: Any, base_url: Any): ...

class HTTPDatastoreAPI:
    client: Any = ...
    def __init__(self, client: Any) -> None: ...
    def lookup(self, project_id: Any, keys: Any, read_options: Optional[Any] = ...): ...
    def run_query(
        self,
        project_id: Any,
        partition_id: Any,
        read_options: Optional[Any] = ...,
        query: Optional[Any] = ...,
        gql_query: Optional[Any] = ...,
    ): ...
    def begin_transaction(
        self, project_id: Any, transaction_options: Optional[Any] = ...
    ): ...
    def commit(
        self,
        project_id: Any,
        mode: Any,
        mutations: Any,
        transaction: Optional[Any] = ...,
    ): ...
    def rollback(self, project_id: Any, transaction: Any): ...
    def allocate_ids(self, project_id: Any, keys: Any): ...
