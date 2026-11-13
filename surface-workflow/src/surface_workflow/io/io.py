from ase.io import read, write 
from pymatgen.io.ase import AseAtomsAdaptor



def write_atoms(atoms, output, format="extxyz", pbc = [True, True, False]): 
    """ Pass in pymatgen object write xyz"""  
    atoms = AseAtomsAdaptor.get_atoms(atoms)
    atoms.pbc = pbc 
    output = output 

    write(output, atoms, format=format) 
    print(f"Generated {output}") 


