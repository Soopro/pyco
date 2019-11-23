echo 'Stoping'

ID1=`ps -ef | grep "pyco" | grep -v "grep" | awk '{print $2}'`
ID2=`ps -ef | grep "pyco_admin" | grep -v "grep" | awk '{print $2}'`

for id in $ID1
do
kill -9 $id
echo 'killed pyco.py at' $id
done

for id in $ID2
do
kill -9 $id
echo 'killed pyco_admin.py at' $id
done

echo 'Starting'
nohup python3 pyco.py >> out.log &
nohup python3 pyco_admin.py >> out.log &