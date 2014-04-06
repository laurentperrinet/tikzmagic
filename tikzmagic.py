from IPython.core.magic import Magics, magics_class, line_magic, line_cell_magic
from IPython.core.display import Image

import os
import subprocess
import shlex
import shutil
import tempfile
import argparse

@magics_class
class TikzMagic(Magics):
        
    @line_magic
    def tikzfile(self, line):
        # parse input
        parser = argparse.ArgumentParser()
        parser.add_argument('input_file')
        parser.add_argument('-p', '--packages', default=None)
        parser.add_argument('-d', '--density', default=96, type=int)
        parser.add_argument('-f', '--format', default="png",
            choices=['png','jpg','jpeg','gif'])
        args = parser.parse_args(shlex.split(line))
    
        # get full file path to tikzfile
        file_path = os.getcwd() + '/' + args.input_file
    
        # get parts of the file path
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        file_base = os.path.splitext(file_name)[0]
    
        # output file
        output_file = file_dir + "/" + file_base + "." + args.format
        
        # convert to latex file format
        latex_data = self.format_latex(open(file_path, 'r').read(), packages=args.packages)
    
        return self.latex2image(latex_data, output_file, args.density)
    
    @line_cell_magic
    def tikz (self, line, cell=None):
        # parse input
        parser = argparse.ArgumentParser()
        parser.add_argument('tikz_commands', nargs='?', default=None)
        parser.add_argument('-o', '--out_file', required=True)
        parser.add_argument('-p', '--packages', default=None)
        parser.add_argument('-d', '--density', default=96, type=int)
        args = parser.parse_args(shlex.split(line))
        
        latex_data = ""
        
        if args.tikz_commands:
            latex_data = self.format_latex(self.wrap_tikz(args.tikz_commands), packages=args.packages)
            
        elif cell:
            latex_data = self.format_latex(self.wrap_tikz(cell), packages=args.packages)
            
        else:
            return "No Tikz found!"
            
        return self.latex2image(latex_data, args.out_file, args.density)
    
    
    # helper functions
    def wrap_tikz(self,tikz_commands):
        return '\\begin{tikzpicture}\n' + tikz_commands + '\n\\end{tikzpicture}'
    
    def format_latex(self, content, packages):
        latex_template = r'''\documentclass{standalone}
            \usepackage{tikz,amsmath,amssymb,amsfonts,xcolor}
            %(preamble)s
            \begin{document}
            %(content)s
            \end{document}
            '''
            
        preamble = ""
        if packages:
            preamble = "\\usepackage{%s}" % packages
        
        return latex_template % {'content':content, 'preamble':preamble}
                
    def latex2image(self, latex_data, output_file, density):

        try:
            # make a temporary directory
            temp_dir = tempfile.mkdtemp()
            temp_tex = temp_dir + "/tikzfile.tex"
            temp_pdf = temp_dir + "/tikzfile.pdf"
    
            # write tex file
            open(temp_tex,'w').write(latex_data)
    
            # run latex (in temp_directory), convert to image (in file_directory)
            self.run_latex(infile=temp_tex, outdir=temp_dir)
            
            if not os.path.isfile(temp_pdf):
                raise Exception("PDF was not produced, check your input.")
            
            self.run_convert(infile=temp_pdf, outfile=output_file, density=density)
        
            return Image(filename=output_file)
            
        except:
            raise
        finally:
            try:
                # remove temporary directory
                shutil.rmtree(temp_dir)
            except:
                pass

    # functions to run command line scripts
    def run_latex(self, infile, outdir):
        rep = {'infile':infile, 'outdir':outdir}
        cmd = "pdflatex -output-directory=%(outdir)s %(infile)s " % rep
        subprocess.call(shlex.split(cmd))
        
    def run_convert(self, infile, outfile, density):
        rep = {'density':density, 'infile':infile, 'outfile':outfile}
        cmd = "convert -density %(density)d %(infile)s '%(outfile)s'" % rep
        subprocess.call(shlex.split(cmd))
        
ip = get_ipython()
ip.register_magics(TikzMagic)
