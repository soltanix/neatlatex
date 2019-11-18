#!/usr/bin/env python3

import argparse, os, shutil, subprocess, sys
# from pathlib import Path

def nl_uninstall(caller_scr_loc, is_rb, insdir_path = None):
  # Uninstallation
  if is_rb:
    print('Something went wrong during the installation. Rolling back.')
  print('Uninstalling NeatLatex...')
  uninst_fail = False
  
  insfiles = ['reqs.pip', 'bin', 'lib', 'neatlatex3.py', 'include', 'local']
  if insdir_path:
    udir = insdir_path
  elif insdir_path == None and os.path.isfile(caller_scr_loc+'/neatlatex'):
    with open(caller_scr_loc+'/neatlatex') as nl_caller:
      udir = os.path.dirname(nl_caller.read().split()[3])
      #I know it's dirty but I'm too lazy to clean it.
  else:
    print('Error: The caller script could not be located at %s/neatlatex' %caller_scr_loc)

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
    
  if not os.path.isdir(udir):
    print('Cannot locate installation directory. Exiting...')
    uninst_fail = True
    return -1

  flist = os.listdir(udir)
  if not (udir.strip('/').endswith('neatlatex') or udir.strip('/').endswith('NeatLatex')) and 'neatlatex3.py' not in flist:
    print('The indicated directory does not seem to be a NeatLatex installation.')
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
        
  print('Removing base directory %s and caller script %s/neatlatex' %(udir, caller_scr_loc))
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
    print('Some installation files could not be located or the uninstallation was not completed successfully.\nSome files/directories might be remaining. Check possible installation directories and /usr/local/bin')
    return -1

def main():

  ap = argparse.ArgumentParser(description = 'Installs NeatLatex script on a given directory.')
  argrp = ap.add_mutually_exclusive_group(required=True)
  argrp.add_argument('-i', '--install', action = 'store', help = 'Installs NeatLatex into given directory')
  argrp.add_argument('-u', '--uninstall', action = 'store_true', help = 'Uninstalls NeatLatex from /usr/bin/')
  args = ap.parse_args()

  if (sys.version_info < (3, 0)):
    print('This script has been tested with Python 3\nYou\'re using Python version %s' %sys.version)
  
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
          print('%s is not empty. Cannot install NeatLatex there.\nIf you want to install NeatLatex inside the indicated directory, add "/neatlatex" to the end of your installation path.' %insdir)
          ins_fail = True
          return -1
      else:
        print('%s is not a directory. Cannot install NeatLatex there.' %insdir)
        ins_fail = True
        return -1

    if not ins_fail:
      try:
        import virtualenv
      except ImportError as imperr:
        print('Unable to find virtualenv: %s\nMake sure virtualenv is installed properly using pip3.' %imperr)
        ins_fail = True
        return -1

    if not (insdir.strip('/').endswith('neatlatex') or insdir.strip('/').endswith('NeatLatex')):
      print('[Warning] Your installation directory name is not neatlatex or NeatLatex.')
      sure = input('Are you sure you want to continue installing neatlatex to %s? (yes/No) ' %insdir)
      if not sure in ['Y', 'y', 'Yes', 'yes']:
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
        nl_uninstall('', True, insdir)
        return -1

    if not ins_fail:
      try:
        subprocess.run(['virtualenv', insdir])
        subprocess.run([insdir+'/bin/pip', 'install', '-r', 'reqs.pip'])
      except Exception as e:
        print(e)
        ins_fail = True
        nl_uninstall('', True, insdir)
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
        ins_fail = True
        nl_uninstall(caller_scr_loc+'/neatlatex', True, insdir)
        return -1
      
    if not ins_fail:
      print('NeatLatex installed successfully at %s' %insdir)
      print('A caller script has been created at %s/neatlatex.\nAdd %s to your system PATH variable, if it already is not.' %(caller_scr_loc,caller_scr_loc))
    else:
      print('Installer has encountered errors during isntallation.')
      nl_uninstall(caller_scr_loc, True)

        
if  __name__ == '__main__':
  main()
