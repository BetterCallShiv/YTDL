#!/bin/bash
# Coded By Shivam Raj
# https://github.com/BetterCallShiv

#######################
boldred="\033[1;31m"
boldgreen="\033[1;32m"
boldblue="\033[1;34m"
boldmagenta="\033[1;38;5;4m"
boldcyan="\033[1;36m"
boldyellow="\033[1;33m"
light_cyan="\033[0;96m"
color1="\033[1;38;5;51m"
color2="\033[1;38;5;112m"
color3="\033[1;38;5;47m"
#######################

# Run this once IMPORTANT
# python3 -m pip install -U https://github.com/bindestriche/srt_fix/archive/refs/heads/master.zip
# Dependencies ffmpeg wget yt-dlp

clear
echo -e "${boldgreen}"
echo "██╗   ██╗████████╗██████╗ ██╗     "
echo "╚██╗ ██╔╝╚══██╔══╝██╔══██╗██║     "
echo " ╚████╔╝    ██║   ██║  ██║██║     "
echo "  ╚██╔╝     ██║   ██║  ██║██║     "
echo "   ██║      ██║   ██████╔╝███████╗"
echo "   ╚═╝      ╚═╝   ╚═════╝ ╚══════╝"
echo -e "${boldcyan}         YouTube Downloader v1.0"
echo -e "${boldyellow}         By Shivam Raj"
echo -e "${boldmagenta}         github.com/BetterCallShiv"
echo


mkdir ytdl &> /dev/null;
cd ytdl
wget https://github.com/BetterCallShiv/YTDL/raw/refs/heads/main/Montara%20Gothic.ttf &> /dev/null;
extension="mkv"

read -p $'\e[1;4;38;5;147mPaste YouTube Link:\e[0m ' input
if [[ $input =~ playlist ]]; then
    read -p $'\e[1;4;38;5;211mSelect Playlist Video Quality (144, 240, 360, 480, 720, 1080, 1440, 2160, best):\e[0m ' quality
    if [[ ! "$quality" =~ ^(144|240|360|480|720|1080|1440|2160|best)$ ]]; then
        echo -e "${boldred}Error Please Select A Valid Quality."
        exit
    fi
    echo -e "${color3}Downloading Playlist..."
    start=`date +%s`
    if [[ "$quality" == "best" ]]; then
        yt-dlp -q --progress --add-metadata --write-thumbnail --convert-thumbnails jpg -f "bestvideo+bestaudio" --write-sub --write-auto-sub --sub-lang "en" --convert-subs srt --use-postprocessor srt_fix --merge-output-format $extension -o "%(playlist_index)s - %(title)s.%(ext)s" $input
    else
    yt-dlp -q --progress --add-metadata --write-thumbnail --convert-thumbnails jpg -f "bestvideo[height<=$quality]+bestaudio/best[height<=$quality]" --write-sub --write-auto-sub --sub-lang "en" --convert-subs srt --use-postprocessor srt_fix --merge-output-format $extension -o "%(playlist_index)s - %(title)s.%(ext)s" $input
    fi
    if ls -1 *.srt &> /dev/null; then
        echo -e "${color2}Merging Video & Subtitles..."
    fi
    for f in *.$extension ; do
        base_name="${f%.*}"
        ffmpeg -i "${base_name}.en-fixed.srt" "${base_name}.ass" &> /dev/null;
    done
    for subtitle in *.ass ; do
        [[ -f "$subtitle" ]] && sed -i 's/Default,Arial,16/Default,Montara Gothic,20/' "$subtitle" &> /dev/null;
    done
    for f in *.$extension ; do
        base_name="${f%.*}"
        mv "${base_name}.jpg" cover.jpg &> /dev/null ; ffmpeg -i "${f}" -i "${base_name}.ass" -attach "cover.jpg" -metadata:s:t:0 mimetype=image/jpeg -attach "Montara Gothic.ttf" -metadata:s:t:1 mimetype=application/x-truetype-font -c copy -c:s ass -disposition:s:0 default -metadata:s:s:0 title="YouTube En Subs ∫ YTDL v1.0 BY BetterCallShiv" -metadata DOWNLOADED_USING_YTDL="https://github.com/BetterCallShiv/YTDL" "${base_name}_SUB.$extension" &> /dev/null;
    done
    for file in *"_SUB.mkv"; do
        mv -f "$file" "${file/_SUB/}" &> /dev/null;
    done
    if ls -1 *.srt &> /dev/null; then
        find . -type f ! -name "*.mkv" -exec rm {} \; &> /dev/null;
    fi
    mv * .. &> /dev/null;
    end=`date +%s`
    runtime=$((end-start))
    hours=$((runtime / 3600))
    minutes=$(( (runtime % 3600) / 60 ))
    seconds=$(( (runtime % 3600) % 60 ))
    echo -e "${color1}[✓] Finished Downloading in ${hours}h${minutes}m${seconds}s$color1"

