#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil

# from ffmpegwrapper import FFmpeg, FFProbe, Input, Output, \
#     VideoCodec, AudioCodec, VideoFilter
# from ffmpegwrapper.parameters import Parameter

from .ffmpeg import *
from .codec import *
from .filter import *
from .parameters import *

from .timerCounter import *

class FFProbeFactory(object):
    """docstring for FFProbeFactory"""
    def __init__(self, inFile):
        self.input = Input(inFile)
        self.input.add_formatparam('-hide_banner', None)
        self.output = Output(None)

    def getVideoLen(self):
        self.input.add_formatparam('-print_format', 'ini')
        self.input.add_formatparam('-show_format', None)
        self.input.add_formatparam('-show_streams', None)

        result = self.run()
        for item in result:
            print(item)

        # with open("videoInfo.json", "w", encoding='utf-8') as f:
        #     f.write(str(result))
        #     json.dump(result, f, indent=4, ensure_ascii=False)
        # print(json.dumps(result))

    """
    Other Handle
    """
    def run(self):
        return FFProbe(os.path.join(os.path.abspath('.'), 'bin','ffprobe.exe'), self.input, self.output).run()

class FFMpegFactory(object):
    """docstring for FFMpegFactory"""
    def __init__(self, inFile, outFile):
        self.input = Input('"'+inFile+'"')
        self.input.add_formatparam('-hide_banner', None)
        # self.input.add_formatparam('-loglevel', 'verbose')
        # self.input.add_formatparam('-loglevel', 'warning')
        # self.input.add_formatparam('-loglevel', 'error')
        # self.input.add_formatparam('-report', None)
        # self.input.add_formatparam('-hwaccel', 'dxva2')
        # self.input.add_formatparam('-hwaccel', 'qsv')
        # self.input.add_formatparam('-threads', '4')
        self.output = Output('"'+outFile+'"')
  
    """
    Video Handle
    """
    def outputSarDar(self):
        # Output 
        # self.output.add_formatparam('-vf', 'setsar=1:1')
        # self.output.add_formatparam('-vf', 'setdar=16:9')
        self.output.add_formatparam('-vf', 'setsar=1/1')
        self.output.add_formatparam('-vf', 'setdar=16/9')

    def outputFormat(self):
        # Output
        #self.output.add_formatparam('-an', None)
        # self.output.add_formatparam('-s', '1280x720')
        self.output.add_formatparam('-s', '1920x1080')
        self.output.add_formatparam('-r', '25')
        self.output.add_formatparam('-pix_fmt', 'yuv420p')
        self.output.add_formatparam('-c:v', 'libx264')
        self.output.add_formatparam('-c:a', 'aac')
        self.output.add_formatparam('-strict', '-2') 

        # self.output.add_formatparam('-c:v', 'h264_qsv')
        # self.output.add_formatparam('-look_ahead', '0')
        # self.output.add_formatparam('-b:v', '1.6M')

    def mp4Format_2(self, fRate):
        # Output
        #self.output.add_formatparam('-an', None)
        # self.output.add_formatparam('-s', '1280x720')
        self.output.add_formatparam('-s', '1920x1080')
        self.output.add_formatparam('-pix_fmt', 'yuv420p')
        self.output.add_formatparam('-c:v', 'libx264')
        self.output.add_formatparam('-c:a', 'aac')
        self.output.add_formatparam('-strict', '-2')
        self.output.add_formatparam('-r', fRate) 

    def mp4Format(self):
        # Output
        self.output.add_formatparam('-c:v', 'libx264')
        self.output.add_formatparam('-c:a', 'aac')
        self.output.add_formatparam('-strict', '-2')

        # self.output.add_formatparam('-c:v', 'h264_qsv')
        # self.output.add_formatparam('-look_ahead', '0')
        # self.output.add_formatparam('-b:v', '1.6M')

    def videFormat(self):
        # Input
        # Output
        self.output.add_formatparam('-r', 25)

    def videoCut(self, start, during=None):
        self.outputSarDar()
        # Input
        self.input.add_formatparam('-ss', start)
        #self.input.add_formatparam('-t', during)
        self.input.add_formatparam('-accurate_seek', None)

        # Output
        if not during is None:
            self.output.add_formatparam('-t', during)
        self.output.add_formatparam('-avoid_negative_ts', '1')
        self.output.add_formatparam('-seek2any', '1')

    def addFilter(self, filter):
        # Output
        self.output.add_formatparam('-filter_complex', filter)

    def showTime(self, frameRate, time ,startTime, endTime):
        # Output
        # time ('09\:57\:00\:00')
        strFilter = "drawtext=fontfile=cour.ttf:fontsize=35:fontcolor=#FFFFFF:timecode='%s':r=%s:x=351:y=117:enable=between(t\,%s\,%s)" % (time, frameRate, startTime, endTime)
        self.output.add_formatparam('-filter_complex', strFilter)

    def videoMerge(self):
        # Input
        self.input.add_formatparam('-f', 'concat')
        self.input.add_formatparam('-safe', '0')
        
        # Output
        self.output.add_formatparam('-c', 'copy')

    def twoVideoMerge(self, videoLen, videFile, overlayDuring):
        # Input
        self.input.add_formatparam('-i', '"'+videFile+'"')
        
        # Output
        if overlayDuring == 0:
            # all video slow
            strFilter = '[1:v][0:v]concat[out]'
        elif overlayDuring > 0:
            # slow from start
            strFilter = '[1:v]trim=0:%s,setpts=PTS-STARTPTS[v1];'\
                        '[1:v]trim=start=%s,setpts=PTS-STARTPTS[v2];'\
                        '[0:v]colorkey=0x202020:0.3:0.3[ckout];'\
                        '[ckout][v2]overlay=enable=between(t\,0\,%s)[mergeout];'\
                        '[v1][mergeout]concat[out]'\
                        % (videoLen-overlayDuring, videoLen-overlayDuring, overlayDuring)
        else:
            # slow during
            strFilter = '[1:v]trim=0:%s,setpts=PTS-STARTPTS[v1];'\
                        '[1:v]trim=start=%s,setpts=PTS-STARTPTS,colorkey=0x202020:0.3:0.3[v2];'\
                        '[0:v][v2]overlay=enable=between(t\,0\,%s)[mergeout];'\
                        '[v1][mergeout]concat[out]'\
                        % (videoLen+overlayDuring, videoLen+overlayDuring, abs(overlayDuring))

        self.output.add_formatparam('-filter_complex', strFilter)
        self.output.add_formatparam('-map', '[out]')

    def videoScale(self, x, y, width, height):
        # Output
        strFilter = 'crop=%s:%s:%s:%s' % (width, height, x, y)
        self.output.add_formatparam('-filter_complex', strFilter)
        #self.mp4Format_2()

    def videoRotate(self, angle):
        # Output (以度表示)
        strFilter = 'rotate=-(%s*PI/180)' % (angle)
        self.output.add_formatparam('-filter_complex', strFilter)

    def videoCBS(self, contrast=1, brightness=0, saturation=1):
        # contrast -2.0 to 2.0. The default value is "1".
        # brightness -1.0 to 1.0. The default value is "0".
        # saturation 0.0 to 3.0. The default value is "1".
        # Output
        strFilter = 'eq=contrast=%s:brightness=%s:saturation=%s' % (contrast, brightness, saturation)
        self.output.add_formatparam('-filter_complex', strFilter)

    def videoLogo(self, imgFile):
        #filter_complex "overlay=0:0:enable=between(t,0,2)"
        # Input
        self.input.add_formatparam('-i', '"'+imgFile+'"')
        
        # Output
        self.output.add_formatparam('-c:v', 'libx264')
        self.output.add_formatparam('-c:a', 'copy')
        self.output.add_formatparam('-strict', '-2')
        # strFilter = '[0:v]scale=180:80[logo];'\
        #             '[1:v][logo]overlay=main_w-overlay_w-10:main_h-overlay_h-10[out]' 
        # strFilter = '[1:v][0:v]overlay=main_w-overlay_w-10:main_h-overlay_h-10[out]'
        strFilter = '[1:v][0:v]overlay=0:0[out]' 
        self.output.add_formatparam('-filter_complex', strFilter)
        self.output.add_formatparam('-map', '[out]')

    def videoToOneImg(self, time):
        # Input
        self.input.add_formatparam('-ss', time)
        
        # Output
        self.output.add_formatparam('-f', 'image2')
        self.output.add_formatparam('-vframes', '1')

    def videoEndToOneImg(self, time):
        # Input
        self.input.add_formatparam('-sseof', time)
        
        # Output
        self.output.add_formatparam('-f', 'image2')
        self.output.add_formatparam('-vframes', '1')

    def oneImgToVideo(self, time):
        # Input
        self.input.add_formatparam('-loop', '1')
        self.input.add_formatparam('-f', 'image2')
        
        # Output
        self.output.add_formatparam('-t', time)

    def videoOverlayVideo(self, file):
        # Input
        self.input.add_formatparam('-i', '"'+file+'"')

        # Output
        strFilter = '[1:v]colorkey=0x333333:0.3:0.2[ckout];'\
                    '[0:v][ckout]overlay[out]'

        self.output.add_formatparam('-filter_complex', strFilter)
        self.output.add_formatparam('-map', '[out]')

    def PIP_videoOnImg(self, videoFile):
        # Input
        # Output
        strFilter = "movie='%s',scale=1280:720,drawbox=color=0xD3D3D3@0.5:t=6,fade=in:st=0:d=0.25[wm];"\
                    "[in]boxblur=3:1[img];"\
                    "[img][wm]overlay=(W-w)/2:(H-h)/2[out]"\
                    % (videoFile)
        self.output.add_formatparam('-vf', strFilter)

    def PIP_imgOnVideo(self, imgFile, start, end):
        # Input
        self.input.add_formatparam('-loop', '1')
        self.input.add_formatparam('-i', '"'+imgFile+'"')

        if int(end) - int(start) > 3:
            during = 1
        else:
            during = 0.5
        
        # Output
        strFilter = '[0:0]format=rgba,fade=in:st=%s:d=%s:alpha=1,fade=out:st=%s:d=%s:alpha=1[img];'\
                    '[1:0][img]overlay=0:0:shortest=1[out]'\
                     % (start, during, end, during)
        self.output.add_formatparam('-filter_complex', strFilter)
        self.output.add_formatparam('-map', '[out]')
    
    def PIP_imgOnVideo_2(self, imgFile, start, end):
        # Input
        self.input.add_formatparam('-loop', '1')
        self.input.add_formatparam('-i', '"'+imgFile+'"')

        # during = 0
        
        # # Output
        # strFilter = '[0:0]format=rgba,fade=in:st=%s:d=%s:alpha=1,fade=out:st=%s:d=%s:alpha=1[img];'\
        #             '[1:0][img]overlay=0:0:shortest=1[out]'\
        #              % (start, during, end, during)
        # # Output
        strFilter = '[0:0]format=rgba[img];'\
                    '[1:0][img]overlay=0:0:shortest=1:enable=between(t\,%s\,%s)[out]'\
                     % (start, end)
        self.output.add_formatparam('-filter_complex', strFilter)
        self.output.add_formatparam('-map', '[out]')

    def videoFadeIn(self, during):
        # Output
        strFilter = 'fade=t=in:st=0:d=%s' % (during)
        self.output.add_formatparam('-filter_complex', strFilter)

    def videoFadeOut(self, start):
        # Output
        strFilter = 'fade=t=out:st=%s' % (start)
        self.output.add_formatparam('-filter_complex', strFilter)

    def videoSpeed(self, videoStart, videoEnd, slowStart, slowEnd, speed):
        # Input
        # Output
        speed = 1/speed
        #strFilter = '[0:v]setpts=%s*PTS[v]' % (speed)
        if slowStart == videoStart and slowEnd == videoEnd:
            # all video slow
            strFilter = '[0:v]setpts=%s*PTS[out]' % (speed)
        elif slowStart == videoStart:
            # slow from start
            strFilter = '[0:v]trim=0:%s,setpts=PTS-STARTPTS[v1];'\
                        '[0:v]trim=start=%s,setpts=PTS-STARTPTS[v2];'\
                        '[v1]setpts=%s*PTS[slow];[slow][v2]concat[out]'\
                         % (slowEnd, slowEnd, speed)
        elif slowEnd == videoEnd:
            # slow to end
            strFilter = '[0:v]trim=0:%s,setpts=PTS-STARTPTS[v1];'\
                        '[0:v]trim=start=%s,setpts=PTS-STARTPTS[v2];'\
                        '[v2]setpts=%s*PTS[slow];[v1][slow]concat[out]'\
                         % (slowStart, slowStart, speed)
        else:
            # slow during
            strFilter = '[0:v]trim=0:%s,setpts=PTS-STARTPTS[v1];'\
                        '[0:v]trim=%s:%s,setpts=PTS-STARTPTS[v2];'\
                        '[0:v]trim=start=%s,setpts=PTS-STARTPTS[v3];'\
                        '[v2]setpts=%s*PTS[slow];'\
                        '[v1][slow][v3]concat=n=3:v=1:a=0[out]'\
                         % (slowStart, slowStart, slowEnd, slowEnd, speed)

        self.output.add_formatparam('-filter_complex', strFilter)
        self.output.add_formatparam('-map', '[out]')

    def imgMoveScale(self, during):
        # Input
        self.input.add_formatparam('-loop', '1')
        # Output
        strFilter = "zoompan='if(lte(on,%s*15),zoom+0.003,zoom-0.003)':d=%s*30:fps=30" \
                    % (during, during)
        self.output.add_formatparam('-vf', strFilter)
        self.output.add_formatparam('-t', during)

    def cameraMove(self, x, y, frameRate):
        # Output
        strFilter = 'zoompan=z="1+in/800":d=1:x=%s:y=%s:fps=%s' % (x, y, frameRate)
        #strFilter = "zoompan=z='1+in/1000':d=1:y='if(gte(zoom,1.5),y,y+1)':x='x'"
        self.output.add_formatparam('-filter_complex', strFilter)
        # self.mp4Format_2('60')

    def vidstabdetect(self):
        # Output
        strFilter = 'vidstabdetect=stepsize=6:shakiness=8:accuracy=9:result=mytransforms.trf'
        self.output.add_formatparam('-filter_complex', strFilter)
        self.output.add_formatparam('-f', 'null')

    def vidstabtransform(self):
        strFilter = 'vidstabtransform=input=mytransforms.trf:zoom=1:maxangle=3*PI/180:smoothing=30,unsharp=5:5:0.8:3:3:0.4'
        self.output.add_formatparam('-filter_complex', strFilter)

    def palettegen(self):
        # Output
        self.output.add_formatparam('-r', '5')
        strFilter = 'fps=5,scale=560:-1:flags=lanczos,palettegen'
        self.output.add_formatparam('-filter_complex', strFilter)

    def paletteuse(self, file):
        # Input
        self.input.add_formatparam('-i', '"'+file+'"')
        # Output
        self.output.add_formatparam('-r', '5')
        strFilter = '[1:v]fps=5,scale=560:-1:flags=lanczos[x];[x][0:v]paletteuse'
        self.output.add_formatparam('-filter_complex', strFilter)

    """
    Audio Handle
    """
    def addMergeMusic(self, music):
        # Input
        #self.input.add_formatparam('-stream_loop', '100')
        self.input.add_formatparam('-i', '"'+music+'"')
        # Output
        strFilter = '"[0:a][1:a]amix=duration=first,pan=stereo|c0<c0+c1|c1<c2+c3,pan=mono|c0=c0+c1[a]"'
        # strFilter = '"[1:a]volume=1[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=0[a]"'
        self.output.add_formatparam('-filter_complex', strFilter)
        self.output.add_formatparam('-map_metadata', '-1')
        self.output.add_formatparam('-map', '1:v')
        self.output.add_formatparam('-map', '[a]')
        self.mp4Format()
        # self.output.add_formatparam('-shortest', None)
        self.output.add_formatparam('-ac', '2')
        self.output.add_formatparam('-b', '4M')

    def splitAudio(self):
        # Output
        strFilter = 'volume=2.3'
        self.output.add_formatparam('-filter_complex', strFilter)
        self.output.add_formatparam('-vn', None)
        self.output.add_formatparam('-b:a', '128k')
        self.output.add_formatparam('-ar', '48000')
        self.output.add_formatparam('-ac', '2')

    def mergeAudio(self, file):
        # Input
        self.input.add_formatparam('-i', '"'+file+'"')
        # Output
        self.output.add_formatparam('-map_metadata', '-1')
        self.output.add_formatparam('-map', '1:v')
        self.output.add_formatparam('-map', '0:a')
        self.mp4Format()
        # strFilter = '"[0:a]pan=stereo|c0<c0+c1|c1<c2+c3,pan=mono|c0=c0+c1[a]"'
        # # strFilter = '"[1:a]volume=1[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=0[a]"'
        # self.output.add_formatparam('-filter_complex', strFilter)
        # self.output.add_formatparam('-map_metadata', '-1')
        # self.output.add_formatparam('-map', '1:v')
        # self.output.add_formatparam('-map', '[a]')
        # self.mp4Format()

    def addMusic(self, music):
        # Input
        #self.input.add_formatparam('-stream_loop', '100')
        self.input.add_formatparam('-i', '"'+music+'"')
        # Output
        self.output.add_formatparam('-map_metadata', '-1')
        self.output.add_formatparam('-map', '1:v:0')
        self.output.add_formatparam('-map', '0:a:0')
        self.mp4Format()
        # self.output.add_formatparam('-shortest', None)
        # self.output.add_formatparam('-b', '4M')

    def addNullAudio(self, nullFile):
        # Input
        self.input.add_formatparam('-i', '"'+nullFile+'"')
        # Output
        self.output.add_formatparam('-c:v', 'copy')
        self.output.add_formatparam('-c:a', 'aac')
        self.output.add_formatparam('-b:a', '128k')
        self.output.add_formatparam('-ar', '48000')
        self.output.add_formatparam('-ac', '2')
        self.output.add_formatparam('-shortest', None)

    def creatMuteAudio(self, during):
        # Input
        self.input.add_formatparam('-ss', '0')
        self.input.add_formatparam('-accurate_seek', None)

        
        # Output
        self.output.add_formatparam('-t', during)
        self.output.add_formatparam('-avoid_negative_ts', '1')
        self.output.add_formatparam('-seek2any', '1')
        self.output.add_formatparam('-b:a', '128k')
        self.output.add_formatparam('-ar', '48000')
        self.output.add_formatparam('-ac', '2')

    def audioMute(self):
        # Output
        self.output.add_formatparam('-an', None)
        #self.output.add_formatparam('-vcodec', 'copy')

    def audioMix(self, audioFile):
        # Input
        self.input.add_formatparam('-i', '"'+audioFile+'"')
        # Output
        strFilter = 'amix=inputs=2:duration=longest:dropout_transition=2'
        self.output.add_formatparam('-filter_complex', strFilter)

    def transVideoRate(self, rate):
        # Output
        self.output.add_formatparam('-b', rate)
        
    """
    Subtitle Handle
    """
    def addSubtitle(self, txtFile):
        # Output
        strFilter = '"drawtext=fontfile=zhanku.ttf:x=800:y=900:fontsize=72:fontcolor=#FF0000:alpha=0.9:textfile=%s:enable=between(t\,3.5\,6.5)"' \
        % (txtFile)
        self.output.add_formatparam('-filter_complex', strFilter)


    """
    Other Handle
    """
    def run(self):
        self.output.overwrite()
        # FFmpeg(sys.path[0]+'/bin/ffmpeg.exe', self.input, self.output).run()
        return FFmpeg(os.path.join(os.path.abspath('.'), 'bin','ffmpeg.exe'), self.input, self.output).run()

