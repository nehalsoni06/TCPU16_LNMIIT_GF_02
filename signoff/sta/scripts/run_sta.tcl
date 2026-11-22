# TCPU-16 standalone OpenSTA analysis
# GF180MCU-D, TT corner
# Assumed timing constraints; not routed signoff

set PDK_ROOT $env(PDK_ROOT)
set PDK $env(PDK)
set LIB "$PDK_ROOT/$PDK/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib"

set NETLIST "signoff/standalone_synth/out/tt_um_nehalsoni06_tcpu16_mapped.v"
set TOP "tt_um_nehalsoni06_tcpu16"
set SDC "signoff/sta/constraints.sdc"

read_liberty $LIB
read_verilog $NETLIST
link_design $TOP
read_sdc $SDC

report_checks -path_delay max -format full_clock_expanded -digits 4 > signoff/sta/reports/setup_paths.txt
report_checks -path_delay min -format full_clock_expanded -digits 4 > signoff/sta/reports/hold_paths.txt
report_check_types -max_delay -verbose > signoff/sta/reports/max_check.txt
report_check_types -min_delay -verbose > signoff/sta/reports/min_check.txt

exit
