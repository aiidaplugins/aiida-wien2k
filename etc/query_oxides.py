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