from typing import Self

# what allowSelfVoting determines is this
    # if allowed then the amount of a rank (rank 1, or rank 2 for example) will be equal to the amount of contenders
    # else it will be equal to the amount of contenders - 1
# what voteSize determines is this
    # the vote size will be equal to the max number aka last rank that is in the votes for contenders

class Calculator:
    def __init__(self:Self, contenders:dict[str,list[int]], voteSize:int=None, unanimityWeight:float=0.25, allowSelfVoting:bool=False) -> None:
        """creates new Unanimity Calculator with provided settings

        Args:
            contenders (dict[str,tuple[int]]): a dict of contenders and the votes they recieved
            voteSize (int, optional): The amount of elements that are ranked. Defaults to None which converts to the length of contenders; all elements being ranked.
            unanimityWeight (float, optional): The weight of the unanimity portion; the weight of the ranking portion will be decided out of 1 from the unanimity weight. Defaults to 0.25.
        """

        # dict check for contenders
        if (not isinstance(contenders, dict)): raise ValueError(f"the provided contenders value is not a dict: {type(contenders)}")

        # allow set voting check 
        if (not isinstance(allowSelfVoting, bool)): raise ValueError(f"the provided allowSelfVoting is not a boolean: {allowSelfVoting}")
        self.__allowSelfVoting = allowSelfVoting

        # set contenders size
        self.__contendersSize = len(contenders)

        # set max sum value
            # maxSum accounts for that users cannot self vote (the - 1 part)
        self.__maxSum = ((self.__contendersSize - self.__selfVotingMod(0)) ** 2)

        # set max difference value
            # -2 instead of -1 here for the same reason as maxSum, accounts for that users cannot self vote
        self.__maxDifference = (self.__contendersSize - self.__selfVotingMod(1))

        # vote size check
        if (voteSize == None): self.__voteSize = len(self.__contenders) - (1 if (self.__allowSelfVoting == False) else 0)
        elif (not isinstance(voteSize, int)): raise ValueError(f"the provided voteSize is not an int: {voteSize}")
        else: self.__voteSize = voteSize

        # contenders subvalue type checks
        if (
            any((not isinstance(key, str)) for key in contenders.keys()) # check keys of dictionary
            or any((not isinstance(value, list)) for value in contenders.values()) # check values of dictionary
        ): raise ValueError(f"the provided contenders are not of valid format dict{{string, list}}: {type(contenders)}")
        self.__contenders = contenders

        # contenders sub-sub value type check and range check (for each value for each contender)
        amountUsed = {} # holds the number of times each number is used
        for values in contenders.values():
            for value in values: 
                # int type check
                if (not isinstance(value, int)): raise ValueError(f"the provided contenders are not of valid format dict{{string, list(int, )}}: {values}")

                # vote size range check
                if (value > voteSize): raise ValueError(f"the provided contenders values are out of range of the voteSize: {values}, {self.__voteSize}")
        
                # self voting range check
                if (value not in amountUsed): amountUsed[value] = 0
                amountUsed[value] += 1
                if (amountUsed[value] > self.__contendersSize): raise ValueError(f"the provided contenders values contain too many votes for a particular rank: {value}")  

        # unanimity weight check
        if (unanimityWeight < 0) or (1 < unanimityWeight): raise ValueError(f"the provided unanimityWeight is out of the range of range (0-1): {unanimityWeight}") # range check
        self.__unanimityWeight = unanimityWeight

        # get ranking weight
        self.__rankingWeight = 1 - unanimityWeight

        # set results
        self.__results = {}
    
    def __selfVotingMod(self:Self, num:int) -> int:
        """modifies a value based on if self.allowSelfVoting is set. The value will be increased by 1 if true, and nothing if false

        Args:
            num (int): the value to be modified

        Returns:
            int: modified value
        """

        return num + (1 if (self.__allowSelfVoting == False) else 0)

    def __difference(self:Self, values:tuple) -> int:
        """gets the amount of difference between values

        Args:
            values (tuple): a tuple of rankings

        Returns:
            int: total amount of difference
        """

        # sort before checking
        values = sorted(values)

        difference = 0
        for i, currValue in enumerate(values):
            if (i == len(values) - 1): break # dont compute the last value (which would be out of range)
            nextValue = values[i + 1]

            # difference count
            if (abs(nextValue - currValue) != 0):
                difference += 1

        # return difference
        return difference
    
    def __fillContenders(self:Self) -> None:
        """fills contenders to the voteSize with average placement votes"""

        # - average ranking of a non pick -
        # take the largest (worst) possible ranking and subtrack that from the total possible rankings; this gives you the range of possible values that are nonpicks
        # divide the possible range by 2; this gives you the half way point of possible nonpick values
        # add the half way non pick to the vote size to find the average placement of a non-pick
        averageRankingOfNonPick = self.__voteSize + round((self.__contendersSize - self.__voteSize) / 2)

        # for every contender fill values as needed
        for currContenderKey, currContenderValues in self.__contenders.items():
            if (self.__contendersSize > len(currContenderValues)): # if the current values is too small
                # for the remaining values, fill
                for _ in range(len(currContenderValues), (self.__contendersSize - self.__selfVotingMod(0))): # - 1 is included here because someone cannot self vote
                    self.__contenders[currContenderKey].append(averageRankingOfNonPick)

    def compute(self:Self, doNormalize:bool=True, doPrint:bool=False) -> None: 
        """computes the best choice based on unanimity and ranking; stores the results in self.results.

        Args:
            doNormalize (bool, optional): normalizes the results if true. Defaults to True.
            doPrint (bool, optional): show print debug log. Defaults to False.
        """

        # fill contenders with padded average values
        self.__fillContenders()

        # for item in contenders, compute the final percentage and add it to the results
        for name, values in self.__contenders.items():
            # print set
            if (doPrint == True): print(f"set of '{name}': {values}")

            # get the percentage sum average value
                # get the average as if it were a scale from 0 to size - 1 (1 to 3 becomes 0 to 2) (this ensures the range is from 0% to 100%) 
                    # contenders size - 1 is for self voting changes, it's what does the scale change
                # besides the offsetting this is a normal average
                # the value is inversed (1 - ) so that it's in terms of popularity (1 is the top, 100% value)
            sumPercentage = 1 - (
                (sum(values) - (self.__contendersSize - self.__selfVotingMod(0))) 
                / (self.__maxSum - (self.__contendersSize - self.__selfVotingMod(0)))
            )

            # apply weight to sum percent
            sumWeighted = sumPercentage * self.__rankingWeight

            # print sum
            if (doPrint == True): print(f"sum: {sumPercentage} ({sumWeighted})")

            # get the percentage difference average value
                # get the average as if it were a scale from 0 to sizwe - 1 (1 to 3 becmoes 0 to 2) (this ensures the range is from 0% to 100%) 
                    # difference calculators already include value compensation for self voting restrictions, because it isn't directly impacted by self voting
                # besides the offsetting this is a normal average
                # the value is inversed (1 - ) so that it's in terms of popularity (1 is the top, 100% value)
            diffPercentage = 1 - (
                self.__difference(values)
                / self.__maxDifference
            )

            # apply weight to diff percent
            diffWeighted = diffPercentage * self.__unanimityWeight

            # print weight
            if (doPrint == True): print(f"diff: {diffPercentage} ({diffWeighted})\n")

            # get composite value and add to results
            self.__results[name] = sumWeighted + diffWeighted

        # sort the results
        self.__results = dict(sorted(self.__results.items(), key=(lambda item: item[1]), reverse=True))

        # redistribute values such that they stretch from 0 to 100%
        if (doNormalize == True): self.normalizeResults()
    
    def normalizeResults(self:Self) -> None:
        """redistributes the result values such that they stretch from 0% to 100%"""

        # get min 
        minValue = min(self.__results.values())
        # correction value
            # gets the max - min (range from min to max)
            # divides by 1 to get the value which will correct a value in the range 0 to max to move towards 1 (where the max will be 1 and min will be 0)
        rangeMinToMax = max(self.__results.values()) - minValue
        if (rangeMinToMax == 0): return # do nothing, keep as is
        correctionValue = 1 / rangeMinToMax

        # for every result, reweigh it
            # values will always be normalized because the minimum value (after cumulation of both sum and diff) is 0.25
        for name, value in self.__results.items():
            self.__results[name] = (value - minValue) * correctionValue

    def showResults(self:Self, recomputeResults:bool=True, doNormalize:bool=True, doPrint:bool=False) -> None:
        """prints the results of the calculation
        
        Args:
            recomputeResults (bool, optional): recomputes the results if true. Defaults to True. 
            doNormalize (bool, optional): normalizes the results if true. Defaults to True.
            doPrint (bool, optional): show print debug log. Defaults to False.
        """

        # recompute
        if (recomputeResults == True): self.compute(doNormalize=doNormalize, doPrint=doPrint)

        # show
        for name, percent in self.__results.items():
            print(f"{name}: {(percent * 100):.2f}%")

    def showRankingAnalysis(self:Self) -> None:
        """prints the results of an analysis made strictly by ranking"""

        # sort the contenders sums high to low (does change original, but this only serves to help)
        self.__contenders = dict(sorted(self.__contenders.items(), key=(lambda item: sum(item[1]))))

        # show
        for name, values in self.__contenders.items(): # doesn't include value padding (doesn't use average non-pick)
            valuesSum = sum(values)
            if (valuesSum == 0): continue
            print(f"{name}: {valuesSum}")
