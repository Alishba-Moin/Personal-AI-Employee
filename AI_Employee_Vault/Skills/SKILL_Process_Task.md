---
skill_name: Process Task
description: High-level reasoning to process a task from /Needs_Action, create Plan.md, and move to /Done if complete.
---

# Skill: Process Task

## Instructions for Autonomy

This skill outlines the high-level reasoning for processing tasks that appear in the `AI_Employee_Vault/Needs_Action` folder. The goal is to create a plan, execute it, and then move the processed task to the `AI_Employee_Vault/Done` folder.

### Steps:

1.  **Read Task File:** Identify and read the content of the `.md` task file from the `AI_Employee_Vault/Needs_Action` directory. This will be the input for the current task.
    *   Tool: `Read(file_path="AI_Employee_Vault/Needs_Action/<task_file>.md")`
    *   Utilize `SKILL_Read_File` internally for this step.

2.  **Reference Company Handbook Rules:** Before planning, consult the `AI_Employee_Vault/Company_Handbook.md` to ensure compliance with established rules (e.g., payment approval thresholds, communication politeness).
    *   Tool: `Read(file_path="AI_Employee_Vault/Company_Handbook.md")`

3.  **Generate Plan with Checkboxes:** Based on the task file content and handbook rules, generate a detailed `Plan.md` in a new `AI_Employee_Vault/Plans` folder (create if needed). This plan should break down the task into actionable steps with checkboxes.
    *   Create folder: `Bash(command="mkdir -p AI_Employee_Vault/Plans", description="Create /Plans folder")`
    *   Write plan: `Write(file_path="AI_Employee_Vault/Plans/Plan_<task_name>.md", content="<plan_content_with_checkboxes>")`
    *   Utilize `SKILL_Write_File` internally for this step.

4.  **Execute Plan (Iterative Process):** Follow the steps in the generated `Plan.md`. This will involve using various tools (e.g., `Read`, `Write`, `Bash`, `Task` with specialized agents) as needed to complete each step of the plan. Mark checkboxes in `Plan.md` as steps are completed.

5.  **Move File to /Done if Complete:** Once all steps in the `Plan.md` are marked as complete and the original task is fully processed, move the original task file from `AI_Employee_Vault/Needs_Action` to `AI_Employee_Vault/Done`.
    *   Tool: `Bash(command="mv AI_Employee_Vault/Needs_Action/<task_file>.md AI_Employee_Vault/Done/<task_file>.md", description="Move task file to /Done")`

6.  **Update Dashboard:** Append a summary of the processed task and its outcome to `AI_Employee_Vault/Dashboard.md`.
    *   Utilize `SKILL_Write_File` internally for this step.

7.  **Handle Errors:** If any errors occur during task processing (e.g., during file operations or script execution), log the error to `AI_Employee_Vault/Logs/errors.md` (creating the file if it doesn't exist) and report it to the user.
    *   Create Logs folder: `Bash(command="mkdir -p AI_Employee_Vault/Logs", description="Create /Logs folder")`
    *   Append error: `Write(file_path="AI_Employee_Vault/Logs/errors.md", content="<error_details>")`
