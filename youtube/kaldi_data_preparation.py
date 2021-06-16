from pytube import YouTube, extract
import os


class Kaldi_Data_Preparation:
    kaldi_text_format = "{v_id}_{begin}-{end} {content}"
    kaldi_seg_format = "{v_id}_{begin}-{end} {v_id} {seg_begin} {seg_end}"
    language_codes = ['zh-CN', 'zh-Hans', 'zh-TW']

    def __init__(self, url):
        self.source = YouTube(url)
        self.v_id = extract.video_id(url)
        self.lc = None

    @staticmethod
    def parse_time_lazy(time_str):
        return time_str.replace(':', '').replace(',', '')

    @staticmethod
    def parse_time_to_sec(time_str):
        s, ms = time_str.split(',')
        hrs, mins, secs = [int(t) for t in s.split(':')]
        return str(secs + mins*60 + hrs*3600) + '.' + ms

    def download_audio(self, destination='.'):
        # extract only audio
        video = self.source.streams.filter(only_audio=True).first()

        # download the file
        out_file = video.download(output_path=destination.format(lc=self.lc))

        # save the file
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)

        # result of success
        print(self.source.title + " has been successfully downloaded.")

    def download_caption(self, text_file, seg_file):
        avail_lans = self.source.captions.keys()
        for lan in self.language_codes:
            if lan in avail_lans:
                self.lc = lan
                break
        print(self.lc)
        caption = self.source.captions.get_by_language_code(self.lc)
        caption_str = (caption.generate_srt_captions()).split('\n')

        kaldi_text = ''
        kaldi_seg = ''
        begin = end = None
        for i in range(len(caption_str)):
            if i % 4 == 0:              # check segment id
                assert int(caption_str[i]) == i / 4 + 1
            elif i % 4 == 1:            # parse begin end time
                begin, _, end = caption_str[i].split(' ')
            elif i % 4 == 2:
                content = caption_str[i]
            else:
                kaldi_text_param = {'v_id': self.v_id, 'begin': self.parse_time_lazy(begin),
                                    'end': self.parse_time_lazy(end), 'content': content}

                kaldi_seg_param = {'v_id': self.v_id, 'begin': self.parse_time_lazy(begin),
                                   'end': self.parse_time_lazy(end), 'seg_begin': self.parse_time_to_sec(begin),
                                   'seg_end':self.parse_time_to_sec(end)}

                kaldi_text = kaldi_text + self.kaldi_text_format.format(**kaldi_text_param) + '\n'
                kaldi_seg = kaldi_seg + self.kaldi_seg_format.format(**kaldi_seg_param) + '\n'

        print(kaldi_text)
        print(kaldi_seg)

        with open(text_file.format(lc=self.lc), "a+") as t_file:
            t_file.write(kaldi_text)

        with open(seg_file.format(lc=self.lc), "a+") as s_file:
            s_file.write(kaldi_seg)


def create_new_lan_folders(languages):
    for l in languages:
        os.makedirs('data/' + l, exist_ok=True)
        os.makedirs('data/' + l + '/videos', exist_ok=True)


if __name__ == '__main__':
    urls = ['https://www.youtube.com/watch?v=N0zhdMwD2Z8&list=PL-2gsH0BOSxGwtLx6qnEH3Av7HMhhzbha&ab_channel=TEDxTaipeiTEDxTaipeiVerified',
            'https://www.youtube.com/watch?v=5YIT-byVUOY&list=PL-2gsH0BOSxGwtLx6qnEH3Av7HMhhzbha&index=4&ab_channel=TEDxTalksTEDxTalksVerified']

    videos_destination = 'data/{lc}/videos/'
    segements_file = 'data/{lc}/segments'
    text_file = 'data/{lc}/text'

    create_new_lan_folders(['zh-CN', 'zh-Hans', 'zh-TW'])

    for url in urls:
        kaldi_data_prep = Kaldi_Data_Preparation(url)
        kaldi_data_prep.download_caption(text_file=text_file, seg_file=segements_file)
        kaldi_data_prep.download_audio(destination=videos_destination)
