PropFile=$1
StrtDate=$2
End_Date=$3

if [ "X$PropFile" = "X" ];then
   echo "The propertyfilename is required"
   echo "Usage: Scriptname propfile "
   echo "Usage: Scriptname propfile Startdate enddate"
   exit 1
fi

echo "Activity report Script started at `date`"
dropBox_Script=`grep dropBox_Script= $PropFile |cut -d'=' -f2`


ActityReport=`grep ^garageActivityReport_Generatd= $PropFile |cut -d'=' -f2`
Cloud_Report=`grep ^garageActivityCloudReportName= $PropFile |cut -d'=' -f2`


# Generate report
python3 activityreport.py $PropFile $StrtDate $End_Date

echo "Uploading report to Dropbox"
uploadScript="$dropBox_Script  upload "
uploadCmd="$uploadScript  $ActityReport $Cloud_Report"

$uploadCmd
echo "Activity report completed started at `date`"



