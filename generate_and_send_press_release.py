import openai
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
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
    new_code = os.popen(f'git show {commit_hash} --name-only --pretty=""').read().strip()

    return commit_message, new_code


# Define a function to generate the press release based on the latest commit details
def generate_press_release():
    commit_message, new_code = get_latest_commit_details()

    # Use the commit message and new lines of code to prompt the LLM
    prompt = (
        f"Generate a marketing/press release based on the following code update:\n\n"
        f"Commit Message: {commit_message}\n\n"
        f"New Code Changes:\n{new_code}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    press_release = response['choices'][0]['message']['content'].strip()

    # Save the press release to a file
    with open('press_release.txt', 'w') as file:
        file.write(press_release)

    return press_release


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
    press_release = generate_press_release()
    send_email("New Press Release", press_release, recipient_email)
