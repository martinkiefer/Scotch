QUARTUS_PREFIX=$1
SEED=$2
PROJECT_NAME="no-io"
SDC_FILE="tl.sdc"


FMAX=400
if [ ! -z "$3" ]; then
    FMAX=$3
fi

function handlerc {
    if [ $1 -eq 0 ]; then
        echo "$task successful." >> experiment.log
    else
        echo "$2 failed. Exiting. Return code: $1" >> experiment.log
        exit $3
    fi
}


# Append file list to project directory
for file in sketch/functions_pkg*; do
    echo "set_global_assignment -name VHDL_FILE $file" >> $PROJECT_NAME.qsf
done

for file in sketch/*_pkg.vhd; do
    echo "set_global_assignment -name VHDL_FILE $file" >> $PROJECT_NAME.qsf
done

for file in sketch/*.vhd; do
    echo "set_global_assignment -name VHDL_FILE $file" >> $PROJECT_NAME.qsf
done

#At least for matrix sketches, placement of shift registers in BRAMS wastes ressources
echo "set_global_assignment -name SEED $SEED" >> $PROJECT_NAME.qsf
echo "set_global_assignment -name AUTO_SHIFT_REGISTER_RECOGNITION OFF" >> $PROJECT_NAME.qsf
echo "set_global_assignment -name OPTIMIZATION_MODE \"SUPERIOR PERFORMANCE WITH MAXIMUM PLACEMENT EFFORT\"" >> $PROJECT_NAME.qsf

echo "create_clock -name clk -period \"${FMAX}MHz\" [get_ports clk]" >> $SDC_FILE

 "$QUARTUS_PREFIX"_ipgenerate $PROJECT_NAME -c $PROJECT_NAME --run_default_mode_op &> ipgen.out
RESULT=$?
task="ipgenerate"
handlerc $RESULT $task 1

"$QUARTUS_PREFIX"_syn --read_settings_files=on --write_settings_files=off $PROJECT_NAME -c $PROJECT_NAME &> syn.out
RESULT=$?
task="synthesis"
handlerc $RESULT $task 2

"$QUARTUS_PREFIX"_fit --read_settings_files=on --write_settings_files=off $PROJECT_NAME -c $PROJECT_NAME &> fit.out
RESULT=$?
task="fitter"
handlerc $RESULT $task 3


"$QUARTUS_PREFIX"_sta $PROJECT_NAME -c $PROJECT_NAME --mode=finalize &> sta.out
RESULT=$?
task="timing analysis"
handlerc $RESULT $task 4

"$QUARTUS_PREFIX"_asm --read_settings_files=on --write_settings_files=off $PROJECT_NAME -c $PROJECT_NAME &> asm.out
RESULT=$?
task="assembler"
handlerc $RESULT $task 5

exit 0
