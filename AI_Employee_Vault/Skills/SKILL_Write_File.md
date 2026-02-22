---
skill_name: Write File
description: Write or append content to a .md file in the vault.
---

# Skill: Write File

## Instructions for Autonomy

This skill is designed to write new content to a specified Markdown (`.md`) file or append content to an existing one within the `AI_Employee_Vault`.

### Steps:

1.  **Determine File Path and Content:** Identify the absolute or relative path to the target `.md` file and the content that needs to be written. The content can include YAML frontmatter if it's a new file or if existing frontmatter needs updating.
    *   Example File Path: `AI_Employee_Vault/Dashboard.md`
    *   Example Content: `"\n## New Section\nThis is new content to be added.\n"`

2.  **Check if File Exists (Optional but Recommended for Appending):** Before appending, it's good practice to read the existing file content to ensure you don't accidentally overwrite it or to retrieve existing content if you need to modify it.
    *   Tool: `Read(file_path="<your_file_path>")`

3.  **Format Content with YAML (If Needed):** If the content includes YAML frontmatter, ensure it is correctly formatted at the beginning of the string.

4.  **Write/Append using File System Tool:** Utilize the `Write` tool to either create a new file or overwrite an existing one with the provided content. If appending, concatenate the existing content with the new content before using the `Write` tool.
    *   Tool: `Write(file_path="<your_file_path>", content="<your_content>")`
    *   **Important:** Remember to read the file first before attempting to write to an existing file. If you are appending, read the file, append the new content to the existing content, and then write the full content back to the file.

5.  **Handle Errors:** Implement error handling for potential issues like invalid file paths or permission errors. If a write operation fails, log the error to `AI_Employee_Vault/Logs/errors.md` (creating the file if it doesn't exist) and report it.
