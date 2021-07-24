from aiida.orm import QueryBuilder, Node, Code
from aiida.tools import delete_nodes
from aiida.plugins.factories import CalculationFactory

# first clean all WIEN2k x sgroup calculations and related output
Wien2kXSgroup = CalculationFactory("wien2k-x-sgroup")
query = QueryBuilder()
query.append(Wien2kXSgroup, project=['id'])
query.all()
for node in query.iterall():
    print(node)
    delete_nodes(node, dry_run=False)

# get list of all remaining nodes in DB
query = QueryBuilder()
query.append(Node)
query.all()
nodes_all = []
for node in query.iterall():
    nodes_all.append(node[0].id)
print('nodes_all =', nodes_all)

# set up a list of nodes to keep
nodes_to_keep = []
for node in Group.get(label='commonwf-oxides/set1/structures').nodes: # Giovanni structures
    nodes_to_keep.append(node.id)

# append pk of codes to the list of nodes to keep
query = QueryBuilder()
query.append(Code) # all codes
query.all()
for node in query.iterall():
    nodes_to_keep.append(node[0].id)
print('nodes_to_keep =', nodes_to_keep)

# remove all other nodes
nodes_to_remove = list(set(nodes_all) - set(nodes_to_keep)) # diff between two lists
print('nodes_to_remove =', nodes_to_remove)
for node in nodes_to_remove:
    print(node)
    delete_nodes([node], dry_run=False)