filename=hoot

#pdf: ps
#	ps2pdf ${filename}.ps
#pdf: dvi
#	dvipdf -t letter ${filename}.dvi

#ps: dvi
#	dvips ${filename}.dvi

#	pdflatex -t letter ${filename}
#	bibtex ${filename}||true
#	pdflatex -t letter ${filename}
#	pdflatex -t letter ${filename}

#dvi:
#	latex ${filename}
#	bibtex ${filename}||true
#	latex ${filename}
#	latex ${filename}

pdf:
	pdflatex ${filename}
	mv ${filename}.bbl ${filename}.bblx
	perl bblfix.pl < ${filename}.bblx > ${filename}.bbl
	pdflatex ${filename}
	pdflatex ${filename}
	pdflatex ${filename}

read:
	open ${filename}.pdf &

clean:
	rm -f ${filename}.ps ${filename}.pdf ${filename}.log ${filename}.aux ${filename}.out ${filename}.bbl ${filename}.blg ${filename}.bblx

