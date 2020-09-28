#Scaling script for Column Sketches with Map-Apply
cwd=$(pwd)
PROJECT_FOLDER="$cwd/../.."
GENERATOR="$PROJECT_FOLDER/ScotchDSL/Translation/DataParallelColumnSketchGenerator.py"

#Adjust parameters according to your setup.
PYTHON="/usr/bin/python3.6"
TOOLCHAIN="quartus"

#Adjust parameters according to the sketch and FPGA you want to evaluate.
TEMPLATE="$PROJECT_FOLDER/IO-Controllers/A10-10AX115S2F45I1SG-dummy-superior-flex-1"
DESCRIPTOR="$PROJECT_FOLDER/Sketches/Map-Apply/AGMS-DP1/descriptor.json"


#You won't have to touch those.
DISPATCH_FACTOR=4
COLLECT_FACTOR=4

#Absurdly high operating frequnency. Use worst-case slack to determine actual fmax.
FMAX=900

rm -rf "./work"
mkdir -p work

GRANULARITY=128
i=0
while true; do
    let i=i+1
    for SEED in {1..5}; do
        let ROWS=i*GRANULARITY
        FOLDER="work/$i-$SEED"

        mkdir $FOLDER
        cp -r $TEMPLATE $FOLDER/template

        $PYTHON $GENERATOR $DESCRIPTOR $ROWS $DISPATCH_FACTOR $COLLECT_FACTOR $FOLDER/template/sketch
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
