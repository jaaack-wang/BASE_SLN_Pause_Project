# BASE_SLN_Pause_Project

This repository stores Python scripts created for BASE slient pause project. 

In the Script folder, `BasePauseExtractor_V3.py` file is the general search engine to scrape matedata and all kind of pauses from BASE, whereas `pause_type_automation.py` is the classifer for all types of slient pauses, except between-utterance pauses, which can be spearately identified by the previous script. Finally, `base_desc_data.py` is the causal script that can count different types of pauses file by file and calculate the descriptive statistics needed out of the counting. 

The excel files in this page resulted from running the above three scripts. `Instructors_Metadata.xlsx` was gotten from `BasePauseExtractor_V3.py` and was later used for the number of tokens instructor produced when running `base_desc_data.py`. `SLN_PAUSE.xlsx` contains the annotated silent pause information, extracted by using both `pause_type_automation.py` and `BasePauseExtractor_V3.py`. `pause_fre_data.xlsx` and `pause_fre_sum_data.xlsx` were created after `base_desc_data.py` was run, which contains the descriptive statistics needed to populate the tables of the draft of the manuscript.  
