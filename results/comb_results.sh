#CLEAN UP
rm out.csv

echo 'alp, gam0, gam1, bet, field_co, lat_co, qual_co, lo1, lo2, p, lat_prob1, lat_prob2, lat_prob3, ip' >> out.csv

for f in out_2*.csv
do
  LINENO=`wc -l "$f" | cut --delimiter=' ' -f 1`
  HALF=$(( LINENO / 2 ))
  echo $HALF
  tail --lines=$HALF "$f" >> out.csv
done
