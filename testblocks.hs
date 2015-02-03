import           Data.List
import           Text.Pandoc

extractPythonRepl ((CodeBlock (_, "python":_, _) s) : blocks) | ">>>" `isPrefixOf` s =
        s : extractPythonRepl blocks
extractPythonRepl (block : blocks) = extractPythonRepl blocks
extractPythonRepl [] = []

extractBash ((CodeBlock (_, "bash":_, _) s) : blocks) | "$" `isPrefixOf` s =
        s : extractBash blocks
extractBash (block : blocks) = extractBash blocks
extractBash [] = []

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
            unlines [
            "#!/usr/bin/env python",
            "class Py(object):",
            "    \"\"\"",
            concat $ extractPythonRepl blocks,
            "\"\"\"",
            "    pass",
            "",
            "class Bash(object):",
            "    \"\"\"",
            concat $ extractBash blocks,
            "\"\"\"",
            "    pass",
            "",
            concat $ extractPythonCode blocks,
            "",
            "import doctest",
            "import shelldoctest",
            "import sys",
            "failures = doctest.testmod()[0] or 0",
            "failures += shelldoctest.testmod()[0] or 0",
            "sys.exit(failures)"
            ]

main = interact extractDocTest
