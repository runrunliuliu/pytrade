echo '1day,9cyb,11sz,12z5,13d5,14ztb,17cje5,18hgt,19rz,20rzb,21rz5gd,22rz5pm,23zl,24jjd,27yh,28zlb,29zl5pm,34z5dj,35z5dj,36z5djts,37z5djpm,38z5djfd,39z5djdf,40rzzl'

cat dapan_20161122.txt | awk -F"," '{print $1","$9","$11","$12 /($10 + 0.0000001)","$13/($10 + 0.000001)","$14","$17","$18","$19","$20","$21","$22","$23","$24","$27","$28","$29","$34","$35","$36","$37","$38","$39","$19/($23+0.0000001)}'
