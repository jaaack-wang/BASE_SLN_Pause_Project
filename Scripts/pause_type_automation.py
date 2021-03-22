import os
import re
from nltk import RegexpTokenizer
import pandas as pd
from bs4 import BeautifulSoup
from collections import Counter

index_3 = 0
pauses_list = [['Filename', 'discipline', 'Pause_type', 'Pause_Example', 'Left_first', 'Right_first']]
pauses_df = pd.DataFrame()
left_con = []
right_con = []
pause_types = []


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
        path = self._path + '/' if not self._path.endswith('/') else self._path
        # file_path = f'{self._path}{self._subject}/{self.filename()}.xml'
        file_path = f'{path}{self.filename()}.xml'
        return file_path

    def file_checker(self):
        return os.path.exists(self.file_path())

    def tokenizer(self, text):
        tokenizer = RegexpTokenizer(r'(<[^>]+>|\S+)')
        text = tokenizer.tokenize(text)
        return text

    def file_content(self):
        file_content = BeautifulSoup(open(self.file_path()), 'lxml')
        return file_content

    def whole_discourse(self):
        discourse = self.file_content().find('text')
        return discourse

    def text_with_sln_pauses_tagged(self):
        soup = BeautifulSoup(open(self.file_path()), 'lxml')
        discourses = soup.find_all('u')
        for discourse in discourses:
            pauses = discourse.find_all('pause')
            who = discourse.attrs['who']
            for pause in pauses:
                pause['who'] = who
        return soup


class InstructorInfo(BaseInfo):

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


