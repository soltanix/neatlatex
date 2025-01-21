#!/usr/bin/env python3

import argparse as argp
import shutil as sh
import subprocess as sp
import bibtexparser
import platform
import sys
import logging
from pathlib import Path
log = logging.getLogger(__name__)

def clear_bib(bibFile, intermDir, poplist, verbose, strsubList):
  if verbose:
    log.info('Removing following fields from {}:\n{}'
             .format(bibFile, ', '.join(poplist)))
  if not intermDir.is_dir():
    intermDir.mkdir()
  try:
    sh.copyfile(bibFile, Path(intermDir, bibFile.name + '.bak'))
  except Exception as e:
    log.warning('Could not create a backup of {}:\n{}'
                .format(bibFile, e))

  try:
    with open(bibFile, 'r') as bf:
      bibDB = bibtexparser.load(bf)
  except Exception as e:
    log.critical('Could not read {}:\n{}'.format(bibFile, e))
    return -1

  if hasattr(bibDB, 'comments'):
    if 'Cleared by NeatLatex' in bibDB.comments:
      log.info('The bibtex file appears to be cleaned before. Skipping.')
      return
    else:
      bibDB.comments = ['Cleared by NeatLatex']
  else:
    log.info('Comments section not available in bibtex. Adding.')
    bibDB.comments = ['Cleared by NeatLatex']
  for e in bibDB.entries:
    for f in poplist:
      try:
        if e['ENTRYTYPE'] == 'misc' and f == 'url':
          continue
        e.pop(f)
      except:
        continue

  if len(strsubList) > 0:
    for e in bibDB.entries:
      if 'url' in e.keys():
        for s in strsubList:
          e['url'] = e['url'].replace(s[0],s[1])

  try:
    with open(bibFile,'w') as bf:
      bibtexparser.dump(bibDB, bf)
  except Exception as e:
    log.info('Error occurred while writing {}!\n'.format(bibFile))
    return -1

  log.info('Bibliography file {} cleaned up.'.format(bibFile))

def clear_wb(outDir, intermDir, allExts):
  pwdFileList = [f for f in Path().iterdir()]
  allExtTuples = tuple(e for e in allExts)
  if len(pwdFileList) == 0 or len(allExts) == 0:
    return
  cleaned = True
  dirs = [outDir, intermDir]
  for d in dirs:
    try:
      sh.rmtree(d)
    except Exception as e:
      cleaned = False
      log.error('Could not remove {}\n{}'.format(d, e))

  for f in pwdFileList:
    if f.name.endswith(allExtTuples):
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
      log.info('[done] pdflatex pass 1')
      if Path(pname+'.bcf') in Path().iterdir():
        proc = sp.Popen('biber '+pname, shell=True, stderr=sp.STDOUT)
        proc.wait()
        log.info('[done] biber')
      else:
        proc = sp.Popen('bibtex '+pname, shell=True, stderr=sp.STDOUT)
        proc.wait()
        log.info('[done] bibtex')
      proc = sp.Popen('pdflatex '+pname, shell=True, stderr=sp.STDOUT)
      proc.wait()
      log.info('[done] pdflatex pass 2')
      proc = sp.Popen('pdflatex '+pname, shell=True, stderr=sp.STDOUT)
      proc.wait()
      log.info('[done] pdflatex pass 3')
    except KeyboardInterrupt:
      sys.stdout.flush()
      sys.exit(-1)
    except Exception as e:
      log.critical('{}'.format(e))
      return -1

  else:
    try:
      proc = sp.Popen(['pdflatex', pname], stdout=sp.PIPE)
      proc.communicate()
      log.info('[done] pdflatex pass 1')
      if Path(pname+'.bcf') in Path().iterdir():
        proc = sp.Popen(['biber', pname], stdout=sp.PIPE)
        proc.communicate()
        log.info('[done] biber')
      else:
        proc = sp.Popen(['bibtex', pname], stdout=sp.PIPE)
        proc.communicate()
        log.info('[done] bibtex')
      proc = sp.Popen(['pdflatex', pname], stdout=sp.PIPE)
      proc.communicate()
      log.info('[done] pdflatex pass 2')
      proc = sp.Popen(['pdflatex', pname], stdout=sp.PIPE)
      proc.communicate()
      log.info('[done] pdflatex pass 3')
    except KeyboardInterrupt:
      sys.stdout.flush()
      sys.exit(-1)      
    except Exception as e:
      log.critical('{}'.format(e))
      return -1


