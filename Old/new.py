# Import numpy
import numpy as np

# Creating a large array
large = np.ones(10)

# Display large array
print("Large array:\n",large,"\n")

# Creating a small array
arr = np.ones(3)

# Display small array
print("Small array:\n",arr,"\n")

# Embedding arr into large
large[1:4] += arr

# Display modified large array
print("Modified Large array:\n",large)