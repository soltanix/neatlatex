#!/usr/bin/env python3

import argparse, os, shutil, subprocess
from pathlib import Path

def nl_uninstall(caller_scr_loc):
  # Uninstallation
  uninst_fail = False
  
  insfiles = ['reqs.pip', 'bin', 'lib', 'neatlatex3.py', 'include']
  if os.path.isfile(caller_scr_loc+'/neatlatex'):
    with open(caller_scr_loc+'/neatlatex') as nl_caller:
      udir = os.path.dirname(nl_caller.read().split()[3])
  else:
    print('Error: The caller script could not be located at '+caller_scr_loc+'/neatlatex')

    while True:
      scr_loc_known = input('Do you know where the caller script is? (Yes/no): ')
      if scr_loc_known.lower() == 'yes' or scr_loc_known.lower() == 'y' or scr_loc_known.lower() == '' or scr_loc_known.lower() == None :
        scr_loc = input('Input the location of the caller script: ')
        with open(scr_loc) as nl_caller:
          udir = os.path.dirname(nl_caller.read().split()[3])
        break
      elif scr_loc_known.lower() == 'no' or scr_loc_known.lower() == 'n':
        while True:
          dir_loc_known = input('Do you know where the installation directory is? (Yes/no): ')
          if dir_loc_known.lower() == 'yes' or dir_loc_known.lower() == 'y' or dir_loc_known.lower() == '' or dir_loc_known.lower() == None :
            udir = input('Input the installation directory: ')
            break
          elif dir_loc_known.lower() == 'no' or dir_loc_known.lower() == 'n':
            print('Uninstallation cannot continue without a script or directory location.')
            udir = ''
            break
          else:
            print('Unrecognized input.')
        break
      else:
        print('Unrecognized input.')
        

    
  if os.path.isdir(udir):
      udir = usr_def_dir
  else:
    print('Cannot locate installation directory. Exiting...')
    return -1

  
  for item in insfiles:
    ipath = udir+'/'+item
    if os.path.isdir(ipath):
      print('Removing directory:', ipath)
      try:
        shutil.rmtree(ipath)
      except Exception as e:
        print(e)
        uninst_fail = True
    else:
      print('Removing file:', ipath)
      try:
        os.remove(ipath)
      except Exception as e:
        print(e)
        uninst_fail = True

  print('Removing base directory', udir, 'and caller script', caller_scr_loc+'/neatlatex')
  try:
    os.rmdir(udir)
  except Exception as e:
    print(e)
    uninst_fail = True

  try:
    os.remove(caller_scr_loc+'/neatlatex')
  except Exception as e:
    print(e)
    uninst_fail = True

  if not uninst_fail:
    print('NeatLatex was successfully uninstalled.')
  else:
    print('Uninstallation was not completed successfully.\nSome files/directories could not be located or removed.')
    return -1

def main():

  ap = argparse.ArgumentParser(description = 'Installs NeatLatex script on a given directory.')
  argrp = ap.add_mutually_exclusive_group(required=True)
  argrp.add_argument('-i', '--install', action = 'store', help = 'Installs NeatLatex into given directory')
  argrp.add_argument('-u', '--uninstall', action = 'store_true', help = 'Uninstalls NeatLatex from /usr/bin/')
  args = ap.parse_args()

  caller_scr_loc = '/usr/local/bin'
  rollback_success = 0

  try:
    Path(caller_scr_loc+'/neatlatex_tmp').touch()
    os.remove(caller_scr_loc+'/neatlatex_tmp')
  except PermissionError:
    print('You need root permissions to do this.')
    return -1
  
  if args.uninstall:
    nl_uninstall(caller_scr_loc)
  
  # Installation
  elif args.install:
    ins_fail = False
    insdir = os.path.abspath(args.install)

    if os.path.exists(insdir):
      if os.path.isdir(insdir):
        if len(os.listdir(insdir)):
          print(insdir, 'is not empty. Cannot install NeatLatex there.')
          return -1
      else:
        print(insdir, 'is not a directory. Cannot install NeatLatex there.')
        return -1

    print('Installing NeatLatex at', insdir)

    if not ins_fail:
      try:
        os.makedirs(insdir, exist_ok=True)
        shutil.copyfile('./neatlatex3.py', insdir+'/neatlatex3.py')
        shutil.copyfile('./reqs.pip', insdir+'/reqs.pip')
      except Exception as e:
        print(e)
        ins_fail = True
        return -1
      except PermissionError:
        print('You need root permissions to do this')
        ins_fail = True
        return -1

    if not ins_fail:
      try:
        import virtualenv
      except ImportError as imperr:
        print('Unable to find pipenv:', imperr, '\nMake sure pipenv is installed properly.')
        ins_fail = True
        return -1

    if not ins_fail:
      try:
        subprocess.run(['virtualenv', insdir])
        subprocess.run([insdir+'/bin/pip', 'install', '-r', 'reqs.pip'])
      except Exception as e:
        print(e)
        ins_fail = True
        return -1

    if not ins_fail:
      run_scr = '#!/usr/bin/env bash\n'+insdir+'/bin/python '+insdir+'/neatlatex3.py "$@"\nexit\n'
      try:
        with open(insdir+'/neatlatex', 'w') as runfile:
          runfile.write(run_scr)
        subprocess.run(['chmod', '755', insdir+'/neatlatex'])
        subprocess.run(['sudo', 'mv', insdir+'/neatlatex', caller_scr_loc])      
      except Exception as e:
        print(e)
      
    if not ins_fail:
      print('NeatLatex installed successfully at', insdir)
      print('A caller script has been created at', caller_scr_loc+'/neatlatex.\nAdd', caller_scr_loc, 'to your system PATH variable, if it already is not.')
    else:
      print('Installation of NeatLatex has failed at some point. Rolling back')
      rollback_success = nl_uninstall(caller_scr_loc)

  if rollback_success == -1:
    return -1
        
if  __name__ == '__main__':
  main()
