# TCPU-16 — GF180MCU TinyTapeout Implementation

## Project Overview

This project implements the TCPU-16 processor and prepares it for physical design using the GF180MCU process design kit (PDK) and the TinyTapeout support tools.

The workflow includes:

1. RTL development and functional simulation.
2. Python and toolchain configuration.
3. TinyTapeout support-tool setup.
4. GF180MCU PDK configuration.
5. LibreLane installation and configuration.
6. Physical design and hardening.
7. GDS generation.
8. TinyTapeout precheck.
9. Gate-Level Simulation (GLS).
10. Final design verification.

---

# 1. Project Environment

### Hardware and software environment

| Component | Configuration |
|---|---|
| Host OS | Windows |
| Virtualization | Oracle VirtualBox |
| Guest OS | Ubuntu 24.04 |
| Project | TCPU-16 |
| PDK | GF180MCU |
| PDK variant | gf180mcuD |
| Physical design tool | LibreLane 3.0.14 |
| Simulation | Icarus Verilog / Cocotb |
| Layout format | GDSII |
| Python | 3.12 |
| Python environment | `~/ttsetup/venv` |
| Docker | Installed and configured |

### Project location

```bash
~/Desktop/tcpu16/TCPU16_LNMIIT_GF_02
```

### GitHub repository

https://github.com/nehalsoni06/TCPU16_LNMIIT_GF_02.git

### Important environment variables

```bash
export PDK_ROOT=~/ttsetup/pdk
export PDK=gf180mcuD
export LIBRELANE_TAG=3.0.14
```

These variables identify the location of the PDK, the selected GF180 process variant and the LibreLane version.

---

# 2. Initial Project and Simulation Work

Before physical design, the TCPU-16 project was developed and tested.

The project contains RTL, simulation, source and testbench directories.

Important directories:

```text
TCPU16_LNMIIT_GF_02/
│
├── rtl/
├── sim/
├── src/
├── tb/
├── tt/
├── runs/
├── test/
└── docs/
```

The exact files may vary as the project evolves.

### Functional simulation

The earlier Cocotb simulation completed successfully.

Reported result:

```text
TESTS=1
PASS=1
FAIL=0
SKIP=0
```

The simulation generated an FST waveform file:

```text
tb.fst
```

GTKWave was used to inspect the processor signals and execution waveforms.

The waveform work included inspecting signals such as:

- Clock and reset.
- Program counter.
- Accumulator.
- Instruction register.
- Halted status.
- Program execution.

**Status:** Initial functional simulation completed successfully.

---

# 3. TinyTapeout Support Tools Setup

The TinyTapeout support tools were cloned into the project directory.

### Command

```bash
git clone https://github.com/TinyTapeout/tt-support-tools tt
```

The support tools provide scripts for:

- User configuration generation.
- PDK configuration.
- Physical-design hardening.
- GDS-related checks.
- Top-module identification.
- TinyTapeout precheck.

### Python virtual environment

The Python virtual environment was created at:

```text
/home/vsduser/ttsetup/venv
```

Commands:

```bash
python3 -m venv ~/ttsetup/venv
```

Activate the environment:

```bash
source ~/ttsetup/venv/bin/activate
```

Install TinyTapeout support-tool requirements:

```bash
uv pip install --python ~/ttsetup/venv/bin/python -r ./tt/requirements.txt
```

The `uv` package manager was used because the virtual environment initially did not have the `pip` Python module.

---

# 4. LibreLane and GF180MCU Configuration

### PDK configuration

```bash
export PDK_ROOT=~/ttsetup/pdk
export PDK=gf180mcuD
```

### LibreLane version

```bash
export LIBRELANE_TAG=3.0.14
```

LibreLane version verification:

```bash
librelane --version
```

LibreLane is responsible for the physical-design flow, including synthesis, floorplanning, placement, routing and layout generation.

### Docker setup

Docker was installed and configured to run the containerized LibreLane environment.

Docker was enabled and the user was added to the Docker group.

The Docker installation was checked using:

```bash
docker info
```

The Docker image used by the hardening flow was:

```text
ghcr.io/librelane/librelane:3.0.14
```

---

# 5. Initial Disk-Space Problem

During the first hardening attempt, Docker failed while extracting the LibreLane image.

### Error encountered

```text
failed to extract layer
no space left on device
```

The problem occurred because the original VirtualBox virtual disk was only 25 GB.

The VM did not have sufficient free space for the LibreLane container and physical-design dependencies.

### Initial disk status

```text
Total disk: 25 GB
Available space: approximately 4 GB
```

