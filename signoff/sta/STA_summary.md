# TCPU-16 Static Timing Analysis (STA)

## Tool and Technology
- Tool: OpenSTA 3.2.0
- PDK: GF180MCU-D
- Standard cell library: gf180mcu_fd_sc_mcu7t5v0
- Corner: TT, 25°C, 3.30 V
- Netlist: Standalone Yosys-mapped netlist

## Timing Constraints
- Clock period: 10 ns (assumed 100 MHz)
- Clock uncertainty: 0.2 ns
- Input delay: 1.0 ns (assumed)
- Output delay: 1.0 ns (assumed)

## Results
- Worst setup slack: -10.6152 ns (VIOLATED)
- Worst hold slack: +0.7330 ns (MET)

## Critical Setup Path
- Startpoint: _749_
- Endpoint: _825_ (accumulator bit 14)
- Data arrival time: 19.9336 ns
- Data required time: 9.3184 ns

## Hold Path
- Startpoint: uio_in[0]
- Endpoint: _827_
- Data arrival time: 1.0000 ns
- Data required time: 0.2670 ns
- Hold slack: +0.7330 ns (MET)

## Limitations
This is a pre-layout timing analysis using the mapped netlist.
The constraints are provisional assumptions, not measured interface requirements.
No routed parasitics, extracted interconnect delays, or clock-tree
effects are included. These results are not post-route signoff.

No RTL or architectural modifications were made for this analysis.
