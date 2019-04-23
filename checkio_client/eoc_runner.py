

def init_subparsers(subparsers):
    get_git = subparsers.add_parser('eoc-get-git', help='Download and prepare EoC mission from git-repo')
    get_git.add_argument('url')
    # TODO: make slug parameter optional
    get_git.add_argument('mission')
    get_git.add_argument('--without-container', action='store_true', default=False,
                        help='start process without using container')
    get_git.set_defaults(module='eoc', func='get_git')

    complile_mission = subparsers.add_parser('eoc-complile-mission', help='Collect all sources in one place')
    complile_mission.add_argument('mission')
    complile_mission.set_defaults(module='eoc', func='complile_mission')

    build_mission = subparsers.add_parser('eoc-build-mission', help='Prepare a docker image')
    build_mission.add_argument('mission')
    build_mission.set_defaults(module='eoc', func='build_mission')

    native_build_mission = subparsers.add_parser('eoc-native-build-mission', help='Prepare a ENV for natove run (Python only)')
    native_build_mission.add_argument('mission')
    native_build_mission.set_defaults(module='eoc', func='native_build_mission')

def add_check_paramas(parser):
    parser.add_argument('--recompile', action='store_true', default=False,
                        help='(EoC only) Recompile mission first')



