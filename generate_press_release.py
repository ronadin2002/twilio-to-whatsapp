import openai
import os

# Load the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")


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

    response = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,
        max_tokens=500
    )

    press_release = response.choices[0].text.strip()

    # Save the press release to a file
    with open('press_release.txt', 'w') as file:
        file.write(press_release)

    print("Press release generated and saved to press_release.txt")


if __name__ == "__main__":
    generate_press_release()
