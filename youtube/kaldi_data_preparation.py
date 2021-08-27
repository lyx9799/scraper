from pytube import YouTube, Playlist, extract
import os


class Kaldi_Data_Preparation:
    kaldi_text_format = "{v_id}_{begin}-{end} {content}"
    kaldi_seg_format = "{v_id}_{begin}-{end} {v_id} {seg_begin} {seg_end}"
    language_codes = ['zh-Hant', 'zh', 'zh-Hans', 'zh-CN', 'zh-TW']
    log_file = 'data/log'

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
        # download the file
        for _ in range(5):
            try:
                # extract only audio
                video = self.source.streams.filter(only_audio=True).first()
                out_file = video.download(output_path=destination.format(lc=self.lc))
                break
            except Exception as e:
                print(e)

        # save the file
        new_file = destination.format(lc=self.lc) + self.v_id + '.mp3'
        os.rename(out_file, new_file)

        # result of success
        print(self.source.title + " has been successfully downloaded.")
        with open(self.log_file, "a") as file_object:
            file_object.write("audio " + self.v_id + " 200\n")

    def download_caption(self, text_file, seg_file):
        for _ in range(5):
            try:
                avail_lans = self.source.captions.keys()
                break
            except Exception as e:
                print(e)

        for lan in self.language_codes:
            if lan in avail_lans:
                self.lc = lan
                break

        if not self.lc:
            return False

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

        with open(self.log_file, "a") as file_object:
            file_object.write("caption " + self.v_id + " 200\n")

        return True


def create_new_lan_folders(languages):
    for l in languages:
        os.makedirs('data/' + l, exist_ok=True)
        os.makedirs('data/' + l + '/videos', exist_ok=True)


if __name__ == '__main__':
    pl = 'https://www.youtube.com/playlist?list=PLzu0ghz97t3ROyBA2-7f5thrqrOYN_g3r'
    urls = Playlist(pl).video_urls

    videos_destination = 'data/{lc}/videos/'
    segements_file = 'data/{lc}/segments'
    text_file = 'data/{lc}/text'

    # cc langs
    # {'zh-Hant': <Caption lang="Chinese (Traditional)" code="zh-Hant">,
    #   'zh': <Caption lang="Chinese" code="zh">,
    #   'zh-Hans': <Caption lang="Chinese (Simplified)" code="zh-Hans">,
    #   'zh-CN': <Caption lang="Chinese (China)" code="zh-CN">,
    #   'zh-TW': <Caption lang="Chinese (Taiwan)" code="zh-TW">

    create_new_lan_folders(['zh-Hant', 'zh', 'zh-Hans', 'zh-CN', 'zh-TW'])

    for url in list(urls)[12:]:
        kaldi_data_prep = Kaldi_Data_Preparation(url)
        success = kaldi_data_prep.download_caption(text_file=text_file, seg_file=segements_file)
        if success:
            kaldi_data_prep.download_audio(destination=videos_destination)

    # redownload url
    # url = list(urls)[42]
    # kaldi_data_prep = Kaldi_Data_Preparation(url)
    # kaldi_data_prep.download_audio(destination=videos_destination)


# url = 'https://www.youtube.com/watch?v=5YIT-byVUOY&list=PL-2gsH0BOSxGwtLx6qnEH3Av7HMhhzbha&index=4&ab_channel=TEDxTalksTEDxTalksVerified'
# source = YouTube(url)
# source.captions.all
