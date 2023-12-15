from brownie import chain
import math

def get_week(n=0):
    WEEK = 604800
    this_week = (chain.time() // WEEK) * WEEK
    return this_week + (n * WEEK)

def estimatedVotingPower(amount, ts):
    slope = math.floor(amount/(4 * 365 * 24 * 60 * 60))
    return slope * ts