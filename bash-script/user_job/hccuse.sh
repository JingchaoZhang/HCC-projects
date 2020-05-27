#!/bin/bash
rm time.job time.user 2> /dev/null

#Set up a time to trace back
days=90
time=`date --date="$days day ago" +%Y-%m-%d`

#Loop through group names and find users
while read group
do
rm time.user 2> /dev/null
ls /home/$group > user.list
#Analyze job per user
while read user
do
rm time.job 2> /dev/null
echo $user
sacct -u $user -S $time -P -o JobID,CPUTimeRAW | sed '/batch/d' | while read line
do
echo $line | cut -d "|" -f 2 >> time.job
done
sed -i '1d' time.job
v1=`paste -sd+ time.job | bc` 2> /dev/null
v2=$(echo "scale=3; $v1/3600" | bc) 2> /dev/null
printf "%s %s \n" $user $v2 >> time.user
done < "user.list"
v3=`cat time.user | sort -t ' ' -k 2 -n | tail -n 1`
printf "%s %s \n" $group $v3 >> time.group
done < "group.list"
exit

#while read user
#do

#sacct -u $user -S $time -s CD -P -o JobID,CPUTimeRAW | sed '/batch/d' | 
#while read line
#do
#time="`echo $line | cut -d "|" -f 2`" >> time.job
#done

#paste -sd+ time.txt | bc >> time.user
#v2=$(echo "scale=3; $v1/3600" | bc) 2> /dev/null
#printf "%s %s \n" $user $v2 >> temp2 2> /dev/null
#done < "user.list"


#cat temp2 | sort -t '|' -k 2 -n 2> /dev/null
