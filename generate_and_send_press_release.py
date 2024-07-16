from openai import OpenAI
import os
import smtplib
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


client = OpenAI()

# Load the OpenAI API key from environment variables
client.api_key = os.getenv("OPENAI_API_KEY")
email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")
recipient_email = os.getenv("RECIPIENT_EMAIL")


# Define a function to get the latest commit message and new lines of code
def get_latest_commit_details():
    # Get the latest commit hash
    commit_hash = subprocess.check_output(['git', 'log', '-1', '--pretty=%H']).decode('utf-8').strip()

    # Get the latest commit message
    commit_message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode('utf-8').strip()

    try:
        # Attempt to get the new lines of code in the latest commit
        diff_output = subprocess.check_output(['git', 'diff', f'{commit_hash}^1', commit_hash, '--unified=0']).decode('utf-8')
    except subprocess.CalledProcessError as e:
        if e.returncode == 128:
            # If it's the initial commit, diff won't work. Get the initial commit changes instead.
            diff_output = subprocess.check_output(['git', 'show', '--unified=0', commit_hash]).decode('utf-8')
        else:
            raise

    new_code_lines = []
    for line in diff_output.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            new_code_lines.append(line)
        elif line.startswith('-') and not line.startswith('---'):
            new_code_lines.append(line)
    new_code = '\n'.join(new_code_lines)

    return commit_message, new_code

# Define a function to generate the press release based on the latest commit details
def generate_press_release():
    commit_message, new_code = get_latest_commit_details()

    # Use the commit message and new lines of code to prompt the LLM
    prompt = (
        f"you are about to get to recent change in code of a product, make an marketing update out of it, figure out whats the new feature and describe it like you sale it.:\n\n"
        f"New Code Changes:\n{new_code}"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are CommitMarketer, an AI-powered assistant designed to generate marketing content and updates based on Git commits. be short and inforamtive"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    press_release = response.choices[0].message.content

    # Save the press release to a file
    with open('press_release.txt', 'w') as file:
        file.write(press_release)

    return press_release



# Definej a function to send an email with the press release
def send_email(subject, body, recipient):
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_address, email_password)
    text = msg.as_string()
    server.sendmail(email_address, recipient, text)
    server.quit()

    print("Email sent successfully")


if __name__ == "__main__":
    press_release = generate_press_release()
    send_email("New Press Release", press_release, recipient_email)
