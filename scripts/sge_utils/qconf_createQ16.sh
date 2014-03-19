#!/bin/bash 

# Create a new Q with this name
outQname=ngs.q


# Write a Q configuration file
cat <<'EOF' > ${outQname}
qname                 ngs.q
hostlist              @allnodes
seq_no                0
load_thresholds       np_load_avg=1.75
suspend_thresholds    NONE
nsuspend              1
suspend_interval      00:05:00
priority              0
min_cpu_interval      00:05:00
processors            UNDEFINED
qtype                 BATCH INTERACTIVE
ckpt_list             NONE
pe_list               make orte
rerun                 FALSE
EOF

echo -n "slots                 1," >> ${outQname}
cat /etc/hosts | grep node0 | cut -f 2 -d " " | tr '\n' ' ' | sed -e 's/\b\(\w\+\)\b/[\1=16],/g' -e 's/, $//' >> ${outQname}
echo "" >> ${outQname}

cat <<'EOF' >> ${outQname}
tmpdir                /tmp
shell                 /bin/bash
prolog                NONE
epilog                NONE
shell_start_mode      posix_compliant
starter_method        NONE
suspend_method        NONE
resume_method         NONE
terminate_method      NONE
notify                00:00:60
owner_list            NONE
user_lists            NONE
xuser_lists           NONE
subordinate_list      NONE
complex_values        NONE
projects              NONE
xprojects             NONE
calendar              NONE
initial_state         default
s_rt                  INFINITY
h_rt                  INFINITY
s_cpu                 INFINITY
h_cpu                 INFINITY
s_fsize               INFINITY
h_fsize               INFINITY
s_data                INFINITY
h_data                INFINITY
s_stack               INFINITY
h_stack               INFINITY
s_core                INFINITY
h_core                INFINITY
s_rss                 INFINITY
h_rss                 INFINITY
s_vmem                INFINITY
h_vmem                INFINITY
EOF

# Remove q if it exists
qconf -dq ngs.q
# Add a new q 
qconf -Aq ngs.q

