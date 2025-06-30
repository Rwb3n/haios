import os

def update_clarification_files():
    clarifications_dir = "D:\\PROJECTS\\haios\\docs\\ADR\\clarifications"
    for filename in os.listdir(clarifications_dir):
        if filename.endswith("_clarification.md"):
            filepath = os.path.join(clarifications_dir, filename)
            
            # Extract ADR-ID and set QUESTION_ID
            adr_id = filename.split('_')[0]
            question_id = "1"

            with open(filepath, 'r') as f:
                content = f.read()

            # Replace placeholders
            content = content.replace("{{ADR-ID}}", adr_id)
            content = content.replace("{{QUESTION_ID}}", question_id)

            with open(filepath, 'w') as f:
                f.write(content)

if __name__ == "__main__":
    update_clarification_files()
