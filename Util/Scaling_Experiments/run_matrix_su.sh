#Scaling script for Matrix/Row Sketches with Select-Update
cwd=$(pwd)
PROJECT_FOLDER="$cwd/../.."
GENERATOR="$PROJECT_FOLDER/ScotchDSL/Translation/ReplicatedMatrixSketchGenerator.py"

#Adjust parameters according to your setup.
PYTHON="/usr/bin/python3.6"
TOOLCHAIN="quartus"

#Adjust parameters according to the sketch and FPGA you want to evaluate.
TEMPLATE="$PROJECT_FOLDER/IO-Controllers/A10-10AX115S2F45I1SG-dummy-superior-flex-1"
N_REPS=1
DESCRIPTOR="$PROJECT_FOLDER/Sketches/Select-Update/CM/descriptor.json"
ROWS=8
RAM_DEPTH=512


#You won't have to touch those.
DISPATCH_FACTOR=4
COLLECT_FACTOR=4

#Absurdly high operating frequnency. Use worst-case slack to determine actual fmax.
#Set to maximum RAM frequency for Xilinx.
FMAX=900

rm -rf "./work"
mkdir -p work

GRANULARITY=16
i=0
while true; do
    let i=i+1
    for SEED in {1..5}; do
        let COL_RAMs=i*GRANULARITY
        FOLDER="work/$i-$SEED"

        mkdir $FOLDER
        cp -r $TEMPLATE $FOLDER/template

        $PYTHON $GENERATOR $DESCRIPTOR $RAM_DEPTH $COL_RAMs $ROWS $DISPATCH_FACTOR $COLLECT_FACTOR $N_REPS $FOLDER/template/sketch
        cd $FOLDER/template
        bash compile.sh $TOOLCHAIN $SEED $FMAX
        X=$?
        if [ $X -ne 0 ]; then
            echo $X
            exit
        fi
        cd $cwd
    done
done
