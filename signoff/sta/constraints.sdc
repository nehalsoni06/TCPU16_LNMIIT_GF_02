# TCPU-16 standalone STA constraints
# Assumed clock and interface timing; not post-route signoff

create_clock -name core_clk -period 10.0 [get_ports clk]

set_clock_uncertainty 0.2 [get_clocks core_clk]

# Assumed external input timing
set_input_delay 1.0 -clock core_clk [get_ports {ui_in[*] uio_in[*] ena rst_n}]

# Assumed external output timing
set_output_delay 1.0 -clock core_clk [get_ports {uo_out[*] uio_out[*] uio_oe[*]}]

