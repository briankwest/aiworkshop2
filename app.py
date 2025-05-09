from typing import overload
from flask import Flask, request, jsonify
from signalwire_swml.swml import SignalWireSWML
from signalwire_swaig.swaig import SWAIG, SWAIGArgument
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Get transfer targets from environment variables
TRANSFER_TARGETS = {
    "sales": os.getenv("TRANSFER_SALES"),
    "support": os.getenv("TRANSFER_SUPPORT"),
    "billing": os.getenv("TRANSFER_BILLING"),
    "general": os.getenv("TRANSFER_GENERAL")
}

app = Flask(__name__)
swaig = SWAIG(app)

@swaig.endpoint("Transfer call",
    target=SWAIGArgument("string", "the target to transfer the user to (sales, support, billing, general)"))
def transfer(target, meta_data_token=None, meta_data=None):
    transfer = SignalWireSWML(version="1.0.0")
    
    # Check if the target exists in our TRANSFER_TARGETS dictionary
    if target.lower() not in TRANSFER_TARGETS:
        return f"Sorry, there is no department by that name: {target}. Please ask for sales, support, billing, or general inquiries.", {}
    
    # Determine the transfer method based on the target format
    target_uri = TRANSFER_TARGETS[target.lower()]
    if target_uri.startswith("sip:"):
        transfer.add_application(
            "main",
            "sip_refer",
            {"to_uri": target_uri},
        )
    elif target_uri.startswith("+"):
        transfer.add_application(
            "main",
            "connect",
            {"to": target_uri},
        )
    
    return "Tell the user you are going to transfer the call to whoever they asked for. Do not change languages from the one you are currently using. Do not hangup.", [{"set_meta_data": meta_data,"SWML": transfer.render(), "transfer": "true"}]

@swaig.endpoint("Send message",
    to=SWAIGArgument("string", "Phone number to send the message to in e.164 format. eg +1234567890"),
    message=SWAIGArgument("string", "Message content to send"))
def send_message(to, message, meta_data_token=None, meta_data=None):
        msg = SignalWireML(version="1.0.0")

        msg.add_application(
            "main",
            "send_sms",
            {
                "to_number": to,
                "from_number": os.getenv("FROM_NUMBER"),
                "body": message,
            }
        )
        return "Message has been sent.", [{"SWML": msg.render()}]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), debug=os.getenv('DEBUG', False))