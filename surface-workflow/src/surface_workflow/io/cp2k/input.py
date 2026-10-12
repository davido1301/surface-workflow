from pymatgen.io.cp2k.inputs import Cp2kInput

from surface_workflow.config import load_config 

from pathlib import Path 

def read_input(input_file): 
    cp2k_inp = Cp2kInput().from_file(input_file) 
    return cp2k_inp 

def change_startstructure(cp2k_inp, structure):
    topology = cp2k_inp.by_path("FORCE_EVAL/SUBSYS/TOPOLOGY") 
    topology["COORD_FILE_NAME"] = structure 

def generate_new_cp2kinp(config,structure, filename): 
    config = load_config(config)
    input_path = Path(config["cp2k"]["directory"]) / "cp2k.inp"
    cp2k_inp = read_input(input_path) 
    change_startstructure(cp2k_inp, structure)
    cp2k_inp.write_file(filename) 
