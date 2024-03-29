noinst_LIBRARIES += python/libenigma_python.a

python_libenigma_python_a_SOURCES = \
	python/connections.cpp \
	python/python.cpp \
	python/pythonconfig.cpp \
	python/python_helpers.cpp

pythonincludedir = $(pkgincludedir)/lib/python
pythoninclude_HEADERS = \
	python/connections.h \
	python/python.h \
	python/pythonconfig.h \
	python/python_helpers.h \
	python/swig.h

nodist_python_libenigma_python_a_SOURCES = \
	python/enigma_python.cpp

EXTRA_DIST += \
	python/enigma_python.i \
	python/python_service.i \
	python/python_dvb.i \
	python/python_base.i \
	python/python_console.i \
	python/python_pmt.i \
	python/python/pcore.i

@AMDEP_TRUE@@am__include@ @am__quote@./$(DEPDIR)/python/enigma_python.Pcpp@am__quote@

@ENABLE_SH_TRUE@sh_def = -D__sh__

.i.cpp:
	$(AM_V_GEN)$(SWIG) $(AX_SWIG_PYTHON_OPT) -MT $@ -MD -MF $(DEPDIR)/$*.Tpo -I$(top_srcdir) $(sh_def) -O -nortti -nothreads -o $@ $<
	$(AM_V_at)mv -f $(DEPDIR)/$*.Tpo $(DEPDIR)/$*.Pcpp
	$(AM_V_at)sed -i 's/_ENUMS\([(),]\)/\1/g' python/enigma.py
# more details about why the sed transform is needed can be found in lib/service/iservice.h

python/enigma.py: python/enigma_python.cpp

CLEANFILES += python/enigma.py python/enigma_python.cpp

nobase_install_PYTHON += \
	python/enigma.py
