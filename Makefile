.PHONY: test site serve all

SITE = $(patsubst content/%.md, site/%.html, $(shell find content -name "*.md")) \
	   $(patsubst content/%.jinja, site/%, $(shell find content -name "*.jinja")) \
	   $(patsubst content/%, site/%, $(shell find content -type f ! -name "*.md" ! -name "*jinja"))

all: site

testblocks: testblocks.hs
	ghc --make testblocks.hs

test/%.out.py: content/%.md testblocks
	mkdir -p $(shell dirname $@)
	./testblocks < $< > $@
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


site/%.html: content/%.md
	mkdir -p $(shell dirname $@)
	mkdir -p $(shell dirname deps/$@.d)
	./render.py $< --deps > deps/$@.d
	./render.py $< > $@

site/%.html: content/%.html
	mkdir -p $(shell dirname $@)
	mkdir -p $(shell dirname deps/$@.d)
	./render.py $< --deps > deps/$@.d
	./render.py $< > $@

site/%: content/%.jinja
	mkdir -p $(shell dirname $@)
	mkdir -p $(shell dirname deps/$@.d)
	./render.py $< --deps > deps/$@.d
	./render.py $< > $@

site/%: content/%
	mkdir -p $(shell dirname $@)
	mkdir -p $(shell dirname deps/$@)
	touch deps/$@.d
	cp $< $@

-include $(patsubst site/%, deps/site/%.d, $(SITE))

site: $(SITE)

watch:
	while true; do \
		make site; \
		inotifywait -qre close_write .; \
	done;

clean:
	rm -rf test site deps
	rm -f testblocks *.hi *.o *.pyc
