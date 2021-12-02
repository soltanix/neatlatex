#!/usr/bin/env python3

import argparse as argp
import shutil as sh
import subprocess as sp
import bibtexparser
import logging
from pathlib import Path
log = logging.getLogger(__name__)

def clear_bib(bibf, int_dir, poplist, verbose, strsubList):
  if verbose:
    log.info('Removing following fields from {}:\n{}'
             .format(bibf, ', '.join(poplist)))
  if not int_dir.is_dir():
    int_dir.mkdir()
  try:
    sh.copyfile(bibf, Path(int_dir, bibf.name + '.bak'))
  except Exception as e:
    log.warning('Could not create a backup of {}:\n{}'
                .format(bibf, e))

  try:
    with open(bibf, 'r') as bf:
      bib_db = bibtexparser.load(bf)
  except Exception as e:
    log.critical('Could not read {}:\n{}'.format(bibf, e))
    return -1

  if hasattr(bib_db, 'comments'):
    if 'Cleared by NeatLatex' in bib_db.comments:
      log.info('The bibtex file appears to be cleaned before. Skipping.')
      return
    else:
      bib_db.comments = ['Cleared by NeatLatex']
  else:
    log.info('Comments section not available in bibtex. Adding.')
    bib_db.comments = ['Cleared by NeatLatex']
  for e in bib_db.entries:
    for f in poplist:
      try:
        if e['ENTRYTYPE'] == 'misc' and f == 'url':
          continue
        e.pop(f)
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
    log.info('Error occurred while writing {}!\n'.format(bibf))
    return -1

  log.info('Bibliography file {} cleaned up.'.format(bibf))

def clear_wb(out_dir, int_dir, all_exts):
  flist = sh.os.listdir('.')
  if len(flist) == 0 or len(all_exts) == 0:
    return
  cleaned = True
  dirs = [out_dir, int_dir]
  for d in dirs:
    try:
      sh.rmtree(d)
    except Exception as e:
      cleaned = False
      log.error('Could not remove {}\n{}'.format(d, e))

  for f in flist:
    for ext in all_exts:
      if f.endswith(ext):
        try:
          sh.os.remove(f)
        except Exception as e:
          cleaned = False
          log.error('Could not remove {}\n{}'.format(f, e))

  if cleaned:
    log.info('Working directory cleaned up.')
  else:
    log.warning('Some files/directories could not be removed.')


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
      log.critical('{}'.format(e))
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
      log.critical('{}'.format(e))
      return -1


def tidyup(out_dir, output_exts, int_dir, interm_exts, verbose):
  log.info('Cleaning up the working directory...')
  fList = [f for f in out_dir.parent.iterdir()]
  moveFailed = False
  for f in fList:
    if f.suffix in output_exts:
      try:
        sh.move(f, Path(out_dir, f))
      except Exception as e:
        log.error('Could not move output files to {}\n{}'.format(out_dir, e))
        moveFailed = True

  if not moveFailed:
    log.debug('All {} file(s) moved to {}'
              .format(','.join(output_exts), out_dir))

  moveFailed = False
  for f in fList:
    if f.suffix in interm_exts:
      try:
        sh.move(f, Path(int_dir, f))
      except Exception as e:
        log.error('Could not move intermediate files to {}\n{}'
                  .format(int_dir, e))
        moveFailed = True

  if not moveFailed:
    log.debug('All {} file(s) moved to {}'
              .format(','.join(interm_exts), int_dir))


def main():
  logLevels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
  }

  ap = argp.ArgumentParser(description = 'Neatly compiles LaTex projects.',
                           prog = 'neatlatex')
  ap.add_argument('-p', '--proj', help = 'Project name to comile')
  ap.add_argument('-c', '--clear',
                  help = 'Clear the project directory from Aux or Log files.',
                  action = 'store_true')
  ap.add_argument('-l', '--log', help = 'Indicate log level',
                  choices = logLevels.keys(), default = 'info')
  ap.add_argument('-b', '--bibfile',
                  help = 'Bibtex file auto-generated by Mendeley.')
  ap.add_argument('-v', '--verbose', help = 'Toggles verbosity',
                  action = 'store_true')
  args = ap.parse_args()

  logLevel = logLevels.get(args.log.lower())
  if logLevel is None:
    raise ValueError('Log level must be one of{}'
                     .format(' | '.join(logLevels.keys())))
  logging.basicConfig(level = logLevel, format='%(levelname)s: %(message)s')
  log.debug('Log level: {}'.format(logLevel))  

  verbose = args.verbose
  output_exts = ['.pdf']  
  interm_exts = ['.aux', '.dvi', '.log', '.out', '.xcp', '.bbl', '.blg']
  bibexclude = ['abstract', 'keywords', 'file', 'comment', 'url']
  strSubList = [('{~}','~'), ('{\&}','&'), ('{\_}','_'), ('{\%}','%'),
                ('%20',' '), ('%5F', '_'), ('%7E', '~'),('%3D', '='),
                ('%2F', '/'), ('%2B', '+'),('%3B', ';')]
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
    log.critical('Must indicate main project .tex file to compile.')
    return
  if len(args.proj) <= 0:
    log.critical('Invalid project name.')
    return
  if not (Path(args.proj).exists() or
          Path(args.proj + '.tex').exists()):
    log.critical('File does not exist.')
    return
  
  if not out_dir.is_dir():
    out_dir.mkdir()
  if not int_dir.is_dir():
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
    log.info('Done! Find {} files(s) in {} directory.'
             .format(','.join(output_exts), out_dir))

    
if __name__ == '__main__':
  main()
