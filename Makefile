.PHONY: test

testblocks:
	ghc --make testblocks.hs

%.out.py: %.md testblocks
	./testblocks < $< > $@

test: $(patsubst %.md, %.out.py, $(shell ls *.md))
	for test in $^ ; do \
		python $$test -v ; \
	done

clean:
	rm -f *.out.py
	rm -f testblocks testblocks.hi testblocks.o
