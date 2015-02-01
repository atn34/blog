.PHONY: test site

testblocks:
	ghc --make testblocks.hs

test/%.out.py: content/%.md testblocks
	mkdir -p test
	./testblocks < $< > $@

test: $(patsubst content/%.md, test/%.out.py, $(shell find content -name "*.md"))
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
