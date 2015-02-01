import           Data.List
import           Text.Pandoc

extractPythonRepl ((CodeBlock (_, "python":_, _) s) : blocks) | ">>>" `isPrefixOf` s =
        s : extractPythonRepl blocks
extractPythonRepl (block : blocks) = extractPythonRepl blocks
extractPythonRepl [] = []

extractPythonCode ((CodeBlock (_, "python":_, _) s) : blocks) | not (">>>" `isPrefixOf` s) =
        s : extractPythonCode blocks
extractPythonCode (block : blocks) = extractPythonCode blocks
extractPythonCode [] = []

readBlocks (Pandoc _ blocks) = blocks

readDoc = readMarkdown def

extractDocTest = formatBlocks . readBlocks . readDoc
    where
        formatBlocks :: [Block] -> String
        formatBlocks blocks =
            let docstring = concat $ extractPythonRepl blocks in
            let code = concat $ extractPythonCode blocks in
            unlines [
            "\"\"\"",
            docstring,
            "\"\"\"",
            "",
            code,
            "",
            "import doctest",
            "doctest.testmod()"
            ]

main = interact extractDocTest
