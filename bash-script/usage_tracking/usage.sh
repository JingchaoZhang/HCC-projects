#!/bin/bash

printf 'Use default time? y/n \n'; read ans

if [ "$ans" = "n" ]
then
	printf 'end date "mm/dd/yy":\n';read endtime
	printf 'month period?\n';read period
else
	endtime=`date +'%D'`
	period=6
fi

weeknum=$((period*4))
starttime=`date --date="$endtime -$weeknum week" +'%D'`
printf "Statistics from $starttime to $endtime ... (~$period month period)\n"

while read user
do 

printf "user found: $user ..."
endtemp=`date --date="$starttime" +'%D'`
i=1
until [ $i -gt $weeknum ]
do
	starttemp=`date --date="$endtemp" +'%D'`
	endtemp=`date --date="$starttemp +1 week" +'%D'`
	sacct -u $user -S $starttemp -E $endtemp --format=cputimeraw,User | grep $user >> data_$i.dat
	sum=`awk '{x += $1} END {print (x+0)/3600}' < data_$i.dat `
	isgreater=`echo "$sum > 0" | bc`
	if [ "$isgreater" -eq 1 ]
	then 
		plot=yes
	fi
	echo $i $sum >> data_sum.dat
	i=$((i+1))
done 

if [ "$plot" = "yes" ]
then
printf ' usage plot\n'
cat << End_plot | gnuplot
set terminal postscript color
set output '| ps2pdf - plot_$user.pdf'
set logscale y
set xlabel 'Time (week)'
set ylabel 'Total CPU Time (hour)'
set title 'Usage Statistics ($starttime - $endtime)'
set grid
plot 'data_sum.dat' using 1:2 with linespoints pt 7 lc rgb 'red' title '$user'
End_plot
else 
	printf ' no usage in this period\n'
fi

plot=no
rm *.dat

done < "userlist.txt"

exit 0