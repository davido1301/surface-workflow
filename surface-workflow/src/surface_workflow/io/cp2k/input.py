from pymatgen.io.cp2k.inputs import Cp2kInput

from surface_workflow.config import load_config 

from pathlib import Path 



def read_input(input_file): 
    cp2k_inp = Cp2kInput().from_file(input_file) 
    return cp2k_inp 

def change_startstructure(cp2k_inp, structure):
    topology = cp2k_inp.by_path("FORCE_EVAL/SUBSYS/TOPOLOGY") 
    topology["COORD_FILE_NAME"] = structure 

def change_spin_config(cp2k_inp, structure): 
    ATOMIC_MULTIPLICITIES = {
            "H": 2,
            "C": 3, 
            "N": 4, 
            "O": 3, 
            "Si": 3, 
            "Al": 2, 
            }
    element = Path(structure).stem 
    multiplicity = ATOMIC_MULTIPLICITIES[element] 
    dft = cp2k_inp.by_path("FORCE_EVAL/DFT")
    dft["UKS"] = True 
    dft["CHARGE"] = 0 
    dft["MULTIPLICITY"] = multiplicity 

    

def generate_new_cp2kinp(config, structure, filename, isolated=False): 
    config = load_config(config)
    input_path = Path(config["cp2k"]["directory"]) / "cp2k.inp"
    cp2k_inp = read_input(input_path) 
    change_startstructure(cp2k_inp, structure)
    if isolated: 
        change_spin_config(cp2k_inp, structure) 
    cp2k_inp.write_file(filename) 
