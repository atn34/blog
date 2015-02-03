.PHONY: test site serve

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


site/%.html: content/%.md $(shell find content -name "*.md") render.py default.html
	mkdir -p $(shell dirname $@)
	python render.py < $< | pandoc --template default.html --standalone > $@

site/%: content/%.jinja $(shell find content -name "*.md") render.py
	mkdir -p $(shell dirname $@)
	python render.py < $< > $@

site/%: content/%
	mkdir -p $(shell dirname $@)
	cp $< $@

site: $(patsubst content/%.md, site/%.html, $(shell find content -name "*.md")) \
	$(patsubst content/%.jinja, site/%, $(shell find content -name "*.jinja")) \
	$(patsubst content/%, site/%, $(shell find content -type f ! -name "*.md" ! -name "*jinja"))

watch:
	while true; do \
		make site; \
		inotifywait -qre close_write .; \
	done;

clean:
	rm -rf test site
	rm -f testblocks *.hi *.o *.pyc
