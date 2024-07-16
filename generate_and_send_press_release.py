from openai import OpenAI
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize the OpenAI client
client = OpenAI()

# Load the OpenAI API key and other environment variables
client.api_key = os.getenv("OPENAI_API_KEY")
email_address = os.getenv("EMAIL_ADDRESS")
email_password = os.getenv("EMAIL_PASSWORD")
recipient_email = os.getenv("RECIPIENT_EMAIL")


# Function to get the latest commit message and new lines of code
def get_latest_commit_details():
    try:
        # Get the latest commit hash
        commit_hash = os.popen('git log -1 --pretty=%H').read().strip()
        if not commit_hash:
            raise ValueError("Failed to retrieve the latest commit hash.")

        # Get the latest commit message
        commit_message = os.popen('git log -1 --pretty=%B').read().strip()
        if not commit_message:
            raise ValueError("Failed to retrieve the latest commit message.")

        # Get the new lines of code in the latest commit
        new_code = os.popen(f'git diff {commit_hash}^1 {commit_hash} --unified=0 | grep "^[+-]" | grep -v "^[+-][+-]"').read().strip()
        if not new_code:
            raise ValueError("Failed to retrieve new lines of code in the latest commit.")

        return commit_message, new_code

    except Exception as e:
        print(f"Error retrieving commit details: {e}")
        return None, None


# Function to generate the press release based on the latest commit details
def generate_press_release():
    commit_message, new_code = get_latest_commit_details()
    if not commit_message or not new_code:
        print("Failed to retrieve commit details or new code.")
        return

    # Use the commit message and new lines of code to prompt the LLM
    prompt = (
        f"You are about to get to recent change in code of a product, make a marketing update out of it, figure out what's the new feature and describe it like you sell it:\n\n"
        f"New Code Changes:\n{new_code}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are CommitMarketer, an AI-powered assistant designed to generate marketing content and updates based on Git commits. Be short and informative."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        press_release = response.choices[0].message.content

        # Save the press release to a file
        with open('press_release.txt', 'w') as file:
            file.write(press_release)

        return press_release

    except Exception as e:
        print(f"Error generating press release: {e}")
        return None


# Function to send an email with the press release
def send_email(subject, body, recipient):
    try:
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

    except Exception as e:
        print(f"Error sending email: {e}")


if __name__ == "__main__":
    press_release = generate_press_release()
    if press_release:
        send_email("New Press Release", press_release, recipient_email)
