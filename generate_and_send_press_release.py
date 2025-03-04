from openai import OpenAI
import os
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


client = OpenAI()


client.api_key = os.getenv("OPENAI_API_KEY")
email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")
recipient_email = os.getenv("RECIPIENT_EMAIL")


# Define a function to get the latest commit message and new lines of code
def get_latest_commit_details():
    # Get the latest commit hash
    commit_hash = os.popen('git log -1 --pretty=%H').read().strip()

    # Get the latest commit message
    commit_message = os.popen('git log -1 --pretty=%B').read().strip()

    # Get the new lines of code in the latest commit
    new_code = os.popen(f'git diff {commit_hash}~1 {commit_hash} --unified=0').read().strip()
    print(new_code)
    return commit_message, new_code


def get_changed_code():
    prev_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD~1']).strip().decode('utf-8')
    current_commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
    new_code = subprocess.check_output(['git', 'diff', prev_commit, current_commit]).strip().decode('utf-8')
    commit_message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).strip().decode('utf-8')
    print(new_code)
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

    return press_release, commit_message, new_code


# Define a function to send an email with the press release
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
    press_release, commit_message, new_code = generate_press_release()
    email_body = f"{press_release}\n\nCommit Message:\n{commit_message}\n\nNew Code Changes:\n{new_code}"
    send_email("New Press Release", email_body, recipient_email)