def tidyup(outDir, outputExts, intermDir, intermExts, verbose):
  log.info('Cleaning up the working directory...')
  fList = [f for f in outDir.parent.iterdir()]
  outputExtTuples = tuple(e for e in outputExts)
  intermExtTuples = tuple(e for e in intermExts)
  moveFailed = False
  for f in fList:
    if f.name.endswith(outputExtTuples):
      try:
        sh.move(f, Path(outDir, f))
      except Exception as e:
        log.error('Could not move output files to {}\n{}'.format(outDir, e))
        moveFailed = True
  if not moveFailed:
    log.debug('All {} file(s) moved to {}'
              .format(','.join(outputExts), outDir))

  moveFailed = False
  for f in fList:
    if f.name.endswith(intermExtTuples):
      try:
        sh.move(f, Path(intermDir, f))
      except Exception as e:
        log.error('Could not move intermediate files to {}\n{}'
                  .format(intermDir, e))
        moveFailed = True
  if not moveFailed:
    log.debug('All {} file(s) moved to {}'
              .format(','.join(intermExts), intermDir))


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
  outputExts = ['.pdf']  
  intermExts = ['.aux', '.dvi', '.log', '.out', '.xcp', '.bbl', '.blg',
                 '.lof', '.lot', '.run.xml', '.bcf', '.toc', '.fdb_latexmk',
                '.fls', '.out.ps', '.tdo']
  bibexclude = ['abstract', 'keywords', 'file', 'comment', 'url']
  strSubList = [('{~}','~'), ('{\\&}','&'), ('{\\_}','_'), ('{\\%}','%'),
                ('%20',' '), ('%5F', '_'), ('%7E', '~'),('%3D', '='),
                ('%2F', '/'), ('%2B', '+'),('%3B', ';')]
  allExts = outputExts + intermExts

  if args.proj:
    proj_dir = Path(args.proj).parent
  else:
    proj_dir = Path('.')
  outDir = Path(proj_dir, 'output')
  intermDir = Path(proj_dir, 'auxlog')

  if args.clear:
    clear_wb(outDir, intermDir, allExts)
    return
  elif args.bibfile:
    bibFile = Path(args.bibfile)
    res = clear_bib(bibFile, intermDir, bibexclude, verbose, strSubList)
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
  
  if not outDir.is_dir():
    outDir.mkdir()
  if not intermDir.is_dir():
    intermDir.mkdir()

  pname = args.proj.strip('.tex')
  res = makepdf(pname, verbose)
  if res == -1:
    return res
  
  tidyup(outDir, outputExts, intermDir, intermExts, verbose)

  # # Passive aggressive helper
  # if verbose:
  #   while True:
  #     seepdf = False
  #     wannasee = input('Do you want to see the output pdf file or what? (Yes/no): ')
  #     if wannasee == '' or wannasee == None:
  #       print('No answer!.. OK. Here it is just in case.')
  #       seepdf = True
  #     elif wannasee in ['Yes', 'yes', 'y', 'Y']:
  #       print('\nHere is your gloriuos work.')
  #       seepdf = True
  #     elif wannasee == 'YES':
  #       print('\nAlright man.. Calm down! Here\'s your damn paper.. Have a blast!')
  #       seepdf = True
  #     elif wannasee in ['No', 'no', 'N', 'n']:
  #       print('\nSure.. you made me do all that and you don\'t even wanna see it.. No problem! It\'s fine.. It\'s totally fine..')
  #     elif wannasee == 'NO':
  #       print('\nYou know what! I don\'t wanna see it either! I don\'t even CARE what it looks like!')
  #     elif wannasee.lower() == 'or what':
  #       print('\nCome come, I clap for you.. you veeery funny ah!')
  #     else:
  #       print('\nDid you really think the person who wrote this script made me smart enough to understand what you\'re saying? Yes or No man.. YES or NO!\nDamn it.. every day a smart ass! every damn day!')
  #       continue

  # Passive aggressive helper
  if verbose:
    while True:
      seepdf = False
      wannasee = input('Open output pdf file? (Yes/no): ')
      if wannasee == '' or wannasee == None:
        seepdf = True
      elif wannasee.lower() in ['yes', 'y']:
        print('\nHere is your gloriuos work!')
        seepdf = True
      elif wannasee.lower() in ['no', 'n']:
        break
      else:
        print('Invalid input.')
        continue

      if seepdf:
        outpath = Path(outDir, pname+'.pdf').as_posix()
        if platform.system() == 'Darwin':
          sp.call(('open', outpath))
        elif platform.system() == 'Windows':
          os.startfile(outpath)
        else:
          sp.call(('xdg-open', outpath))
        break
      else:
        break

  else:
    log.info('Done! Find {} files(s) in {} directory.'
             .format(','.join(outputExts), outDir))

    
if __name__ == '__main__':
  main()
