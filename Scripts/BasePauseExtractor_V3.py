import os
import re
import nltk
from nltk import RegexpTokenizer, FreqDist
import pandas as pd
from bs4 import BeautifulSoup

lct_num = index = index_2 = index_3 = 0
time_format = {'hour': 0, 'min': 0, 'sec': 0}
speakers_df = pd.DataFrame(columns=['Filename', 'Duration', '# of Tokens', '# of M Speaker', '# of F Speaker',
                                   '# of Unknown Sex', '# of Main Speaker', '# of Participant', '# of Observer',
                                   '# of Speakers', '# of Utterances', '# of Turn Switching', '# of Silent Pauses',
                                   'Total Time of Sln Pauses', '# of Filled Pauses', '# of Trans Pauses'])
instructors_df = pd.DataFrame(columns=['Filename', '# of Tokens', '# of Male', '# of Female', '# of Unknown Sex',
                                              '# of Utterances', '# of Responding', '# of Silent Pauses',
                                              'Total Time of Sln Pauses', '# of Filled Pauses', '# of Trans Pauses'])
pauses_list = [['Filename', 'Pause_Type', 'Pause_Example', 'Left_Context', 'Right_Context']]
pauses_df = pd.DataFrame()


class BaseInfo:

    def __init__(self, path, subject, speech_type):
        self._path = path
        self._subject = subject
        self._speech_type = speech_type

    def filename(self):
        global lct_num
        filename = '%s%s%03d' % \
                   (self._subject, self._speech_type, lct_num)
        return filename

    def file_path(self):
        self._path = self._path + '/' if not self._path.endswith('/') else self._path
        # file_path = f'{self._path}{self._subject}/{self.filename()}.xml'
        file_path = f'{self._path}{self.filename()}.xml'
        return file_path

    def file_checker(self):
        return os.path.exists(self.file_path())

    def tokenizer(self, text):
        tokenizer = RegexpTokenizer(r'(<[^>]+>|\w\S*|#[^\s]?)')
        text = tokenizer.tokenize(text)
        return text

    def file_content(self):
        file_content = BeautifulSoup(open(self.file_path()), 'lxml')
        return file_content

    def file_title(self):
        file_title = self.file_content().find('title').string
        return file_title

    def recording_info(self):
        recording_info = self.file_content().find('recording')
        return recording_info

    def file_duration(self):
        duration = self.recording_info().attrs['dur']
        return duration

    def duration_addition(self):
        global time_format
        dur = self.file_duration().split(':')
        hour, min, sec = float(dur[0]), float(dur[1]), float(dur[-1])
        time_format['sec'] += sec
        if time_format['sec'] >= 60:
            time_format['min'] += 1
            time_format['sec'] -= 60
            time_format['min'] += min
            if time_format['min'] >= 60:
                time_format['hour'] += 1
                time_format['min'] -= 60
                time_format['hour'] += hour
        return time_format

    def duration_to_sec(self):
        dur = self.file_duration().split(':')
        hour, min, sec = float(dur[0]), float(dur[1]), float(dur[-1])
        return 3600 * hour + 60 * min + sec

    def num_of_reported_tokens(self):
        tokens_num = self.recording_info().attrs['n']
        return float(tokens_num)

    def num_of_counted_tokens(self):
        text = self.whole_discourse().text
        tokens = text.split()
        return len(tokens)

    def language_used(self):
        lang = self.file_content().find_all('language')
        lang = [lg.string for lg in lang]
        return f'{lang} were used in "{self.filename()}"'

    def whole_discourse(self):
        discourse = self.file_content().find('text')
        return discourse

    def text_with_sln_pauses_tagged(self):
        soup = BeautifulSoup(open(self.file_path()), 'lxml')
        discourses = soup.find('text').find_all('u')
        for discourse in discourses:
            pauses = discourse.find_all('pause')
            who = discourse.attrs['who']
            for pause in pauses:
                pause['who'] = who
        return soup