class InstructorPause(InstructorInfo):

    def __init__(self, path, subject, speech_type, span=10):
        super().__init__(path, subject, speech_type)
        self._span = span

    def concordance_creator(self, tar_text, tar_tokens):
        global index_3, pauses_list, left_con, right_con
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
            left_context_str = ' '.join([token for token in left_context])
            right_context = tar_text[idx + 2:idx + span + 2]
            right_context_str = ' '.join([token for token in right_context])
            concordance_text = f'{left_context_str}                             {tar_text[idx]}' \
                               f'                             {right_context_str}'

            # The following 4 assignments are meant to make the extraction independent of the assigned value of span
            # So that no matter how many tokens we want to extract around a silent pause, the program can always
            # get the right number of cases for both event-related pauses and disfluency-related pauses

            left_8 = tar_text[idx - 8 if idx - 8 > 0 else 0: idx]
            right_8 = tar_text[idx + 2:idx + 8 + 2]

            left_first = left_8[-1]
            right_first = right_8[0]
            left_sec = left_8[-2]
            right_sec = right_8[1]
            right_third = right_8[2]

            left_2_str = ' '.join([w.split('_')[0] for w in left_8[-2:]])
            right_2_str = ' '.join([w.split('_')[0] for w in right_8[:2]])
            right_5_str = ' '.join([w for w in right_8[:5]])

            left_8_no_pos = [w.split('_')[0] for w in left_8]
            right_8_no_pos = [w.split('_')[0] for w in right_8]

            def repetition():
                lth = 0
                while lth < 8:
                    lth += 1
                    if left_8_no_pos[-lth:] == right_8_no_pos[:lth]:
                        return True
                return False

            def partial_repetition():
                for i in range(2,5):
                    left_part = left_8[:i]
                    right_part = right_8[:i + 2]
                    if left_part in right_part:
                        return True
                return False

            events = [('</vocal>', '</kinesic>', '</event>', '</shift>', '</reading>', '</distinct>'),
                      ('<vocal', '<kinesic', '<event', '<shift', '<reading', '</reading>', '<distinct')]
            fillers = ('you know', 'i mean', 'I mean')
            nouns = ('_NN', '_NNS', '_NNP', '_NNPS', '_PRP', 'i_FW')
            pronouns = ('_PRP', '_PRP$', 'i_FW')
            adjs = ('_JJ', '_JJR', '_JJS', '_RBS', '_RBR')
            verbs = ('_VB', '_VBD', '_VBG', '_VBP', '_VBN', '_VBZ')
            adverbs = ('_RB', '_RBR', '_RBS', 'RP')
            clause_pos = ('_CC', '_WDT', '_EX', 'WP', 'WP$', '_WRB')
            clause_marker = ('if_', 'because_', "'cause", 'although_', 'nevertheless_', 'hence_',
                             'so_', 'therefore_', 'after_', 'before_', 'since_', 'though', 'unless',
                             'however_', 'while', 'when', 'whereas', 'whenever', 'until', 'till', 'whether',
                             'surprisingly', 'yeah_', 'yes', 'right_', 'well', 'then_', 'finally', 'today_',
                             'okay_',  'now_', 'no_',  'here_', 'basically_', 'indeed_', 'essentially',
                             'clearly_', 'actually_', 'sometimes_')
            noun_modifiers = ('_DT', '_CD', 'PDT', '_IN', '_PRP$', '_WP$', "_POS") + adjs
            question_markers = ('_MD', 'is_VB', 'do_VB', 'do_VBP', 'are_VBP', 'did_VBD', 'was_VBD', 'were_VBD', 'have_VBP', 'has_VBZ')

            #   event-related
            if left_first in events[0] or right_first.startswith(events[1]):
                pause_type = 'event-related'
            #   when a gap occurs for a certain duration, something happens
            elif '<gap' in left_sec and 'sec' in left_sec:
                pause_type = 'event-related'
            elif '<gap' in right_first and 'sec' in right_first:
                pause_type = 'event-related'

            #   disfluency
            elif left_first.startswith(('a_', 'an_')) and right_first.startswith(('a_', 'an_')):
                pause_type = 'disfluency'
            elif left_2_str.startswith(fillers) or right_2_str.startswith(fillers):
                pause_type = 'disfluency'
            elif left_first.startswith(('</trunc>', '#', 'mm_', 'oh_')) or right_first.startswith(('<trunc>', '#', 'mm_', 'oh_')) \
                    or repetition() or partial_repetition():
                pause_type = 'disfluency'

            #   a patch. The rest between-phrase codes are shown below
            elif left_first.endswith('_CC') and left_sec.split('_')[-1] in right_first + right_sec \
                    and left_sec != verbs:
                pause_type = 'between-phrase'
            elif right_first.endswith('_CC') and left_first.split('_')[-1] in right_sec + right_third \
                    and left_first != verbs:
                pause_type = 'between-phrase'
            #   between-clause
            elif left_first.endswith(('_CC', '_WRB')) or right_first.endswith(clause_pos):
                pause_type = 'between-clause'
            elif left_first.endswith(('_WDT', 'WP', '_EX')) and not right_first.endswith(verbs + adverbs):
                pause_type = 'between-clause'
            elif left_first.startswith(clause_marker) or right_first.startswith(clause_marker):
                pause_type = 'between-clause'
            elif not right_sec.endswith(nouns) and right_first.endswith(question_markers) and right_sec.endswith(pronouns):
                pause_type = 'between-clause'
            elif right_first.endswith(question_markers) and right_sec.endswith(pronouns):
                pause_type = 'between-clause'
            #  <pause> in which + clause ....
            elif right_first.endswith('_IN') and right_sec.endswith('WDT'):
                pause_type = 'between-clause'
            #   before a clause
            elif right_first.endswith(nouns) and right_sec.endswith(verbs):
                pause_type = 'between-clause'
            elif right_first.endswith(adverbs) and right_sec.endswith(nouns) and 'V_' in right_5_str:
                pause_type = 'between-clause'
            elif left_first.endswith(nouns + adverbs + ('that_IN',)) \
                    and right_first.endswith(nouns) and right_sec.endswith(verbs):
                pause_type = 'between-clause'
            elif left_first.startswith(nouns) and right_first.endswith(nouns + noun_modifiers) \
                    and not right_sec.endswith(verbs) and right_third.endswith(verbs):
                pause_type = 'between-clause'
            elif left_first.endswith(('_NN', '_NNS')) \
                    and right_first.endswith(pronouns + ('_NNP', '_NNPS')) and not right_sec.endswith('_CC'):
                pause_type = 'between-clause'
            #   that clause
            elif left_first.endswith(adjs + nouns + verbs) and right_first.startswith('that_IN'):
                pause_type = 'between-clause'
            elif "in" in right_first and "that" in right_sec:
                pause_type = 'between-clause'
            #   as adj cannot modifier verbs and noun modifers whatsoever, it is possible that it a clause that follows
            elif right_first.endswith('</u>'):
                pause_type = 'between-clause'
            #   calling someone's name is a word sentence by itself
            elif '<gap' in left_sec and 'name' in left_sec:
                pause_type = 'between-clause'
            elif '<gap' in right_first and 'name' in right_first:
                pause_type = 'between-clause'
            elif left_first.startswith('as_') and '_V' in right_5_str:
                pause_type = 'between-clause'
            elif right_first.startswith('as_') and '_V' in right_5_str:
                pause_type = 'between-clause'

            #     between-phrase
            elif right_first.startswith('as_'):
                pause_type = 'between-phrase'
            #   before a NP
            elif left_first.endswith(verbs + ('_IN',) + adverbs) and right_first.endswith(noun_modifiers):
                pause_type = 'between-phrase'
            elif left_first.endswith(('_NNP', '_NNPS')) and right_first.endswith(('_NNP', '_NNPS')):
                pause_type = 'between-phrase'
            #   right after a question sentence's head, e.g., can <pause> you ....?
            elif left_first.endswith(question_markers) and right_first.endswith(pronouns):
                pause_type = 'between-phrase'
            elif left_first.endswith(nouns) and right_first.endswith(verbs + adverbs):
                pause_type = 'between-phrase'
            elif left_first.endswith(('_WDT', 'WP', '_EX')) and right_first.endswith(verbs + adverbs):
                pause_type = 'between-phrase'
            elif right_first.endswith('_MD') and right_sec.endswith(verbs):
                pause_type = 'between-phrase'
            #   before a prepositional phrase
            elif left_first.endswith(nouns + verbs + adjs) and right_first.endswith('_IN'):
                pause_type = 'between-phrase'
            elif left_first.endswith(nouns + verbs + adjs) and right_first.endswith(adverbs) \
                    and right_sec.endswith('_IN'):
                pause_type = 'between-phrase'
            #   before a to phrase
            elif left_first.endswith(nouns + adjs + verbs) and right_first.endswith('_TO'):
                pause_type = 'between-phrase'
            #   before a than phrase
            elif right_first.startswith('than_'):
                pause_type = 'between-phrase'
            #   before a adverb modified phrase, VP, AdjP, AdP, PP
            elif right_first.endswith(adverbs) and right_sec.endswith(verbs + ('_IN',) + adjs):
                pause_type = 'between-phrase'
            #   before a noun-related phrase
            elif right_first.endswith(verbs + ('_IN',) + adverbs) and right_sec.endswith(nouns) \
                    and not right_third.endswith(verbs + adverbs):
                pause_type = 'between-phrase'
            elif left_first.endswith('_CD') and right_first.endswith('_CD'):
                pause_type = 'between-phrase'

            #   within-phrase
            #   within NP
            elif left_first.endswith(noun_modifiers):
                pause_type = 'within-phrase'
            elif left_first.startswith(nouns) and right_first.endswith(nouns) \
                    and not right_sec.endswith(verbs + adverbs):
                pause_type = 'within-phrase'
            elif left_sec.endswith('_EX') and left_first.endswith(verbs) \
                    and right_first.endswith(nouns) and not right_sec.endswith(nouns):
                pause_type = 'between-phrase'
            elif left_first.endswith(nouns) and right_first.endswith(nouns) and right_sec.endswith('_CC'):
                pause_type = 'within-phrase'
            #   within VP
            elif left_first.endswith(verbs) and right_first.endswith(adverbs + nouns):
                pause_type = 'within-phrase'
            elif left_first.endswith('_MD') and right_first.endswith(verbs):
                pause_type = 'within-phrase'
            #   within adverb modified phrase
            elif left_first.endswith(adverbs) and right_first.endswith(verbs + adjs + adverbs):
                pause_type = 'within-phrase'
            #   within a to phrase
            elif left_sec.endswith(nouns + adjs + verbs) and left_first.endswith('_TO'):
                pause_type = 'within-phrase'
            #   within a PP
            elif left_first.endswith('_IN') and right_first.endswith(nouns):
                pause_type = 'within-phrase'
            #   within a word
            elif left_first.endswith('-_:') or right_first.endswith('-_:'):
                pause_type = 'within-phrase'

            #   after all the possibilities, this becomes most likely
            elif left_first.endswith(verbs + ('_TO', 'up_RP', '_MD') + adverbs):
                pause_type = 'within-phrase'
            elif left_first.endswith(nouns) and right_first.endswith(nouns) and right_sec.endswith(nouns):
                pause_type = 'within-phrase'
            elif left_first.endswith(nouns) and right_first.endswith(nouns) and not '_V' in right_5_str:
                pause_type = 'within-phrase'
            elif right_first.endswith(verbs + adverbs + noun_modifiers + ('_MD', '_TO', )):
                pause_type = 'between-phrase'
            elif left_first.startswith('i_'):
                pause_type = 'between-phrase'
            elif right_first.startswith('i_'):
                pause_type = 'between-clause'
            elif left_first.endswith(nouns) and right_first.endswith(nouns) and '_V' in right_5_str:
                pause_type = 'between-clause'

            else:
                pause_type = 'within-phrase'
                # #   word_plus_pos
                # left_con.append(left_first)
                # right_con.append(right_first)
                # #   pos
                left_con.append(left_first.split('_')[-1])
                right_con.append(right_first.split('_')[-1])

            pause_types.append(pause_type)
            pauses_list.append([filename, self._subject, pause_type, concordance_text, left_first, right_first])

    def pause_extractor(self, tar_text, regex):
        tar_text = str(tar_text)
        tar_tokens = re.findall(rf'{regex}', tar_text)
        self.concordance_creator(tar_text, tar_tokens)

    def get_all_sln_pauses(self):
        instructor_id = self.instructor_id()
        text = self.text_with_sln_pauses_tagged()
        self.pause_extractor(text, f'<pause.+?{instructor_id}">')


