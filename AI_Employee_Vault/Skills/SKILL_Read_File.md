---
skill_name: Read File
description: Read content from a .md file in the vault.
---

# Skill: Read File

## Instructions for Autonomy

This skill is designed to read the content of a specified Markdown (`.md`) file located within the `AI_Employee_Vault`.

### Steps:

1.  **Identify File Path:** Determine the absolute or relative path to the `.md` file that needs to be read. Ensure the path is correct and points to a file within the `AI_Employee_Vault`.
    *   Example: `AI_Employee_Vault/Company_Handbook.md`

2.  **Use File System Tool to Read:** Utilize the `Read` tool to access the content of the identified file. The `Read` tool will return the file's content, including any YAML frontmatter.
    *   Tool: `Read(file_path="<your_file_path>")`

3.  **Parse YAML (If Present):** If the file is expected to contain YAML frontmatter, parse it to extract metadata. The YAML block will be at the beginning of the file, typically delimited by `---`.

4.  **Process Content:** Analyze the extracted content as required by the current task. This might involve summarizing, extracting specific information, or preparing it for further actions (e.g., appending to another file).
