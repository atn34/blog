.PHONY: test site

testblocks:
	ghc --make testblocks.hs

test/%.out.py: content/%.md testblocks
	mkdir -p test
	./testblocks < $< > $@

test: $(patsubst content/%.md, test/%.out.py, $(shell ls content/*.md))
	for test in $^ ; do \
		python $$test -v ; \
	done

site/%.html: content/%.md
	mkdir -p site
	pandoc --standalone < $< > $@

site: $(patsubst content/%.md, site/%.html, $(shell ls content/*.md))

clean:
	rm -rf test site
	rm -f testblocks testblocks.hi testblocks.o
