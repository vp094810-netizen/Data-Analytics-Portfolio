
import pandas as pd

# ---------------------------------------------------------
# HELPER FUNCTION: CREATE DATAFRAME FROM USER INPUT
# ---------------------------------------------------------
def get_dataframe(df_name, columns):
    print(f"\n--- Enter data for {df_name} ---")

    while True:
        try:
            num_rows = int(input("How many rows? "))
            if num_rows < 0:
                print("Enter zero or a positive number.")
                continue
            break
        except ValueError:
            print("Please enter a valid integer.")

    data = {col: [] for col in columns}

    for r in range(num_rows):
        print(f"\nRow {r + 1}:")

        for col in columns:
            value = input(f"Enter {col}: ").strip()

            # Convert numeric values automatically
            try:
                if value == "":
                    pass
                elif "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass

            data[col].append(value)

    df = pd.DataFrame(data)
    print(f"\n{df_name}:\n", df)

    return df


# ---------------------------------------------------------
# 1. CREATE DATASETS
# ---------------------------------------------------------
print("\n===== DATASET 1: STUDENT INFORMATION =====")
students_df1 = get_dataframe(
    "Students",
    ["StudentID", "Name", "Branch"]
)

print("\n===== DATASET 2: STUDENT MARKS =====")
marks_df2 = get_dataframe(
    "Marks",
    ["StudentID", "Marks"]
)

print("\n===== DATASET 3: NEW STUDENTS =====")
students_df3 = get_dataframe(
    "New Students",
    ["StudentID", "Name", "Branch"]
)


# ---------------------------------------------------------
# 2. CONCATENATION
# ---------------------------------------------------------

# Vertical concatenation: combine rows
combined_students = pd.concat(
    [students_df1, students_df3],
    axis=0,
    ignore_index=True
)

print("\n===== VERTICAL CONCATENATION =====")
print(combined_students)

# Horizontal concatenation: combine columns
print("\nEnter attendance for Dataset 1:")

attendance = []

for i in range(len(students_df1)):
    while True:
        try:
            value = float(input(f"Attendance for row {i + 1} (%): "))
            attendance.append(value)
            break
        except ValueError:
            print("Enter a valid number.")

extra_info = pd.DataFrame({
    "Attendance(%)": attendance
})

horizontal_concat = pd.concat(
    [students_df1, extra_info],
    axis=1
)

print("\n===== HORIZONTAL CONCATENATION =====")
print(horizontal_concat)


# ---------------------------------------------------------
# 3. MERGE USING A COMMON COLUMN
# ---------------------------------------------------------

# Inner Merge
inner_merge = pd.merge(
    students_df1, marks_df2,
    on="StudentID", how="inner"
)
print("\n===== INNER MERGE =====")
print(inner_merge)

# Left Merge
left_merge = pd.merge(
    students_df1, marks_df2,
    on="StudentID", how="left"
)
print("\n===== LEFT MERGE =====")
print(left_merge)

# Right Merge
right_merge = pd.merge(
    students_df1, marks_df2,
    on="StudentID", how="right"
)
print("\n===== RIGHT MERGE =====")
print(right_merge)

# Outer Merge
outer_merge = pd.merge(
    students_df1, marks_df2,
    on="StudentID", how="outer"
)
print("\n===== OUTER MERGE =====")
print(outer_merge)


# ---------------------------------------------------------
# 4. JOIN USING INDEX
# ---------------------------------------------------------

df_a = students_df1.set_index("StudentID")
df_b = marks_df2.set_index("StudentID")

joined_df = df_a.join(df_b, how="inner")

print("\n===== INNER JOIN =====")
print(joined_df)

joined_outer_df = df_a.join(df_b, how="outer")

print("\n===== OUTER JOIN =====")
print(joined_outer_df)


# ---------------------------------------------------------
# 5. MERGE WITH DIFFERENT COLUMN NAMES
# ---------------------------------------------------------

marks_df_renamed = marks_df2.rename(
    columns={"StudentID": "ID"}
)

merge_diff_cols = pd.merge(
    students_df1,
    marks_df_renamed,
    left_on="StudentID",
    right_on="ID",
    how="inner"
)

merge_diff_cols = merge_diff_cols.drop(columns=["ID"])

print("\n===== MERGE WITH DIFFERENT COLUMN NAMES =====")
print(merge_diff_cols)


# ---------------------------------------------------------
# 6. MERGE USING MULTIPLE KEYS
# ---------------------------------------------------------

print("\n===== DATASET X: SUBJECTS =====")
df_x = get_dataframe(
    "Subjects",
    ["StudentID", "Semester", "Subject"]
)

print("\n===== DATASET Y: GRADES =====")
df_y = get_dataframe(
    "Grades",
    ["StudentID", "Semester", "Grade"]
)

merge_multi_key = pd.merge(
    df_x,
    df_y,
    on=["StudentID", "Semester"],
    how="inner"
)

print("\n===== MERGE ON MULTIPLE KEYS =====")
print(merge_multi_key)


# ---------------------------------------------------------
# END OF PROGRAM
# ---------------------------------------------------------
print("\n===== ALL OPERATIONS COMPLETED SUCCESSFULLY =====")
