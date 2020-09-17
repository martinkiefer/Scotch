VIVADO_PREFIX=$1
CONSTRAINT_FILE="constraints.xdc"
SEED=$2

FMAX="400"
if [ ! -z "$3" ]; then
    FMAX=$3
fi

PERIOD=$(echo "print(1000/$FMAX)" | python3)
echo $SEED > ./SEED

printf "\ncreate_clock -period $PERIOD -name clk [get_ports clk]" >> constraints.xdc

$VIVADO_PREFIX/vivado -mode batch -stack 2000 -source ./generate.tcl -tclargs $SEED

if ls *.runs/impl_1/*utilization_placed.rpt 1> /dev/null 2>&1; then
    exit 0
elif ls *.runs/impl_1/* 1> /dev/null 2>&1; then
    exit 3
else
    exit 2
fi