### Cleanup operations performed

Old disabled Snap revisions were removed.

Examples of commands:

```bash
sudo snap remove core22 --revision=2411
sudo snap remove firmware-updater --revision=127
sudo snap remove gnome-42-2204 --revision=176
sudo snap remove gnome-46-2404 --revision=153
sudo snap remove mesa-2404 --revision=1165
sudo snap remove snap-store --revision=1173
sudo snap remove snapd --revision=21759
sudo snap remove snapd-desktop-integration --revision=387
sudo snap remove thunderbird --revision=1155
```

Journal cleanup:

```bash
sudo journalctl --vacuum-size=100M
```

APT cache cleanup:

```bash
sudo apt clean
```

Snap cache cleanup:

```bash
sudo rm -f /var/lib/snapd/cache/*
```

Docker storage was checked:

```bash
docker system df
```

However, cleanup did not provide sufficient space for the hardening flow.

**Decision:** Expand the existing VirtualBox virtual disk rather than deleting additional system files.

---

# 6. VirtualBox Disk Expansion

The existing VDI disk was expanded from 25 GB to 60 GB.

### Step 1: Shut down Ubuntu

```bash
sudo poweroff
```

The VM was verified as Powered Off in VirtualBox.

### Step 2: Locate the VDI file

This command was executed in Windows PowerShell:

```powershell
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" list hdds
```

The existing virtual disk was located at:

```text
D:\vsdsquadron_fpga_mini\vsdsquadron_fpga_mini.vdi
```

### Step 3: Resize the virtual disk

Windows PowerShell command:

```powershell
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" modifymedium disk "D:\vsdsquadron_fpga_mini\vsdsquadron_fpga_mini.vdi" --resize 61440
```

The disk was successfully expanded to 60 GB.

### Step 4: Verify the disk in Ubuntu

```bash
lsblk
```

Initially, the output showed:

```text
sda      60G
├─sda1    1M
└─sda2   25G
```

The virtual disk had expanded, but the Ubuntu partition was still 25 GB.

### Step 5: Check filesystem

```bash
findmnt -no FSTYPE /
```

Result:

```text
ext4
```

Available utilities were checked:

```bash
which growpart
which sgdisk
```

Results:

```text
/usr/bin/growpart
/usr/sbin/sgdisk
```

### Step 6: Repair the backup GPT location

```bash
sudo sgdisk -e /dev/sda
```

Output:

```text
The operation has completed successfully.
```

Verification:

```bash
sudo sgdisk -v /dev/sda
```

Result:

```text
No problems found.
```

The tool reported approximately 35 GiB of available unallocated space.

### Step 7: Expand partition 2

```bash
sudo growpart /dev/sda 2
```

Output:

```text
CHANGED: partition=2 start=4096 old: size=52422656 end=52426751 new: size=125824991 end=125829086
```

The partition was successfully expanded.

### Step 8: Expand the ext4 filesystem

```bash
sudo resize2fs /dev/sda2
```

Output:

```text
Filesystem at /dev/sda2 is mounted on /;
on-line resizing required

The filesystem on /dev/sda2 is now 15728123 (4k) blocks long.
```

### Step 9: Verify final disk size

```bash
lsblk
```

Final result:

```text
sda      60G
├─sda1    1M
└─sda2   60G /
```

Check filesystem capacity:

```bash
df -h /
```

Final output:

```text
Filesystem      Size  Used  Avail  Use%
/dev/sda2        59G   20G    38G   35%
```

**Status: Successfully completed.**

The disk-space problem was resolved.

---

# 7. TinyTapeout User Configuration

After the disk expansion, the environment was activated and configured.

```bash
source ~/ttsetup/venv/bin/activate

export PDK_ROOT=~/ttsetup/pdk
export PDK=gf180mcuD
export LIBRELANE_TAG=3.0.14
```

The TinyTapeout user configuration was generated using:

```bash
./tt/tt_tool.py --pdk $PDK --create-user-config
```

This generated the configuration required by the TinyTapeout workflow.

**Status: Completed.**

---

# 8. GF180MCU Physical Design and Hardening

The physical-design flow was started using:

```bash
./tt/tt_tool.py --pdk $PDK --harden
```

### First hardening attempt

The Docker image was successfully downloaded:

```text
ghcr.io/librelane/librelane:3.0.14
```

However, the first attempt encountered a download timeout while retrieving Ciel support files.

### Error encountered

```text
Downloading common.tar.zst... 60%

httpx.ReadTimeout:
The read operation timed out
```

