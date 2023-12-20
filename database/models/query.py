"""Defines the query model for the database."""
from abc import abstractmethod
from enum import Enum
from typing import Any, Iterable, List, Optional, Set, Tuple, Union

# from database.interface.client import DatabaseInterface
from datamodel.data.model import Data, FieldPath


class Operator(str, Enum):
    IS_EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    CONTAINS = "contains"
    ANY = "all"
    ALL = "any"


class Conjunction(str, Enum):
    AND = "and"
    OR = "or"


class Modifier(str, Enum):
    NOT = "not"


Operand = Union[str, int, float, bool, List[Union[str, int, float, bool, "Operand"]]]


class Operation(Data):
    field: FieldPath
    operator: Operator
    operand: Optional[Any]
    modifier: Optional[Modifier]

    def __call__(self, item: Data) -> bool:
        value = item.get(self.field)
        result: bool
        # Handle the different operators.
        if self.operator == Operator.IS_EQUAL:
            result = value == self.operand
        elif self.operator == Operator.NOT_EQUAL:
            result = value != self.operand
        elif self.operator == Operator.GREATER_THAN:
            result = value > self.operand
        elif self.operator == Operator.LESS_THAN:
            result = value < self.operand
        elif self.operator == Operator.CONTAINS:
            result = self.operand in value
        elif self.operator == Operator.ANY:
            if not isinstance(value, Iterable):
                raise TypeError(f"Value {value} is not iterable.")
            result = any(value)
        elif self.operator == Operator.ALL:
            if not isinstance(value, Iterable):
                raise TypeError(f"Value {value} is not iterable.")
            result = all(value)
        else:
            raise NotImplementedError(f"Operator {self.operator} is not implemented.")

        # Handle the modifier.
        if self.modifier == Modifier.NOT:
            result = not result
        return result

    def __repr__(self) -> str:
        if self.operand:
            return f"{self.operator}({repr(self.field)}, {repr(self.operand)})"
        return f"{self.operator}({repr(self.field)})"

    def to_data(self) -> str:
        if self.operand:
            return f"({self.field} {self.operator} {self.operand})"
        return f"({self.field} {self.operator})"


# Yields, for example: field == 1 and field != 2 or field > 3
class Statement:
    def __init__(self, statement: Union[Tuple[Operation, Conjunction, "Statement"], Operation]):
        self.statement = statement

    def __call__(self, item: Any) -> bool:
        if isinstance(self.statement, tuple):
            operation, conjunction, statement = self.statement
            if conjunction == Conjunction.AND:
                return operation(item) and statement(item)
            if conjunction == Conjunction.OR:
                return operation(item) or statement(item)
            raise NotImplementedError(f"Conjunction {conjunction} is not implemented.")
        if isinstance(self.statement, Operation):
            return self.statement(item)
        raise NotImplementedError(f"Statement {self.statement} is not implemented.")

    def to_data(self) -> str:
        if isinstance(self.statement, tuple):
            operation, conjunction, statement = self.statement
            return f"({operation.to_data()} {conjunction} {statement.to_data()})"
        if isinstance(self.statement, Operation):
            return self.statement.to_data()
        raise NotImplementedError(f"Statement {self.statement} is not implemented.")


# Condition = Tuple[FieldPath, Statement]
class Condition(Tuple[FieldPath, Statement]):
    def __repr__(self) -> str:
        return f"Condition({repr(self[0])}, {repr(self[1])})"

    def __call__(self, value: Data) -> bool:
        field, statement = self
        return statement(value.get(field))