def main():
    global lct_num
    # The path of where BASE is in your computer
    path = '/Users/wzx/Downloads/BASE/BASE_Modified/Tagged_XML'
    subject_list = ['ss']
    # To set speech_type = 'sem' and run the program,
    # please delete lssem006.xml and sssem006.xml files first
    speech_type = 'lct'
    for subject in subject_list:
        lct_num = 0
        # Instructor related classes (Pause or Info) are s
        ex = InstructorPause(path, subject, speech_type, 10)
        for _ in range(40):
            lct_num += 1
            if ex.file_checker():
                ex.get_all_sln_pauses()
                print(ex.filename())

    pauses_df.append(pauses_list).to_excel('SLN_PAUSE.xlsx')

                # For getting a pause concordance
                # Can either run one of these commands or print, or something like that since they return a list back
                # ex.get_all_sln_pauses() / ex.get_all_tran_pauses() / ex.get_all_fld_pauses()
    # To add all items in pauses_list into an excel spreadsheet
    # pauses_df.append(pauses_list).to_excel('Instructor_Pauses.xlsx')


if __name__ == '__main__':
    main()
    # left_con_df = Counter(left_con).most_common()
    # pd.DataFrame(left_con_df).to_excel("left_context_df.xlsx")
    # right_con_df = Counter(right_con).most_common()
    # pd.DataFrame(right_con_df).to_excel("right_context_df.xlsx")
    pause_types_df = Counter(pause_types).most_common()
    pd.DataFrame(pause_types_df).to_excel("pause_types_df.xlsx")



