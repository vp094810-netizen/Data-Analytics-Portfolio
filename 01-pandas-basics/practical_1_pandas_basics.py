
import pandas as pd

df = pd.DataFrame({
    "Name": ["Amit", "Priya", "Rahul", "Sneha"],
    "Dept": ["CSE", "IT", "CSE", "IT"],
    "Marks": [85, 92, 78, 88]
})

print("Original Data:\n", df)

# Data Subsetting
print("\nSubset (Marks > 50):\n", df[df["Marks"] > 50])

# Sorting in Ascending Order
print("\nSorted by Marks (Ascending):\n", df.sort_values("Marks"))

# Sorting in Descending Order
print("\nSorted by Marks (Descending):\n", df.sort_values("Marks", ascending=False))

# Grouping
print("\nGrouped (Average Marks by Department):\n",
      df.groupby("Dept")["Marks"].mean())

# Statistical Operations
print("\nMean =", df["Marks"].mean())

print("Median =", df["Marks"].median())

print("Mode =")
print(df["Marks"].mode())
