

def init_subparsers(subparsers):
    get_git = subparsers.add_parser('eoc-get-git', help='Download and prepare EoC mission from git-repo')
    get_git.add_argument('url')
    # TODO: make slug parameter optional
    get_git.add_argument('mission')
    get_git.add_argument('--without-container', action='store_true', default=False,
                        help='start process without using container')
    get_git.set_defaults(module='eoc', func='get_git')

    complile_mission = subparsers.add_parser('eoc-compile-mission', help='Collect all sources in one place')
    complile_mission.add_argument('mission')
    complile_mission.set_defaults(module='eoc', func='complile_mission')

    build_mission = subparsers.add_parser('eoc-build-mission', help='Prepare a docker image')
    build_mission.add_argument('mission')
    build_mission.set_defaults(module='eoc', func='build_mission')

    native_build_mission = subparsers.add_parser('eoc-native-build-mission', help='Prepare a ENV for natove run (Python only)')
    native_build_mission.add_argument('mission')
    native_build_mission.set_defaults(module='eoc', func='native_build_mission')

    p_repo_init = subparsers.add_parser('eoc-initrepo', help='creates a folder with an empty mission')
    p_repo_init.add_argument('mission', type=str, default='.', nargs=1,
        metavar='mission',
        help='name of the mission')
    p_repo_init.add_argument('repository', type=str, nargs='?',
        metavar='repository',
        help='url to git repository')
    p_repo_init.add_argument('--template', type=str,
        metavar='template',
        help='url to git repository you want to take as a template')
    p_repo_init.add_argument('--without-container', action='store_true', default=False,
                        help='start process without using container')
    p_repo_init.set_defaults(module='eoc', func='init_mission')

    p_autofill_repo = subparsers.add_parser('eoc-autofillrepo', help='fill up animation, referee, description and initial code by basic tests and passed names for function')
    p_autofill_repo.add_argument('mission', type=str, default='.', nargs='?',
        metavar='mission',
        help='name of the mission')
    p_autofill_repo.add_argument('--js-function', type=str)
    p_autofill_repo.add_argument('--py-function', type=str)
    p_autofill_repo.set_defaults(module='autofill', func='main_eoc')

    p_reset_intiial = subparsers.add_parser('eoc-reset-initial', help='overwrite solution to an initial code')
    p_reset_intiial.add_argument('mission', type=str, default='.', nargs='?',
        metavar='mission',
        help='name of the mission')
    p_reset_intiial.set_defaults(module='eoc', func='reset_initial')

    p_battle = subparsers.add_parser('eoc-battle', help='test your battle solution')
    p_battle.add_argument('filename', type=str, nargs='?', metavar='filename',
        help='path to the file with solution')
    p_battle.add_argument('--balance', type=str, default=None)
    p_battle.add_argument('--mission', type=str, default='battle')
    p_battle.add_argument('--repo', type=str, default='https://github.com/checkio/eoc-battle')
    p_battle.add_argument('--force-build', default=False, action='store_true')
    p_battle.add_argument('--output-file', type=str, default=None)
    add_check_paramas(p_battle)
    p_battle.set_defaults(module='eoc', func='battle')

    p_sync_strategies = subparsers.add_parser('eoc-sync-strategies', help='Sync Strategies for EoC')
    p_sync_strategies.set_defaults(module='sync', func='eoc_strategies')

    p_rm_strategy = subparsers.add_parser('eoc-rm-strategy', help='Remove strategy from your base')
    p_rm_strategy.add_argument('name')
    p_rm_strategy.set_defaults(module='sync', func='eoc_rm_strategy')

def add_check_paramas(parser):
    parser.add_argument('--recompile', action='store_true', default=False,
                        help='(EoC only, for --local only) Recompile mission first')
    parser.add_argument('--local', action='store_true', default=False,
                        help='(EoC only) Use local container')
    parser.add_argument('--eoc-referee',  type=str, default=None,
                        help='(EoC only) Path to referee source')



