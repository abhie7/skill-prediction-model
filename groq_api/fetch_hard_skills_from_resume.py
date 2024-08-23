import os
import re
import csv
import time
from groq import Groq
from groq import BadRequestError
from system_prompt import prompt
from pdf_text_extractor.pdf_extractor import PdfParser

def main():
    client = Groq(api_key="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")

    resume_dir = '/home/alois/Abhiraj/Resumes/APAC'
    csv_file_path = '/home/alois/Abhiraj/2. Skill Prediction Model/groq_api/extracted_skills.csv'
    parsed_files_path = '/home/alois/Abhiraj/2. Skill Prediction Model/groq_api/parsed_files.txt'

    # load parsed filenames
    if os.path.exists(parsed_files_path):
        with open(parsed_files_path, 'r') as f:
            parsed_files = set(f.read().splitlines())
    else:
        parsed_files = set()

    # open csv file in append mode
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # write header if the file is empty
        if os.stat(csv_file_path).st_size == 0:
            writer.writerow(['resume_text', 'skills'])

        for filename in os.listdir(resume_dir):
            if filename.endswith('.pdf') and filename not in parsed_files:
                resume_pdf_path = os.path.join(resume_dir, filename)

                try:
                    pdf_parser = PdfParser(resume_pdf_path)
                    resume_text = pdf_parser.get_cleaned_text()
                except TypeError as e:
                    print(f"Skipping {filename} due to a TypeError: {e}")
                    continue

                try:
                    response = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[
                            {
                                "role": "system",
                                "content": prompt
                            },
                            {
                                "role": "user",
                                "content": resume_text
                            }
                        ],
                        temperature=0.5,
                        max_tokens=8192,
                        top_p=1,
                        stream=False,
                        stop=None,
                    )
                except BadRequestError as err:
                    print(f"Error processing {filename}: {err}")
                    continue

                response_content = response.choices[0].message.content.strip()
                print(f'\nResponse for {filename}: {response_content}')

                # skills_match = re.search(r'^(.*)$', response_content)
                # skills_match = re.search(r'^"(.*)"$', response_content)
                skills_match = re.search(r'(?:list of hard technical skills extracted from the resume:\s*)?"(.*)"', response_content, re.DOTALL)
                if skills_match:
                    skills = skills_match.group(1).split(',')
                    skills = [skill.strip().strip('"') for skill in skills]  # Strip whitespace and quotes
                    skills = [skill.lower() for skill in skills]
                else:
                    skills = []

                print(f'Skill extracted for {filename}: {skills}')

                # write to csv
                if skills:
                    writer.writerow([resume_text, ', '.join(skills)])

                    # append the filename to the parsed_files
                    parsed_files.add(filename)
                    with open(parsed_files_path, 'a') as f:
                        f.write(filename + '\n')
                    print(f'\nSkills added to {filename}: \n{skills}')

                print('\nWaiting for 2 seconds before next hit.\n')
                time.sleep(2)

            # else:
                # print(f'\nSkipping {filename}')

if __name__ == "__main__":
    main()