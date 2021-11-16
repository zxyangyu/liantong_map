#!/bin/bash
# excute ./filename.sh 20210830 10.7.19.19:27019/oss_lbs xingyuan kdHyjU3

if [ $# != 4 ] ; then
echo "pls input paramter"
exit 1
fi

workdir=$(cd $(dirname $0); pwd)

begintime=$1
oss_lbs_path=$2
oss_lbs_user=$3
oss_lbs_password=$4

user_file="user_${begintime}.txt"
querys_js="querys_js_${begintime}.js"
result_json="result_json_${begintime}.json"
rm_date=`date -d "${begintime} 28 days ago" '+%Y%m%d'`
#oss_lbs隐藏节点配置
#oss_lbs_slave="mongo 10.7.19.19:27019/oss_lbs -u xingyuan -p kdHyjU3"
oss_lbs_slave="mongo ${oss_lbs_path} -u ${oss_lbs_user} -p ${oss_lbs_password}"

# 判断用户文件是否存在 读取文件 解析文件
if [ ! -f "$user_file" ]; then
    echo "pls check userfile"
    exit 1
fi
rm ${querys_js}
echo "start generate query js file ${querys_js}"
sed -i "s/[[:space:]]//g" $user_file
for line in `cat $user_file`;
do 
#if [[ $line == *",,"* ]] || [[ $line == *"null"* ]]; then
#continue
#fi
array=(${line//;/ })
FLOWSIZE=${array[0]} 
IMEI=${array[1]}
MCC=${array[2]}
MNC=${array[3]}
CELLID=${array[4]}
LAC=${array[5]}
PROVINCE=${array[6]}
CITY=${array[7]}
UCC=${array[8]}
#if [[ ! -n "$MCC" ]] || [[ ! -n "$MNC" ]] || [[ ! -n "$CELLID" ]] || [[ ! -n "$LAC" ]]; then
#continue
#fi
joinSql="var a=0;db.getCollection(\"cellLocation\").aggregate([{\$match :{cellId:${CELLID},lac:${LAC},mcc:\"${MCC}\",mnc:\"${MNC}\"} },{ \$project: {_id:0,cellId:1,lac:1,mcc:1,mnc:1,lat:1,lng:1,iso2:1,flowsize:{\$literal:\"${FLOWSIZE}\"},province:{\$literal:\"${PROVINCE}\"},city:{\$literal:\"${CITY}\"},imei:{\$literal:\"${IMEI}\"},ucc_count:{\$literal:\"${UCC}\"} } }]).forEach(function(e){a++;printjson(e)});if (a== 0) {printjson({\"cellId\":${CELLID},\"lac\":${LAC},\"mcc\":\"${MCC}\",\"mnc\":\"${MNC}\",\"flowsize\":\"${FLOWSIZE}\",\"province\":\"${PROVINCE}\",\"city\":\"${CITY}\",\"imei\":\"${IMEI}\",\"ucc_count\":\"${UCC}\"})}"


echo $joinSql  >> ${querys_js}
#echo "$oss_lbs_slave --quiet --eval "$joinSql""
#`$oss_lbs_slave --quiet --eval "$joinSql" >> ./test_2.json`
done
sed -i "s/\r//g" ${querys_js}
split -l 10000 -d -a 2 ${querys_js} ${querys_js//.js/_}
rm ${result_json}
echo "[" > ${result_json}
for file in `ls|grep ${querys_js//.js/_}|xargs -n1`;
do
sed -i '1 i\rs.slaveOk();' ${file}
$oss_lbs_slave --quiet ${file} >> ${result_json}
if [ $? -ne 0 ]; then
    echo "${file} failure"
    exit 1
else
    echo "${file} finish"
fi
done 
sed -i 's/}/},/g' ${result_json}
sed -i '$d' ${result_json}
echo "}]" >> ${result_json}
rm ${querys_js//.js/_}*
rm ${querys_js}
#zip ${result_json}.zip ${result_json}
#zip ${querys_js}.zip ${querys_js}
#rm ${result_json}
#rm ${querys_js}
#sz ${result_json}.zip
#sz ${querys_js}.zip

python3 processor.py ${begintime}
if [ $? -ne 0 ]; then
    echo "data process failure"
    exit 1
else
    echo "data process success"
fi

str=`find ../html -name \*.html`  # 会产生一个列表
file=" $str "   # 需要在列表前后加空格，在shell中，列表或数组的括号前后必须是空格
for i in $file
do
mv $i ${i%%_*}_${begintime}.html
done

rm report_${begintime}.zip
html_path=$(dirname $workdir)/html

zip -r -q report_${begintime}.zip ../html
python3 send_mail.py ${begintime}
if [ $? -ne 0 ]; then
    exit 1
else
    echo "email success"
fi
rm ./*_${rm_date}*

exit 0
