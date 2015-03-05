rm spread0.csv
rm spread1.csv
rm spread2.csv

echo 'cf0,cf1,cf2,cf3,cf4,cf5,cf6,cf7,cf8,cf9,cf10,cf11,cf12,df0,df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,sd0,sd1,sd2,sd3,sd4,sd5,sd6,sd7,sd8,sd9,sd10,sd11,sd12,cv0,cv1,cv2,cv3,cv4,cv5,cv6,cv7,cv8,cv9,cv10,cv11,cv12' >> spread0.csv
echo 'cf0,cf1,cf2,cf3,cf4,cf5,cf6,cf7,cf8,cf9,cf10,cf11,cf12,df0,df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,sd0,sd1,sd2,sd3,sd4,sd5,sd6,sd7,sd8,sd9,sd10,sd11,sd12,cv0,cv1,cv2,cv3,cv4,cv5,cv6,cv7,cv8,cv9,cv10,cv11,cv12' >> spread1.csv
echo 'cf0,cf1,cf2,cf3,cf4,cf5,cf6,cf7,cf8,cf9,cf10,cf11,cf12,df0,df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,sd0,sd1,sd2,sd3,sd4,sd5,sd6,sd7,sd8,sd9,sd10,sd11,sd12,cv0,cv1,cv2,cv3,cv4,cv5,cv6,cv7,cv8,cv9,cv10,cv11,cv12' >> spread2.csv

for f in sp0_2*.csv
do
  LINENO=`wc -l "$f" | cut --delimiter=' ' -f 1`
  HALF=$(( LINENO / 1 ))
  echo $HALF
  tail --lines=$HALF "$f" >> spread0.csv
done
for f in sp05_2*.csv
do
  LINENO=`wc -l "$f" | cut --delimiter=' ' -f 1`
  HALF=$(( LINENO / 1 ))
  echo $HALF
  tail --lines=$HALF "$f" >> spread1.csv
done
for f in sp10_2*.csv
do
  LINENO=`wc -l "$f" | cut --delimiter=' ' -f 1`
  HALF=$(( LINENO / 1 ))
  echo $HALF
  tail --lines=$HALF "$f" >> spread2.csv
done
