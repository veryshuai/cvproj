#CLEAN UP
rm out.csv

echo 'alp_q0_f0_l0, alp_q0_f1_l0, alp_q0_f1_l1, alp_q1_f0_l0, alp_q1_f1_l0, alp_q1_f1_l1, alp_q2_f0_l0, alp_q2_f1_l0, alp_q2_f1_l1, gam_q0_f0_l0, gam_q0_f1_l0, gam_q0_f1_l1, gam_q1_f0_l0, gam_q1_f1_l0, gam_q1_f1_l1, gam_q2_f0_l0, gam_q2_f1_l0, gam_q2_f1_l1, bet, field_co, lat_co, qual_co, lo, p, lat_prob' >> out.csv

for f in out_2*.csv
do
  LINENO=`wc -l "$f" | cut --delimiter=' ' -f 1`
  HALF=$(( LINENO / 2 ))
  echo $HALF
  tail --lines=$HALF "$f" >> out.csv
done