else
    read -p $'\e[1;4;38;5;211mSelect Video Quality (144, 240, 360, 480, 720, 1080, 1440, 2160, best):\e[0m ' quality
    if [[ ! "$quality" =~ ^(144|240|360|480|720|1080|1440|2160|best)$ ]]; then
        echo -e "${boldred}Error Please Select A Valid Quality."
        exit
    fi
    echo -e "${color3}Downloading Video..."
    start=`date +%s`
    if [[ "$quality" == "best" ]]; then
        yt-dlp -q --progress --add-metadata --write-thumbnail --convert-thumbnails jpg -f "bestvideo+bestaudio" --write-sub --write-auto-sub --sub-lang "en" --convert-subs srt --use-postprocessor srt_fix --merge-output-format $extension -o "%(title)s.%(ext)s" $input
    else
    yt-dlp -q --progress --add-metadata --write-thumbnail --convert-thumbnails jpg -f "bestvideo[height<=$quality]+bestaudio/best[height<=$quality]" --write-sub --write-auto-sub --sub-lang "en" --convert-subs srt --use-postprocessor srt_fix --merge-output-format $extension -o "%(title)s.%(ext)s" $input
    fi
    if ls -1 *.srt &> /dev/null; then
        echo -e "${color2}Merging Video & Subtitles..."
    fi
    for f in *.$extension ; do
        base_name="${f%.*}"
        ffmpeg -i "${base_name}.en-fixed.srt" "${base_name}.ass" &> /dev/null;
    done
    for subtitle in *.ass ; do
        [[ -f "$subtitle" ]] && sed -i 's/Default,Arial,16/Default,Montara Gothic,20/' "$subtitle" &> /dev/null;
    done
    for f in *.$extension ; do
        base_name="${f%.*}"
        mv "${base_name}.jpg" cover.jpg &> /dev/null ; ffmpeg -i "${f}" -i "${base_name}.ass" -attach "cover.jpg" -metadata:s:t:0 mimetype=image/jpeg -attach "Montara Gothic.ttf" -metadata:s:t:1 mimetype=application/x-truetype-font -c copy -c:s ass -disposition:s:0 default -metadata:s:s:0 title="YouTube En Subs ∫ YTDL v1.0 BY BetterCallShiv" -metadata DOWNLOADED_USING_YTDL="https://github.com/BetterCallShiv/YTDL" "${base_name}_SUB.$extension" &> /dev/null;
    done
    for file in *"_SUB.mkv"; do
        mv -f "$file" "${file/_SUB/}" &> /dev/null;
    done
    if ls -1 *.srt &> /dev/null; then
        find . -type f ! -name "*.mkv" -exec rm {} \; &> /dev/null;
    fi
    mv * .. &> /dev/null;
    end=`date +%s`
    runtime=$((end-start))
    hours=$((runtime / 3600))
    minutes=$(( (runtime % 3600) / 60 ))
    seconds=$(( (runtime % 3600) % 60 ))
    echo -e "${color1}[✓] Finished Downloading in ${hours}h${minutes}m${seconds}s$color1"
fi

