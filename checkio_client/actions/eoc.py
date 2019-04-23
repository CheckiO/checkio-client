
from checkio_client.eoc.getters import mission_git_getter, recompile_mission, rebuild_native,\
    rebuild_mission
from checkio_client.eoc.initial import init_home_file

def get_git(args):
    mission_git_getter(args.url, args.mission)
    recompile_mission(args.mission)
    if not args.without_container:
        rebuild_mission(args.mission)
    init_home_file(args.mission)

def complile_mission(args):
    recompile_mission(args.mission)
    rebuild_native(args.mission)

def build_mission(args):
    rebuild_mission(args.mission)

def native_build_mission(args):
    rebuild_native(args.mission)