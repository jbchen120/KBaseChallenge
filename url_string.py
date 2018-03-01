##############
# URL String #
##############

# A URL String is a special type of string that treats URL-encoded letters
# (letters that are encoded by a '%' sign, followed by two hexadecimal digits)
# as single letters. This provides some key functionality for the URL suffix
# tree, as well as functionality for joining together two strings with overlap.

from urllib.parse import unquote, unquote_plus

TERMINATOR = '$' # Terminating character, used in the suffix tree

class URLString:
    """
    A URLString takes in a URL-encoded string and marks the location of all
    'real' letters.

    self.string: The URL-encoded string that the URLString stores.
    self.true_positions: A list of all the positions in the URL-encoded string
                         that correspond to actual letters when decoded.
    """

    def __init__(self, string):
        self.string = string
        self.true_positions = []

        self.update_true_positions()

    def __repr__(self):
        return self.string

    def __len__(self):
        return len(self.true_positions) - 1

    def __getitem__(self, key):
        if isinstance(key, int):
            i = self.true_positions[key]
            j = self.true_positions[key + 1]
            return URLString(self.string[i:j])
        i = self.true_positions[key.start] if key.start else None
        j = self.true_positions[key.stop] if key.stop else None
        return URLString(self.string[i:j])

    def __eq__(self, string):
        if isinstance(string, URLString):
            return self.string == string.string
        return self.string == string

    def __add__(self, new_string):
        if isinstance(new_string, URLString):
            return URLString(self.string + new_string.string)
        return URLString(self.string + new_string)

    def update_true_positions(self):
        """
        Called when it is required to update the positions stored in
        self.true_positions. This method is called during initialization, as well
        as when any modification to self.string is made.

        return: None
        """
        self.true_positions = []
        i = 0
        while i < len(self.string):
            self.true_positions.append(i)
            if self.string[i] == '%': # URL-encoded letter
                i += 2
            elif self.string[i] == TERMINATOR: # Terminating character
                break
            i += 1
        self.true_positions.append(len(self.string))

    def to_convention_text(self):
        """
        Decodes the URL-encoded string.

        return: The decoded string.
        """
        return unquote_plus(self.string)

    def join(self, join_string, overlap=0):
        """
        Takes another string and appends it to the end of the current string,
        then updates the true positions. Also takes into account any overlap
        between the two strings by slicing off the overlap amount from the
        joined string.

        join_string: The string to be joined to this URLString. Can be a normal
                     string, or can be another URLString.
        overlap: How much the strings should overlap. Defaults to 0.

        return: None
        """
        if isinstance(join_string, URLString):
            self.string = self.string + join_string[overlap:].string
        else:
            self.string = self.string + join_string[overlap:]
        self.update_true_positions()