class SpeakersInfo(BaseInfo):

    def __init__(self, path, subject, speech_type):
        super().__init__(path, subject, speech_type)

    def speakers_info(self):
        speakers_info = self.file_content().find_all('person')
        return speakers_info

    def first_speaker_info(self):
        speaker_info = self.file_content().find('person')
        return speaker_info

    def num_of_speakers(self):
        speakers_num = len(self.speakers_info())
        # BASE annotation consistently add an extra 2 to 3 people to the total number of speakers,
        # as shown in the <presonGrp> tags in the end of <particDesc> tag.
        # This program only count people who were part of the transcribed discourse.
        return speakers_num

    def speakers_role(self):
        roles = []
        for speaker_info in self.speakers_info():
            roles.append(speaker_info.attrs['role'])
        return roles

    def speakers_role_data(self):
        role_data = {'main speaker': 0, 'participant': 0, 'observer': 0}
        for r in self.speakers_role():
            if r == 'main speaker':
                role_data['main speaker'] += 1
            elif r == 'participant':
                role_data['participant'] += 1
            else:
                role_data['observer'] += 1
        return role_data

    def speakers_sex(self):
        sexes = []
        for speaker_info in self.speakers_info():
            sexes.append(speaker_info.attrs['sex'])
        return sexes

    def speakers_sex_data(self):
        sex_data = {'male': 0, 'female': 0, 'unknown': 0}
        for s in self.speakers_sex():
            if s == 'm':
                sex_data['male'] += 1
            elif s == 'f':
                sex_data['female'] += 1
            else:
                sex_data['unknown'] += 1
        return sex_data

    def num_of_utterances(self):
        num = self.file_content().find_all('u')
        return len(num)

    def num_of_turns(self):
        turns_num = self.num_of_utterances() - 2
        return turns_num

    def num_of_sln_pauses(self):
        sln_pauses = self.whole_discourse().find_all('pause')
        return len(sln_pauses)

    def total_time_sln_pauses(self):
        sln_pauses = self.whole_discourse().find_all('pause')
        total_time = 0
        for sln_pause in sln_pauses:
            dur = sln_pause.attrs['dur']
            dur = dur[:-1] if dur[-1] == '.' else dur
            dur = 60 * float(dur[0]) + float(dur[2:]) if ':' in dur else float(dur)
            total_time += dur
        return total_time

    def num_of_fld_pauses(self):
        fld_num = re.findall(r'#', str(self.whole_discourse()))
        return len(fld_num)

    def num_of_tran_pauses(self):
        tran_pauses = self.file_content().find_all('u', {'trans': 'pause'})
        return len(tran_pauses)

    def speakers_meta_data(self):
        global index, speakers_df
        index += 1
        speakers_df.loc[index] = [self.filename(), self.file_duration(), self.num_of_reported_tokens()] + \
                                list(self.speakers_sex_data().values()) + list(self.speakers_role_data().values()) + \
                                [self.num_of_speakers()] + [self.num_of_utterances()] + [self.num_of_turns()] + \
                                [self.num_of_sln_pauses()] + [self.total_time_sln_pauses()] + [self.num_of_fld_pauses()] + \
                                [self.num_of_tran_pauses()]
        return speakers_df


class InstructorInfo(SpeakersInfo):

    def __init__(self, path, subject, speech_type):
        super().__init__(path, subject, speech_type)

    def speech_event_checker(self):
        if self._speech_type == 'sem':
            print('Not a lecture. Wrong speech event type! Please refer to SpeakersInfo class instead!')
            return False
        else:
            return True

    def instructor_info(self):
        if self.speech_event_checker():
            instructor_info = self.file_content().find('person', {'role': 'main speaker'})
            return instructor_info

    def instructor_id(self):
        if self.speech_event_checker():
            instructor_id = self.instructor_info().attrs['id']
            return instructor_id

    def instructor_sex(self):
        if self.speech_event_checker():
            instructor_sex = self.instructor_info().attrs['sex']
            return instructor_sex

    def instructors_sex_data(self):
        sex_data = {'male': 0, 'female': 0, 'unknown': 0}
        if self.instructor_sex() == 'm':
            sex_data['male'] += 1
        elif self.instructor_sex() == 'f':
            sex_data['female'] += 1
        else:
            sex_data['unknown'] += 1
        return sex_data

    def instructor_discourse(self):
        if self.speech_event_checker():
            instructor_discourse = self.file_content().find_all('u', {'who': self.instructor_id()})
            return instructor_discourse

    def num_of_ins_tokens(self):
        if self.speech_event_checker():
            tokens = 0
            for dis in self.instructor_discourse():
                tokens += len(dis.text.split())
            return tokens

    def num_of_speaking_times(self):
        if self.speech_event_checker():
            return len(self.instructor_discourse())

    def num_of_responding(self):
        if self.speech_event_checker():
            # Instructors are always the first one to speak in the transcribed discourse,
            # so by - 1, we get the number of times of their responding to others
            return self.num_of_speaking_times() - 1

    def instructor_sln_pauses(self):
        if self.speech_event_checker():
            sln_pauses = re.findall(r'<pause dur=[^>]*>', str(self.instructor_discourse()))
            return sln_pauses

    def num_of_sln_pauses(self):
        if self.speech_event_checker():
            return len(self.instructor_sln_pauses())

    def ins_sln_pause_dur(self):
        if self.speech_event_checker():
            durs = re.findall(r'(?<=pause dur=\")[\d:.]+', str(self.instructor_discourse()))
            return durs

    def ins_sln_pause_fd(self):
        if self.speech_event_checker():
            durs = self.ins_sln_pause_dur()
            durs_fd = nltk.FreqDist(durs).most_common()
            return durs_fd

    def total_time_sln_pauses(self):
        if self.speech_event_checker():
            total_time = 0
            durs = self.ins_sln_pause_dur()
            for dur in durs:
                dur = dur[:-1] if dur[-1] == '.' else dur
                dur = 60 * float(dur[0]) + float(dur[2:]) if ':' in dur else float(dur)
                total_time += dur
            return total_time

    def num_of_fld_pauses(self):
        if self.speech_event_checker():
            fld_pauses = re.findall(r'#', str(self.instructor_discourse()))
            return len(fld_pauses)

    def num_of_tran_pauses(self):
        if self.speech_event_checker():
            tran_pauses = re.findall(r'trans="pause"', str(self.instructor_discourse()))
            return len(tran_pauses)

    def instructor_meta_data(self):
        global index_2, instructors_df
        if self.speech_event_checker():
            index_2 += 1
            instructors_df.loc[index_2] = \
                [self.filename(), self.num_of_ins_tokens()] + list(self.instructors_sex_data().values()) \
                                    + [self.num_of_speaking_times()] + [self.num_of_responding()] + \
                                    [self.num_of_sln_pauses(), self.total_time_sln_pauses()] + \
                                               [self.num_of_fld_pauses()] + [self.num_of_tran_pauses()]
            return instructors_df


