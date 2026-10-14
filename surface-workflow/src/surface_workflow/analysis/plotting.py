import matplotlib.pyplot as plt 



def plot_energy_steps_scf(energy_steps, out_dir): 

    x = [_ for _ in range(0, len(energy_steps))]  
    y = [] 
    for step_e in energy_steps:
         y.append(step_e) 
    plt.plot(x, y) 
    plt.savefig(out_dir) 
    plt.close() 

def plot_convergence(energies, out_dir): 
    x = [_ for _ in range(0, len(energies))] 
    y = energies 

    plt.plot(x, y) 
    plt.savefig(out_dir)
    plt.close() 


