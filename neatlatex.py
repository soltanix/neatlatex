#!/usr/bin/env python2

import argparse as argp
import shutil as sh
import subprocess as sp
import ntpath

def main():
  ap = argp.ArgumentParser(description = 'Neatly compiles or cleans LaTex projects.')
  ap.add_argument('p', help = 'Project name')
  ap.add_argument('-c', '--clean', help = 'Clear the project directory from Aux or Log files.', action = 'store_true')

  args = ap.parse_args()

  out_dir = './output'
  int_dir = './auxlog'
  output_exts = ['.pdf']  
  interm_exts = ['.aux', '.dvi', '.log', '.out', '.xcp', '.bbl', '.blg']
  all_exts = output_exts + interm_exts
  
  if args.clean:
    try:
      sh.rmtree(out_dir)
      sh.rmtree(int_dir)  
      print 'Aux and Log directories as well as the output have been removed.'
      
    except Exception as e:
      if e.startswith('[Errno 2]'):
        pass
      else:
        print 'Error:', e
        
    finally:
      flist = sh.os.listdir('.')
      for f in flist:
        for ext in all_exts:
          if f.endswith(ext):
            sh.os.remove(f)
    
      return

  if not sh.os.path.exists(out_dir):
    sh.os.mkdir(out_dir)
  if not sh.os.path.exists(int_dir):
    sh.os.mkdir(int_dir)

  pname = args.p
  proc = sp.Popen('latex '+pname, shell=True, stderr=sp.STDOUT)
  proc.wait()
  proc = sp.Popen('bibtex '+pname, shell=True, stderr=sp.STDOUT)
  proc.wait()
  proc = sp.Popen('latex '+pname, shell=True, stderr=sp.STDOUT)
  proc.wait()
  proc = sp.Popen('pdflatex '+pname, shell=True, stderr=sp.STDOUT)
  proc.wait()
  
  flist = sh.os.listdir('.')
  for oext in output_exts:
    for f in flist:
      if f.endswith(oext):
        sh.move(f, out_dir+'/'+ntpath.basename(f))
  
  flist = sh.os.listdir('.')
  for iext in interm_exts:
    for f in flist:
      if f.endswith(iext):
        sh.move(f, int_dir+'/'+ntpath.basename(f))

  sh.os.popen('xdg-open '+out_dir+'/'+pname+'.pdf')

  

if __name__ == '__main__':
  main()
