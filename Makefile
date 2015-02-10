.PHONY: test site serve all

all: site

test/%.out.py: content/%.md
	mkdir -p $(shell dirname $@)
	./render.py test $< > $@
	chmod +x $@

test/%: content/%
	mkdir -p $(shell dirname $@)
	cp $< $@

test: $(patsubst content/%.md, test/%.out.py, $(shell find content -name "*.md")) \
	$(patsubst content/%, test/%, $(shell find content -type f ! -name "*.md" ! -name "*jinja")) \
	render_test.py
	@errors=0; \
	pwd=$$(pwd); \
	for test in $^ ; do \
		if [ -x $$test ] ; then \
			echo running $$test; \
			(cd $$(dirname $$test) && exec $$pwd/$$test) || errors=`expr $$errors + 1`; \
			count=`expr $$count + 1`; \
		fi; \
	done; \
	echo `expr $$count - $$errors` of $$count tests pass; \
	exit $$errors


site:
	mkdir -p site
	./render.py content site

watch:
	while true; do \
		./render.py --dev content site; \
		echo done; \
		inotifywait -qre close_write .; \
	done;

clean:
	rm -rf test site/* *.pyc
