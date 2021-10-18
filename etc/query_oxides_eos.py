from aiida.orm import QueryBuilder
from aiida.plugins.factories import WorkflowFactory
import numpy
import math
import json

def BMEOSfitpoly(volumes, energies):
    """Fit energies and volumes to the Birch-Murnaghan equation of state.
    Determine:
    - total energy at min (E0)
    - equilibrium volume (V0) corresponding to E0
    - bulk modulus (B0)
    - pressure derivative of the bulk modulus (B01)
    - residuals from the fit (ssr)
    - errors for E0, V0, B0, B01 (errX vector)"""

    fitdata = numpy.polyfit(volumes**(-2./3.), energies, 3, full=True)
    ssr = fitdata[1][0] # residuals sum[(y_i - y_calc_i)**2]
    deriv0 = numpy.poly1d(fitdata[0])
    deriv1 = numpy.polyder(deriv0, 1)
    deriv2 = numpy.polyder(deriv1, 1)
    deriv3 = numpy.polyder(deriv2, 1)

    V0 = 0
    x = 0
    for x in numpy.roots(deriv1):
        # Last check: it's real, no imaginary part
        if x > 0 and deriv2(x) > 0 and abs(x.imag) < 1.e-8:
            V0 = x**(-3./2.)
            break

    if V0 == 0:
        E0 = None
        V0 = None
        B0 = None
        B01 = None
        errX = [None, None, None, None]
        return [E0, V0, B0, B01], ssr, errX
        

    # Get also the E0 and return it
    E0 = deriv0(x)
    # Find B0 and B01
    derivV2 = 4./9. * x**5. * deriv2(x)
    derivV3 = (-20./9. * x**(13./2.) * deriv2(x) -
        8./27. * x**(15./2.) * deriv3(x))
    B0 = derivV2 / x**(3./2.)
    B01 = -1 - x**(-3./2.) * derivV3 / derivV2

    # Hessian with variables: 1-E0, 2-V0, 3-B0, 4-B01
    # d2f/dx1dx2
    H11 = 0; H12 = 0; H13 = 0; H14 = 0
    H21 = 0; H22 = 0; H23 = 0; H24 = 0
    H31 = 0; H32 = 0; H33 = 0; H34 = 0
    H41 = 0; H42 = 0; H43 = 0; H44 = 0
    for energy, volume in zip(energies, volumes):
        r = volume**(-2./3.)
        # due to symmetry we calculate only upper triangle of the matrix H_ij
        H11 += 2
        H12 += -2*((-9*B0*(2 + (-4 + B01)*(-1 + r*V0**(2./3.)))* \
                (-1 + r*V0**(2./3.))**2)/16. - \
                (3*B0*r*(2 + (-4 + B01)*(-1 + r*V0**(2./3.)))* \
                (-1 + r*V0**(2./3.))*V0**(2./3.))/4. \
                - (3*B0*(-4 + B01)*r*(-1 + r*V0**(2./3.))**2* \
                V0**(2./3.))/8.)
        H13 += (9*(2 + (-4 + B01)*(-1 + r*V0**(2./3.)))* \
                (-1 + r*V0**(2./3.))**2*V0)/8.
        H14 += (9*B0*(-1 + r*V0**(2./3.))**3*V0)/8.
        H22 += (B0*((2*r*(16*E0 - 16*energy + \
                9*B0*(-1 + r*V0**(2./3.))**2* \
                (6 - B01 + (-4 + B01)*r*V0**(2./3.))*V0)* \
                (-80 + 15*B01 + \
                14*(14 - 3*B01)*r*V0**(2./3.) + \
                27*(-4 + B01)*r**2*V0**(4./3.)))/ \
                V0**(1./3.) + \
                9*B0*(3*(-6 + B01) + \
                5*(16 - 3*B01)*r*V0**(2./3.) + \
                7*(-14 + 3*B01)*r**2*V0**(4./3.) - \
                9*(-4 + B01)*r**3*V0**2)**2))/128.
        H23 += (3*(-1 + r*V0**(2./3.))* \
                (8*E0 - 8*energy + \
                9*B0*(-1 + r*V0**(2./3.))**2* \
                (6 - B01 + (-4 + B01)*r*V0**(2./3.))*V0)* \
                (3*(-6 + B01) + 2*(31 - 6*B01)*r*V0**(2./3.) + \
                9*(-4 + B01)*r**2*V0**(4./3.)))/64.
        H24 += (9*B0*(-1 + r*V0**(2./3.))**2* \
                (energy*(8 - 24*r*V0**(2./3.)) + \
                8*E0*(-1 + 3*r*V0**(2./3.)) + \
                3*B0*(-1 + r*V0**(2./3.))**2*V0* \
                (3*(-6 + B01) + 4*(16 - 3*B01)*r*V0**(2./3.) + \
                9*(-4 + B01)*r**2*V0**(4./3.))))/64.
        H33 += (81*(2 + (-4 + B01)*(-1 + r*V0**(2./3.)))**2* \
                (-1 + r*V0**(2./3.))**4*V0**2)/128.
        H34 += (9*(-1 + r*V0**(2./3.))**3*V0* \
                (8*E0 - 8*energy + \
                9*B0*(-1 + r*V0**(2./3.))**2* \
                (6 - B01 + (-4 + B01)*r*V0**(2./3.))*V0))/64.
        H44 += (81*B0**2*(-1 + r*V0**(2./3.))**6*V0**2)/128.
    H = numpy.array([\
            [H11, H12, H13, H14],\
            [H12, H22, H23, H24],\
            [H13, H23, H33, H34],\
            [H14, H24, H34, H44]
    ]) # Hessiam matrix
    Hinv = numpy.linalg.inv(H/2) # (H/2)**(-1)
    ndeg = len(energies) - 4 # number of degries of friedom for 4 fit variables
    s2 = ssr/ndeg # standard deviation**2
    errX = numpy.sqrt(s2*numpy.diag(Hinv)) # error for fir parameters E0, V0, B0, B01

    return [E0, V0, B0, B01], ssr, errX

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
data['eos_data'] = {}
data['DFT_engine'] = 'WIEN2k v22.1'
data['DFT_settings'] = '-prec 2'
data['EOS_volume_grid_percents'] = [-6, -4, -2, 0, 2, 4, 6]
prec = '2' # set precision of interest
for q in query.iterall():
    if( q[0].inputs.inpdict2.attributes['-prec'] != prec ):
        continue # skip if precision does not matc
    state = q[0].process_state.value
    structure_sup_aiida = q[0].inputs.aiida_structure
    chemformula = structure_sup_aiida.get_formula()
    element = structure_sup_aiida.extras['element']
    conf = structure_sup_aiida.extras['configuration']
    print('Formula:', element+'-'+conf, ',', chemformula,\
            ', state:', state, ', ID: ', q[0].pk)
    if(state=='finished'):
        if( q[0].exit_status >= 400):
            continue # skip if the workchain had errors
        result_dict = q[0].outputs.workchain_result.get_dict()
        print('Raw results:', result_dict)
        etot_Ry_list = result_dict['EtotRyd']
        vol_Bohr3_list = result_dict['VolBohr3']
        etot_Ry = numpy.array(etot_Ry_list)
        vol_Bohr3 = numpy.array(vol_Bohr3_list)
        etot_eV = etot_Ry*13.6056980659
        vol_Ang3 = vol_Bohr3*(0.529177249**3.0)
        #params, covariance = fit_birch_murnaghan_params(volumes=vol_Ang3,\
        #       energies=etot_eV)
        params, residuals,errX = BMEOSfitpoly(volumes=vol_Ang3,\
                energies=etot_eV)
        nat, vol_sup = nat_vol(structure_sup_aiida) # AiiDA input structure number of atoms and volume
        v0 = params[1]
        if( v0 != None ):
            if(v0 > vol_Ang3.min() and v0 < vol_Ang3.max()):
                eos_fit_warning = ''
            else:
                eos_fit_warning = 'warn: V0 is out of range'
        else:
            eos_fit_warning = 'Error: EOS fit not found'
        # print('EOS fit output (E0_eV, V0_Ang3, B0_eV/Ang3, B0pr):', params,\
        #         'V_sup vs v0 (%) = ', 100*math.log(vol_sup/v0), eos_fit_warning, '\n')
        fmtstr = 'EOS fit output (E0_eV, V0_Ang3, B0_eV/Ang3, B0pr):'+\
                '[{:.15e}, {:e}, {:e}, {:+e}, {:e}] V_sup vs v0 (%) = {:+e} {}\n'
        if( v0 != None ):
            print(fmtstr.format(params[0], params[1],\
                    params[2], params[3], residuals, 100*math.log(vol_sup/v0), eos_fit_warning))
        else:
            print(eos_fit_warning+'\n')
        # add data for later export to json file
        warnings = ''
        if (eos_fit_warning != ''):
            warnings = warnings + eos_fit_warning
        data['BM_fit_data'][element+'-'+conf] = {
            'E0': params[0],
            'err_E0': errX[0],
            'min_volume': params[1],
            'err_min_volume': errX[1],
            'bulk_modulus_ev_ang3': params[2],
            'err_bulk_modulus_ev_ang3': errX[2],
            'bulk_deriv': params[3],
            'err_bulk_deriv': errX[3],
            'residuals': residuals,
            'EOS_workchain_exit_code': q[0].exit_status,
            'warnings': warnings
        }
        # prepare energy vs volume data for json file
        vol_vs_ene = []
        for i in range(len(vol_Ang3)):
            vol_vs_enei = [vol_Ang3[i],etot_eV[i]]
            vol_vs_ene.append(vol_vs_enei)
        data['eos_data'][element+'-'+conf] = vol_vs_ene
    else:
        print('\n')
# write json file with results
with open('results.json', 'w') as outfile:
    json.dump(data, outfile, indent=2)
