#!/usr/bin/env bash

export PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PDK_ROOT="${PDK_ROOT:-$HOME/ttsetup/pdk}"
export PDK="${PDK:-gf180mcuD}"
export STD_CELL_LIBRARY="gf180mcu_fd_sc_mcu7t5v0"

export LIB_DIR="$PDK_ROOT/$PDK/libs.ref/$STD_CELL_LIBRARY/lib"
export LIB_TT="$LIB_DIR/${STD_CELL_LIBRARY}__tt_025C_3v30.lib"

export RTL_DIR="$PROJECT_ROOT/src"
export TOP="tt_um_nehalsoni06_tcpu16"

export SYNTH_DIR="$PROJECT_ROOT/signoff/standalone_synth"
export LOG_DIR="$SYNTH_DIR/logs"
export OUT_DIR="$SYNTH_DIR/out"
export REPORT_DIR="$SYNTH_DIR/reports"

