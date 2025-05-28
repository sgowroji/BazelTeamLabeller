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

**Triaging Instructions & Decision Process:**
1.  **Understand the Issue's Core Subject:**
    *   Carefully read the GitHub issue title and body to identify the **user's primary problem, request, or question.**
    *   **URL Analysis (Important):**
        *   If URLs are present, examine the surrounding text to understand their **purpose and context.**
        *   A URL might point to:
            *   A code snippet or a specific file/commit (often related to a `bug` or `refactor`).
            *   An error log or a failing CI run (often related to a `bug` or test failure label).
            *   An external documentation page (which could be for context of expected behavior for a `bug`, a source for a `feature_request`, or the subject of a `documentation` issue if the problem *is with that documentation*).
            *   A related issue, a forum discussion, or other external resources.
        *   **Crucially, the mere presence of a URL (even to a documentation site) does NOT automatically mean the issue's primary purpose is "documentation". The issue's *main subject matter and the user's intent* dictate the label.** For example, if a user links to documentation to show how a feature *should* work but reports it's broken, it's likely a `bug`, not `documentation`.

2.  **Consult Label Definitions:** Review the "Allowed Labels & Their Definitions" above. Pay close attention to the precise meaning of each.
3.  **Determine Primary Focus & Intent:**
    *   Based on the core subject identified in step 1, determine the *primary nature* of the issue.
    *   Is the user reporting something functionally broken, an unexpected error, or incorrect behavior in the software? (Likely `bug`).
    *   Is the user suggesting new functionality or an enhancement to existing software features? (Likely `feature_request`).
    *   Is the **main topic of the issue itself an error in, or a request to improve/create, official project documentation** (e.g., a typo in a guide, a request for a new tutorial)? (Only then is it likely `documentation`).
    *   Is the user primarily asking for help, clarification, or how to use something? (Likely `question`).
    *   (Adapt these guiding questions based on your specific labels and their definitions).
4.  **Select Best Fit Label:** Choose the SINGLE label from the "Allowed Labels" list whose definition most accurately and comprehensively describes this primary nature and intent.
5.  **No Perfect Fit - Closest Match:** If no single label perfectly describes the issue, select the one whose definition is the *closest and most relevant match* to the dominant aspect of the issue. Do not invent new labels or combine labels.
6.  **Output Requirement:** Your response MUST be ONLY the selected label name. Do not include any other text, explanations, or formatting.

**Examples:**
Issue Title: '[bazel.build] Building the tutorial app in /start/android-app fails'
Issue Body: '### Page link: https://bazel.build/start/android-app ### Problem description: When I try to build I get an error: $ bazel build //src/main:app ERROR: Traceback (most recent call last): File \'C:/src/learnbazel/examples-main/android/tutorial/src/main/BUILD\', line 1, column 15, in <toplevel> android_binary( Error in android_binary: Couldn't auto load 'android_binary' from '@rules_android//rules:rules.bzl'. Ensure that you have a 'bazel_dep(name = \'rules_android\', ...)' in your MODULE.bazel file...'
Predicted Label: team-Android

Issue Title: 'Where is the error log?'
Issue Body: '### Description of the bug: When I use `bazel build //... -c opt --jobs 8 --sandbox_debug` to compile a repository, it just says \'bazel FAILED: Build did NOT complete successfully\'. But there are no more error messages. Where can I find the log that locates the error? ### Which category does this issue belong to? Configurability'
Predicted Label: team-Bazel

Issue Title: '[8.1.0] Fix docs link rewriting for rules_android'
Issue Body: 'Fixes https://github.com/bazelbuild/bazel/issues/24905 RELNOTES: None PiperOrigin-RevId: 717532897...'
Predicted Label: team-Android

Issue Title: 'Bzlmod: Unable to resolve dependency @my_external_repo//:lib'
Issue Body: 'After migrating to Bzlmod, my build fails with an error indicating it cannot find `@my_external_repo//:lib`. My MODULE.bazel file includes `bazel_dep(name = \'my_external_repo\', version = \'1.2.3\')`. The remote repository exists and is accessible. Previously, this worked with a `http_archive` rule in WORKSPACE.'
Predicted Label: team-ExternalDeps

Issue Title: '[8.2.0] Fix encoding of Starlark source lines in error messages'
Issue Body: 'Closes #25327. PiperOrigin-RevId: 736919575 Change-Id: I008207f53b9464f69fff3be81862f5d3f3a0f15d Commit...'
Predicted Label: team-Core

Issue Title: 'Feature Request: Expose new 'ToolchainInfoSubprovider' in Starlark Rule Definition API'
Issue Body: 'When writing custom rules that interact heavily with toolchains, the current `ToolchainInfo` provider is too opaque. We need a sub-provider, say `ToolchainInfoSubprovider`, that gives access to the resolved tool paths and configuration fragments. This would allow rules to more dynamically configure actions based on the selected toolchain. This affects how `provides` and `ctx.attr.toolchain_type` are used.'
Predicted Label: team-Rules-API

---
**GitHub Issue to Triage:**

Title: {github_issue_title}
Body Description: {github_issue_description}

**Predicted Label:**
    """,
        pdf_uri,  # In the local version, this is a file path.
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