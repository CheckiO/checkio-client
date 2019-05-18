
from checkio_client.eoc.getters import mission_git_getter, recompile_mission, rebuild_native,\
    rebuild_mission
from checkio_client.eoc.initial import init_home_file

from checkio_client.eoc.folder import Folder
from checkio_client.settings import conf

def get_git(args):
    mission_git_getter(args.url, args.mission)
    recompile_mission(args.mission)
    if not args.without_container:
        rebuild_mission(args.mission)
    init_home_file(args.mission)

def reset_initial(args):
    init_home_file(args.mission)

def complile_mission(args):
    recompile_mission(args.mission)

def build_mission(args):
    rebuild_mission(args.mission)

def native_build_mission(args):
    rebuild_native(args.mission)

def init_mission(args):
    from checkio_client.actions.repo import link_folder_to_repo, clone_repo_to_folder
    domain_data = conf.default_domain_data
    mission = args.mission[0]
    folder = Folder(mission)

    
    if folder.exists():
        print('Folder exists already')
        return

    if args.template:
        template = args.template
    else:
        domain_data = conf.default_domain_data
        template = domain_data['repo_template']

    clone_repo_to_folder(template, folder.mission_folder())    

    if args.repository:
        print('Send to git...')
        link_folder_to_repo(folder.mission_folder(), args.repository)

    recompile_mission(mission)
    if not args.without_container:
        rebuild_mission(mission)
    init_home_file(mission)

    print('Done')