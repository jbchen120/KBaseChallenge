########
# Main #
########

# Task 1 of the Developer Programming Task.
#
# Takes in either 0 or 1 arguments from the command line; if 0 arguments,
# fragments are read from standard input, and if 1 argument, fragments are read
# from the file passed in.
#
# The logic for solving this task is as follows:
# 1. Take the fragments and turn them all into URL Strings. Then, place them all
#    into a URL Suffix Tree.
# 2. Run depth-first search to traverse the suffix tree. Whenever the traversal
#    hits a node corresponding to an original fragment, it records the potential
#    fragments it overlaps with and stores it in an array.
# 3. Go through the possible combinations of overlaps and attempt to stitch together
#    the fragments. When a valid stitching has been found, it is returned.

import sys, copy
from url_suffix_tree import *

MIN_OVERLAP = 3 # Overlap guarantee

def reconstruct(filename=None):
    """
    Reconstructs the original source text, given a bunch of randomized fragments
    that overlap. It does this by constructing a suffix tree to store the
    fragments, searching through that tree to find the potential overlaps, and
    then attempting to stitch together the fragments using that information.
    When a stitching has been found, it prints and returns that result.

    filename: The file to be opened, containing the fragments. If None, then
              the fragments are read from stdin.

    return: The full, reconstructed source text.
    """
    if filename:
        file_object = open(filename)
    else:
        file_object = sys.stdin # Read from STDIN

    # Step 1: Build a URL Suffix Tree
    fragments = []
    suffix_tree = URLSuffixTree(MIN_OVERLAP)
    for i, frag in enumerate(file_object):
        fragments.append(URLString(frag.rstrip()))
        suffix_tree.insert(URLString(fragments[i].string), (i, 0))

    # Step 2: Run DFS
    join_array = [0] * len(fragments)
    dfs_join(suffix_tree.root, suffix_tree.root.string, [], join_array)

    # Step 3: Stitch together fragments
    if [x for x in join_array if len(x) == 0]: # join_array has an entry with 0 matches
        search = list(range(len(fragments)))
        search.sort(key=lambda x: len(join_array[x]))
        seen_array = [0] * len(fragments)
        stitchings = [0] * len(fragments)
        overlaps = [0] * len(fragments)
        result = stitch(join_array, 0, search, seen_array, stitchings, overlaps, fragments)
    else: # No entries in join_array have 0 matches
        for j in range(len(join_array)):
            join_array_copy = join_array[:]
            join_array_copy[j] = []
            search = list(range(len(fragments)))
            search.sort(key=lambda x: len(join_array_copy[x]))
            seen_array = [0] * len(fragments)
            stitchings = [0] * len(fragments)
            overlaps = [0] * len(fragments)
            result = stitch(join_array_copy, 0, search, seen_array, stitchings, overlaps, fragments)
            if result:
                break

    print(result)
    return result

def dfs_join(node, string, match_stack, join_array):
    """
    Perform depth-first search on the suffix tree. As the function traverses
    the tree, it will fill the join_array with potential matches for each
    fragment, which are collected on the match_stack during traversal.

    node: The current node in the traversal process. Starts with the root node.
    string: The full string built from the root to the current node.
    match_stack: A stack that represents the current potential overlaps at any
                 particular node.
    join_array: An array that corresponds to each fragment. It is filled during
                the DFS whenever the traversal gets to a node corresponding to
                an original fragment.

    return: None
    """
    # Found a node corresponding to original fragment
    if node.identity and node.identity[1] == 0:
        join_array[node.identity[0]] = match_stack[:]
        return

    # Stack pushing logic: Search children for strings that begin with a terminator
    term = [key for key in node.children.keys() if key[0] == TERMINATOR]
    stack_pushed = 0 # Stack push counter
    if term and len(string) >= MIN_OVERLAP:
        for t in range(len(term)):
            if node.children[term[t]].identity[1] != 0:
                match_stack.append((node.children[term[t]].identity[0], string))
                stack_pushed += 1

    # Recursive call to each child
    for child in node.children.values():
        dfs_join(child, string + child.string, match_stack, join_array)

    # Pop all matches that were pushed on this node level
    while stack_pushed > 0:
        match_stack.pop()
        stack_pushed -= 1

def stitch(join_array, index, search, seen_array, stitchings, overlaps, fragments):
    """
    Search through possible combinations of fragment overlappings, and return the
    best one. It does this by building up a potential stitchings list using the
    join_array, making sure that no two stitchings are mapped to the same
    fragment. Once a potential stitching has been found, an attempt is made to
    stitch the fragments together. If it works, the result is returned; if not,
    then a new combination of stitchings is attempted.

    join_array: The join_array constructed from the DFS.
    index: A counter to keep track of how many stitchings have been made so far.
           When this number reaches the number of fragments, a stitch attempt
           is made.
    search: A list of indices, sorted by the size of its corresponding entry in
            the join_array, that determines the order of searching. Used to
            prevent unnecessarily long backtracking.
    seen_array: A bit array that flags whether or not a fragment has already
                been assigned a stitching. Used to prevent unnecessary invalid
                stitch attempts.
    stitchings: An array that is filled with potential stitchings. Each index
                corresponds to a fragment, and the number stored at that index
                corresponds to the index of the suffix that will be stitched to
                the fragment. The entry is set to -1 if it maps that fragment
                to the front of the fully stitched-together string.
    overlaps: An array that directly corresponds with the stitchings, but instead
              stores how much that potential stitching should overlap.
    fragments: The fragments to be stitched together.

    return: A valid stitching, or None if nothing is found.
    """
    # Attempt to stitch if stitchings array is filled
    if index == len(join_array):
        result = None
        stitch_attempt = copy.deepcopy(fragments)
        cur_index = -1 # Start from the front
        while cur_index is not None:
            try:
                cur_index = stitchings.index(cur_index) # Index of current fragment
                next_index = stitchings.index(cur_index) # Index of next fragment to be stitched together
                stitch_attempt[cur_index].join(stitch_attempt[next_index], overlaps[next_index])
                stitch_attempt[next_index] = stitch_attempt[cur_index] # Change pointer to same string
            except ValueError:
                cur_index = None
        if stitch_attempt.count(stitch_attempt[0]) == len(stitch_attempt): # Valid stitching found
            result = stitch_attempt[0].to_convention_text()
        return result

    # Fill stitchings array and overlaps array
    if len(join_array[search[index]]) == 0: # Potential start of full string
        stitchings[search[index]] = -1
        result = stitch(join_array, index + 1, search, seen_array, stitchings, overlaps, fragments)
        if result:
            return result
    else:
        for i in range(len(join_array[search[index]])): # Go through matches backwards, to prioritize bigger overlaps
            if seen_array[join_array[search[index]][-(i+1)][0]]: # Check if stitching has been assigned yet
                continue
            stitchings[search[index]] = join_array[search[index]][-(i+1)][0]
            overlaps[search[index]] = len(join_array[search[index]][-(i+1)][1])
            seen_array[join_array[search[index]][-(i+1)][0]] = 1 # Flag as seen
            result = stitch(join_array, index + 1, search, seen_array, stitchings, overlaps, fragments)
            if result:
                return result
            seen_array[join_array[search[index]][-(i+1)][0]] = 0 # Unflag

if __name__ == '__main__':
    if len(sys.argv) == 1:
        reconstruct()
    elif len(sys.argv) == 2:
        reconstruct(sys.argv[1])
    else:
        print("Too many arguments passed in!\nOnly 0 or 1 arguments are accepted.")
