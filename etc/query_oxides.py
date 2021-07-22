from aiida.orm import QueryBuilder, Node, SinglefileData, Dict

query = QueryBuilder()
query.append(Node)
query.count()