The error occurred during the download of the required LibreLane PDK support data.

This was a network timeout, not the earlier disk-space error.

### Resolution

The hardening command was executed again:

```bash
./tt/tt_tool.py --pdk $PDK --harden
```

The user subsequently reported that the process completed.

The generated GDS file was then verified.

### Final GDS location

```text
runs/wokwi/final/gds/
```

### GDS file

```text
tt_um_nehalsoni06_tcpu16.gds
```

### File verification

Command:

```bash
ls -lh runs/wokwi/final/gds/
```

Output:

```text
total 1.4M
-rw-r--r-- 1 vsduser vsduser 1.4M Nov 17 20:42 tt_um_nehalsoni06_tcpu16.gds
```

**Status: GDS successfully generated and its existence verified.**

### Print hardening warnings

Command:

```bash
./tt/tt_tool.py --pdk $PDK --print-warnings
```

The command returned no output.

This is encouraging, but separate DRC, LVS and timing verification should still be checked before declaring the design fully verified.

---

# 9. Python PIP Error and Its Resolution

During the installation of the precheck and test dependencies, the following command was attempted:

```bash
pip install -r test/requirements.txt ciel==3.2.0
```

### Error encountered

```text
error: externally-managed-environment
```

This happened because the system `pip` was being used instead of the virtual environment's Python package installer.

### Diagnostic commands

```bash
which python
which pip
python --version
python -m pip --version
```

Output:

```text
/home/vsduser/ttsetup/venv/bin/python
/usr/bin/pip
Python 3.12.3

No module named pip
```

This established that:

- Python was pointing to the virtual environment.
- Pip was pointing to the Ubuntu system installation.
- The virtual environment did not have the pip module.

### Corrected installation approach

The virtual environment's packages were installed using `uv`:

```bash
uv pip install --python ~/ttsetup/venv/bin/python -r test/requirements.txt ciel==3.2.0
```

The same approach was used for precheck requirements.

### Precheck requirements installation

The following command was executed:

```bash
pip install -r tt/precheck/requirements.txt ciel==3.2.0
```

This time, the command completed successfully.

Packages installed included:

| Package | Installed version |
|---|---|
| Ciel | 3.2.0 |
| Click | 8.3.1 |
| Gdstk | 0.9.52 |
| KLayout | 0.30.13 |
| Pytest | 8.2.2 |
| PyYAML | 6.0.1 |
| Wasmtime | 42.0.0 |
| Yosys (YoWASP) | 0.63.0.0.post1107 |

### Important dependency conflict

The installer reported:

```text
librelane 3.0.14 requires ciel<3,>=2.3.1,
but you have ciel 3.2.0

librelane 3.0.14 requires click<8.3,>=8,
but you have click 8.3.1
```

This means that the precheck installation changed packages in the same Python environment used by LibreLane.

**Important:** Do not assume that the LibreLane Python environment is still dependency-clean.

The GDS already generated remains available, so do not repeat hardening simply to resolve this Python dependency issue.

### Recommended solution

Maintain separate environments:

1. A main environment for LibreLane 3.0.14 and physical design.
2. A precheck environment for TinyTapeout precheck dependencies.

This prevents the precheck requirements from changing the versions needed by LibreLane.

---

# 10. Current Project Status

The following table summarizes the work completed.

| Task | Status |
|---|---|
| TCPU-16 RTL development | Completed previously |
| Functional simulation | Passed previously |
| Cocotb simulation | Passed previously |
| GTKWave waveform inspection | Completed previously |
| TinyTapeout support tools | Installed |
| Python virtual environment | Created |
| Docker | Installed and configured |
| GF180MCU PDK configuration | Completed |
| LibreLane configuration | Completed |
| TinyTapeout user configuration | Generated |
| VirtualBox disk expansion | Completed |
| Ubuntu partition expansion | Completed |
| ext4 filesystem expansion | Completed |
| GF180 hardening | Completed |
| GDS generation | Completed |
| GDS file existence check | Passed |
| Hardening warnings command | No output |
| Precheck dependencies | Installed, conflicts reported |
| Gate-level simulation | Pending |
| Final physical-design verification | Pending |

---

# 11. Remaining Work

The following tasks remain according to the TinyTapeout workflow.

## A. Resolve Python environment conflicts

The precheck requirements installed Ciel 3.2.0 and Click 8.3.1, which conflict with LibreLane 3.0.14 requirements.

The next task is to isolate the precheck dependencies from the main LibreLane environment.

Do not randomly downgrade or uninstall packages in the current environment.

