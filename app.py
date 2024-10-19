import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initialize app with bot token
app: App = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Listen for "++" in any messages.
# scope is set by which events the bot subscribes)
@app.message(r'\+\+')
def grant_karma(message: dict, say) -> None:
    full_message_text: str = message['text']
    total_karma: int = 0
    words: list[str] = full_message_text.split()
    parsed_recipient: bool = False
    for word in words:
        if word.endswith('++'):
            recipient: str = word[:-len('++')]
            # send a message to the channel where the event happened
            say(f"{recipient} leveled up ({total_karma} karma)")
            say(f"Hey there <@{message['user']}>!")
            parsed_recipient = True
            break
    if not parsed_recipient:
        print("ERROR: couldn't parse the message to get the recipient "
              "out of full message text: {full_message_text}")

# Fire up the app
if __name__ == "__main__":
    (SocketModeHandler(app=app,
                      app_token=os.environ["SLACK_APP_TOKEN"]).start())