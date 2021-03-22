import pandas as pd
import numpy as np
##
df = pd.read_excel('/Users/wzx/Downloads/SLN_PAUSE.xlsx')
metad = pd.read_excel('/Users/wzx/Downloads/Instructors_Metadata.xlsx')

ptypes = ['event-related', 'disfluency', 'between-utterance', 'between-clause', 'between-phrase', 'within-phrase']


###### frequency analysis
####fre_data = []
####
####
####for pt in ptypes:
####    sub = df[df['Pause_type'] == pt]
####    for j in range(160):
####        fname = metad.Filename.loc[j]
####        tokens = metad.Tokens.loc[j]
####        disp = metad.Discipline.loc[j]
####        p_num_raw = len(sub[sub['Filename']==fname])
####        p_num_norm = p_num_raw / tokens * 1000
####        fre_data.append([pt, fname, disp, p_num_raw, p_num_norm])
####
####
######## save all the fre data by pause type and filename (6 * 160)
######pd.DataFrame(fre_data, columns=['Pause Type', 'Filename', 'Discipline', 'Raw Frequency', 'Frequency per 1000 words']).to_excel('pause_fre_data.xlsx')
####        
####
###### summary data
####
####fre_data = pd.DataFrame(fre_data, columns=['Pause Type', 'Filename', 'Discipline', 'Raw Frequency', 'Frequency per 1000 words'])
######## or load the previously saved fre data if these two steps are separate
######fre_data = pd.read_excel('/Users/wzx/Downloads/pause_fre_data.xlsx')
####
####sum_data = []
####dis = ['ah', 'ls', 'ps', 'ss']
####
####
####for pt in ptypes:
####    sub = fre_data[fre_data['Pause Type'] == pt]
####    for d in dis:
####        sub_dis = sub[sub['Discipline']==d]
####        raw_fre = sub_dis['Raw Frequency']
####        mean = np.around(np.mean(raw_fre), 2)
####        min_max = f'{np.min(raw_fre)}/{np.max(raw_fre)}'
####        sd = np.around(np.std(raw_fre), 2)
####
####        fre_nm = sub_dis['Frequency per 1000 words']
####        mean_nm = np.around(np.mean(fre_nm), 2)
####        min_max_nm = f'{np.around(np.min(fre_nm), 2)}/{np.around(np.max(fre_nm), 2)}'
####        sd_nm = np.around(np.std(fre_nm), 2)
####
####        sum_data.append([pt, d, mean, min_max, sd, mean_nm, min_max_nm, sd_nm])
####
####
####pd.DataFrame(sum_data, columns=['Pause Type', 'Discipline', 'Mean', 'Min/Max', 'SD', 'Mean_NM', 'Min/Max_NM', 'SD_NM']).to_excel('pause_fre_sum_data.xlsx')
####



###### duration analysis
dis = ['ah', 'ls', 'ps', 'ss']
dur_data = []


for pt in ptypes:
    sub = df[df['Pause_type'] == pt]
    for d in dis:
        sub_dis = sub[sub['discipline']==d]
        dur = sub_dis['duration']
        mean = np.around(np.mean(dur), 2)
        min_max = f'{np.around(np.min(dur), 2)}/{np.around(np.max(dur), 2)}'
        sd = np.around(np.std(dur), 2)

        dur_data.append([pt, d, mean, min_max, sd])

pd.DataFrame(dur_data, columns=['Pause Type' , 'Discipline' , 'Mean', 'Min/Max', 'SD']).to_excel('pause_dur_data.xlsx')
        