class VideoAutoEditor():
    """docstring for VideoAutoEditor"""
    def __init__(self):
        self.timerCounter = CountingTimer()

    def getFrameRate(self, file):
        item_list = None
        cmd = '%s -i "%s"' % (os.path.join(os.path.abspath('.'), 'bin','ffmpeg.exe'),file)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        p.wait()
        item_list = p.stdout.read().splitlines()

        duration = None
        for i in range(len(item_list)):
            try:
                item = item_list[i].decode('utf-8')
            except:
                item = str(item_list[i])

            if "Stream" in item:
                begin_index = item.find("kb/s,")
                end_index = item.find("fps")
                frmateRate = item[begin_index + 5: end_index].strip()

        return frmateRate

    def checkVideoMute(self, file):
        item_list = None
        cmd = '%s -i "%s"' % (os.path.join(os.path.abspath('.'), 'bin','ffmpeg.exe'),file)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        p.wait()
        item_list = p.stdout.read().splitlines()

        for i in range(len(item_list)):
            try:
                item = item_list[i].decode('utf-8')
            except:
                item = str(item_list[i])

            if "Audio" in item:
                return False
        return True

    def getVideoLen(self, file):
        '''
        Get Video/Audio total time (s)
        :param file: video/audio file
        '''
        item_list = None
        cmd = '%s -i "%s"' % (os.path.join(os.path.abspath('.'), 'bin','ffmpeg.exe'),file)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        p.wait()
        item_list = p.stdout.read().splitlines()

        duration = None
        for i in range(len(item_list)):
            try:
                item = item_list[i].decode('utf-8')
            except:
                item = str(item_list[i])

            if "Duration" in item:
                begin_index = item.find(":")
                end_index = item.find(",")
                duration = item[begin_index + 1: end_index].strip()
                microTime = duration[duration.find(".") :]
                print(microTime)
                duration = duration[ : duration.find(".")]
                duration = duration.split(':')
                duration = int(duration[0])*3600 + int(duration[1])*60 + int(duration[2])+float(microTime)
           
        return duration

    def videoCut(self, listParam):
        """
        handle : ['videoCut', 'inFile', 'start', 'during', 'outFile']
        """

        # check Param
        if len(listParam) != 5:
            print(listParam)
            print("COMMAND: cut -> param format invalid")
            print("['cut', 'inFile', 'start', 'during', 'outFile']")
            return 1
        
        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.videoCut(listParam[2], listParam[3])
        # check if Mute
        ffmpegManger.audioMute()
        result = ffmpegManger.run()
        return result

    def videoCut_a(self, listParam):
        """
        handle : ['videoCut_a', 'inFile', 'start', 'during', 'outFile']
        """

        # check Param
        if len(listParam) != 5:
            print(listParam)
            print("COMMAND: videoCut_a -> param format invalid")
            print("['videoCut_a', 'inFile', 'start', 'during', 'outFile']")
            return 1
        
        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.videoCut(listParam[2], listParam[3])
        result = ffmpegManger.run()
        return result

    def audioMute(self, listParam):
        """
        handle : ['mute', 'inpFile', 'outFile']
        """
        # check Param
        if len(listParam) != 3:
            print("COMMAND: mute -> param format invalid")
            print("['mute', 'inpFile', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.audioMute()
        result = ffmpegManger.run()
        return result

    def creatMuteAudio(self, listParam):
        """
        handle : ['creatMuteAudio', 'inpFile', 'outFile']
        """
        # check Param
        if len(listParam) != 3:
            print("COMMAND: creatMuteAudio -> param format invalid")
            print("['creatMuteAudio', 'inpFile', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(os.path.join(os.path.abspath('.'), 'bin','null.mp3'), listParam[-1])
        videoLen = self.getVideoLen(listParam[1])
        ffmpegManger.creatMuteAudio(videoLen)
        result = ffmpegManger.run()
        return result

    def eachVideoMerge(self, listParam):
        """
        handle : ['eachVideoMerge', [['inpFile1','1'], ..., ['inFile2','2']], 'outFile']
        """
        # check Param
        if len(listParam) != 3:
            print("COMMAND: eachVideoMerge -> param format invalid")
            print("['eachVideoMerge', [['inpFile1','1'], ..., ['inFile2','2']], 'outFile']")
            return 1

        # handle
        result = 0
        n = 0
        inFile = ''
        outPath = os.path.dirname(listParam[-1])
        for item in listParam[1]:
            n = n + 1
            if n == 1:
                # first file to merge
                inFile = item[0]
                continue
            outFile = os.path.join(outPath, 'product_merge'+str(n)+inFile[-4:])
            ffmpegManger = FFMpegFactory(inFile, outFile)
            videoLen = self.getVideoLen(inFile)
            mergeFile = item[0]
            mergeDuring = int(item[1])
            ffmpegManger.twoVideoMerge(videoLen, mergeFile, mergeDuring)
            result = ffmpegManger.run()

            # change inFile
            inFile = outFile

        # final output mp4
        if os.path.exists(listParam[-1]):
            os.remove(listParam[-1])
        shutil.copyfile(outFile, listParam[-1])
        return result

    def videoMerge(self, listParam):
        """
        handle : ['merge', 'inpFile1', 'inFile2', ..., 'outFile']
        """
        # check Param
        if len(listParam) < 3:
            print("COMMAND: merge -> param format invalid")
            print("['merge', 'inpFile1', 'inFile2', ..., 'outFile']")
            return 1

        # create video list
        listLen = len(listParam)
        f = open("filelist.txt", "w", encoding='utf-8')
        str = ''
        for i in range(1, listLen - 1):
            str += "file '%s' \n" % listParam[i]
        f.write(str)
        f.close()

        # handle
        ffmpegManger = FFMpegFactory('filelist.txt', listParam[listLen-1])
        ffmpegManger.videoMerge()
        result = ffmpegManger.run()

        os.remove("filelist.txt")
        return result

    def videoOverlayVideo(self, listParam):
        """
        handle : ['videoOverlayVideo', 'videoFile1', 'videoFile2', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print("COMMAND: videoOverlayVideo -> param format invalid")
            print("['videoOverlayVideo', 'videoFile1', 'videoFile2', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.videoOverlayVideo(listParam[2])
        result = ffmpegManger.run()
        return result

    def videoCBS(self, listParam):
        """
        handle : ['videoCBS', 'inFile', 'contrast', 'brightness', 'saturation', 'outFile']
        """
        # check Param
        if len(listParam) != 6:
            print("COMMAND: videoCBS -> param format invalid")
            print("['videoCBS', 'inFile', 'contrast', 'brightness', 'saturation', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.videoCBS(listParam[2], listParam[3], listParam[4])
        result = ffmpegManger.run()
        return result

    def videoToOneImg(self, listParam):
        """
        handle : ['videoToOneImg', 'videoFile', 'time', 'imgFile']
        """
        # check Param
        if len(listParam) != 4:
            print("COMMAND: toimg -> param format invalid")
            print("['toimg', 'videoFile', 'time', 'imgFile']")
            return 1

        # -1 mean to get last frame from video
        if listParam[2] == '-1':
            listParam[2] = self.getVideoLen(listParam[1])  

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.videoToOneImg(listParam[2])
        result = ffmpegManger.run()
        return result

    def videoEndToOneImg(self, listParam):
        """
        handle : ['videoEndToOneImg', 'videoFile', 'time', 'imgFile']
        """
        # check Param
        if len(listParam) != 4:
            print("COMMAND: videoEndToOneImg -> param format invalid")
            print("['videoEndToOneImg', 'videoFile', 'time', 'imgFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.videoEndToOneImg(listParam[2])
        result = ffmpegManger.run()
        return result

    def oneImgToVideo(self, listParam):
        """
        handle : ['imgToVideo', 'imgFile', 'during', 'videoFile']
        """
        # check Param
        if len(listParam) != 4:
            print("COMMAND: imgToVideo -> param format invalid")
            print("['imgToVideo', 'imgFile', 'during', 'videoFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.oneImgToVideo(listParam[2])
        result = ffmpegManger.run()
        return result

    def PIP_videoOnImg(self, listParam):
        """
        handle : ['PIP_videoOnImg', 'imgFile', 'videoFile', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print("COMMAND: PIP_videoOnImg -> param format invalid")
            print("['PIP_videoOnImg', 'imgFile', 'videoFile', 'outFile']")
            return 1

        if os.path.exists("tmpStar.mp4"):
            os.remove("tmpStar.mp4")
        shutil.copyfile(listParam[2], "tmpStar.mp4")

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.PIP_videoOnImg("tmpStar.mp4")
        result = ffmpegManger.run()

        # del file
        os.remove("tmpStar.mp4")
        return result

    def PIP_imgOnVideo(self, listParam):
        """
        handle : ['PIP_imgOnVideo', 'videoFile', 'imgFile', 'start', 'end', 'outFile']
        """
        # check Param
        if len(listParam) != 6:
            print("COMMAND: PIP_imgOnVideo -> param format invalid")
            print("['PIP_imgOnVideo', 'videoFile', 'imgFile', 'start', 'end', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.PIP_imgOnVideo(listParam[2], listParam[3], listParam[4])
        result = ffmpegManger.run()
        return result

    def PIP_imgOnVideo_2(self, listParam):
        """
        handle : ['PIP_imgOnVideo_2', 'videoFile', 'imgFile', 'start', 'end', 'outFile']
        """
        # check Param
        if len(listParam) != 6:
            print("COMMAND: PIP_imgOnVideo_2 -> param format invalid")
            print("['PIP_imgOnVideo_2', 'videoFile', 'imgFile', 'start', 'end', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.PIP_imgOnVideo_2(listParam[2], listParam[3], listParam[4])
        result = ffmpegManger.run()
        return result

    def videoLogo(self, listParam):
        """
        handle : ['videoLogo', 'videoFile', 'imgFile', 'size', 'outFile']
        """
        # check Param
        if len(listParam) != 5:
            print("COMMAND: videoLogo -> param format invalid")
            print("['videoLogo', 'videoFile', 'imgFile', 'size', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.videoLogo(listParam[2])
        result = ffmpegManger.run()
        return result

    def cameraMove(self, listParam):
        """
        handle : ['cameraMove', 'videoFile', 'x', 'y', 'outFile']
        """
        # check Param
        if len(listParam) != 5:
            print("COMMAND: cameraMove -> param format invalid")
            print("['cameraMove', 'videoFile', 'x', 'y', 'outFile']")
            return 1


        # get frame rate
        frameRate = self.getFrameRate(listParam[1])

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.cameraMove(listParam[2], listParam[3], frameRate)
        result = ffmpegManger.run()
        return result

    def addSubtitle(self, listParam):
        """
        handle : ['addSubtitle', 'videoFile', 'txtSubtitle', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print("COMMAND: addSubtitle -> param format invalid")
            print("['addSubtitle', 'videoFile', 'txtSubtitle', 'outFile']")
            return 1

        # 1. get Subtitle from File Name
        if os.path.exists("tmpSubtitle.txt"):
            os.remove("tmpSubtitle.txt")
        with open("tmpSubtitle.txt", "w", encoding='utf-8') as f:
            f.write(listParam[2])
        f.close()

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.addSubtitle("tmpSubtitle.txt")
        result = ffmpegManger.run()
        
        os.remove("tmpSubtitle.txt")
        return result

    def videoScale(self, listParam):
        """
        handle : ['videoScale', 'videoFile', 'x', 'y', 'width', 'height' 'outFile']
        """
        # check Param
        if len(listParam) != 7:
            print(listParam)
            print("COMMAND: videoScale -> param format invalid")
            print("['videoScale', 'videoFile', 'x', 'y', 'width', 'height' 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.videoScale(listParam[2], listParam[3], listParam[4], listParam[5])
        result = ffmpegManger.run()
        return result

    def videoFade(self, listParam):
        """
        handle : ['videoFade', 'videoFile', 'fadetype', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print(listParam)
            print("COMMAND: videoFade -> param format invalid")
            print("['videoFade', 'videoFile', 'fadetype', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        # check type
        if listParam[2] == 1:
            # fade in
            ffmpegManger.videoFadeIn(0.5)
        else:
            # fade out
            videoLen = self.getVideoLen(listParam[1])
            print(videoLen)
            ffmpegManger.videoFadeOut(videoLen-0.5)
        result = ffmpegManger.run()
        return result

    def videoRotate(self, listParam):
        """
        handle : ['videoRotate', 'videoFile', 'angle', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print("COMMAND: videoRotate -> param format invalid")
            print("['videoRotate', 'videoFile', 'angle', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.videoRotate(listParam[2])
        result = ffmpegManger.run()
        return result

    def videoSpeed(self, listParam):
        """
        handle : ['videoSpeed', 'videoFile', 'videoStart', 'videoEnd', 'slowStart', 'slowEnd', 'spead', 'outFile']
        """
        # check Param
        if len(listParam) != 8:
            print("COMMAND: videoSpeed -> param format invalid")
            print("['videoSpeed', 'videoFile', 'videoStart', 'videoEnd', 'slowStart', 'slowEnd', 'spead', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.videoSpeed(listParam[2], listParam[3], listParam[4], listParam[5], listParam[6])
        result = ffmpegManger.run()
        return result

    def outputFormat(self, listParam):
        """
        handle : ['outputFormat', 'videoFile', 'outFile']
        """
        # check Param
        if len(listParam) != 3:
            print(listParam)
            print("COMMAND: outputFormat -> param format invalid")
            print("['outputFormat', 'videoFile', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.outputFormat()
        result = ffmpegManger.run()
        return result

    def addFilter(self, listParam):
        """
        handle : ['addFilter', 'videoFile', 'filter', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print(listParam)
            print("COMMAND: addFilter -> param format invalid")
            print("['addFilter', 'videoFile', 'filter', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.addFilter(listParam[2])
        result = ffmpegManger.run()
        return result

    def addVoice(self, listParam):
        """
        handle : ['addVoice', 'videoFile', 'type', 'startTime', 'outFile']
        """
        # check Param
        if len(listParam) != 5:
            print(listParam)
            print("COMMAND: addVoice -> param format invalid")
            print("['addVoice', 'videoFile', 'type', 'startTime', 'outFile']")
            return 1

        outputPath = os.path.dirname(listParam[-1])
        print(">>>>>", outputPath)
        
        # step 1  -> get audio from video
        if self.checkVideoMute(listParam[1]):
            ffmpegManger = FFMpegFactory(os.path.join(os.path.abspath('.'), 'bin','null.mp3'), 
                os.path.join(outputPath, "step1.mp3"))
            videoLen = self.getVideoLen(listParam[1])
            ffmpegManger.creatMuteAudio(videoLen)
            result = ffmpegManger.run()
        else:
            ffmpegManger = FFMpegFactory(listParam[1], os.path.join(outputPath, "step1.mp3"))
            ffmpegManger.splitAudio()
            result = ffmpegManger.run()

        # step 2 -> split audio (front) ffmpeg.exe -y -ss 0 -i .\step1.mp3 -t 3 step2.mp3
        ffmpegManger = FFMpegFactory(os.path.join(outputPath, "step1.mp3"), os.path.join(outputPath, "step2.mp3"))
        ffmpegManger.videoCut(0, listParam[3])
        result = ffmpegManger.run()

        # step 3 -> split audio (tail) ffmpeg.exe -y -ss 3 -i .\step1.mp3  step3.mp3
        ffmpegManger = FFMpegFactory(os.path.join(outputPath, "step1.mp3"), os.path.join(outputPath, "step3.mp3"))
        ffmpegManger.videoCut(listParam[3])
        result = ffmpegManger.run()

        # step 4 -> merge voice and tail audio ffmpeg.exe -y -i .\step3.mp3 -i .\3s.mp3 -filter_complex "amix=inputs=2:duration=longest:dropout_transition=5" .\step4.mp3
        if listParam[2] == '1': # 开场哨
            voiceFile = os.path.join(os.path.abspath('.'), 'bin','start.mp3')
        else:
            voiceFile = os.path.join(os.path.abspath('.'), 'bin','end.mp3')
        ffmpegManger = FFMpegFactory(os.path.join(outputPath, "step3.mp3"), os.path.join(outputPath, "step4.mp3"))
        ffmpegManger.audioMix(voiceFile)
        result = ffmpegManger.run()
        # step 5 -> merge front audio and tail audio ffmpeg.exe -y -f concat -safe 0 -i videolist.txt step5.mp3
        # create video list
        f = open("filelist.txt", "w", encoding='utf-8')
        str = ''
        str += "file '%s' \n" % os.path.join(outputPath, "step2.mp3")
        str += "file '%s' \n" % os.path.join(outputPath, "step4.mp3")
        f.write(str)
        f.close()
        # handle
        ffmpegManger = FFMpegFactory('filelist.txt', os.path.join(outputPath, "step5.mp3"))
        ffmpegManger.videoMerge()
        result = ffmpegManger.run()
        os.remove("filelist.txt")

        # step 6 -> merge audio and video ffmpeg.exe -y -i .\step5.mp3 -i .\clip.mp4 -map 1:v -map 0:a output.mp4
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.mergeAudio(os.path.join(outputPath, "step5.mp3"))
        result = ffmpegManger.run()
        return result

    def showTime(self, listParam):
        """
        handle : ['showTime', 'videoFile', 'time', 'startTime', 'endTime', 'outFile']
        """
        # check Param
        if len(listParam) != 6:
            print(listParam)
            print("COMMAND: showTime -> param format invalid")
            print("['showTime', 'videoFile', 'time', 'startTime', 'endTime', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        frameRate = self.getFrameRate(listParam[1])
        time = self.formatTime(listParam[2])
        ffmpegManger.showTime(frameRate, time, listParam[3], listParam[4])
        result = ffmpegManger.run()
        return result

    def formatTime(self, time):
        # 00:00 -> 00\:00\:00\:00
        time = time.replace(':', '\:')
        time = '00\:'+time+'\:00'
        return time

    def imgMoveScale(self, listParam):
        """
        handle : ['imgMoveScale', 'imgFile', 'during', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print(listParam)
            print("COMMAND: imgMoveScale -> param format invalid")
            print("['imgMoveScale', 'imgFile', 'during', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.imgMoveScale(listParam[2])
        result = ffmpegManger.run()
        return result

    def mergeAudio(self, listParam):
        """
        handle : ['mergeAudio', 'videoFile', 'music', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print(listParam)
            print("COMMAND: mergeAudio -> param format invalid")
            print("['mergeAudio', 'videoFile', 'audioFile', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.mergeAudio(listParam[2])
        result = ffmpegManger.run()
        return result

    def addMusic(self, listParam):
        """
        handle : ['addMusic', 'videoFile', 'music', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print(listParam)
            print("COMMAND: addMusic -> param format invalid")
            print("['addMusic', 'videoFile', 'music', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.addMusic(listParam[2])
        result = ffmpegManger.run()
        return result

    def transVideoRate(self, listParam):
        """
        handle : ['transVideoRate', 'videoFile', 'outFile']
        """
        # check Param
        if len(listParam) != 3:
            print(listParam)
            print("COMMAND: transVideoRate -> param format invalid")
            print("['transVideoRate', 'videoFile', outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.transVideoRate('1.6M')
        result = ffmpegManger.run()
        return result    

    def addMergeMusic(self, listParam):
        """
        handle : ['addMergeMusic', 'videoFile', 'music', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print(listParam)
            print("COMMAND: addMergeMusic -> param format invalid")
            print("['addMergeMusic', 'videoFile', 'music', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.addMergeMusic(listParam[2])
        result = ffmpegManger.run()
        return result

    def splitAudio(self, listParam):
        """
        handle : ['splitAudio', 'videoFile', 'outFile']
        """
        # check Param
        if len(listParam) != 3:
            print(listParam)
            print("COMMAND: splitAudio -> param format invalid")
            print("['splitAudio', 'videoFile', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.splitAudio()
        result = ffmpegManger.run()
        return result

    def addNullAudio(self, listParam):
        """
        handle : ['addNullAudio', 'videoFile', 'nullFile', 'outFile']
        """
        # check Param
        if len(listParam) != 4:
            print(listParam)
            print("COMMAND: addNullAudio -> param format invalid")
            print("['addNullAudio', 'videoFile', 'nullFile', 'outFile']")
            return 1

        # handle
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.addNullAudio(listParam[2])
        result = ffmpegManger.run()
        return result

    def videoToGif(self, listParam):
        """
        handle : ['videoToGif', 'videoFile', 'outFile']
        """
        # check Param
        if len(listParam) != 3:
            print(listParam)
            print("COMMAND: videoToGif -> param format invalid")
            print("['videoToGif', 'videoFile', 'outFile']")
            return 1

        # remove temp Palett file
        if os.path.exists("tmpPalett.png"):
            os.remove("tmpPalett.png")

        # step 1 -> palettegen
        ffmpegManger = FFMpegFactory(listParam[1], 'tmpPalett.png')
        ffmpegManger.palettegen()
        result = ffmpegManger.run()


        # step 2 -> paletteuse
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.paletteuse('tmpPalett.png')
        result = ffmpegManger.run()
        return result

    def rmShaky(self, listParam):
        """
        handle : ['rmShaky', 'videoFile', 'outFile']
        """
        # check Param
        if len(listParam) != 3:
            print(listParam)
            print("COMMAND: rmShaky -> param format invalid")
            print("['rmShaky', 'videoFile', 'outFile']")
            return  1

        # step 1 -> vidstabdetect
        ffmpegManger = FFMpegFactory(listParam[1], '-')
        ffmpegManger.vidstabdetect()
        result = ffmpegManger.run()


        # step 2 -> vidstabtransform
        ffmpegManger = FFMpegFactory(listParam[1], listParam[-1])
        ffmpegManger.vidstabtransform()
        result = ffmpegManger.run()
        return result

    def handleCmd(self, listParam):
        if not len(listParam):
            print("cmd error")
            return 1

        # counter time
        self.timerCounter.begin()

        # handle 
        print(listParam)
        result = eval("self."+listParam[0])(listParam)
        print('command handle result is :', result)

        # counter time
        self.timerCounter.end()
        print("%s spend %s s" % (listParam[0], self.timerCounter.diff()))
        return result

    def run(self):
        # handle = ['cut', 'demo.mp4', '00:00:05', '5', 'output.mp4']
        # self.videoCut(handle)

        # handle = ['mute', 'demo.mp4', 'output.mp4']
        # self.audioMute(handle)

        # handle = ['merge', 'demo1.mp4', 'demo2.mp4', 'demo2.mp4', 'outFile.mp4']
        # self.videoMerge(handle)

        # handle = ['toimg', 'demo.mp4', '00:00:05', 'outFile.png']
        # self.videoToImg(handle)

        # handle = ['imgToVideo', 'outFile.png', '00:00:05', 'output.mp4']
        # self.imgToVideo(handle)

        # handle = ['videoOnImg', 'outFile.png', 'demo.mp4', 'output.mp4']
        # self.PIP_videoOnImg(handle)

        # handle = ['videoLogo', 'demo.mp4', 'logo.png', '20:20', 'output.mp4']
        # self.videoLogo(handle)

        handle = ['videoSpeed', 'demo.mp4', '2', 'output.mp4']
        self.videoSpeed(handle)

def main():
    editor = VideoAutoEditor()
    editor.run()
        
if __name__ == '__main__':
    main()