# Brightside Dental demo: AI chatbot + lead automation

A portfolio demo for a fictional dental office. Shows one chatbot and one automation built in n8n, embedded on a branded site.

```
site/                                    Static demo site (index.html, case-study.html, config.js)
n8n/1-chat-assistant.workflow.json       Chatbot: Chat Trigger -> Claude agent (+ memory, save_lead tool)
n8n/2-lead-automation.workflow.json      Automation: Webhook -> clean -> HubSpot upsert -> Slack alert -> respond
n8n/build.py                             Regenerates both JSON files if you want to edit the prompt
```

## Setup (about 20 minutes)

The workflows were generated from n8n's node format but not run inside n8n yet. Expect to fix small field differences on first import, depending on your n8n version.

### 1. Import the automation first

1. In n8n: Workflows > Import from file > `2-lead-automation.workflow.json`.
2. Open **Save Contact in HubSpot**. Pick your HubSpot credential (the sandbox account from the lead pipeline works). If the Upsert operation looks different in your version, use Create or Update Contact by email.
3. Open **Alert Front Desk in Slack**. Pick your Slack credential and an existing channel (default name is `#new-patient-leads`).
4. Click **Publish / Activate**. Copy the **Production URL** from the Webhook node. It ends in `/webhook/brightside-lead`.

### 2. Import the chatbot

1. Import `1-chat-assistant.workflow.json`.
2. Open the **Claude** node and pick your Anthropic credential. If the model id is not in the list, type `claude-sonnet-5-5` or choose any current Sonnet model.
3. Open the **save_lead** tool node. Replace `https://YOUR-N8N-HOST/webhook/brightside-lead` with the Production URL from step 1.4.
4. Open **Website Chat**. Confirm "Make Chat Publicly Available" is on and the mode is Embedded. Allowed Origins is `*` for the demo. Tighten it to your site's domain later.
5. Activate the workflow. Copy the chat **Production URL**.

### 3. Connect the site

Open `site/config.js`, replace `PASTE_YOUR_N8N_CHAT_WEBHOOK_URL_HERE` with the chat Production URL, and save. (The URL lives in this one file so design changes to `index.html` never overwrite it.)

Run it locally:

```
cd site
python3 -m http.server 8080
```

Open http://localhost:8080.

### 4. Test before recording

1. Ask: "What time do you open on Friday?" Expect 8:00 am to 1:00 pm.
2. Ask: "Do you take Delta Dental?" Expect a front desk follow-up, not a yes or no.
3. Ask: "My tooth really hurts and my face is swollen." Expect the safety message, no diagnosis.
4. Say you want to book Wed 11:00. Give a test name, email and reason. Expect the Slack alert and a contact in HubSpot.
5. Check the n8n **Executions** tab for both workflows. Keep a successful run open for the video.

## Recording checklist (60 seconds)

- Tabs open and ready: demo site, n8n chat workflow canvas, n8n lead workflow canvas, Slack channel, HubSpot contact list.
- Use a fake test lead that is easy to read, like "Jordan Test".
- Hide bookmarks bar (Cmd+Shift+B) and personal tabs.
- Order: site and chat (20s) > ask a question and book (15s) > Slack alert and HubSpot contact (10s) > n8n canvas of the two workflows (10s) > close (5s).

## Going live later

Deploy `site/` to Azure Static Web Apps (free tier). Host n8n somewhere always on, set Allowed Origins to the site's domain, and update the webhook URLs.

## Hero photo

The right side of the hero shows a placeholder illustration. To use a photo, save a landscape or portrait image as `site/images/hero.jpg` (create the `images` folder). It fills the panel automatically. Use a photo you have the license for, such as a free-license image from Unsplash or Pexels, or one you generate yourself. If the file is missing, the placeholder stays.
