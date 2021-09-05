from aiida.orm import QueryBuilder, Dict, StructureData
from aiida.plugins.factories import CalculationFactory



Wien2kRunLapw = CalculationFactory("wien2k-run_lapw")
query = QueryBuilder()
query.append(Wien2kRunLapw, tag='calculation')
query.append(Dict, with_incoming='calculation', project=['id'])
query.append(StructureData, with_descendants='calculation', project=['id'])
query.all()
for q in query.iterall():
    iddict, idstruct = q
    ndict = load_node(iddict)
    nstruct = load_node(idstruct)
    print(nstruct.get_formula(), ndict.attributes)

query = QueryBuilder()
query.append(Wien2kRunLapw)
query.all()
count_total = 0
count_ok = 0
for node in query.iterall():
    print(f"run_lapw PK: {node[0].pk}, status: {node[0].process_state.value}")
    count_total += 1
    if( node[0].is_finished_ok ):
        count_ok += 1
print(f"total {count_total} processes, {count_ok} finished OK")