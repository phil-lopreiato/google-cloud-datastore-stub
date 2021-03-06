from google.cloud.ndb import _options
from typing import Any, Optional

class PropertyOrder:
    name: Any = ...
    reverse: Any = ...
    def __init__(self, name: Any, reverse: bool = ...) -> None: ...
    def __neg__(self): ...

class RepeatedStructuredPropertyPredicate:
    name: Any = ...
    match_keys: Any = ...
    match_values: Any = ...
    def __init__(self, name: Any, match_keys: Any, entity_pb: Any) -> None: ...
    def __call__(self, entity_pb: Any): ...

class ParameterizedThing:
    def __eq__(self, other: Any) -> Any: ...
    def __ne__(self, other: Any) -> Any: ...

class Parameter(ParameterizedThing):
    def __init__(self, key: Any) -> None: ...
    def __eq__(self, other: Any) -> Any: ...
    @property
    def key(self): ...
    def resolve(self, bindings: Any, used: Any): ...

class ParameterizedFunction(ParameterizedThing):
    func: Any = ...
    values: Any = ...
    def __init__(self, func: Any, values: Any) -> None: ...
    def __eq__(self, other: Any) -> Any: ...
    def is_parameterized(self): ...
    def resolve(self, bindings: Any, used: Any): ...

class Node:
    def __new__(cls): ...
    def __eq__(self, other: Any) -> Any: ...
    def __ne__(self, other: Any) -> Any: ...
    def __le__(self, unused_other: Any) -> Any: ...
    def __lt__(self, unused_other: Any) -> Any: ...
    def __ge__(self, unused_other: Any) -> Any: ...
    def __gt__(self, unused_other: Any) -> Any: ...
    def resolve(self, bindings: Any, used: Any): ...

class FalseNode(Node):
    def __eq__(self, other: Any) -> Any: ...

class ParameterNode(Node):
    def __new__(cls, prop: Any, op: Any, param: Any): ...
    def __getnewargs__(self): ...
    def __eq__(self, other: Any) -> Any: ...
    def resolve(self, bindings: Any, used: Any): ...

class FilterNode(Node):
    def __new__(cls, name: Any, opsymbol: Any, value: Any): ...
    def __getnewargs__(self): ...
    def __eq__(self, other: Any) -> Any: ...

class PostFilterNode(Node):
    def __new__(cls, predicate: Any): ...
    def __getnewargs__(self): ...
    def __eq__(self, other: Any) -> Any: ...

class _BooleanClauses:
    name: Any = ...
    combine_or: Any = ...
    or_parts: Any = ...
    def __init__(self, name: Any, combine_or: Any) -> None: ...
    def add_node(self, node: Any) -> None: ...

class ConjunctionNode(Node):
    def __new__(cls, *nodes: Any): ...
    def __getnewargs__(self): ...
    def __iter__(self) -> Any: ...
    def __eq__(self, other: Any) -> Any: ...
    def resolve(self, bindings: Any, used: Any): ...

class DisjunctionNode(Node):
    def __new__(cls, *nodes: Any): ...
    def __getnewargs__(self): ...
    def __iter__(self) -> Any: ...
    def __eq__(self, other: Any) -> Any: ...
    def resolve(self, bindings: Any, used: Any): ...

AND = ConjunctionNode
OR = DisjunctionNode

class QueryOptions(_options.ReadOptions):
    project: Any = ...
    namespace: Any = ...
    def __init__(
        self, config: Optional[Any] = ..., context: Optional[Any] = ..., **kwargs: Any
    ) -> None: ...

class Query:
    default_options: Any = ...
    kind: Any = ...
    ancestor: Any = ...
    filters: Any = ...
    order_by: Any = ...
    project: Any = ...
    namespace: Any = ...
    projection: Any = ...
    distinct_on: Any = ...
    def __init__(
        self,
        kind: Optional[Any] = ...,
        filters: Optional[Any] = ...,
        ancestor: Optional[Any] = ...,
        order_by: Optional[Any] = ...,
        orders: Optional[Any] = ...,
        project: Optional[Any] = ...,
        app: Optional[Any] = ...,
        namespace: Optional[Any] = ...,
        projection: Optional[Any] = ...,
        distinct_on: Optional[Any] = ...,
        group_by: Optional[Any] = ...,
        default_options: Optional[Any] = ...,
    ) -> None: ...
    @property
    def is_distinct(self): ...
    def filter(self, *filters: Any): ...
    def order(self, *props: Any): ...
    def analyze(self): ...
    def bind(self, *positional: Any, **keyword: Any): ...
    def fetch(self, limit: Optional[Any] = ..., **kwargs: Any): ...
    def fetch_async(self, limit: Optional[Any] = ..., **kwargs: Any): ...
    def run_to_queue(
        self,
        queue: Any,
        conn: Any,
        options: Optional[Any] = ...,
        dsquery: Optional[Any] = ...,
    ) -> None: ...
    def iter(self, **kwargs: Any): ...
    __iter__: Any = ...
    def map(self, callback: Any, **kwargs: Any): ...
    def map_async(self, callback: Any, **kwargs: Any) -> None: ...
    def get(self, **kwargs: Any): ...
    def get_async(self, **kwargs: Any) -> None: ...
    def count(self, limit: Optional[Any] = ..., **kwargs: Any): ...
    def count_async(self, limit: Optional[Any] = ..., **kwargs: Any) -> None: ...
    def fetch_page(self, page_size: Any, **kwargs: Any): ...
    def fetch_page_async(self, page_size: Any, **kwargs: Any) -> None: ...

def gql(query_string: Any, *args: Any, **kwds: Any): ...
