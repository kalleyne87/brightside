import json

SYSTEM = """You are the front-desk assistant for Brightside Family Dental, a small dental office. This is a demo business.

FACTS YOU MAY USE (answer only from these):
- Address: 214 Maple Street, Suite 3, Springfield. Free parking behind the building. Step-free entrance on the east side.
- Hours: Monday to Thursday 8:00 am to 5:00 pm. Friday 8:00 am to 1:00 pm. Closed Saturday and Sunday.
- Services and typical prices: cleaning and exam $120 to $180, teeth whitening $350, digital X-rays $60 to $110, fillings $150 to $300, crowns $900 to $1,300, emergency visit $95 plus treatment.
- Insurance: we work with most major plans. Exact coverage is confirmed by the front desk, never by you.
- New patients are welcome. First visit is a 45 minute cleaning and exam.
- Open slots this week: Tue 9:00, Tue 2:15, Wed 11:00, Wed 3:45, Thu 9:45, Thu 1:00. These are requests, not confirmed bookings.

RULES:
1. Answer only from the facts above. If you do not know, say so and offer to have the front desk follow up.
2. Never give medical advice or diagnose. For severe pain, swelling, bleeding that will not stop, or a knocked-out tooth, tell the person to call the office during open hours or go to urgent care or call emergency services right away.
3. Keep replies short and friendly, two or three sentences.
4. When someone wants to book or have the office follow up, collect their full name, an email or phone number, and the reason for the visit. Ask for one missing detail at a time.
5. As soon as you have a name, a contact method and a reason, call the save_lead tool once. Then tell the person the front desk will confirm by the next business morning.
6. Never invent availability, prices or policies. Never promise insurance coverage."""

chat = {
  "name": "Brightside Dental - Chat Assistant",
  "nodes": [
    {
      "parameters": {
        "public": True,
        "mode": "webhook",
        "options": {"allowedOrigins": "*", "responseMode": "lastNode"}
      },
      "id": "chat-trigger",
      "name": "Website Chat",
      "type": "@n8n/n8n-nodes-langchain.chatTrigger",
      "typeVersion": 1.1,
      "position": [0, 0],
      "webhookId": "brightside-dental-chat"
    },
    {
      "parameters": {
        "promptType": "define",
        "text": "={{ $json.chatInput }}",
        "options": {"systemMessage": SYSTEM}
      },
      "id": "agent",
      "name": "Front Desk Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.7,
      "position": [320, 0]
    },
    {
      "parameters": {
        "model": {"__rl": True, "value": "claude-sonnet-5-5", "mode": "id"},
        "options": {"temperature": 0.3, "maxTokensToSample": 500}
      },
      "id": "model",
      "name": "Claude",
      "type": "@n8n/n8n-nodes-langchain.lmChatAnthropic",
      "typeVersion": 1.3,
      "position": [200, 240]
    },
    {
      "parameters": {
        "sessionIdType": "customKey",
        "sessionKey": "={{ $('Website Chat').item.json.sessionId }}",
        "contextWindowLength": 10
      },
      "id": "memory",
      "name": "Conversation Memory",
      "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
      "typeVersion": 1.3,
      "position": [360, 240]
    },
    {
      "parameters": {
        "toolDescription": "Save a patient's request to be contacted or to book. Call once, only after you have the patient's full name, an email or phone number, and the reason for the visit.",
        "method": "POST",
        "url": "https://YOUR-N8N-HOST/webhook/brightside-lead",
        "sendBody": True,
        "specifyBody": "json",
        "jsonBody": "={\n  \"name\": \"{name}\",\n  \"email\": \"{email}\",\n  \"phone\": \"{phone}\",\n  \"reason\": \"{reason}\",\n  \"preferred_time\": \"{preferred_time}\"\n}",
        "placeholderDefinitions": {
          "values": [
            {"name": "name", "description": "Patient's full name", "type": "string"},
            {"name": "email", "description": "Patient's email, or an empty string if not given", "type": "string"},
            {"name": "phone", "description": "Patient's phone number, or an empty string if not given", "type": "string"},
            {"name": "reason", "description": "Reason for the visit, in a few words", "type": "string"},
            {"name": "preferred_time", "description": "Preferred appointment time, or an empty string if not given", "type": "string"}
          ]
        }
      },
      "id": "save-lead-tool",
      "name": "save_lead",
      "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
      "typeVersion": 1.1,
      "position": [520, 240]
    }
  ],
  "connections": {
    "Website Chat": {"main": [[{"node": "Front Desk Agent", "type": "main", "index": 0}]]},
    "Claude": {"ai_languageModel": [[{"node": "Front Desk Agent", "type": "ai_languageModel", "index": 0}]]},
    "Conversation Memory": {"ai_memory": [[{"node": "Front Desk Agent", "type": "ai_memory", "index": 0}]]},
    "save_lead": {"ai_tool": [[{"node": "Front Desk Agent", "type": "ai_tool", "index": 0}]]}
  },
  "settings": {"executionOrder": "v1"},
  "pinData": {}
}

