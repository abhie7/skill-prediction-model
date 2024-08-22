import os
import re
import csv
from groq import Groq
from system_prompt import prompt
from pdf_text_extractor.pdf_extractor import PdfParser

def main():
    client = Groq(api_key="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")

    resume_dir = 'test_resumes'
    csv_file_path = 'extracted_skills.csv'
    parsed_files_path = 'groq_api/parsed_files.txt'

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

                pdf_parser = PdfParser(resume_pdf_path)
                resume_text = pdf_parser.get_cleaned_text()

                response = client.chat.completions.create(
                    model="llama3-70b-8192",
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

                response_content = response.choices[0].message.content.strip()
                print(f'\nResponse for {filename}: {response_content}')

                skills_match = re.search(r'^(.*)$', response_content)
                if skills_match:
                    skills = skills_match.group(1).split(',')
                    skills = [skill.strip() for skill in skills]
                    skills = [skill.lower() for skill in skills]
                else:
                    skills = []
                print(f'Skill extracted for {filename}: {skills}')

                # write to csv
                writer.writerow([resume_text, ', '.join(skills)])

                # append the filename to the parsed_files
                parsed_files.add(filename)
                with open(parsed_files_path, 'a') as f:
                    f.write(filename + '\n')
            else:
                print(f'\nSkipping {filename}')

if __name__ == "__main__":
    main()