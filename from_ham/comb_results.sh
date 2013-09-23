#CLEAN UP
rm out.csv

echo 'alp_q0_f0_l0, alp_q0_f1_l0, gam_q0_f0_l0, gam_q0_f1_l0, bet_q0_f0_l0, bet_q0_f1_l0, field_co, lat_co, qual_co, lo, p, lat_prob1, lat_prob2, ip' >> out.csv

for f in out_2*.csv
do
  LINENO=`wc -l "$f" | cut --delimiter=' ' -f 1`
  HALF=$(( LINENO / 2 ))
  echo $HALF
  tail --lines=$HALF "$f" >> out.csv
done
