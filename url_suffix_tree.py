###################
# URL Suffix Tree #
###################

# A URL Suffix Tree is a data structure that stores strings, as well as each of
# its suffixes, in a tree. Suffixes with similar prefixes will share the same
# branches on the tree for as much as those two suffixes overlap. This data
# structure will make it easy to tell how much one suffix overlaps with
# another, which will be useful in determining which fragments to stitch
# together.

from url_string import *

EMPTY_URL_STRING = URLString('')

class URLSuffixTreeNode:
    """
    Represents a node in the suffix tree. A node has knowledge of its immediate
    children, as well as whether or not it represents the end of a suffix or
    not. If it does represent the end of a suffix (denoted by the string being
    capped off by a terminating character), the node holds the identity of the
    string as well as which suffix of that string it is. A node also holds the
    fragment of a string that extends along the branch from its parent to
    itself, for use in searching and reconstructing suffixes.

    self.string: The string fragment that runs along the branch from its parent
                 up to this node.
    self.identity: A tuple storing the string ID in the first spot, and the
                   suffix ID (for that string) in the second spot. Any
                   intermediate nodes do not have an identity.
    self.children: A dictionary storing all of the children of this node. The
                   keys correspond to the first letter of each children's string,
                   making it easier to search through.
    """

    def __init__(self, string=EMPTY_URL_STRING, identity=None):
        self.string = string
        self.identity = identity
        self.children = {}

    def split(self, split_point, new_back_string, new_identity=None):
        """
        When a new suffix is inserted, it may overlap partially with a node's
        string but diverges for the rest of the string. This method handles the
        logic for splitting a node in the middle of its string, to form a new
        divergence point in the tree.

        split_point: The index of the node's string at which the split happens.
                     If not a positive integer (meaning that the split point is
                     at the beginning of the string), then simply form a new
                     child node.
        new_back_string: The new string to be added to the tree, which will be
                         appended at the split point.
        new_identity: The identity of the newly inserted string.

        return: None
        """
        if split_point <= 0:
            self.children[new_back_string[0].string] = URLSuffixTreeNode(new_back_string, new_identity)
            return

        front_string = self.string[:split_point]
        old_back_string = self.string[split_point:]

        # Create two new nodes for each of the strings
        old_node = URLSuffixTreeNode(old_back_string, self.identity)
        old_node.children = self.children
        new_node = URLSuffixTreeNode(new_back_string, new_identity)

        # Turn the existing node into an intermediate node
        self.string = front_string
        self.identity = None
        self.children = {old_back_string[0].string: old_node, new_back_string[0].string: new_node}

class URLSuffixTree:
    """
    A URLSuffixTree holds the root node of the suffix tree, which is used to
    traverse all of its children. All logic pertaining to the suffix tree data
    structure itself, rather than with each individual node, is done here.

    self.root: The root node of the suffix tree, which holds an empty string.
    self.min_suffix_len: The minimum suffix length allowed in the tree. Used to
                         prevent any suffix from being inserted that is below
                         the overlap guarantee.
    """

    def __init__(self, min_suffix_len):
        self.root = URLSuffixTreeNode()
        self.min_suffix_len = min_suffix_len

    def insert(self, string, str_id):
        """
        Inserts a new string, as well as all of its suffixes, into the suffix
        tree. Each suffix is terminated by a terminating character, unique to
        each string ID, that allows a differentiation between two suffixes from
        two different strings that consist of the same characters.

        string: The string to be inserted. Recursive calls to this function will
                transform this string into each of its suffixes.
        str_id: The string ID, used to differentiate between each string.

        return: None
        """
        if len(string) < self.min_suffix_len:
            return

        # Search through the suffix tree for a split point, if any
        suffix = string + (TERMINATOR + str(str_id[0])) # Append unique terminator
        cur_node, index = self.root, 0
        for c in range(len(suffix)):
            if index == len(cur_node.string):
                index = -1
                if suffix[c].string in cur_node.children:
                    cur_node, index = cur_node.children[suffix[c].string], 0
            if index == -1 or suffix[c] != cur_node.string[index]:
                cur_node.split(index, suffix[c:], str_id)
                break
            index += 1

        # Recursive call to insert next suffix
        self.insert(string[1:], (str_id[0], str_id[1] + 1))
