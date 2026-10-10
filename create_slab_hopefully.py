from pymatgen.core import Structure
from pymatgen.core.surface import SlabGenerator
from pymatgen.analysis.interfaces import CoherentInterfaceBuilder
from pymatgen.io.ase import AseAtomsAdaptor
from ase.io import write 
from math import ceil 

MIN_THICKNESS = 10 # A PARAM PARSE LATER ON 
STRUC = Structure.from_file("SiO2_mp-8352_conventional_standard.cif")
STRUC = Structure.from_file("Cu_mp-30_conventional_standard.cif")
MILLER_INDEX = [0, 0, 1]
for i in range(1, 5):
    slabgen = SlabGenerator(initial_structure=STRUC,
                         miller_index=MILLER_INDEX, 
                         min_slab_size=i, 
                         in_unit_planes=True,
                         min_vacuum_size=30
                         )
    slabs_list = slabgen.get_slabs() # symmetrize = True can remove atoms 
    candidate_slabs =  [slab for slab in slabs_list ] 
    print(f"Number of all slabs: {len(slabs_list)}") 
     # MIN_THICKNESS IN VECTOR a, b  
    a, b, c = candidate_slabs[0].lattice.abc 
    print(a, b, c) 
    n_b = ceil( MIN_THICKNESS / b )
    n_a = ceil(MIN_THICKNESS/ a) 
    xyz = candidate_slabs[0].make_supercell(scaling_matrix=[n_a,n_b,1]) 
    atoms = AseAtomsAdaptor.get_atoms(xyz)
    atoms.pbc = [True, True, False] 
    write(f"xyz{i}.extxyz", atoms)

exit()

slab_slab = CoherentInterfaceBuilder(
        substrate_structure = sio2_struc,
        film_structure = sio2_struc, 
        film_miller = [0, 0, 1],
        substrate_miller = [0, 0, 1], 
        )

slab = SlabGenerator(initial_structure=slab_slab,
                     miller_index=[0, 0, 1], 
                     min_slab_size=50, 
                     min_vacuum_size=80
                     )



