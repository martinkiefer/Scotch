set outputdir ./
create_project -part xcvu29p-fsga2577-2L-e cproject $outputdir
add_files [glob ./sketch/*.vhd]
add_files -fileset constrs_1 ./constraints.xdc 
add_files ./tl.vhd
set_property top tl [current_fileset]
set_property STEPS.SYNTH_DESIGN.ARGS.KEEP_EQUIVALENT_REGISTERS true [get_runs synth_1]
set_property STEPS.SYNTH_DESIGN.ARGS.FLATTEN_HIERARCHY none [get_runs synth_1]

if { "[lindex $argv 0]" == "1" } {
    set_property strategy Performance_Explore [get_runs impl_1]
} elseif { "[lindex $argv 0]" == "2" } {
    set_property strategy Performance_ExplorePostRoutePhysOpt [get_runs impl_1]
} elseif { "[lindex $argv 0]" == "3" } {
    set_property strategy Performance_NetDelay_low [get_runs impl_1]
} elseif { "[lindex $argv 0]" == "4" } {
    set_property strategy Performance_Retiming [get_runs impl_1]
} else {
    set_property strategy Performance_RefinePlacement [get_runs impl_1]
}

launch_runs synth_1 -jobs 20
wait_on_run synth_1
launch_runs impl_1 -jobs 20
wait_on_run impl_1
open_run impl_1
report_utilization -hierarchical  -file utilization_hierarchy.rpt
