#Helper functions that are not database wrappers go here

#converting
def timestamp_to_dict(timestamp):
    return {
    "t": timestamp.time,
    "i": timestamp.inc
    }