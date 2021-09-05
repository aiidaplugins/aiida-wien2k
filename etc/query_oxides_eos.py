from aiida.orm import QueryBuilder
from aiida.plugins.factories import WorkflowFactory
from scipy.optimize import curve_fit
import numpy
import math
import json

def birch_murnaghan(V, E0, V0, B0, B01):
    """Compute energy by Birch Murnaghan formula."""
    # pylint: disable=invalid-name
    r = (V0 / V)**(2. / 3.)
    return E0 + 9. / 16. * B0 * V0 * (r - 1.)**2 * (2. + (B01 - 4.) * (r - 1.))


def fit_birch_murnaghan_params(volumes, energies):
    """Fit Birch Murnaghan parameters."""
    # pylint: disable=invalid-name

    params, covariance = curve_fit(  # pylint: disable=unbalanced-tuple-unpacking
        birch_murnaghan,
        xdata=volumes,
        ydata=energies,
        p0=(
            energies.min(),  # E0
            volumes.mean(),  # V0
            0.1,  # B0
            3.,  # B01
        ),
        sigma=None
    )
    return params, covariance

def nat_vol(structure_aiida):
    "AiiDA structure number of atoms and volume"
    structure_ase = structure_aiida.get_ase() # AiiDA -> ASE struct
    vol = structure_ase.cell.volume # cell volume
    nat = structure_ase.cell.itemsize # number of atoms
    return nat, vol

Wien2kEOS = WorkflowFactory("wien2k.eos_wf")
query = QueryBuilder()
query.append(Wien2kEOS, tag='calculation')
query.all()
data = {} # collect data for json file
data['BM_fit_data'] = {}
data['DFT_engine'] = 'WIEN2k v22.1'
data['DFT_settings'] = 'prec 3'
data['EOS_volume_grid_percents'] = [-8, -6, -4, -2, 0, 2, 4, 6, 8]
for q in query.iterall():
    state = q[0].process_state.value
    structure_sup_aiida = q[0].inputs.aiida_structure
    chemformula = structure_sup_aiida.get_formula()
    element = structure_sup_aiida.extras['element']
    conf = structure_sup_aiida.extras['configuration']
    
    print('Formula:', element+'-'+conf, ', state:', state, ', ID: ', q[0].pk)
    if(state=='finished'):
        result_dict = q[0].outputs.workchain_result.get_dict()
        print('Raw results:', result_dict)
        etot_Ry_list = result_dict['EtotRyd']
        vol_Bohr3_list = result_dict['VolBohr3']
        etot_Ry = numpy.array(etot_Ry_list)
        vol_Bohr3 = numpy.array(vol_Bohr3_list)
        etot_eV = etot_Ry*13.6056980659
        vol_Ang3 = vol_Bohr3*(0.529177249**3.0)
        params, covariance = fit_birch_murnaghan_params(volumes=vol_Ang3, energies=etot_eV)
        nat, vol_sup = nat_vol(structure_sup_aiida) # AiiDA input structure number of atoms and volume
        v0 = params[1]
        if(v0 > vol_Ang3.min() and v0 < vol_Ang3.max()):
            eos_fit_warning = ''
        else:
            eos_fit_warning = 'warn: V0 is out of range'
        print('EOS fit output (E0_eV, V0_Ang3, B0_eV/Ang3, B0pr):', params,\
                'V_sup vs v0 (%) = ', 100*math.log(vol_sup/v0), eos_fit_warning, '\n')
        # add data for later export to json file
        warnings = ''
        if (eos_fit_warning != ''):
            warnings = warnings + eos_fit_warning
        data['BM_fit_data'][element+'-'+conf] = {
            'E0': params[0],
            'min_volume': params[1],
            'bulk_modulus_ev_ang3': params[2],
            'bulk_deriv': params[3],
            'residuals': None,
            'EOS_workchain_exit_code': q[0].exit_status,
            'warnings': warnings
        }
    else:
        print('\n')
# write json file with results
with open('results.json', 'w') as outfile:
    json.dump(data, outfile, indent=2)
