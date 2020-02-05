#!/usr/bin/env python3

import argparse as argp
import shutil as sh
import subprocess as sp
import ntpath
import bibtexparser


def clear_bib(bibf, int_dir, poplist, verbose):
  if verbose:
    print('Cleaning the bibtex file', bibf, 'from fields like', end = ' ')
    for f in poplist:
      print(f, end = ' ')
    print('.')

  try:
    sh.copyfile(bibf, int_dir+'/'+bibf+'.bak')
  except Exception as e:
    print('[Warning] Could not create a backup of', bibf)

  try:
    with open(bibf, 'r') as bf:
      bib_db = bibtexparser.load(bf)
  except Exception as e:
    print ('Error occurred while reading', bibf, '!\n', e)
    return -1

  if bib_db.comments:
    bib_db.comments = []

  for e in bib_db.entries:
    for f in poplist:
      e.pop(f, None)

  try:
    with open(bibf,'w') as bf:
      bibtexparser.dump(bib_db, bf)
  except Exception as e:
    print('Error occurred while writing', bibf, '!\n')
    return -1

  print('Bibliography file', bibf,' cleaned up.')

def clear_wb(out_dir, int_dir, all_exts):
  flist = sh.os.listdir('.')
  if len(flist) == 0 or len(all_exts) == 0:
    return

  dirs = [out_dir, int_dir]

  for d in dirs:
    try:
      sh.rmtree(d)
    except Exception as e:
      print(str(e).replace('Errno 2', 'Warning'))
    
  for f in flist:
    for ext in all_exts:
      if f.endswith(ext):
        try:
          sh.os.remove(f)
        except Exception as e:
          print(e)

  print('Working directory cleaned up.')


def makepdf(pname, verbose):
  if verbose:
    try:
      proc = sp.Popen('pdflatex '+pname, shell=True, stderr=sp.STDOUT)
      proc.wait()
      proc = sp.Popen('bibtex '+pname, shell=True, stderr=sp.STDOUT)
      proc.wait()
      proc = sp.Popen('pdflatex '+pname, shell=True, stderr=sp.STDOUT)
      proc.wait()
      proc = sp.Popen('pdflatex '+pname, shell=True, stderr=sp.STDOUT)
      proc.wait()

    except Exception as e:
      print(e)
      return -1

  else:
    try:
      proc = sp.Popen(['pdflatex', pname], stdout=sp.PIPE)
      proc.communicate()
      proc = sp.Popen(['bibtex', pname], stdout=sp.PIPE)
      proc.communicate()
      proc = sp.Popen(['pdflatex', pname], stdout=sp.PIPE)
      proc.communicate()
      proc = sp.Popen(['pdflatex', pname], stdout=sp.PIPE)
      proc.communicate()
      
    except Exception as e:
      print(e)
      return -1
      

def tidyup(out_dir, output_exts, int_dir, interm_exts, verbose):
  if verbose:
    print('\nCleaning up the working directory...')
  
  flist = sh.os.listdir('.')

  mov_fail = True  
  for oext in output_exts:
    for f in flist:
      if f.endswith(oext):
        try:
          sh.move(f, out_dir+'/'+ntpath.basename(f))
          mov_fail = False
        except Exception as e:
          print('Error occurred while moving output files to', out_dir, '\n', e)
  if verbose and not mov_fail:
    print ('All', end = ' ')
    for e in output_exts:
      print (e+',', end = ' ')
    print('file(s) moved to', out_dir)

  mov_fail = True 
  flist = sh.os.listdir('.')
  for iext in interm_exts:
    for f in flist:
      if f.endswith(iext):
        try:
          sh.move(f, int_dir+'/'+ntpath.basename(f))
          mov_fail = False
        except Exception as e:
          print('Error occurred while moving intermediate files to', int_dir, '\n', e)
          
  if verbose and not mov_fail:
    print ('All', end = ' ')
    for e in interm_exts:
      print (e+',', end = ' ')
    print('file(s) moved to', int_dir)



def main():
  ap = argp.ArgumentParser(description = 'Neatly compiles or cleans LaTex projects.', prog = 'neatlatex')
  ap.add_argument('p', help = 'Project name')
  ap.add_argument('-c', '--clean', help = 'Clear the project directory from Aux or Log files.', action = 'store_true')
  ap.add_argument('-b', '--bibfile', help = 'Bibtex (.bib) file to cleanup the mess Mendeley leaves behind while syncing.')
  ap.add_argument('-v', '--verbose', help = 'Toggles verbosity', action = 'store_true')
  args = ap.parse_args()

  verbose = args.verbose
  
  out_dir = './output'
  int_dir = './auxlog'
  output_exts = ['.pdf']  
  interm_exts = ['.aux', '.dvi', '.log', '.out', '.xcp', '.bbl', '.blg']
  bibexclude = ['abstract', 'keywords', 'file', 'comment']
  all_exts = output_exts + interm_exts

  if args.clean:
    clear_wb(out_dir, int_dir, all_exts)
    return
  
  if not sh.os.path.exists(out_dir):
    sh.os.mkdir(out_dir)
  if not sh.os.path.exists(int_dir):
    sh.os.mkdir(int_dir)
  
  if args.bibfile != None:
    bibfile = args.bibfile
  else:
    bibfile = None

  res = 0
  
  if bibfile:
    res = clear_bib(bibfile, int_dir, bibexclude, verbose)
  if res == -1:
    return res
    
  pname = args.p
  res = makepdf(pname, verbose)
  if res == -1:
    return res

  tidyup(out_dir, output_exts, int_dir, interm_exts, verbose)

  if verbose:
    while True:
      seepdf = False
      wannasee = input('Do you want to see the output pdf file or what? (Yes/no): ')
      if wannasee == '' or wannasee == None:
        print('Well.. here silence is Yes!')
        seepdf = True
      elif wannasee in ['Yes', 'yes', 'y', 'Y']:
        print('\nHere is your gloriuos work.')
        seepdf = True
      elif wannasee == 'YES':
        print('\nAlright man.. Calm down! Here\'s your damn paper.. Have a blast!')
        seepdf = True
      elif wannasee in ['No', 'no', 'N', 'n']:
        print('\nSure.. you made me do all that and you don\'t even wanna see it.. No problem! It\'s fine.. It\'s totally fine..')
      elif wannasee == 'NO':
        print('\nYou know what! I don\'t wanna see it either! I don\'t even CARE what\'s inside!')
      elif wannasee.lower() == 'or what':
        print('\nCome come, I give you I give you.. you veeery funny ah!')
      else:
        print('\nDid you really think the person who wrote this script made me smart enough to understand what you\'re saying? Yes or No man.. YES or NO!\nDamn it.. every day a smart ass! every damn day!')
        continue

      if seepdf:
        sh.os.popen('xdg-open '+out_dir+'/'+pname+'.pdf')
        break
      else:
        break
      
  else:
    print ('Done! Find', end = ' ')
    for e in output_exts:
      print (e+',', end = ' ')
    print ('file(s) in', out_dir, 'directory.')


    
if __name__ == '__main__':
  main()
