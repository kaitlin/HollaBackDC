# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d doc-build/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) docs

.PHONY: help clean html web htmlhelp latex changes linkcheck

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  web       to make files usable by Sphinx.web"
	@echo "  htmlhelp  to make HTML files and a HTML help project"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  changes   to make an overview over all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"
	@echo
	@echo "  read      to open html version in browser"

clean:
	-rm -rf doc-build/*

html:
	mkdir -p doc-build/html doc-build/doctrees
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) doc-build/html
	@echo
	@echo "Build finished. The HTML pages are in doc-build/html."

read: html
	open doc-build/html/index.html

web:
	mkdir -p doc-build/web doc-build/doctrees
	$(SPHINXBUILD) -b web $(ALLSPHINXOPTS) doc-build/web
	@echo
	@echo "Build finished; now you can run"
	@echo "  python -m sphinx.web doc-build/web"
	@echo "to start the server."

htmlhelp:
	mkdir -p doc-build/htmlhelp doc-build/doctrees
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) doc-build/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in doc-build/htmlhelp."

latex:
	mkdir -p doc-build/latex doc-build/doctrees
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) doc-build/latex
	@echo
	@echo "Build finished; the LaTeX files are in doc-build/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

changes:
	mkdir -p doc-build/changes doc-build/doctrees
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) doc-build/changes
	@echo
	@echo "The overview file is in doc-build/changes."

linkcheck:
	mkdir -p doc-build/linkcheck doc-build/doctrees
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) doc-build/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in doc-build/linkcheck/output.txt."
