set -e
C=../clips
seg(){ # idx file start dur speed
  echo "[$1:v]trim=start=$3:duration=$4,setpts=(PTS-STARTPTS)/$5,scale=1280:720:flags=lanczos,setsar=1,fps=24,format=yuv420p[v$1];"
}
F=""
F+=$(seg 0 x 0.3 6.0 1.3)
F+=$(seg 1 x 1.6 2.4 1)
F+=$(seg 2 x 1.0 2.0 1)
F+=$(seg 3 x 1.5 1.5 1)
F+=$(seg 4 x 1.5 1.5 1)
F+=$(seg 5 x 1.5 1.5 1)
F+=$(seg 6 x 0.0 5.0 1)
F+="[v0][v1][v2][v3][v4][v5][v6]concat=n=7:v=1:a=0[out]"
ffmpeg -y -v error -i $C/van_scene.mp4 -i $C/box_open.mp4 -i $C/robot_01.mp4 -i $C/robot_02b.mp4 -i $C/robot_04.mp4 -i $C/robot_06.mp4 -i ../logo/aerial_logo8.mp4 \
 -filter_complex "$F" -map "[out]" -c:v libx264 -crf 15 -preset slow -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 silent_v3.mp4
ffprobe -v error -show_entries stream=width,height,r_frame_rate,duration,nb_frames -of csv=p=0 silent_v3.mp4
