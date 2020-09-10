# generates a header for the resulting LaTeX file
def generateHeader(name, author, pageColor, textColor, width, height, margin):
    header = """\\documentclass{{book}}
    \\usepackage[utf8]{{inputenc}}
    \\usepackage[T1]{{fontenc}}
    \\usepackage{{graphicx}}
    \\usepackage[margin={5}px,paperwidth={3}px,paperheight={4}px,footskip=0px]{{geometry}}
    \\usepackage{{xcolor}}
    \\usepackage{{pagecolor}}
    \\usepackage{{fancyhdr}}
    \\usepackage{{sectsty}}
    \\usepackage{{tocloft}}

    \\renewcommand\\cftchapfont{{\\LARGE\\bfseries}}
    \\renewcommand\\cftsecfont{{\\LARGE}}
    
    \\renewcommand\\cftchappagefont{{\\LARGE\\bfseries}}
    \\renewcommand\\cftsecpagefont{{\\LARGE}}

    \\sectionfont{{\\fontsize{{50}}{{15}}\\selectfont}}
    \\setcounter{{secnumdepth}}{{0}}

    \\setlength{{\\lineskip}}{{0pt}}

    \\renewcommand\\cftchapafterpnum{{\\vskip25pt}}
    \\renewcommand\\cftsecafterpnum{{\\vskip25pt}}
    
    \\def \\ifempty#1{{\\def\\temp{{#1}}\\ifx\\temp\\empty }}
    
    \\newcommand{{\\comic}}[3]{{
        \\begingroup
        \\raggedbottom
        \\par
        \\setlength{{\\baselineskip}}{{0pt}}
        \\begin{{samepage}}

            \\ifempty{{#1}}
            \\else
                \\vspace{{10px}}
                {{\\fontfamily{{qag}}\\selectfont{{\\huge#1\\\\}}}}
                \\nopagebreak
                \\vspace{{2px}}
            \\fi

            \\centerline{{\\includegraphics{{#2}}}}

            \\ifempty{{#3}}
            \\else
                \\vspace{{5px}}
                \\nopagebreak
                {{\\Large\\textit{{\\newline #3\\newline}}\\\\}}
                \\vspace{{10px}}
            \\fi

        \\end{{samepage}}
        \\par
        \\endgroup
    }}
    
    \\fancypagestyle{{plain}}{{
        \\fancyhf{{}}
        \\fancyfoot[C]{{\\sffamily\\fontsize{{20pt}}{{20pt}}
        \\selectfont\\textcolor{{{2}}}\\thepage}}
        \\renewcommand{{\\headrulewidth}}{{0pt}}
        \\renewcommand{{\\footrulewidth}}{{0pt}}}}
    \\pagestyle{{plain}}
    
    \\definecolor{{bgcolor}}{{RGB}}{{{6},{7},{8}}}
    
    \\title{{\\fontsize{{50}}{{20}}\\selectfont{{{0}}}}}
    \\author{{\\Large{{{1}}}}}
    \\date {{}}
    
    \\begin{{document}}
    \\pagecolor{{bgcolor}}
    \\color{{{2}}}
    \\maketitle
    \\noindent\n""".format(
        name,           #{0}
        author,         #{1}
        textColor,      #{2}
        width,          #{3}
        height,         #{4}
        margin,         #{5}
        pageColor[0],   #{6}
        pageColor[1],   #{7}
        pageColor[2])   #{8}
        

    with open("header.txt", "w") as headerFile:
        headerFile.write(header)