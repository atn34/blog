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

site/%.html: content/%.md.jinja $(shell find content -name "*.md") jinja.py default.html
	mkdir -p $(shell dirname $@)
	python jinja.py < $< | pandoc --template default.html --standalone > $@

site/%: content/%
	cp $< $@

site: $(patsubst content/%.md, site/%.html, $(shell find content -name "*.md")) \
	$(patsubst content/%.md.jinja, site/%.html, $(shell find content -name "*.md.jinja")) \

clean:
	rm -rf test site
	rm -f testblocks testblocks.hi testblocks.o
