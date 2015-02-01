.PHONY: test

testblocks:
	ghc --make testblocks.hs

test/%.out.py: content/%.md testblocks
	mkdir -p test
	./testblocks < $< > $@

test: $(patsubst content/%.md, test/%.out.py, $(shell ls content/*.md))
	for test in $^ ; do \
		python $$test -v ; \
	done

clean:
	rm -rf test
	rm -f testblocks testblocks.hi testblocks.o
