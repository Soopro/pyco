echo 'Stoping'
ID1=`ps -ef | grep "pyco" | grep -v "grep" | awk '{print $2}'`
for id in $ID1
do
kill -9 $id
echo 'killed pyco.py at' $id
done

echo 'Starting'
nohup python pyco.py >> out.log &