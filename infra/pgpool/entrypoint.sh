#!/bin/sh
set -eu
umask 077; : > /tmp/pool_passwd
for pair in 'bovi_app_a:app_a_password' 'bovi_app_b:app_b_password' 'bovi_repl:repl_password' 'bovi_worker:worker_password'; do
 role=${pair%%:*}; secret=${pair#*:}
 printf '%s:TEXT%s\n' "$role" "$(cat /run/secrets/$secret)" >> /tmp/pool_passwd
done
chmod 600 /tmp/pool_passwd
exec pgpool -n -f /etc/pgpool2/pgpool.conf -a /etc/pgpool2/pool_hba.conf
