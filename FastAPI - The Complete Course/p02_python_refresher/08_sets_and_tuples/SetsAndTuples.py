"""
Sets are similar to lists but are unordered and cannot contain duplications
Use curly brackets
"""

my_set = {1, 2, 3, 4, 5, 1, 2}
print(my_set)
print(len(my_set))

for x in my_set:
    print(x)

my_set.discard(3) # removes an element if it exists, does nothing if it doesn't
print(my_set)
my_set.add(6)
print(my_set)
my_set.update([7, 8]) # adds multiple elements
print(my_set)

"""
Tuples are similar to lists but are immutable (cannot be changed)
Use parentheses"""

my_tuple = (1, 2, 3, 4, 5)
print(my_tuple[1])
# my_tuple[1] = 100  -> This will raise an error