class InstructorPause(InstructorInfo):

    def __init__(self, path, subject, speech_type, span=10):
        super().__init__(path, subject, speech_type)
        self._span = span

    def concordance_creator(self, tar_text, tar_tokens):
        global index_3, pauses_list
        span = self._span
        filename = self.filename()
        tar_text = self.tokenizer(tar_text)
        idx_all = [idx for (idx, elem) in enumerate(tar_text) if elem in tar_tokens]
        for idx in idx_all:
            index_3 += 1
            # concordance_text = tar_text[
            #                    idx - span if idx - span > 0 else 0: idx + span + 1]
            # concordance_text = ' '.join([token for token in concordance_text])
            left_context = tar_text[idx - span if idx - span > 0 else 0: idx]
            left_context = ' '.join([token for token in left_context])
            right_context = tar_text[idx + 1:idx + span + 1]
            right_context = ' '.join([token for token in right_context])
            concordance_text = f'{left_context}                             {tar_text[idx]}                             {right_context}'
            pauses_list.append([filename, concordance_text, left_context, right_context])

    def pause_extractor(self, tar_text, regex):
        tar_text = str(tar_text)
        tar_tokens = re.findall(rf'{regex}', tar_text)
        self.concordance_creator(tar_text, tar_tokens)

    def get_all_sln_pauses(self):
        instructor_id = self.instructor_id()
        text = self.text_with_sln_pauses_tagged()
        self.pause_extractor(text, f'<pause.+?{instructor_id}">')
        # text = self.instructor_discourse()
        # self.pause_extractor(text, f'<pause[^>]+>')

    def get_all_tran_pauses(self):
        instructors_id = self.instructor_id()
        text = str(self.whole_discourse())
        tokenized_text = self.tokenizer(text)
        tar_tokens = []
        for i in tokenized_text:
            if 'trans="pause"' in i and instructors_id in i:
                tar_tokens.append(i)
        self.concordance_creator(text, tar_tokens)

    def get_all_fld_pauses(self):
        text = self.instructor_discourse()
        self.pause_extractor(text, '#')

    def get_all_gaps(self):
        text = self.whole_discourse()
        self.pause_extractor(text, '<gap[^>]+>')


def main():
    global lct_num
    # The path of where BASE is in your computer
    path = '/Users/wzx/Downloads/BASE/BASE_Modified/Tagged_XML'
    subject_list = ['ah', 'ls', 'ss', 'ps']
    # To set speech_type = 'sem' and run the program,
    # please delete lssem006.xml and sssem006.xml files first
    speech_type = 'lct'
    for subject in subject_list:
        lct_num = 0
        # Instructor related classes (Pause or Info) are s
        ex = InstructorPause(path, subject, speech_type, 10)
        for _ in range(1):
            lct_num += 1
            ex.instructor_meta_data()
            print(ex.filename())
        speakers_df.to_excel('Instructors_Metadata.xlsx')

    # pauses_df.append(pauses_list).to_excel('SLN_PAUSE.xlsx')
            # if ex.file_checker():
            #     print(ex.num_of_ins_tokens())

                # For getting a pause concordance
                # Can either run one of these commands or print, or something like that since they return a list back
                # ex.get_all_sln_pauses() / ex.get_all_tran_pauses() / ex.get_all_fld_pauses()
    # To add all items in pauses_list into an excel spreadsheet
    # pauses_df.append(pauses_list).to_excel('Instructor_Pauses.xlsx')


if __name__ == '__main__':
    main()
    # right_con_df = FreqDist(right_con).most_common()
    # pd.DataFrame(right_con_df).to_excel("left_context_df.xlsx")
