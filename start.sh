echo 'Pyco Admin Stoping'

IDS_ADMIN=`ps -ef | grep "pyco_admin.py" | grep -v "grep" | awk '{print $2}'`
for admin_id in $IDS_ADMIN
do
kill -9 $admin_id
echo 'killed pyco_admin.py at' $admin_id
done

echo 'Pyco Stoping'

IDS=`ps -ef | grep "pyco.py" | grep -v "grep" | awk '{print $2}'`
for id in $IDS
do
kill -9 $id
echo 'killed pyco.py at' $id
done

echo 'Starting'
nohup python3 pyco.py >> out.log &
nohup python3 pyco_admin.py >> out.log &