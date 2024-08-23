import csv

def is_invalid_skill(skill):
    # check if the skill is only numbers, 'none', empty string, or completely empty
    return skill.isdigit() or skill.lower() == 'none' or skill.strip() == '' or skill == '""'

def clean_csv(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            skills = row['skills']
            if not is_invalid_skill(skills):
                writer.writerow(row)

if __name__ == "__main__":
    input_file = '/home/alois/Abhiraj/2. Skill Prediction Model/groq_api/extracted_skills.csv'
    output_file = '/home/alois/Abhiraj/2. Skill Prediction Model/reskill_dataset_v1.csv'
    clean_csv(input_file, output_file)