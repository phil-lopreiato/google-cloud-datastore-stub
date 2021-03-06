from google.cloud.datastore_v1.gapic import (
    datastore_client_config as datastore_client_config,
    enums as enums,
)
from google.cloud.datastore_v1.gapic.transports import (
    datastore_grpc_transport as datastore_grpc_transport,
)
from google.cloud.datastore_v1.proto import (
    datastore_pb2 as datastore_pb2,
    datastore_pb2_grpc as datastore_pb2_grpc,
    entity_pb2 as entity_pb2,
    query_pb2 as query_pb2,
)
from google.oauth2 import service_account as service_account
from typing import Any, Optional

class DatastoreClient:
    SERVICE_ADDRESS: str = ...
    @classmethod
    def from_service_account_file(cls, filename: Any, *args: Any, **kwargs: Any): ...
    from_service_account_json: Any = ...
    transport: Any = ...
    def __init__(
        self,
        transport: Optional[Any] = ...,
        channel: Optional[Any] = ...,
        credentials: Optional[Any] = ...,
        client_config: Optional[Any] = ...,
        client_info: Optional[Any] = ...,
        client_options: Optional[Any] = ...,
    ) -> None: ...
    def lookup(
        self,
        project_id: Any,
        keys: Any,
        read_options: Optional[Any] = ...,
        retry: Any = ...,
        timeout: Any = ...,
        metadata: Optional[Any] = ...,
    ): ...
    def run_query(
        self,
        project_id: Any,
        partition_id: Any,
        read_options: Optional[Any] = ...,
        query: Optional[Any] = ...,
        gql_query: Optional[Any] = ...,
        retry: Any = ...,
        timeout: Any = ...,
        metadata: Optional[Any] = ...,
    ): ...
    def begin_transaction(
        self,
        project_id: Any,
        transaction_options: Optional[Any] = ...,
        retry: Any = ...,
        timeout: Any = ...,
        metadata: Optional[Any] = ...,
    ): ...
    def commit(
        self,
        project_id: Any,
        mode: Any,
        mutations: Any,
        transaction: Optional[Any] = ...,
        retry: Any = ...,
        timeout: Any = ...,
        metadata: Optional[Any] = ...,
    ): ...
    def rollback(
        self,
        project_id: Any,
        transaction: Any,
        retry: Any = ...,
        timeout: Any = ...,
        metadata: Optional[Any] = ...,
    ): ...
    def allocate_ids(
        self,
        project_id: Any,
        keys: Any,
        retry: Any = ...,
        timeout: Any = ...,
        metadata: Optional[Any] = ...,
    ): ...
    def reserve_ids(
        self,
        project_id: Any,
        keys: Any,
        database_id: Optional[Any] = ...,
        retry: Any = ...,
        timeout: Any = ...,
        metadata: Optional[Any] = ...,
    ): ...
