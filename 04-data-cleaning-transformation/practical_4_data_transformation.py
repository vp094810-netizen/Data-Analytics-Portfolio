
import pandas as pd

# --------------------------------
# 1. TAKE INPUT FROM USER
# --------------------------------

n = int(input("Enter number of students: "))

names = []
ages = []
departments = []
dates = []

for i in range(n):
    print("\nEnter details of student", i + 1)

    name = input("Enter Name: ")
    age = input("Enter Age: ")
    department = input("Enter Department: ")
    date = input("Enter Admission Date (DD-MM-YYYY): ")

    names.append(name)
    ages.append(age)
    departments.append(department)
    dates.append(date)


# --------------------------------
# 2. CREATE DATAFRAME
# --------------------------------

data = {
    "Name": names,
    "Age": ages,
    "Department": departments,
    "Admission_Date": dates
}

df = pd.DataFrame(data)

print("\nOriginal Data:")
print(df)

print("\nOriginal Data Types:")
print(df.dtypes)


# --------------------------------
# 3. DATA TYPE CONVERSION
# --------------------------------

df["Age"] = df["Age"].astype(int)


# --------------------------------
# 4. STRING MANIPULATION
# --------------------------------

# Remove extra spaces
df["Name"] = df["Name"].str.strip()
df["Department"] = df["Department"].str.strip()

# Convert to title case
df["Name"] = df["Name"].str.title()
df["Department"] = df["Department"].str.title()


# --------------------------------
# 5. DATE TYPE TRANSFORMATION
# --------------------------------

df["Admission_Date"] = pd.to_datetime(
    df["Admission_Date"],
    format="%d-%m-%Y"
)

# Extract year, month and day
df["Year"] = df["Admission_Date"].dt.year
df["Month"] = df["Admission_Date"].dt.month
df["Day"] = df["Admission_Date"].dt.day


# --------------------------------
# 6. DISPLAY TRANSFORMED DATA
# --------------------------------

print("\nTransformed Data:")
print(df)

print("\nTransformed Data Types:")
print(df.dtypes)

print("\nData Transformation Completed Successfully!")
