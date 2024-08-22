from pdf_text_extractor.pdf_extractor import PdfParser
import json
import os
import re
from groq import Groq
from system_prompt import prompt

def load_skills_from_json(json_file_path):
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            return json.load(file)
    return []

def save_skills_to_json(json_file_path, skills):
    existing_skills = load_skills_from_json(json_file_path)
    existing_skill_set = {skill['skill'] for skill in existing_skills}  # Set of existing skills for quick lookup

    for skill in skills:
        if skill['skill'] not in existing_skill_set:  # Check for duplicates
            existing_skills.append(skill)  # Append only if it's a new skill

    with open(json_file_path, 'w') as file:
        json.dump(existing_skills, file, indent=4)

def main():
    client = Groq(api_key="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")
    
    resume_pdf_path = r'test_resumes/54665_Manjunath_S.pdf'
    
    pdf_parser = PdfParser(resume_pdf_path)
    resume_text = pdf_parser.get_cleaned_text()

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

    response_content = response.choices[0].message.content
    print(response_content)
    if not response_content.strip():
        print(f"\nNo content received from Groq API for {resume_pdf_path}. Skipping.")
        return None

    try:
        json_match = re.search(r'\[.*\]', response_content, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON array found in the response content")
        response_skills = json.loads(json_match.group(0))
    except (json.JSONDecodeError, ValueError) as e:
        print(f"\nError decoding JSON for {resume_pdf_path}: {e}")
        print(f"\nReceived content: {response_content}")
        return None

    # Save skills to JSON file
    json_file_path = 'extracted_skills.json'
    save_skills_to_json(json_file_path, response_skills)

if __name__ == "__main__":
    main()