## B. Run TinyTapeout precheck

The precheck dependencies are installed, but the precheck itself has not yet been confirmed as executed.

The precheck is intended to inspect the design and check requirements associated with the TinyTapeout submission.

The exact precheck command should be confirmed against the checked-out support-tool version and project configuration.

## C. Identify the top module

The video workflow uses:

```bash
TOP_MODULE=$(cd .. && ./tt/tt_tool.py --pdk $PDK --print-top-module)

echo $TOP_MODULE
```

This should be executed from the `test` directory, assuming the project directory structure matches the video.

## D. Copy the gate-level netlist

The video workflow uses:

```bash
cp ../runs/wokwi/final/pnl/$TOP_MODULE.pnl.v gate_level_netlist.v
```

This copies the generated post-layout gate-level netlist into the test directory.

The actual file location must be verified before copying.

## E. Run Gate-Level Simulation

The video uses:

```bash
make -B GATES=yes
```

This forces a new build using the gate-level netlist instead of the RTL implementation.

The simulation should be checked for:

- Successful compilation.
- Correct GF180 standard-cell model inclusion.
- No unresolved module errors.
- Correct reset behaviour.
- Correct instruction execution.
- Correct accumulator behaviour.
- Correct program-counter behaviour.
- Correct HALT operation.

The gate-level simulation must pass before it can be considered verified.

## F. Inspect the final physical-design reports

The following should be checked:

- Final GDS.
- Final gate-level netlist.
- LEF file.
- Timing reports.
- Placement and routing reports.
- Design-rule-check results.
- Antenna reports, if applicable.
- LVS results, if the flow provides them.

The exact artifact names and locations should be obtained from the generated run directory.

## G. Final GDS verification

The generated GDS should be checked for:

- Correct top-level cell.
- Correct design geometry.
- Expected GF180 technology.
- Valid GDS structure.
- Successful TinyTapeout precheck.

The GDS file exists, but its complete integrity and submission readiness have not yet been independently verified.

## H. Final documentation

The final repository should contain updated documentation covering:

- Processor architecture.
- RTL module descriptions.
- Testbench description.
- Functional simulation results.
- Cocotb verification.
- Gate-level simulation results.
- GF180 hardening procedure.
- GDS generation.
- Final verification reports.

---

# 12. Important Commands Reference

This section collects the principal commands used during the project.

### Activate Python environment

```bash
source ~/ttsetup/venv/bin/activate
```

### Configure PDK

```bash
export PDK_ROOT=~/ttsetup/pdk
export PDK=gf180mcuD
export LIBRELANE_TAG=3.0.14
```

### Check Python and pip

```bash
which python
which pip
python --version
python -m pip --version
```

### Install support-tool requirements

```bash
uv pip install --python ~/ttsetup/venv/bin/python -r ./tt/requirements.txt
```

### Install precheck requirements

```bash
uv pip install --python ~/ttsetup/venv/bin/python -r tt/precheck/requirements.txt ciel==3.2.0
```

### Install test requirements

```bash
uv pip install --python ~/ttsetup/venv/bin/python -r test/requirements.txt ciel==3.2.0
```

### Check disk capacity

```bash
lsblk
df -h /
```

### Generate user configuration

```bash
./tt/tt_tool.py --pdk $PDK --create-user-config
```

### Run hardening

```bash
./tt/tt_tool.py --pdk $PDK --harden
```

### Print warnings

```bash
./tt/tt_tool.py --pdk $PDK --print-warnings
```

### Inspect GDS directory

```bash
ls -lh runs/wokwi/final/gds/
```

### Identify top module

```bash
./tt/tt_tool.py --pdk $PDK --print-top-module
```

### Run gate-level simulation

```bash
make -B GATES=yes
```

---

# 13. Final Milestone Summary

The most important milestone achieved so far is the successful generation of the GF180MCU GDS file.

**Generated artifact:**

```text
runs/wokwi/final/gds/tt_um_nehalsoni06_tcpu16.gds
```

**File size:** 1.4 MB

**Physical-design tool:** LibreLane 3.0.14

**Technology:** GF180MCU-D

**Current stage:** Post-hardening verification and gate-level simulation.

The project has progressed from RTL simulation and toolchain configuration through physical-design hardening and GDS generation.

The remaining work is to resolve the Python environment separation, execute TinyTapeout precheck, perform gate-level simulation and verify the final physical-design reports.

**Note:** GDS generation is complete, but the entire TinyTapeout submission and sign-off process should not be considered complete until the remaining verification stages have been performed and their results documented.
