echo 'Pyco Status'

IDS=`ps -ef | grep "pyco.py" | grep -v "grep" | awk '{print $2}'`
for id in $IDS
do
echo 'run pyco.py at' $id
done

echo 'Pyco Admin Status'

IDS_ADMIN=`ps -ef | grep "pyco_admin.py" | grep -v "grep" | awk '{print $2}'`
for admin_id in $IDS_ADMIN
do
echo 'run pyco_admin.py at' $admin_id
done
