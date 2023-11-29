# Diagnosis of Package Installation Incompatibility via Knowledge Base
This repository stores the materials for our paper entitled "Diagnosis of Package Installation Incompatibility via Knowledge Base" which will be published on the *Science of Computer Programming* journal.


## Materials
The following sections describe the main materials included in this repository.    
### [HELP](https://github.com/NJUJisq/Diagnosis_Install/tree/master/HELP)
This folder stores the source code of HELP. *README.md* contains the documentation of HELP. Our constructed knowledge base is on the "HELP/data" folder.

### [Empirical_Study](https://github.com/NJUJisq/Diagnosis_Install/tree/master/Empirical_Study)
This folder stores the data used in the study of Python version compatibility in Python libraries. 
- *Pkg_info.csv* lists the information of 8502 libraries used in RQ1 and RQ2.
- The *RQ1_Declaration_in_the_wild* folder lists the results in RQ1. 
    - *Prop_LC.json* lists the results of the metric Prop_LC collected in 8502 libraries, where 'yes' means the number of library versions that declaring LC. 
    - *LC_format.json* lists the formats of LC in 8502 libraries.
- The *RQ2_InstallStatus* folder lists the results of running virtual installations including successful installations (*install_success.csv*) and failed installations (*install_fail.csv*) in RQ2.


### [Evaluation of HELP](https://github.com/NJUJisq/Diagnosis_Install/tree/master/Evaluation%20of%20HELP) 
This folder stores the used dataset and results in the evaluation. 
- RQ3_effectiveness.
    - *sampleSet_old.csv* and *sampleSet_new.csv* list the information of sampled dataset.  
    - The *HELP* and *smartPip* folder list the results when running two tools on the sampled dataset.
- RQ4_efficiency. This folder contains the lists of installation tasks (*installSet.csv*) and the time for Table 5-Table 7 (*time_Table_5.csv,time_Table_6.csv,and time_Table_7.csv*).
### [Discussion](https://github.com/NJUJisq/Diagnosis_Install/tree/master/Discussion) 
This folder stores the results of two experiments in the discussion.
- *Precision_Virtual_Install.csv* lists the results of manual inspection for virtual installations.
- *GenerateLC.csv* lists the generated LCs using HELP

We also provide the artifact at Zenodo.org. You can get the zip file via the link [https://doi.org/10.5281/zenodo.10216230](https://doi.org/10.5281/zenodo.10216230)