# Modify the join to be a list of joins, each with a field, client/table, and query.
# Execute join queries at run, not at build.
# Define better order of operations. Maybe use a stack? ...or a phased approach where each operation
# has its precedence. Like, limit after select, but before order_by, etc.
# This means repeated calls to the same method will create a new phase.
# Handle limit, offset, order_by, group_by, distinct, union and intersect
class Query(Data):
    """
    A Query class for building, representing and manipulating database queries.

    This class provides methods to create and modify queries for databases, supporting common query operations such as
    select, where, join, limit, offset, order_by, group_by, distinct, union, and intersect. Queries can be executed
    through the use of DatabaseInterface objects, and the class also provides utility methods to obtain a list of
    fields used in the query and check its validity. Any sum, avg, min, max, or count operations can be performed on
    the results of the query.

    Attributes:
    outputs (List[FieldPath]): A list of output field paths for the query.
    conditions (List[Condition]): A list of query conditions.
    foreign (Optional[List[Tuple[Optional[FieldPath], Union[JSON, List[JSON]]]]]): A list of join operations, each
    with a field, a client/table, and a query. Can be None if no join is specified.

    Methods:
    select(*outputs: FieldPath) -> "Query": Adds output fields to the query.
    where(*conditions: Condition) -> "Query": Adds conditions to the query.
    join(foreign: Optional[FieldPath], data: DatabaseInterface, query: "Query") -> "Query": Adds a join operation
        to the query.
    limit(limit: int) -> "Query": Adds a limit to the number of rows returned in the query.
    offset(offset: int) -> "Query": Skips a specified number of rows before returning results.
    order_by(*fields: FieldPath) -> "Query": Sorts the query results by one or more attributes.
    group_by(*fields: FieldPath) -> "Query": Groups the query results by one or more attributes.
    distinct(field: FieldPath) -> "Query": Filters out duplicate rows based on a specific attribute.
    union(*queries: "Query") -> "Query": Returns a Query object representing the union of the current query
        and other queries.
    intersect(*queries: "Query") -> "Query": Returns a Query object representing the intersection of the current query
        and other queries.
    fields(self) -> List[FieldPath]: Returns a list of all fields used in the query excluding joins.
    is_valid(self) -> bool: Checks whether the query is valid.
    to_data(self) -> str: Returns a data representation of the query.
    """

    outputs: List[FieldPath] = []
    conditions: List[Condition] = []
    foreign: Optional[List[Tuple[Optional[FieldPath], Union[Data, List[Data]]]]] = None

    def __repr__(self) -> str:
        return f"Query(outputs={repr(self.outputs)}, conditions={repr(self.conditions)})"

    def __call__(self, value: Optional[Data]) -> Optional[Data]:
        if value is None:
            return None

        # Fill out the foreign data.
        if self.foreign and isinstance(self.foreign, list):
            for new in self.foreign:
                field, data = new
                # If field specified, just place the data there.
                if field:
                    # TODO: Handle list of data.
                    value[field] = data
                else:
                    # Otherwise, update the value with the data.
                    if isinstance(data, list):
                        for item in data:
                            value.update(item)
                    else:
                        value.update(data)

        for condition in self.conditions:
            if not condition(value):
                return None
        return value

    def select(self, *outputs: FieldPath) -> "Query":
        self.outputs = self.outputs + list(outputs)
        return self

    def where(self, *conditions: Condition) -> "Query":
        self.conditions = self.conditions + list(conditions)
        return self

    # Avoiding circular import, temporary by data: Any instead of data: DatabaseInterface
    def join(self, foreign: Optional[FieldPath], data: Any, query: "Query") -> "Query":
        """
        Performs a join operation between two data sources.

        Args:
            foreign (FieldPath): The field path to put the foreign data.
            data (DatabaseInterface): The client for the foreign data source.
            query (Query): The query object for foreign data selection.

        Returns:
            Query: The joined query object.
        """
        if not self.foreign:
            self.foreign = []

        join = data.query(query)
        if foreign:
            self.foreign.append((foreign, join))
        else:
            self.foreign.append((None, join))
        return self

    @abstractmethod
    def limit(self, limit: int) -> "Query":
        """
        Returns a new Query object that limits the number of rows returned.

        The limit method can be used to limit the number of rows returned by the query to a specific number.
        The resulting Query object will contain all the columns from the original query.

        Args:
            limit (int): The maximum number of rows to return.

        Returns:
            Query: A new Query object that limits the number of rows returned.
        """

    @abstractmethod
    def offset(self, offset: int) -> "Query":
        """
        Returns a Query object that skips a certain number of rows before returning results.

        The offset method can be used to skip a certain number of rows before returning results. The resulting Query
        object will contain all the columns from the original query.

        Args:
            offset (int): The number of rows to skip.

        Returns:
            Query: Query object that skips the specified number of rows before returning results.
        """

    @abstractmethod
    def order_by(self, *fields: FieldPath) -> "Query":
        """
        Returns a Query object that sorts the results by one or more attributes.

        The order_by method can be used to sort the rows in the query result by one or more attributes. The resulting
        Query object will contain all the columns from the original query.

        Args:
            *fields (FieldPath): One or more attributes to sort by.

        Returns:
            Query: Query object that sorts the results by the specified attributes.
        """

    @abstractmethod
    def group_by(self, *fields: FieldPath) -> "Query":
        """
        Returns a Query object that groups the results by one or more attributes.

        The group_by method can be used to group the rows in the query result by one or more attributes. The resulting
        Query object will contain only the grouped attributes and any aggregated values specified in the query.

        Args:
            *fields (FieldPath): One or more attributes to group by.

        Returns:
            Query: Query object that groups the results by the specified attributes.
        """

    @abstractmethod
    def distinct(self, field: FieldPath) -> "Query":
        """
        Returns a Query object that represents the current query with duplicates removed for a specific attribute.

        The distinct method can be used to filter out duplicate rows based on a specific attribute. The resulting Query
        object will contain all the columns from the original query.

        Args:
            field (FieldPath): The field to filter out duplicates.

        Returns:
            Query: Query object that represents the current query with duplicates removed for the specified attribute.
        """

    @abstractmethod
    def union(self, *queries: "Query") -> "Query":
        """
        Returns a Query object that represents the union of the current query and one or more other queries.

        The union of two queries returns all the rows from both queries, with duplicates removed. The resulting Query
        object will contain all the columns from the original query. The union method can be used to combine the
        results of multiple queries into a single result set.

        Args:
            *queries (Query): One or more Query objects to combine with the current query.

        Returns:
            Query: Query object that represents the union of the current query and the specified queries.
        """

    @abstractmethod
    def intersect(self, *queries: "Query") -> "Query":
        """
        Returns a Query object that represents the intersection of the current query and one or more other queries.

        The intersection of two queries returns only the rows that are present in both queries. The resulting Query
        object will contain all the columns from the original query. The intersect method can be used to filter a Query
        object by multiple conditions.

        Args:
            *queries (Query): One or more Query objects to intersect with the current query.

        Returns:
            Query: Query object that represents the intersection of the current query and the specified queries.
        """

    @property
    def fields(self) -> List[FieldPath]:
        """
        Returns a list of all fields used in the query excluding joins.

        Returns:
            List[FieldPath]: A list of all fields used in the query.
        """
        fields: Set[FieldPath] = set(self.outputs)
        for condition in self.conditions:
            field, _ = condition
            fields.add(field)
        return list(fields)

    @property
    def is_valid(self) -> bool:
        """
        Checks whether the query is valid. A query is considered valid if it has at least one output field
        and one condition.

        Returns:
            bool: True if the query is valid, False otherwise.
        """
        return bool(self.outputs) and bool(self.conditions)

    @abstractmethod
    def to_data(self) -> str:
        """
        Returns a JSON representation of the query.

        Returns:
            str: A JSON representation of the query.
        """
        # It should result in a minimal representation of the query.
        # It should be possible to reconstruct the query from the JSON.
        # Any contained structures should be minimised so that humans can write it easier.
        # For exmaple, an Operation into: field: "{FieldPath} {modifier} {operator} {operand}"
