"""
Upwork Winning Proposal Generator v4.0
Pain point focused. Solution driven. Natural language.
"""

import re

class UpworkProposalGenerator:

    def __init__(self):
        self.skills = {
            "data_annotation": ["data annotation", "labeling", "tagging", "annotation", "ai training", "machine learning data", "classify", "categorize", "label"],
            "virtual_assistant": ["virtual assistant", "va", "admin", "administrative", "calendar", "email management", "scheduling", "assistant", "support"],
            "web_research": ["research", "lead generation", "list building", "data collection", "web scraping", "linkedin", "contact list", "find", "leads", "contacts", "emails"],
            "data_entry": ["data entry", "typing", "excel", "spreadsheet", "copy paste", "transcription", "form filling", "input", "migrate", "transfer"]
        }

        # Tools you use for each job type
        self.my_tools = {
            "data_annotation": "Label Studio and Google Sheets",
            "virtual_assistant": "Google Workspace and Notion",
            "web_research": "Apollo, LinkedIn Sales Navigator and Google Sheets",
            "data_entry": "Excel, Google Sheets and Airtable"
        }

        # Pain points clients usually have
        self.pain_points = {
            "data_annotation": {
                "pain": "Most annotation work comes back inconsistent or full of errors. Then you waste time fixing it yourself.",
                "solution": "I follow strict guidelines and double check every label before delivery. You get clean data the first time."
            },
            "virtual_assistant": {
                "pain": "Most VAs need constant hand holding. You end up spending more time explaining than doing the work yourself.",
                "solution": "I figure things out on my own. You give me the task and I handle it. No back and forth."
            },
            "web_research": {
                "pain": "Bad lead lists are everywhere. Wrong emails. Outdated info. You pay for data you cannot even use.",
                "solution": "I verify every contact before adding it. If the email bounces or the person left the company I remove it. You only get leads that actually work."
            },
            "data_entry": {
                "pain": "Data entry mistakes create bigger problems down the line. One wrong entry can mess up reports and decisions.",
                "solution": "I check my work twice. Every row. Every field. You get accurate data without surprises later."
            }
        }

    def detect_job_type(self, job_description):
        job_lower = job_description.lower()
        scores = {}
        for job_type, keywords in self.skills.items():
            score = sum(1 for keyword in keywords if keyword in job_lower)
            scores[job_type] = score
        best_match = max(scores, key=scores.get)
        return best_match if scores[best_match] > 0 else "data_entry"

    def extract_key_info(self, job_description):
        info = {
            "main_task": "",
            "quantity": None,
            "deliverable": "",
            "tool_mentioned": None,
            "urgency": False
        }

        sentences = re.split(r'[.!?\n]', job_description)
        clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        if clean_sentences:
            info["main_task"] = clean_sentences[0]

        qty_match = re.search(r'(\d{1,6}(?:,\d{3})*)\s*(?:leads?|contacts?|entries?|rows?|records?|items?|emails?|names?|companies?|data points?)', job_description, re.IGNORECASE)
        if qty_match:
            info["quantity"] = qty_match.group(1)
            info["deliverable"] = qty_match.group(0)

        tools = ["excel", "google sheets", "airtable", "notion", "salesforce", "hubspot", "linkedin", "apollo", "zoominfo"]
        for tool in tools:
            if tool in job_description.lower():
                info["tool_mentioned"] = tool.title()
                break

        if any(word in job_description.lower() for word in ["asap", "urgent", "immediately", "quickly", "fast", "today"]):
            info["urgency"] = True

        return info

    def generate_proposal(self, job_description, past_experience=None, your_name=None):
        job_type = self.detect_job_type(job_description)
        info = self.extract_key_info(job_description)
        pain = self.pain_points[job_type]
        tools = self.my_tools[job_type]

        lines = []

        # OPENING
        if info["quantity"] and info["deliverable"]:
            lines.append("Hi,")
            lines.append("")
            lines.append(f"I can get you those {info['deliverable']}.")
        elif info["main_task"]:
            task_short = info["main_task"][:60].rstrip()
            lines.append("Hi,")
            lines.append("")
            lines.append(f"Read your post. I can help with this.")
        else:
            lines.append("Hi,")
            lines.append("")
            lines.append("I can help with this.")

        lines.append("")

        # PAIN POINT - show you understand their problem
        lines.append(pain["pain"])
        lines.append("")

        # SOLUTION - what you do differently
        lines.append(pain["solution"])
        lines.append("")

        # TOOLS - always mention what you use
        if info["tool_mentioned"]:
            lines.append(f"I work with {info['tool_mentioned']} daily. Also use {tools} depending on what the project needs.")
        else:
            lines.append(f"I use {tools} for this type of work.")

        lines.append("")

        # EXPERIENCE - if provided
        if past_experience:
            lines.append(f"Recently I {past_experience}.")
            lines.append("")

        # URGENCY
        if info["urgency"]:
            lines.append("I see this is time sensitive. I can start today.")
            lines.append("")

        # QUESTION
        questions = {
            "data_annotation": "Do you have guidelines ready or do you need me to set up a system?",
            "virtual_assistant": "What tools are you already using? I can adapt to your setup.",
            "web_research": "What info do you need for each contact? I want to make sure the list is actually useful for you.",
            "data_entry": "Where is the source data and where should it go? I want to understand the workflow."
        }
        lines.append(questions[job_type])
        lines.append("")

        # CLOSE
        lines.append("Happy to do a test batch first so you can see the quality before committing.")
        lines.append("")
        lines.append("Let me know.")

        if your_name:
            lines.append("")
            lines.append(your_name)

        return "\n".join(lines), job_type


def main():
    print("=" * 50)
    print("UPWORK PROPOSAL GENERATOR v4")
    print("=" * 50)

    generator = UpworkProposalGenerator()

    while True:
        print("\nPaste job description (Enter twice when done):")
        print("-" * 40)

        lines = []
        empty_count = 0
        while True:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append(line)
            else:
                empty_count = 0
                lines.append(line)

        job_description = "\n".join(lines).strip()

        if not job_description:
            print("No job description. Try again.")
            continue

        print("\nSimilar work you did? (Enter to skip)")
        print("Example: built a list of 500 SaaS founders with verified emails")
        past_experience = input("> ").strip() or None

        print("\nYour name? (Enter to skip)")
        your_name = input("> ").strip() or None

        print("\n" + "=" * 50)
        print("YOUR PROPOSAL")
        print("=" * 50 + "\n")

        proposal, job_type = generator.generate_proposal(job_description, past_experience, your_name)
        print(proposal)

        print("\n" + "=" * 50)
        print(f"Job type: {job_type.replace('_', ' ').title()}")
        print("=" * 50)

        print("\nBefore submitting:")
        print("1. Add specifics from the job post")
        print("2. Remove parts that do not fit")
        print("3. Keep it short")

        print("\nAnother? (y/n)")
        if input("> ").strip().lower() not in ["y", "yes"]:
            print("\nGood luck!")
            break


if __name__ == "__main__":
    main()
