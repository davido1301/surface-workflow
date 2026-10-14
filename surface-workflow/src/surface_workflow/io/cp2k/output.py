from pymatgen.io.cp2k.outputs import Cp2kOutput 


def collect_energies(cp2koutput_file): 
    output = Cp2kOutput(cp2koutput_file) 

    # COLLECT ENERGIES 
    output.parse_scf_opt() 
    output.parse_energies() 
    # COLLECT N ATOMS 
    output.parse_total_numbers() 

    return output 


