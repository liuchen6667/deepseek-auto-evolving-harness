import pandas as pd

# Test data
data = '''sale_id,product_id,region_code,amount,date
T001,P01,R1,100.00,2024-04-01
T002,P02,R2,,04/02/2024
T002,P02,R2,150.00,04/02/2024
T003,P03,R3,200.00,2024-04-03
T004,P01,R1,75.00,04/04/2024
T004,P01,R1,75.00,2024-04-04'''

import io
df = pd.read_csv(io.StringIO(data))
print("Original data:")
print(df)
print("\nData types:")
print(df.dtypes)
print("\nChecking amount column:")
print(df['amount'])
print("\nIs amount null?")
print(pd.isna(df['amount']))
print("\nAmount as string:")
print(df['amount'].astype(str))
print("\nIs amount empty string?")
print(df['amount'].astype(str).str.strip() == '')