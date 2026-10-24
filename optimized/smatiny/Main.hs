-- | Simple wrapper for Smatiny
-- Version 1.0
module Main where

import Control.Monad (liftM, when)
import System.Environment (getArgs)
import System.Console.GetOpt
import System.Exit
import Smatiny

version = "1.0"

data Flag = Flag_Verbose 
          | Flag_Version
            deriving (Eq, Show)

opts = [ Option "v" ["verbose"] (NoArg Flag_Verbose) "Be verbose?",
         Option "?" ["version"] (NoArg Flag_Version) "Print version and quit" ]

-- | Handle incoming options and error handling
handleOpts :: [String] -> ([Flag], [String])
handleOpts args = case getOpt Permute opts args of
                    (o, n, []) -> (o, n)
                    (_, _, es) -> error $ unlines es

bye :: String -> IO ()
bye s = putStrLn s >> exitWith ExitSuccess

main = do (opts, [file]) <- liftM handleOpts getArgs
          when (Flag_Version `elem` opts) $ bye version
          f              <- readFile file
          let prog    = parseSmatiny f
              verbose = Flag_Verbose `elem` opts
          when verbose $ print prog
          putStrLn $ runProgram prog