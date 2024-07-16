import pandas as pd

# Load the CSV file
file_path = 'file.csv'
sms_log = pd.read_csv(file_path)

# Define the user's phone number
user_phone_number = "whatsapp:+12294045482"

# Group messages by chat
chats = {}
for index, row in sms_log.iterrows():
    contact_number = row["From"] if row["From"] != user_phone_number else row["To"]
    if contact_number not in chats:
        chats[contact_number] = []
    chats[contact_number].append({
        "Body": row["Body"],
        "SentDate": row["SentDate"],
        "Direction": "inbound" if row["Direction"] == "inbound" else "outbound"
    })

# Start the HTML content

# Start the HTML content with a counter
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>the whatsapp scraperfgjjh</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #ece5dd;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 10px;
        }
        .chat-container {
            display: none;
        }
        .chat-list {
            list-style: none;
            padding: 0;
        }
        .chat-list li {
            padding: 10px;
            border-bottom: 1px solid #ddd;
            cursor: pointer;
        }
        .chat-list li:hover {
            background-color: #f1f1f1;
        }
        .message {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            max-width: 80%;
        }
        .message.inbound {
            background-color: #dcf8c6;
            align-self: flex-start;
        }
        .message.outbound {
            background-color: #ffffff;
            align-self: flex-end;
            text-align: right;
        }
        .timestamp {
            font-size: 0.8em;
            color: #999;
        }
        .contact-header {
            font-weight: bold;
            font-size: 1.2em;
            margin-bottom: 10px;
            cursor: pointer;
        }
        .counter {
            text-align: center;
            font-size: 1.5em;
            margin: 20px 0;
        }
    </style>
    <script>
        function showChat(contact) {
            document.querySelectorAll('.chat-container').forEach(chat => {
                chat.style.display = 'none';
            });
            document.getElementById(contact).style.display = 'block';
            document.getElementById('chat-list').style.display = 'none';
        }

        function showChatList() {
            document.querySelectorAll('.chat-container').forEach(chat => {
                chat.style.display = 'none';
            });
            document.getElementById('chat-list').style.display = 'block';
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="counter">
            Number of different contacts: """ + str(len(chats)) + """
        </div>
        <ul id="chat-list" class="chat-list">
"""
#ron is testing

# Generate HTML for the chat list
for contact in chats.keys():
    html_content += f"""
            <li onclick="showChat('{contact}')">Chat with {contact}</li>
    """

html_content += """
        </ul>
"""

# Generate HTML for each chat
for contact, messages in chats.items():
    html_content += f"""
    <div id="{contact}" class="chat-container">
        <div class="contact-header" onclick="showChatList()">Chat with {contact}</div>
    """
    for message in messages:
        html_content += f"""
        <div class="message {message['Direction']}">
            <p>{message['Body']}</p>
            <div class="timestamp">{message['SentDate']}</div>
        </div>
        """
    html_content += """
    </div>
    """

# End the HTML content
html_content += """
    </div>
</body>
</html>
"""

# Save the HTML content to a file
output_path = 'chat_display_with_navigation.html'
with open(output_path, "w", encoding="utf-8") as file:
    file.write(html_content)

output_path
