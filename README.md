# Surface Workflow

A modular Python framework for automated surface generation, CP2K calculations and convergence analysis. 

## Overview 
Surface Workflow is a Python-based framework designed to automate and standarize computational worfklows for studying material surfaces for my PhD project. 

The framework aims to connect structure generation, calculation preparation, execution, output parsing and convergence analysis into a reproducible and extensible pipeline. 

!!! 
The initial focus is on generating surface slabs and achieving energetic convergence for now. Later on adsorption energies will be used as the main convergence criteria. 
The long term goal is to extend the framework toward automated adsoprtion studies and surface property calculations. 

## Workflow: 
Bulk structure -> Surface/Slab Generation -> Layer Variation -> CP2K Input Generation -> Calculation (Local for testing / HPC using SLURM) -> Output Parsing + Validation -> Convergence Analysis -> Results Reports 


## Project Status
Early development! 
