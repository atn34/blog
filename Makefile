.PHONY: test site

testblocks:
	ghc --make testblocks.hs

test/%.py: content/%.md testblocks
	mkdir -p $(shell dirname $@)
	./testblocks < $< > $@

test: $(patsubst content/%.md, test/%.py, $(shell find content -name "*.md"))
	for test in $^ ; do \
		python $$test -v ; \
	done

site/%.html: content/%.md default.html
	mkdir -p $(shell dirname $@)
	pandoc --template default.html --standalone < $< > $@

site/%.html: content/%.mdjinja $(shell find content -name "*.md") jinja.py default.html
	mkdir -p $(shell dirname $@)
	python jinja.py < $< | pandoc --template default.html --standalone > $@

site/%: content/%.jinja $(shell find content -name "*.md") jinja.py
	mkdir -p $(shell dirname $@)
	python jinja.py < $< > $@

site/%: content/%
	mkdir -p $(shell dirname $@)
	cp $< $@

site: $(patsubst content/%.md, site/%.html, $(shell find content -name "*.md")) \
	$(patsubst content/%.mdjinja, site/%.html, $(shell find content -name "*.mdjinja")) \
	$(patsubst content/%.jinja, site/%, $(shell find content -name "*.jinja")) \
	$(patsubst content/%, site/%, $(shell find content -name "*.css"))

serve: site
	cd site && python -m SimpleHTTPServer

clean:
	rm -rf test site
	rm -f testblocks *.hi *.o *.pyc
