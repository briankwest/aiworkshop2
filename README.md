# AI Communication Agent

## Table of Contents

1. [Introduction](#introduction)
2. [Overview](#overview)
3. [API Information](#api-information)
4. [Features & Capabilities](#features--capabilities)
5. [Environment Setup](#environment-setup)
6. [Functions & Implementation](#functions--implementation)
7. [Sample Queries & Responses](#sample-queries--responses)
8. [Conclusion](#conclusion)

---

## Introduction

This AI Communication Agent is designed to handle call transfers and send messages efficiently. It leverages the SignalWire AI Gateway to provide seamless communication services.

## Overview

- Built using **SignalWire AI Gateway (SWAIG)** and **Python**.
- Supports **call transfers** to various departments.
- Allows sending **SMS messages** to specified phone numbers.

## API Information

- **Base API URL:** Not applicable for local Flask application.
- **Expected Usage:**
  - **Transfer call:** Redirects calls to specified departments.
  - **Send message:** Sends SMS messages to specified phone numbers.
- **Required Parameters:**
  - For call transfer: `target` (department to transfer the call to)
  - For sending messages: `to` (recipient's phone number), `message` (content of the message)
- **Authentication:** Managed through environment variables.

## Features & Capabilities

- **Call Transfer**: Redirects calls to sales, support, billing, or general departments.
- **Message Sending**: Sends SMS messages to any phone number in e.164 format.

## Environment Setup

Ensure you have the following installed:

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask signalwire-swaig requests python-dotenv signalwire-swml
```

Create a `.env` file with your configuration:

```ini
# .env file
TRANSFER_SALES=+19184231212
TRANSFER_SUPPORT=+19184231213
TRANSFER_BILLING=+19184231214
TRANSFER_GENERAL=+19184231215
FROM_NUMBER=+16503820000
PORT=5000
DEBUG=True
```

## Functions & Implementation

### Call Transfer and Message Sending

```python
from typing import overload
from flask import Flask, request, jsonify
from signalwire_ml import SignalWireML
from signalwire_swaig.core import SWAIG, SWAIGArgument
import os
import requests
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
    transfer = SignalWireML(version="1.0.0")

    transfer.add_application(
        "main",
        "connect",
        {"to": TRANSFER_TARGETS.get(target.lower(), TRANSFER_TARGETS["general"])},
    )
    return "Tell the user you are going to transfer the call to whoever they asked for. Do not change languages from the one you are currently using. Do not hangup.", {"SWML": transfer.render(), "transfer": "true"}

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
        return "Message has been sent.", {"SWML": msg.render()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), debug=os.getenv('DEBUG', False))
```

## Sample Queries & Responses

### Example Transfer Query:

```json
{
  "function": "transfer",
  "arguments": {
    "target": "sales"
  }
}
```

### Example Message Query:

```json
{
  "function": "send_message",
  "arguments": {
    "to": "+1234567890",
    "message": "Hello from SignalWire!"
  }
}
```

## Conclusion

The AI Communication Agent provides efficient call transfer and messaging capabilities, ensuring seamless communication for your business needs.
