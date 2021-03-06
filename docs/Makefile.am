IMAGE_FILES = images/asciidoc.png \
	images/hostedby.png \
	images/nut_layering.png \
	images/nut-logo.png \
	images/note.png \
	images/warning.png \
	images/blue-arrow.png \
	images/simple.png \
	images/advanced.png \
	images/bigbox.png \
	images/bizarre.png \
	images/old-cgi.png

# Only track here the local deps
SHARED_DEPS = nut-names.txt asciidoc.conf

USER_MANUAL_DEPS = acknowledgements.txt cables.txt config-notes.txt	\
 configure.txt download.txt documentation.txt features.txt history.txt	\
 outlets.txt scheduling.txt security.txt support.txt user-manual.txt

DEVELOPER_GUIDE_DEPS = contact-closure.txt design.txt developers.txt	\
 developer-guide.txt hid-subdrivers.txt macros.txt new-clients.txt	\
 new-drivers.txt net-protocol.txt nutdrv_qx-subdrivers.txt	\
 snmp-subdrivers.txt sock-protocol.txt

CABLES_DEPS = cables/apc-rs500-serial.txt	\
 cables/apc.txt cables/ge-imv-victron.txt cables/imv.txt		\
 cables/mgeups.txt cables/powerware.txt cables/repotec.txt		\
 cables/sms.txt

CABLES_IMAGES = images/cables/73-0724.png images/cables/940-0024C.jpg \
 images/cables/belkin-f6cx-rkm-xu-cable.jpg images/cables/Lansafecable.jpg \
 images/cables/mac-940-0024C.png images/cables/mge-66049.png \
 images/cables/mge-db9-rj12.jpg images/cables/mge-db9-rj45.jpg \
 images/cables/mge-usb-rj45.jpg \
 images/cables/SOLA-330.png

ALL_TXT_SRC = nut-names.txt $(USER_MANUAL_DEPS) $(DEVELOPER_GUIDE_DEPS) \
 $(CABLES_DEPS) FAQ.txt nut-qa.txt packager-guide.txt snmp.txt

NUT_SPELL_DICT = nut.dict
EXTRA_DIST = $(ALL_TXT_SRC) $(SHARED_DEPS) $(IMAGE_FILES) \
 $(CABLES_IMAGES) $(NUT_SPELL_DICT) \
 common.xsl xhtml.xsl chunked.xsl

ASCIIDOC_HTML_SINGLE = user-manual.html \
	developer-guide.html \
	packager-guide.html \
	FAQ.html

ASCIIDOC_HTML_CHUNKED = user-manual.chunked \
	developer-guide.chunked \
	packager-guide.chunked \
	FAQ.html

ASCIIDOC_PDF = user-manual.pdf \
	developer-guide.pdf \
	packager-guide.pdf \
	cables.pdf	\
	FAQ.pdf

SUBDIRS = man
SUFFIXES = .txt .html .pdf

all: doc

doc: @DOC_BUILD_LIST@

pdf: $(ASCIIDOC_PDF)
# also build the HTML manpages with these targets
html-single: $(ASCIIDOC_HTML_SINGLE)
html-chunked: $(ASCIIDOC_HTML_CHUNKED)

clean-local:
	rm -rf *.pdf *.html *.chunked docbook-xsl.css *.bak

### TODO: automatic dependency generation
# Add other directory deps (not for local EXTRA_DIST) and generated contents
FULL_USER_MANUAL_DEPS = $(USER_MANUAL_DEPS) $(SHARED_DEPS) ../README \
	../INSTALL.nut ../UPGRADING ../TODO ../scripts/ufw/README
FULL_DEVELOPER_GUIDE_DEPS = $(DEVELOPER_GUIDE_DEPS) $(SHARED_DEPS) \
	../scripts/augeas/README ../TODO ../lib/README \
	../tools/nut-scanner/README

user-manual.html user-manual.chunked user-manual.pdf: $(FULL_USER_MANUAL_DEPS)
developer-guide.html developer-guide.chunked developer-guide.pdf: $(FULL_DEVELOPER_GUIDE_DEPS)
packager-guide.html packager-guide.chunked packager-guide.pdf: packager-guide.txt asciidoc.conf

# Note: without the "-v", asciidoc (circa 8.6.2) sometimes hangs when
# generating the chunked HTML. In this case, export the environment
# variable ASCIIDOC_VERBOSE to "-v", ie:
#   $ ASCIIDOC_VERBOSE=-v make
A2X_COMMON_OPTS = $(ASCIIDOC_VERBOSE) --attribute icons \
    --xsltproc-opts "--nonet" \
    --xsltproc-opts "--stringparam nut.localdate \"`TZ=UTC date +%Y-%m-%d`\"" \
    --xsltproc-opts "--stringparam nut.localtime \"`TZ=UTC date +%H:%M:%S`\"" \
    --xsltproc-opts "--stringparam nut.nutversion \"@PACKAGE_VERSION@\"" \
    --attribute iconsdir=$(srcdir)/images \
    --attribute=badges \
    --attribute=external_title \
    --attribute tree_version=@TREE_VERSION@ \
    -a toc -a numbered --destination-dir=.

.txt.html: common.xsl xhtml.xsl
	$(A2X) $(A2X_COMMON_OPTS) --attribute=xhtml11_format --format=xhtml --xsl-file=$(srcdir)/xhtml.xsl $<

.txt.chunked: common.xsl chunked.xsl
	$(A2X) $(A2X_COMMON_OPTS) --attribute=chunked_format --format=chunked --xsl-file=$(srcdir)/chunked.xsl $<

.txt.pdf: docinfo.xml
	$(A2X) $(A2X_COMMON_OPTS) --attribute=pdf_format --format=pdf -a docinfo1 $<

if HAVE_ASPELL
# Non-interactively spell check all documentation source files.
# This is useful for Buildbot and automated QA processing
# FIXME: how to present output (std{out,err}, single file or per target)?
SPELLCHECK_SRC = $(ALL_TXT_SRC) ../README ../INSTALL.nut ../UPGRADING  ../NEWS \
	../TODO ../scripts/ufw/README ../scripts/augeas/README ../lib/README \
	../tools/nut-scanner/README

spellcheck: 
	@for docsrc in $(SPELLCHECK_SRC); do \
		echo "Spell checking on $$docsrc"; \
		LANG=C $(ASPELL) -a -t -p $(NUT_SPELL_DICT) < $$docsrc | grep [^*]; \
	done
# Interactively spell check all documentation source files
spellcheck-interactive: 
	@for docsrc in $(SPELLCHECK_SRC); do\
		echo "Spell checking on $$docsrc"; \
		LANG=C $(ASPELL) check -p $(NUT_SPELL_DICT) $$docsrc; \
	done
else !HAVE_ASPELL
spellcheck:
	@echo "Documentation spell check not available since 'aspell' was not found."
spellcheck-interactive:
	@echo "Documentation spell check not available since 'aspell' was not found."
endif !HAVE_ASPELL

.PHONY: html html-single pdf
