filename=hoot

pdf: 
	pdflatex ${filename}
	bibtex ${filename}||true
	mv prop.bbl prop.bblx
	perl bblfix.pl < prop.bblx > prop.bbl
	pdflatex ${filename}
	pdflatex ${filename}

read:
	open ${filename}.pdf &

clean:
	rm -f ${filename}.ps ${filename}.pdf ${filename}.log ${filename}.aux ${filename}.out ${filename}.bbl ${filename}.blg ${filename}.bblx
