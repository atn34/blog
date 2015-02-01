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

site/%.html: content/%.md
	mkdir -p $(shell dirname $@)
	pandoc --standalone < $< > $@

site: $(patsubst content/%.md, site/%.html, $(shell find content -name "*.md"))

clean:
	rm -rf test site
	rm -f testblocks testblocks.hi testblocks.o
