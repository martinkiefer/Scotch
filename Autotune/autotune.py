import argparse
from EAModules.Autotune import Autotune
import sys

if __name__ == "__main__":
    mparser = argparse.ArgumentParser(prog="python3 autotune.py")
    subparsers = mparser.add_subparsers(help="Autotune mode", dest="op") 

    parser_plain = subparsers.add_parser("plain", 
        help="Regular auto-tune, no database connection, no redundancy elimination, no resume functionality. ")

    #Common arguments
    for parser in [parser_plain]:
    #for parser in [parser_plain]:
        #TODO: Add replicated and data parallel versions
        parser.add_argument("-generator", type=str, choices=["column", "matrix", "column-ma"], required=True)

        parser.add_argument("-cfactor", type=int, help="Collect factor", default=4)
        parser.add_argument("-dfactor", type=int, help="Dispatch factor", default=4)
        parser.add_argument("-initial_guess", type=int, help="Initial guess for autotune", default=16)
        parser.add_argument("-dp", type=int, help="Data Parallelism Degree")

        parser.add_argument("-toolchain_prefix", type=str, help="Prefix to quartus/vivado commands. Select according to needs of template.", required=True)
        parser.add_argument("-fixrows", type=int, help="Fix the number of rows. Only available parameter for column generators.")
        parser.add_argument("-fixcols", type=int, help="Fix the number of columns.")
        parser.add_argument("-memseg_depth", type=int, help="BRAM depth, for now. In the future, we will solve this with a device specific look-up table.")

        parser.add_argument("-descriptor_path", type=str, help="Path to descriptor", required=True)
        parser.add_argument("-template_path", type=str, help="Path to IO template", required=True)
        parser.add_argument("-toolchain", type=str, help="Used toolchain (Quartus, Vivado)", default="Quartus")

    args = mparser.parse_args()

    #Column generators have nothing to fix
    if args.generator in ["column", "column-ma"]:
        if (not args.fixrows is None) or (not args.fixcols is None):
            raise argparse.ArgumentTypeError("Nothing can be fixed for column sketches.")

        if not args.memseg_depth is None:
            raise argparse.ArgumentTypeError("There are no memsegments in column sketches.")

    if args.generator in ["column", "matrix"]: 
        if args.dp is None:
            raise argparse.ArgumentTypeError("Column and matrix sketches (select-update) need a degree of parallelism (dp).")

    if args.generator in ["matrix"]:
        if (args.fixrows is None) == (args.fixcols is None):
            raise argparse.ArgumentTypeError("You can't fix rows and cols at the same time or none at all.")

        if not args.memseg_depth is None:
            memseg_depth = args.memseg_depth
        else:
            raise argparse.ArgumentTypeError("Memory segment depth has to be provided.")

    if args.op == "plain":
        sketch = None
        if args.generator == "matrix":
            sketch = Autotune.AutotuneMatrixSketchWrapper(args.descriptor_path, memseg_depth, args.dfactor, args.cfactor, args.dp, fixrow=args.fixrows, fixcol=args.fixcols)
        elif args.generator == "column":
            sketch = Autotune.AutotuneColumnSketchWrapper(args.descriptor_path, args.dfactor, args.cfactor, args.dp)
        elif args.generator == "column-ma":
            sketch = Autotune.AutotuneDataParallelColumnSketchWrapper(args.descriptor_path, args.dfactor, args.cfactor)

        ato = Autotune.Optimizer(sketch, args.toolchain_prefix, args.template_path, args.initial_guess, args.toolchain)
        param, df = ato.optimize()
        print(param, df)
        df.to_csv("./parameter_history.csv") 
    else:
        raise Exception("Command not yet implemented.")
