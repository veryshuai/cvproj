#CLEAN UP
rm out.csv

echo 'alp0, alp1, gam0, gam1, bet0, bet1, field_co, lat_co, qual_co, lo, p, lat_prob1, lat_prob2, lat_prob3, ip' >> out.csv

for f in out_2*
do
  LINENO=`wc -l "$f" | cut --delimiter=' ' -f 1`
  HALF=$(( LINENO / 2 ))
  echo $HALF
  tail --lines=$HALF "$f" >> out.csv
  # tail --lines=100 "$f" >> out.csv
done
