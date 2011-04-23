filename=hoot

pdf: 
	pdflatex ${filename}
	bibtex ${filename}||true
	mv ${filename}.bbl ${filename}.bblx
	perl bblfix.pl < ${filename}.bblx > ${filename}.bbl
	pdflatex ${filename}
	pdflatex ${filename}
	pdflatex ${filename}

read:
	open ${filename}.pdf &

clean:
	rm -f ${filename}.ps ${filename}.pdf ${filename}.log ${filename}.aux ${filename}.out ${filename}.bbl ${filename}.blg ${filename}.bblx
