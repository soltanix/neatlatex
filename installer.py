#!/usr/bin/env python3
import pdb
import argparse
import os, sys
import shutil
import subprocess
from pathlib import Path
import pdb

def findInstDir(caller_scr_loc):
  """Find where the script is calling neatlatex from"""
  # I know it's dirty but I'm too lazy to clean it.  
  if not os.path.isfile(caller_scr_loc+'/neatlatex'):
    print('Error: The caller script could not be located at {}'
          .format(caller_scr_loc))
    return None
  with open(caller_scr_loc+'/neatlatex') as nl_caller:
    call_line = None
    for l in nl_caller.readlines():
      if l.startswith('python3'):
        call_line = l
        break
  if call_line:
    return os.path.dirname(call_line.split()[1])
  else:
    print('Caller script at {} is malformed.'
          .format(caller_scr_loc+'/neatlatex'))
    return None


def nl_uninstall(caller_scr_loc, is_rb, insdir_path = None):
  # Uninstallation
  if is_rb:
    print('Something went wrong while installation. Rolling back.')
  print('Uninstalling NeatLatex...')
  uninst_fail = False  
  insfiles = ['reqs.pip', 'neatlatex3.py', 'env']

  if insdir_path:
    udir = insdir_path
  else:
    udir = findInstDir(caller_scr_loc)

  if udir == None:
    while True:
      scr_loc_known = input(
        'Do you know the location of the caller script? (Yes/no): ')
      if scr_loc_known.lower() in ['yes', 'y', '', None]:
        scr_loc = input('Input the location of the caller script: ')
        if scr_loc.endswith('/neatlatex'):
          scr_loc = scr_loc[:-10]
        udir = findInstDir(scr_loc)
        break
      elif scr_loc_known.lower() in ['no', 'n']:
        while True:
          dir_loc_known = input(
            'Do you know path to installation directory? (Yes/no): ')
          if dir_loc_known.lower() in ['yes', 'y', '', None]:
            udir = input('Input the installation directory: ')
            break
          elif dir_loc_known.lower() in ['no', 'n']:
            break
          else:
            print('Unrecognized input.')
        break
      else:
        print('Unrecognized input.')
  if udir == None or not os.path.isdir(udir):
    print('Cannot locate installation directory. Exiting...')
    uninst_fail = True
    return -1

  flist = os.listdir(udir)
  if not 'neatlatex3.py' in flist:
    print('Cannot identify NeatLatex installation at {}'.format(udir))
    uninst_fail = True
    return -1
  elif not 'env' in flist:
    print('NeatLatex script found, however virtual environment is missing.')
    print('This might or might not be NeatLatex installation location.')
    print('Removing this directory is risky.')
    proceed = input(
      'Are you sure you want to proceed with removing {}? (yes/No): '
      .format(udir))
    if not proceed.lower() in ['yes', 'y']:
      print('Could not find NeatLatex installation directory.')
      uninst_fail = True
      return -1

  print('Removing:')
  for item in insfiles:
    ipath = udir+'/'+item
    if os.path.isdir(ipath):
      print('\t%s' %item)
      try:
        shutil.rmtree(ipath)
      except FileNotFoundError:
        pass
      except Exception as e:
        print(e)
        uninst_fail = True
    else:
      print('\t%s' %item)
      try:
        os.remove(ipath)
      except FileNotFoundError:
        pass
      except Exception as e:
        print(e)
        uninst_fail = True
  print('from %s' %udir)
  print('Removing base directory {} and caller script {}/neatlatex'
        .format(udir, caller_scr_loc))
  try:
    os.rmdir(udir)
  except FileNotFoundError:
    pass
  except Exception as e:
    print(e)
    uninst_fail = True

  try:
    os.remove(caller_scr_loc+'/neatlatex')
  except FileNotFoundError:
    pass
  except Exception as e:
    print(e)
    uninst_fail = True

  if not uninst_fail:
    print('NeatLatex was successfully uninstalled.')
  else:
    print("""
Some installation files could not be located,
or the uninstallation was not completed successfully.
Some files/directories might be remaining. 
Check possible installation directories and /usr/local/bin
""")
    return -1


