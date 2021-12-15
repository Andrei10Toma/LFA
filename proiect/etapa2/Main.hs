
module Main where

import System.Environment (getArgs)

main = do [inFile, outFile] <- getArgs
          dfaStr <- erToDfa inFile
          writeFile outFile dfaStr
