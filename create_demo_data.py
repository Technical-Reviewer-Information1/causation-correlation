import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Number of samples
n_samples = 1000

# Create demo data with blood pressure and income as main example
# Age is the confounding variable that affects both blood pressure and income

# Age distribution (20-70 years)
age = np.random.uniform(20, 70, n_samples)

# Blood pressure: increases with age + random variation
# Normal systolic BP: 90-140 mmHg, increases ~0.5 mmHg per year after 30
base_bp = 100
age_effect_bp = 0.7 * (age - 30)  # 0.7 mmHg increase per year after 30
blood_pressure = base_bp + age_effect_bp + np.random.normal(0, 12, n_samples)
blood_pressure = np.clip(blood_pressure, 80, 200)  # Realistic BP range

# Income: generally increases with age (experience) + random variation
# Peak around 50-55, then slight decline
age_normalized = (age - 20) / 50  # Normalize age to 0-1 scale
income_age_curve = -0.3 * (age_normalized - 0.6)**2 + 0.5  # Parabolic curve peaking at ~50
base_income = 3000000  # Base income in yen (3M yen = ~30k USD)
income = base_income + income_age_curve * 4000000 + np.random.normal(0, 800000, n_samples)
income = np.maximum(income, 2000000)  # Minimum income 2M yen

# Additional variables to demonstrate various correlation patterns

# 1. Education level (affects income, weakly correlated with age)
education_level = np.random.choice([1, 2, 3, 4], n_samples, p=[0.2, 0.3, 0.3, 0.2])  # 1=high school, 4=graduate
education_effect = (education_level - 1) * 500000  # 500k yen per education level
income += education_effect + np.random.normal(0, 200000, n_samples)

# 2. Exercise hours (negatively affects blood pressure)
exercise_hours = np.random.exponential(2, n_samples)
exercise_effect_bp = -1.5 * exercise_hours  # Exercise reduces BP
blood_pressure += exercise_effect_bp

# 3. BMI (affects blood pressure, somewhat related to age and exercise)
bmi_base = 22 + 0.05 * (age - 30) - 0.2 * exercise_hours  # Slight increase with age, decrease with exercise
bmi = bmi_base + np.random.normal(0, 3, n_samples)
bmi = np.clip(bmi, 16, 40)
bmi_effect_bp = 0.8 * (bmi - 22)  # BMI above 22 increases BP
blood_pressure += bmi_effect_bp

# 4. Work stress (affects blood pressure, somewhat related to income)
work_stress = 3 + 0.000001 * income + np.random.normal(0, 2, n_samples)  # Higher income = slightly more stress
work_stress = np.clip(work_stress, 1, 10)
stress_effect_bp = 2 * work_stress
blood_pressure += stress_effect_bp

# 5. Gender (affects income gap)
gender = np.random.choice([0, 1], n_samples)  # 0: female, 1: male
gender_income_gap = np.where(gender == 1, 0, -300000)  # 300k yen gender gap
income += gender_income_gap

# 6. Spurious correlation example: Shoe size and salary (both related to gender and age)
shoe_size_base = np.where(gender == 1, 26.5, 23.5)  # Japanese shoe sizes
shoe_size = shoe_size_base + np.random.normal(0, 1.5, n_samples)

# 7. Sleep hours (affects blood pressure)
sleep_hours = 7 + np.random.normal(0, 1.2, n_samples)
sleep_hours = np.clip(sleep_hours, 4, 10)
sleep_effect_bp = -1.0 * (sleep_hours - 7)  # Deviation from 7 hours increases BP
blood_pressure += sleep_effect_bp

# Ensure realistic ranges
blood_pressure = np.clip(blood_pressure, 80, 200)
income = np.maximum(income, 1500000)

# Create DataFrame
df = pd.DataFrame({
    'Age_Years': age,
    'Blood_Pressure_mmHg': blood_pressure,
    'Annual_Income_Yen': income,
    'Education_Level': education_level,
    'Exercise_Hours_Week': exercise_hours,
    'BMI': bmi,
    'Work_Stress_Scale': work_stress,
    'Gender': gender,
    'Shoe_Size_JP': shoe_size,
    'Sleep_Hours': sleep_hours
})

# Round numerical values for better presentation
df = df.round(2)

# Save to Excel file
df.to_excel('demo_data.xlsx', index=False)
print(f"Demo data created with {len(df)} samples and {len(df.columns)} variables")
print("Variables included:")
for col in df.columns:
    print(f"- {col}")

print("\nKey relationships in this dataset:")
print("- Blood pressure and income show correlation due to age as confounding variable")
print("- Age affects both blood pressure (increases) and income (peaks around 50)")
print("- This demonstrates spurious correlation: Blood Pressure ↔ Income")
print("- True relationship: Age → Blood Pressure, Age → Income")