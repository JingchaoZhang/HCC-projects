#!/bin/bash

time=`date --date='1 week ago' +%Y-%m-%d`
echo "$time to `date +%Y-%m-%d`"

sacct -r batch -S $time -P -o JobID,State,User,Group,Submit,Start,End,Timelimit,ReqMem,MaxRSS,MaxVMSize,ReqCPUS,AllocCPUS,CPUTimeRAW > 1.tmp
sed '/nfsnobody/d' 1.tmp > 2.tmp
sed -n '/COMPLETED/p' 2.tmp > COMPLETED
#sed -n '/PENDING/p' 2.tmp > PENDING
#sed -n '/RUNNING/p' 2.tmp > RUNNING
rm 1.tmp 2.tmp

while read line
do
    submit_time=$(date +%s -d "`echo $line | cut -d "|" -f 5`")
    start_time=$(date +%s -d "`echo $line | cut -d "|" -f 6`")
    wait_time=$(($start_time-$submit_time))
    run_time=$((`echo $line | cut -d "|" -f 14`/`echo $line | cut -d "|" -f 13`))
    ratio=$(echo "scale=5; $run_time/$wait_time" | bc 2> /dev/null)
    echo $ratio"|"$run_time"|"$wait_time"|"$line >> ratio.tmp
    echo $run_time $wait_time >> plot.tmp
done < COMPLETED

sed '/|0|/d' ratio.tmp > ratio.txt
rm ratio.tmp
file1=sorted.txt
[[ "${#file2[@]}" -gt 0 ]] && rm sorted.txt 2> /dev/null
cat ratio.txt | sort -t "|" -k 1 -g > sorted.tmp
sed '1i\Ratio|Run Time(s)|Wait Time(s)|JobID|State|User|Group|Submit|Start|End|Timelimit|ReqMem|MaxRSS|MaxVMSize|ReqCPUS|AllocCPUS|CPUTimeRAW' sorted.tmp > sorted.txt
rm ratio.txt sorted.tmp
echo "Final results is generated in file \"sorted.txt\""

cat plot.tmp | awk '{printf $1/86400" "$2/86400"\n"}' > plot.txt
gnuplot 2> /dev/null << EOF
set terminal png
set size square
set output 'plot.png'
set xlabel 'Run Time (day)'
set ylabel 'Wait Time (day)'
set xrange [-1:8]
set yrange [-1:8]
set title 'Tusker job accounting from $time to `date +%Y-%m-%d`'
set grid
plot "plot.txt"
EOF
rm plot.tmp plot.txt
echo "A plot is generated in file \"plot.png\""
rm COMPLETED
