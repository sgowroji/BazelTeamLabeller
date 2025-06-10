import os
import json
import google.generativeai as genai


PDF_FILE_PATH = "Teamlabels.pdf"  # Make sure this path is correct
BAZEL_TEAM_LABELS = [
    "team-Android",
    "team-Bazel",
    "team-CLI",
    "team-Configurability",
    "team-Core",
    "team-Documentation",
    "team-ExternalDeps",
    "team-Loading-API",
    "team-Local-Exec",
    "team-OSS",
    "team-Performance",
    "team-Remote-Exec",
    "team-Rules-API",
    "team-Rules-CPP",
    "team-Rules-ObjC",
    "team-Rules-Java",
    "team-Rules-Python",
    "team-Rules-Server",
    "team-Starlark-Integration",
    "team-Starlark-Interpreter"
]


def upload_pdf(pdf_file_path):
    """Uploads the PDF file to Gemini and returns the URI."""
    """
    This function attempts to upload a PDF to the Gemini API.  For local execution without
    a server, this part is difficult to replicate exactly.  I've added a placeholder, and
    you'll need to adapt this if you have a way to make files accessible to Gemini.
    """
    try:
        # Placeholder:  In a local script, you might not directly "upload" in the same way.
        #  If you have a publicly accessible URL for your PDF, you could use that.
        #  For local file processing, you might adapt the prompt to read the file content.

        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError(f"Error: PDF file not found at {pdf_file_path}")

        #  Here, we'll just return the file path as a stand-in URI for local processing.
        uploaded_file = genai.upload_file(PDF_FILE_PATH, mime_type="application/pdf")
        genai.upload_file(PDF_FILE_PATH)  # Wait for processing
        print(uploaded_file)  # Check file status
        return uploaded_file.uri
        print(f"Using local file path: {pdf_file_path} as a stand-in for Gemini upload.")
        return pdf_file_path  # Return the local file path

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None



def predict_team_label(pdf_uri, github_issue_title, github_issue_description):
    """Predicts the team label using Gemini."""
    generation_config = {
        "temperature": 0.2,  # More deterministic/focused response
        "max_output_tokens": 30,  # Short label expected
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="Output ONLY the team label (no other text)."
    )

    if not pdf_uri:  # Handle missing PDF
        return None
    label_list_string = ", ".join(f'"{label}"' for label in BAZEL_TEAM_LABELS)
    prompt = [
        f"""   **Role:** You are an expert GitHub issue triager with a deep understanding of software development categories.

**Objective:** Analyze the provided GitHub issue (considering its title, body description, and overall intent) and assign exactly ONE label that best categorizes its primary purpose or problem. **Do not assume an issue is documentation-related solely due to the presence of URLs.**

**Allowed Labels & Their Definitions:**

{label_list_string}

Team labels and their definitions:
----------------------------------
●  team-Android: Issues for Android team 
●  team-Bazel: General Bazel product/strategy issues 
●  team-CLI: Console UI 
●  team-Configurability: Issues for Configurability team. Includes: Core build 
configuration and transition system. Does not include: Changes to new or 
existing flags 
●  team-Core: Skyframe, bazel query, BEP, options parsing, bazelrc 
●  team-Documentation: Issues for Documentation team 
●  team-ExternalDeps: External dependency handling, Bzlmod, remote 
repositories, WORKSPACE file 
●  team-Loading-API: BUILD file and macro processing: labels, package(), 
visibility, glob 
●  team-Local-Exec: Issues for Execution (Local) team 
●  team-OSS: Issues for Bazel OSS team: installation, release process, Bazel 
packaging, website, docs infrastructure 
●  team-Performance: Issues for Bazel Performance team 
●  team-Remote-Exec: Issues for Execution (Remote) team 
●  team-Rules-API: API for writing rules/aspects: providers, runfiles, actions, 
artifacts 
●  team-Rules-CPP / team-Rules-ObjC: Issues for C++/Objective-C rules, 
including native Apple rule logic 
●  team-Rules-Java: Issues for Java rules 
●  team-Rules-Python: Issues for the native Python rules 
●  team-Rules-Server: Issues for server-side rules included with Bazel 
●  team-Starlark-Integration: Non-API Bazel + Starlark integration. Includes: 
how Bazel triggers the Starlark interpreter, Stardoc, builtins injection, character 
encoding. Does not include: BUILD or .bzl language issues. 
●  team-Starlark-Interpreter: Issues for the Starlark interpreter (anything in 
java.net.starlark). BUILD and .bzl API issues (which represent Bazel's integration 
with Starlark) go in team-Build-Language 
 
**GitHub Issue to Triage:**

Title: {github_issue_title}
Body Description: {github_issue_description}

**Predicted Label:**
    """  
    ]
    print("Prompt:", prompt)  # Keep the prompt printing for local debugging

    try:
        response = model.generate_content(prompt)
        if response and response.text:  # Check valid response and text
            predicted_label = response.text.strip()
            return predicted_label
        else:
            print("Error: Gemini API returned an empty response.")
            return None

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None



def main():
    """Main function to run the label prediction locally."""
    # 1.  Load API Key
    api_key = "AIzaSyDHIQAd-o7VKeDzfFwxZ66U3zaC3wWFWHM"
    if not api_key:
        print("Error: Gemini API key is missing.  Set the GEMINI_API_KEY environment variable or create config.json.")
        return  # Exit if no API key

    os.environ["GEMINI_API_KEY"] = api_key
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

    # 2.  Get input (title and description)
    github_title = input("Enter GitHub Issue Title: ")
    github_description = input("Enter GitHub Issue Description: ")
    if not github_title and not github_description:  # Missing args
        print("Error: Missing 'title' or 'description' parameters.")
        return  # Exit if no title or description
    # 3.  Upload PDF (or get local path)
    pdf_uri = upload_pdf(PDF_FILE_PATH)  # Pass the user-provided path
    if not pdf_uri:
        print("Failed to get PDF URI.  Aborting.")
        return

    # 4.  Predict label
    predicted_label = predict_team_label(pdf_uri, github_title, github_description)

    # 5.  Print result
    if predicted_label:
        print(f"Predicted Team Label: {predicted_label}")
    else:
        print("Failed to predict a team label.")



if __name__ == "__main__":
    main()