def main():
  ap = argparse.ArgumentParser(description = 'Installs NeatLatex.')
  argrp = ap.add_mutually_exclusive_group(required=True)
  argrp.add_argument('-i', '--install', action = 'store',
                     help = 'Installation directory')
  argrp.add_argument('-u', '--uninstall', action = 'store_true',
                     help = 'Uninstalls NeatLatex')
  args = ap.parse_args()

  if (sys.version_info < (3, 0)):
    print('NeatLatex requires Python 3.')
    return
  
  caller_scr_loc = '/usr/local/bin'
  rollback_success = 0

  if not os.access(caller_scr_loc, os.W_OK):
    print('You need root permissions to do this.')
    return -1
  
  if args.uninstall:
    nl_uninstall(caller_scr_loc, False)
  
  # Installation
  elif args.install:
    ins_fail = False
    insdir = os.path.abspath(args.install)

    if os.path.exists(insdir):
      if os.path.isdir(insdir):
        if len(os.listdir(insdir)):
          print('{} is not empty.'.format(insdir))
          print("""
Cannot install NeatLatex there.
If you want to install NeatLatex inside the indicated directory, 
add "/neatlatex" to the end of your installation path.
""")
          ins_fail = True
          return -1
      else:
        print('{} is not a directory. Cannot install there.'
              .format(insdir))
        ins_fail = True
        return -1

    # if not ins_fail:
    #   try:
    #     import virtualenv
    #   except ImportError as imperr:
    #     print('Unable to import virtualenv.')
    #     print(imperr)
    #     ins_fail = True
    #     return -1

    if not (insdir.strip('/').endswith('neatlatex') or
            insdir.strip('/').endswith('NeatLatex')):
      print("""
      [Warning] Your installation directory is not neatlatex or NeatLatex.
      """)
      sure = input('Are you sure you want to install in {}? (yes/No) '
                   .format(insdir))
      if not sure.lower() in ['y', 'yes']:
        return -1

    # print('Installing NeatLatex at', insdir)
    if not ins_fail:
      try:
        os.makedirs(insdir, exist_ok=True)
        shutil.copyfile('./neatlatex3.py', insdir+'/neatlatex3.py')
        shutil.copyfile('./reqs.pip', insdir+'/reqs.pip')
        print('Installation files copied to {}'.format(insdir))
      except Exception as e:
        print(e)
        ins_fail = True
        nl_uninstall('', True, insdir)
        return -1

    if not ins_fail:
      pwd = os.getcwd()
      # os.chdir(insdir)
      try:
        subprocess.run(['python3', '-m', 'venv', '{}/env'.format(insdir)])
        # subprocess.run(['{}/env/bin/activate'.format(insdir)])
        subprocess.run(['{}/env/bin/pip3'.format(insdir),
                        'install', '-r', '{}/reqs.pip'.format(insdir)])
        # subprocess.run(['deactivate'])
        os.chdir(pwd)
        print('Python3 requirements installed')
      except Exception as e:
        print(e)
        ins_fail = True
        nl_uninstall('', True, insdir)
        return -1          
      
    if not ins_fail:
      run_scr_list = ['#!/usr/bin/env bash\n',
                      'source '+insdir+'/env/bin/activate',
                      'python3 '+insdir+'/neatlatex3.py "$@"',
                      'deactivate', 'exit\n']
      run_scr = '\n'.join(run_scr_list)
      try:
        with open(insdir+'/neatlatex', 'w') as runfile:
          runfile.write(run_scr)
        subprocess.run(['chmod', '-R', '755', insdir])
        subprocess.run(['sudo', 'mv', insdir+'/neatlatex', caller_scr_loc])
        # pdb.set_trace()
      except Exception as e:
        print(e)
        ins_fail = True
        nl_uninstall(caller_scr_loc+'/neatlatex', True, insdir)
        return -1
      
    if not ins_fail:
      print('NeatLatex installed successfully at %s' %insdir)
      print("""
      A caller script has been created at {}/neatlatex.
      Add {} to your system PATH variable, if it already is not.
      """.format(caller_scr_loc,caller_scr_loc))
    else:
      print('Installer has encountered errors during isntallation.')
      nl_uninstall(caller_scr_loc, True)

        
if  __name__ == '__main__':
  main()
