
def unique(input_list):
    # initialize a null list
    unique_list = []
     
    # traverse for all elements
    for x in input_list:
        # check if exists in unique_list or not
        if x not in unique_list and x is not None:
            unique_list.append(x)
    
    return unique_list
   