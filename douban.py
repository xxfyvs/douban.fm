#-*- encoding: UTF-8 -*-
#---------------------------------import------------------------------------
import cli
import douban_token
import getch
import subprocess
from termcolor import colored
import time
import threading
import string
#---------------------------------------------------------------------------
douban = douban_token.Doubanfm()
class Win(cli.Cli):

    def __init__(self, lines):
        if douban.pro == 0:
            PRO = ''
        else:
            PRO = colored('PRO', attrs = ['reverse'])
        self.TITLE += douban.user_name + ' ' + PRO + ' ' + ' >>\r'
        self.start = 0 # 歌曲播放
        self.q = 0 # 退出
        self.time = 0
        # 守护线程
        self.t = threading.Thread(target=self.protect)
        self.t.start()
        self.t2 = threading.Thread(target=self.display_time)
        self.t2.start()
        super(Win, self).__init__(lines)

    def display_time(self):
        '显示时间的线程'
        length = len(self.TITLE)
        while True:
            if self.q == 1:
                break
            if self.time:
                minute = int(self.time) / 60
                sec = int(self.time) % 60
                show_time = string.zfill(str(minute), 2) + ':' + string.zfill(str(sec), 2)
                self.TITLE = self.TITLE[:length - 1] + '  ' + show_time + '\r'
                self.display()
                self.time -= 1
            else:
                self.TITLE = self.TITLE[:length]
            time.sleep(1)


    def protect(self):
        '守护线程,检查歌曲是否播放完毕'
        while True:
            if self.q == 1:
                break
            if self.start:
                self.p.poll()
                if self.p.returncode == 0:
                    self.play()
            time.sleep(1)

    def play(self):
        '播放歌曲'
        douban.get_song()
        song = douban.playingsong
        '是否是红心歌曲'
        self.time = song['length']
        if song['like'] == 1:
            love = self.love
        else:
            love = ''
        self.SUFFIX_SELECTED = love + colored(song['title'], 'green') + ' ' + song['kbps'] + 'kbps ' + colored(song['albumtitle'], 'yellow') + ' • ' + colored(song['artist'], 'white') + ' ' + song['public_time']
        self.p = subprocess.Popen('mplayer ' + song['url'] + ' >/dev/null 2>&1', shell=True)
        self.display()


    def run(self):
        while True:
            self.display()
            i = getch._Getch()
            c = i()
            if c == 'k':
                self.updown(-1)
            elif c == 'j':
                self.updown(1)
            elif c == 'g':
                'g键返回顶部'
                self.markline = 0
                self.topline = 0
            elif c == "G":
                'G键返回底部'
                self.markline = self.screenline
                self.topline = len(self.lines) - self.screenline - 1
            elif c == ' ':
                '选择频道,播放歌曲'
                if self.markline + self.topline != self.displayline:
                    if douban.playingsong:
                        douban.playingsong = {}
                        subprocess.Popen('killall -9 mplayer', shell=True)
                    self.displaysong()
                    self.SUFFIX_SELECTED = '正在加载请稍后...'
                    self.display()
                    douban.set_channel(douban.channels[self.markline + self.topline]['channel_id'])
                    douban.get_playlist()
                    self.play()
                    self.start = 1

            elif c == 'r':
                '标记红心,取消标记'
                if douban.playingsong:
                    if not douban.playingsong['like']:
                        self.SUFFIX_SELECTED = self.love + self.SUFFIX_SELECTED
                        self.display()
                        douban.rate_music()
                        douban.playingsong['like'] = 1
                    else:
                        self.SUFFIX_SELECTED = self.SUFFIX_SELECTED[len(self.love):]
                        self.display()
                        douban.unrate_music()
                        douban.playingsong['like'] = 0

            elif c =='n':
                '下一首'
                if douban.playingsong:
                    subprocess.Popen('killall -9 mplayer', shell=True)
                    self.SUFFIX_SELECTED = '正在加载请稍后...'
                    self.display()
                    douban.skip_song()
                    self.play()

            elif c =='b':
                '不再播放'
                if douban.playingsong:
                    subprocess.Popen('killall -9 mplayer', shell=True)
                    douban.bye()
                    self.play()

            elif c == 'q':
                self.q = 1
                subprocess.Popen('killall -9 mplayer', shell=True)
                exit()

w = Win(douban.lines)
w.run()
############################################################################