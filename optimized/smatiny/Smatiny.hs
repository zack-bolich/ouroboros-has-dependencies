-- | Implementation of http://esoteric.voxelperfect.net/wiki/SMATINY
--   By David House <dmhouse@gmail.com>
module Smatiny where

import Text.ParserCombinators.Parsec hiding (State)
import Data.Char (isSpace, chr)
import Data.List (maximumBy)
import Control.Arrow (second)
import Control.Monad (liftM)
import Control.Monad.State
import qualified Data.Map as M

-- import Debug.Trace

type StepNum   = Int
data Step      = Swap StepNum StepNum | Nop | Output deriving (Show, Eq)
type Program   = M.Map StepNum Step
type Smatiny a = State (Program, StepNum) a

-- * @String -> Program@. The Parsing Stage.
--

-- | Parse a step number at the beginning of a line
stepNumP :: CharParser st StepNum
stepNumP = liftM read $ digit `manyTill` char '.'

-- | A swap command
swapP :: CharParser st Step
swapP = do string "Swap "
           snum1 <- many digit
           string " with "
           snum2 <- many digit
           char '.'
           return $ Swap (read snum1) (read snum2)

-- | A Do Nothing command
doNothingP :: CharParser st Step
doNothingP = string "Do nothing." >> return Nop

-- | An output command
outputP :: CharParser st Step
outputP = string "Output this block's position." >> return Output

-- | The start of a line
start :: CharParser st Int
start = do n <- stepNumP
           char ' '
           return n

-- | Propogate errors, like the MonadPlus definition of Maybe
concatEithers :: [Either a b] -> Either a [b]
concatEithers [] = error "concatEithers: empty list"
concatEithers es = foldl comb (Right []) es
    where comb (Right es) (Right y) = Right $ es ++ [y]
          comb _          (Left a)  = Left a

-- | Parse an input
parseSmatiny :: String -> Program
parseSmatiny s = program
    where s'            = filter (not . all isSpace) $ lines s
          uncommented   = map (takeWhile (not . (==';'))) s'
          doParse       = parse parseSmatiny' "Smatiny program"
          parsed        = map doParse uncommented
          parseSmatiny' = do n <- start
                             s <- swapP <|> doNothingP <|> outputP
                             return (n, s)
          steps         = either (error . show) id $ concatEithers parsed
          program       = M.fromList steps

-- * @Program -> String@. The interpretation stage.
--

-- | Get the nth step from a program. Fall back on Nop if it doesn't exist (as per the spec)
getStep :: Program -> StepNum -> Step
getStep p s = maybe Nop id $ M.lookup s p

-- | Handle a Nop
doNothing :: Smatiny ()
doNothing = modify (second (+1))

-- | Handle a swap
doSwap :: Step -> Smatiny ()
doSwap (Swap from to) = do (map, loc) <- get
                           let fromEl = map `getStep` from
                               toEl   = map `getStep` to
                               map'   = M.insert from toEl   map
                               map''  = M.insert to   fromEl map'
                               loc' | loc == from = to   + 1
                                    | loc == to   = from + 1
                                    | otherwise   = loc  + 1
                           put (map'', loc')

-- | Handle an ouput (returning the outputted char)
doOutput :: Smatiny Char
doOutput = do (s, n) <- get
              put (s, n + 1)
              return $ chr n

-- | Take a program, run it, and return the string it produces
runProgram :: Program -> String
runProgram p = evalState run' (p, 1)
    where run' = do (map, loc) <- get
                    let x = map `getStep` loc
                    -- trace (show x ++ "\t" ++ show loc) $ do
                    this <- case x of
                              s@(Swap _ _) -> doSwap s  >> return ""
                              s@(Nop     ) -> doNothing >> return ""
                              s@(Output  ) -> liftM (:[]) doOutput
                    if loc > maximum (M.keys map)
                       then return this
                       else liftM (this ++) run'