CODE = """const b = $input.first().json.body ?? $input.first().json;
const clean = (v) => (typeof v === 'string' ? v.trim() : '');
const full = clean(b.name);
const parts = full.split(/\\s+/);
const email = clean(b.email).toLowerCase();
const phone = clean(b.phone);
const reason = clean(b.reason);
const urgent = /pain|swell|bleed|broken|knocked|emergency|infection/i.test(reason);
return [{ json: {
  firstName: parts[0] || '',
  lastName: parts.slice(1).join(' '),
  fullName: full,
  email,
  phone,
  reason,
  preferredTime: clean(b.preferred_time),
  urgent,
  hasContact: Boolean(email || phone),
  receivedAt: new Date().toISOString()
}}];"""

lead = {
  "name": "Brightside Dental - Lead Automation",
  "nodes": [
    {
      "parameters": {"httpMethod": "POST", "path": "brightside-lead", "responseMode": "responseNode", "options": {}},
      "id": "webhook", "name": "New Lead Webhook",
      "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [0, 0],
      "webhookId": "brightside-lead"
    },
    {
      "parameters": {"jsCode": CODE},
      "id": "clean", "name": "Clean and Flag Lead",
      "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [240, 0]
    },
    {
      "parameters": {
        "conditions": {
          "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
          "conditions": [{
            "id": "has-email", "operator": {"type": "string", "operation": "notEmpty", "singleValue": True},
            "leftValue": "={{ $json.email }}", "rightValue": ""
          }],
          "combinator": "and"
        },
        "options": {}
      },
      "id": "has-email", "name": "Has Email?",
      "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": [480, 0]
    },
    {
      "parameters": {
        "authentication": "appToken",
        "resource": "contact",
        "operation": "upsert",
        "email": "={{ $json.email }}",
        "additionalFields": {
          "firstName": "={{ $json.firstName }}",
          "lastName": "={{ $json.lastName }}",
          "phoneNumber": "={{ $json.phone }}"
        }
      },
      "id": "hubspot", "name": "Save Contact in HubSpot",
      "type": "n8n-nodes-base.hubspot", "typeVersion": 2, "position": [720, -100]
    },
    {
      "parameters": {
        "select": "channel",
        "channelId": {"__rl": True, "value": "#new-patient-leads", "mode": "name"},
        "text": "={{ ($('Clean and Flag Lead').item.json.urgent ? ':rotating_light: URGENT ' : '') + 'New patient request\\nName: ' + $('Clean and Flag Lead').item.json.fullName + '\\nContact: ' + ($('Clean and Flag Lead').item.json.email || $('Clean and Flag Lead').item.json.phone || 'none given') + '\\nReason: ' + $('Clean and Flag Lead').item.json.reason + '\\nPreferred time: ' + ($('Clean and Flag Lead').item.json.preferredTime || 'not given') }}",
        "otherOptions": {}
      },
      "id": "slack", "name": "Alert Front Desk in Slack",
      "type": "n8n-nodes-base.slack", "typeVersion": 2.3, "position": [960, 0]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { saved: true, message: 'Request received. The front desk will confirm by the next business morning.' } }}",
        "options": {}
      },
      "id": "respond", "name": "Respond to Chatbot",
      "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.1, "position": [1200, 0]
    }
  ],
  "connections": {
    "New Lead Webhook": {"main": [[{"node": "Clean and Flag Lead", "type": "main", "index": 0}]]},
    "Clean and Flag Lead": {"main": [[{"node": "Has Email?", "type": "main", "index": 0}]]},
    "Has Email?": {"main": [
      [{"node": "Save Contact in HubSpot", "type": "main", "index": 0}],
      [{"node": "Alert Front Desk in Slack", "type": "main", "index": 0}]
    ]},
    "Save Contact in HubSpot": {"main": [[{"node": "Alert Front Desk in Slack", "type": "main", "index": 0}]]},
    "Alert Front Desk in Slack": {"main": [[{"node": "Respond to Chatbot", "type": "main", "index": 0}]]}
  },
  "settings": {"executionOrder": "v1"},
  "pinData": {}
}

json.dump(chat, open("1-chat-assistant.workflow.json", "w"), indent=2)
json.dump(lead, open("2-lead-automation.workflow.json", "w"), indent=2)
print("written")
