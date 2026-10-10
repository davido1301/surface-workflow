from pathlib import Path 

from surface_workflow.config import load_config 
from surface_workflow.structures.slab  import gen_slabs 
from surface_workflow.structures.cell import generate_cell

def main(): 
    config_path = Path("configs/slab.yaml")
    config = load_config(config_path) 

    # Generate candidate slabs
    gen_slabs(config_path)
    
    # Generate cell for CP2K 
    generate_cell(config_path) 

if __name__ == "__main__": 
     main()
