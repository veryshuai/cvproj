rm spread.csv

echo 'cf0,cf1,cf2,cf3,cf4,cf5,cf6,df0,df1,df2,df3,df4,df5,df6,sd0,sd1,sd2,sd3,sd4,sd5,sd6' >> spread.csv

for f in sp_2*.csv
do
  LINENO=`wc -l "$f" | cut --delimiter=' ' -f 1`
  HALF=$(( LINENO / 1 ))
  echo $HALF
  tail --lines=$HALF "$f" >> spread.csv
done
