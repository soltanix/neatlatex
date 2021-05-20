#!/usr/bin/env python3

import argparse as argp
import shutil as sh
import subprocess as sp
import bibtexparser
from pathlib import Path
import pdb


def clear_bib(bibf, int_dir, poplist, verbose, strsubList):
  if verbose:
    print('Removing following fields from {}:\n{}'
          .format(bibf, ', '.join(poplist)))
    
  try:
    sh.copyfile(bibf, Path(int_dir, bibf.as_posix()+'.bak'))
  except Exception as e:
    print('[Warning] Could not create a backup of {}:\n{}'
          .format(bibf, e))

  try:
    with open(bibf, 'r') as bf:
      bib_db = bibtexparser.load(bf)
  except Exception as e:
    print ('[Error] could not read {}:\n{}'.format(bibf, e))
    return -1

  if hasattr(bib_db, 'comments'):
    if 'Cleared by NeatLatex' in bib_db.comments[0]:
      print('The bibtex file appears to be cleaned before. Skipping.')
      return
    else:
      bib_db.comments = ['Cleared by NeatLatex']
  else:
    print('[Info] Comments section not available in bibtex. Adding.')
    bib_db.comments = ['Cleared by NeatLatex']

  for e in bib_db.entries:
    for f in poplist:
      try:
        bib_db.entries.pop(f)
      except:
        continue

  if len(strsubList) > 0:
    for e in bib_db.entries:
      if 'url' in e.keys():
        for s in strsubList:
          e['url'] = e['url'].replace(s[0],s[1])

  try:
    with open(bibf,'w') as bf:
      bibtexparser.dump(bib_db, bf)
  except Exception as e:
    print('Error occurred while writing {}!\n'.format(bibf))
    return -1

  print('Bibliography file {} cleaned up.'.format(bibf))

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
  flist = [f for f in out_dir.parent.iterdir()]
  mov_fail = False
  for f in flist:
    if f.suffix in output_exts:
      try:
        sh.move(f, Path(out_dir, f))
      except Exception as e:
        print('Error occurred while moving output files to',
              out_dir, '\n', e)
        mov_fail = True

  if verbose and not mov_fail:
    print ('All', end = ' ')
    for e in output_exts:
      print (e+',', end = ' ')
    print('file(s) moved to', out_dir)

  mov_fail = False
  for f in flist:
    if f.suffix in interm_exts:
      try:
        sh.move(f, Path(int_dir, f))
      except Exception as e:
        print('Error occurred while moving intermediate files to',
              int_dir, '\n', e)
        mov_fail = True

  if verbose and not mov_fail:
    print ('All', end = ' ')
    for e in interm_exts:
      print (e+',', end = ' ')
    print('file(s) moved to', int_dir)


def main():
  ap = argp.ArgumentParser(description = 'Neatly compiles or cleans LaTex projects.', prog = 'neatlatex')
  ap.add_argument('-p', '--proj', help = 'Project name to comile')
  ap.add_argument('-c', '--clear', help = 'Clear the project directory from Aux or Log files.', action = 'store_true')
  ap.add_argument('-b', '--bibfile', help = 'Bibtex (.bib) file to cleanup from the mess Mendeley leaves behind while syncing libraries')
  ap.add_argument('-v', '--verbose', help = 'Toggles verbosity', action = 'store_true')
  args = ap.parse_args()

  verbose = args.verbose

  output_exts = ['.pdf']  
  interm_exts = ['.aux', '.dvi', '.log', '.out', '.xcp', '.bbl', '.blg']
  bibexclude = ['abstract', 'keywords', 'file', 'comment', 'url']
  strSubList = [('{~}','~'), ('{\&}','&'), ('{\_}','_'), ('{\%}','%'),
                (' ', ', '), ('%20',' '), ('%5F', '_'), ('%7E', '~'),
                ('%3D', '='), ('%2F', '/'), ('%2B', '+'),
                ('%3B', ';')]
  all_exts = output_exts + interm_exts

  if args.proj:
    proj_dir = Path(args.proj).parent
  else:
    proj_dir = Path('.')
  out_dir = Path(proj_dir, 'output')
  int_dir = Path(proj_dir, 'auxlog')

  if args.clear:
    clear_wb(out_dir, int_dir, all_exts)
    return
  elif args.bibfile:
    bibfile = Path(args.bibfile)
    res = clear_bib(bibfile, int_dir, bibexclude, verbose, strSubList)
    return
  
  if not args.proj:
    print('Must indicate main project .tex file to compile.')
    return
  if len(args.proj) <= 0:
    print('Invalid project name.')
    return
  if not (Path(args.proj).exists() or
          Path(args.proj + '.tex').exists()):
    print('File does not exist.')
    return
  
  if not out_dir.exists():
    out_dir.mkdir()
  if not int_dir.exists():
    int_dir.mkdir()

  pname = args.proj.strip('.tex')
  res = makepdf(pname, verbose)
  if res == -1:
    return res
  
  tidyup(out_dir, output_exts, int_dir, interm_exts, verbose)

  # Passive aggressive helper
  if verbose:
    while True:
      seepdf = False
      wannasee = input('Do you want to see the output pdf file or what? (Yes/no): ')
      if wannasee == '' or wannasee == None:
        print('No answer!.. OK. Here it is just in case.')
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
        print('\nYou know what! I don\'t wanna see it either! I don\'t even CARE what it looks like!')
      elif wannasee.lower() == 'or what':
        print('\nCome come, I clap for you.. you veeery funny ah!')
      else:
        print('\nDid you really think the person who wrote this script made me smart enough to understand what you\'re saying? Yes or No man.. YES or NO!\nDamn it.. every day a smart ass! every damn day!')
        continue

      if seepdf:
        sh.os.popen('xdg-open ' + Path(out_dir, pname + '.pdf')
                    .as_posix())
        break
      else:
        break
      
  else:
    print ('Done! Find', end = ' ')
    for e in output_exts:
      print (e + ',', end = ' ')
    print ('file(s) in', out_dir, 'directory.')


    
if __name__ == '__main__':
  main()
