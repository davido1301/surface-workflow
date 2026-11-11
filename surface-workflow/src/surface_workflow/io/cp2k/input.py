from pymatgen.io.cp2k.inputs import Cp2kInput

from surface_workflow.config import load_config 

from pathlib import Path 
from pymatgen.io.cp2k.inputs import Section, Keyword


def read_input(input_file): 
    cp2k_inp = Cp2kInput().from_file(input_file) 
    return cp2k_inp 

def change_startstructure(cp2k_inp, structure):
    topology = cp2k_inp.by_path("FORCE_EVAL/SUBSYS/TOPOLOGY") 
    topology["COORD_FILE_NAME"] = structure 

    structure = Path(structure)
    sec_global = cp2k_inp.by_path("GLOBAL") 
    sec_global["PROJECT"] = structure.stem 

    

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

def change_geo_opt(cp2k_inp, max_iter=200): 
    cp2k_inp.by_path("GLOBAL")["RUN_TYPE"] = "GEO_OPT" 

    if not cp2k_inp.check("MOTION"): 
        cp2k_inp.insert(Section("MOTION")) 


    if not cp2k_inp.check("MOTION/GEO_OPT"): 
        motion = cp2k_inp.by_path("MOTION") 
        motion.insert(Section("GEO_OPT")) 
    
    geo_opt = cp2k_inp.by_path("MOTION/GEO_OPT")  
    geo_opt["TYPE"]= "MINIMIZATION" 
    geo_opt["OPTIMIZER"] = "BFGS" 
    geo_opt["MAX_ITER"] = max_iter 


    
def generate_new_cp2kinp(config, structure, filename, isolated=False, run_type="ENERGY"): 
    config = load_config(config)
    input_path = Path(config["cp2k"]["directory"]) / "cp2k.inp"
    cp2k_inp = read_input(input_path) 
    change_startstructure(cp2k_inp, structure)

    if isolated: 
        change_spin_config(cp2k_inp, structure) 

    if run_type == "GEO_OPT": 
        change_geo_opt(cp2k_inp)

    cp2k_inp.write_file(filename) 
