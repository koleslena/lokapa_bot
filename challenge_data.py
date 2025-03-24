import time

file_name = 'data.txt'
split_elem = '*'

SIVA_NAME = "SIVA_NAME"
QUESTION_ANSWERS = "QUESTION_ANSWERS"
QUESTION = "QUESTION"

class Challenge:
    def __init__(self, url):
        self.url = url
        self.sivaname = None
        self.question = None
        self.question_type = None
        self.answers = None
        self.right_answer = None

def save_challenge(ch):
    txt = f"""{time.strftime('%Y-%m-%d %H:%M:%S')}{split_elem} \
        {ch.url}{split_elem} \
        {ch.question_type}{split_elem} \
        {ch.sivaname if ch.sivaname else ''}{split_elem} \
        {ch.question if ch.question else ''}{split_elem} \
        {';'.join(ch.answers) if ch.answers else ''}{split_elem} \
        {ch.right_answer if ch.right_answer else ''}{split_elem} \
        """
    with open(file_name, 'a') as the_file:
        the_file.write(f'{txt}\n')

def read_challenge():
    with open(file_name) as fp:
        lines = fp.readlines()
        if len(lines) > 0:
            ch_line = [l.strip() for l in lines[-1].replace('\n', '').split(split_elem)]
            ch = Challenge(ch_line[1])
            ch.question_type = ch_line[2]
            ch.sivaname = int(ch_line[3]) if len(ch_line[3]) > 0 and ch_line[3].isdigit() else None
            ch.question = ch_line[4] if len(ch_line[4]) > 0 else None
            ch.answers = ch_line[5].split(';') if len(ch_line[5]) > 0 else None
            ch.right_answer = ch_line[6] if len(ch_line[6]) > 0 else None
            return ch
        else:
            return None
        
