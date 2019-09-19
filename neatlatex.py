#!/usr/bin/env python2

import argparse as argp
import shutil as sh
import subprocess as sp
import ntpath
import bibtexparser


def clear_bib(bibf, int_dir, poplist, verbose):

  if verbose:
    print 'Cleaning the bibtex file', bibf, 'from fields like',
    for f in poplist:
      print f,
    print '.'
  sh.copyfile(bibf, int_dir+'/'+bibf+'.bak')
  
  with open(bibf, 'r') as bf:
    bib_db = bibtexparser.load(bf)

  for e in bib_db.entries:
    for f in poplist:
      e.pop(f, None)
  
  with open(bibf,'w') as bf:
    bibtexparser.dump(bib_db, bf)
  

def clear_wb(out_dir, int_dir, all_exts):
    
  flist = sh.os.listdir('.')
  if len(flist) == 0 or len(all_exts) == 0:
    return

  dirs = [out_dir, int_dir]

  for d in dirs:
    try:
      sh.rmtree(d)
    except Exception as e:
      print str(e).replace('Errno 2', 'Warning')
    
  for f in flist:
    for ext in all_exts:
      if f.endswith(ext):
        sh.os.remove(f)
      

def makepdf(pname, verbose):

  if verbose:
    proc = sp.Popen('latex '+pname, shell=True, stderr=sp.STDOUT)
    proc.wait()
    
    proc = sp.Popen('bibtex '+pname, shell=True, stderr=sp.STDOUT)
    proc.wait()
    
    proc = sp.Popen('latex '+pname, shell=True, stderr=sp.STDOUT)
    proc.wait()
    
    proc = sp.Popen('pdflatex '+pname, shell=True, stderr=sp.STDOUT)
    proc.wait()

  else:
    proc = sp.Popen(['latex', pname], stdout=sp.PIPE)
    proc.communicate()

    proc = sp.Popen(['bibtex', pname], stdout=sp.PIPE)
    proc.communicate()

    proc = sp.Popen(['latex', pname], stdout=sp.PIPE)
    proc.communicate()

    proc = sp.Popen(['pdflatex', pname], stdout=sp.PIPE)
    proc.communicate()
    

def tidyup(out_dir, output_exts, int_dir, interm_exts, verbose):
  if verbose:
    print '\nCleaning up the working directory...'

  if verbose:
    print 'Moving all',
    for e in output_exts:
      print e+',',
    print 'to', out_dir
  
  flist = sh.os.listdir('.')
  for oext in output_exts:
    for f in flist:
      if f.endswith(oext):
        sh.move(f, out_dir+'/'+ntpath.basename(f))

  if verbose:
    print 'Moving all',
    for e in interm_exts:
      print e+',',
    print 'to', int_dir
          
  flist = sh.os.listdir('.')
  for iext in interm_exts:
    for f in flist:
      if f.endswith(iext):
        sh.move(f, int_dir+'/'+ntpath.basename(f))

        

def main():
  ap = argp.ArgumentParser(description = 'Neatly compiles or cleans LaTex projects.')
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
  bibexclude = ['abstract', 'keywords', 'file', 'comments']
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

  if bibfile:
    clear_bib(bibfile, int_dir, bibexclude, verbose)
    return

  pname = args.p
  makepdf(pname, verbose)
  tidyup(out_dir, output_exts, int_dir, interm_exts, verbose)

  if verbose:
    while True:
      seepdf = False
      wannasee = raw_input('Do you want to see the output pdf file or what? (Yes/no): ')
      if wannasee == '':
        print 'Well here silence is consent!'
        seepdf = True
      if wannasee in ['Yes', 'yes', 'y', 'Y']:
        print '\nOoh, look what you made me do\nLook what you made me do\nLook what you just made me do\nLook what you just made me do..'
        seepdf = True
      elif wannasee == 'YES':
        print '\nAlright man.. Calm down! Here\'s your damn paper.. Have a blast!'
        seepdf = True
      elif wannasee in ['No', 'no', 'N', 'n']:
        print '\nSure.. you made me do all that and you don\'t even wanna see it.. No problem! It\'s fine.. It\'s totally fine..'
      elif wannasee == 'NO':
        print '\nYou know what! I don\'t wanna see it either! I don\'t even CARE what\'s inside!'
      elif wannasee.lower() == 'or what':
        print '\nCome come, I give you I give you.. you veeery funny ah!'
      else:
        print '\nDid you really think the person who wrote this script made me smart enough to understand what you\'re saying? Yes or No man.. YES or NO!\nDamn it.. every day a smart ass! every damn day!'
        continue

      if seepdf:
        sh.os.popen('xdg-open '+out_dir+'/'+pname+'.pdf')
        break
      else:
        break
  else:
    print 'Done. Find the output file (.pdf) at', out_dir

if __name__ == '__main__':
  main()
