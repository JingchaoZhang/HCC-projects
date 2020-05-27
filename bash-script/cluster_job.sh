#!/bin/bash

#Set default and help message
days=7

usage()
{
cat << EOF
usage: $0 [-hud]

This script generates a png file and a txt file.

OPTIONS:
-h      Show this message
-d      Number of days to trace back	(default is 7)
EOF
}

while getopts :h:d:u: OPTION
do
	case $OPTION in
		h)
			usage
			exit 1
			;;
		d)
			days=$OPTARG
			;;
		?)
			usage
			exit
			;;
	esac
done
time=`date --date="$days day ago" +%Y-%m-%d`
echo "$time to `date +%Y-%m-%d`"

# s2time () $Time_in_s
s2time () {
if [[ $1 -ge 86400 ]]; then
	day=$(echo "scale=0; $1/86400" | bc)
	residue1=$(echo "$1-$day*86400" | bc)
	if [[ $residue1 -ge 3600 ]]; then
		hour=$(echo "scale=0; $residue1/3600" | bc)
	else
		hour="00"
	fi
	residue2=$(echo "$residue1-$hour*3600" | bc)
	if [[ $residue2 -ge 60 ]]; then
		min=$(echo "scale=0; $residue2/60" | bc)
	else
		min="00"
	fi
	second=$(echo "$residue2-$min*60" | bc)
	printf "%02d-%02d:%02d:%02d\n" $day $hour $min $second
elif [[ "$1 -lt 86400" && "$1 -ge 3600" ]]; then
	hour=$(echo "scale=0; $1/3600" | bc)
	residue1=$(echo "$1-$hour*3600" | bc)
	if [[ $residue1 -ge 60 ]]; then
		min=$(echo "scale=0; $residue1/60" | bc)
	else
		min="00"
	fi
	second=$(echo "$residue1-$min*60" | bc)
	printf "%02d:%02d:%02d\n" $hour $min $second
elif [[ "$1 -lt 3600" && "$1 -ge 60" ]]; then
	hour="00"
	min=$(echo "scale=0; $1/60" | bc)
	second=$(echo "$1-$min*60" | bc)
	printf "%02d:%02d:%02d\n" $hour $min $second
else
	hour="00"
	min="00"
	second="$1"
	printf "%02d:%02d:%02d\n" $hour $min $second
fi
}
#Delete previous files if exist
rm ratio.tmp plot.tmp JobTime 2> /dev/null
file1=sorted.txt; [[ "${#file1[@]}" -gt 0 ]] && rm sorted.txt 2> /dev/null
file2=plot.png; [[ "${#file2[@]}" -gt 0 ]] && rm plot.png 2> /dev/null

#Qurey Sacct
sacct -r batch -s CD -S $time -P -o JobID,User,Group,Submit,Start,End,Timelimit,ReqMem,MaxRSS,AllocCPUS,CPUTimeRAW | sed '/nfsnobody/d' | sed '/JobID/d' | while read line
do
    submit_time=$(date +%s -d "`echo $line | cut -d "|" -f 4`")				#Submit
    start_time=$(date +%s -d "`echo $line | cut -d "|" -f 5`")				#Start
    wait_time=$(($start_time-$submit_time))
    run_time=$((`echo $line | cut -d "|" -f 11`/`echo $line | cut -d "|" -f 10`))	#CPUTimeRAW / AllocCPUS
    wait_h=`s2time $wait_time`
    run_h=`s2time $run_time`
    ratio=$(echo "scale=5; $run_time/$wait_time" | bc 2> /dev/null)
    echo $ratio"|"$run_h"|"$wait_h"|"$line >> ratio.tmp
    echo $run_time $wait_time >> plot.tmp
done

sed '/|00:00:00|/d' ratio.tmp | sort -t "|" -k 1 -g | sed '1i\Ratio|Run Time|Wait Time|JobID|User|Group|Submit|Start|End|Timelimit|ReqMem|MaxRSS|AllocCPUS|CPUTimeRAW(s)' > sorted.txt

#Drawing the plot
cat plot.tmp | awk '{printf $1/86400" "$2/86400"\n"}' > JobTime
gnuplot 2> /dev/null << EOF
set terminal png
set size square
set output 'plot.png'
set xlabel 'Run Time (day)'
set ylabel 'Wait Time (day)'
set xrange [-1:8]
set yrange [-1:8]
set title 'Crane job accounting from $time to `date +%Y-%m-%d`'
set grid
plot "JobTime"
EOF
rm ratio.tmp plot.tmp JobTime 2> /dev/null
echo "Generated file \"sorted.txt\", \"plot.png\""
