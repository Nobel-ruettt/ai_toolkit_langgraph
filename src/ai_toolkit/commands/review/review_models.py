import textwrap
from typing import Optional
from pydantic import BaseModel, Field


class ReviewIssue(BaseModel):
    """Model representing a schema for issues identified during code review."""

    id: str = Field(description="Unique identifier for the issue")
    description: str = Field(description="Detailed description of the issue")
    severity: str = Field(description="Severity level of the issue (e.g., Low, Medium, High)")
    category: str = Field(description="Category of the issue (e.g.,Security, Performance, Maintainability)")
    file_path: Optional[str] = Field(default=None, description="Path to the file where the issue is located")
    snippet:  Optional[str] = Field(description="Optional Code snippet related to the issue")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix or improvement for the issue in clear text")

    def str_markdown__(self) -> str:
        parts = []

        # Add severity and category as header
        parts.append(f"### [{self.severity}] {self.category}")
        
        # Add file path if available
        if self.file_path:
            parts.append(f"**File:** `{self.file_path}`")
        
        # Add description
        parts.append(f"\n**Description:**")
        parts.append(f"{self.description}")

        # Add snippet if available
        if self.snippet:
            parts.append(f"\n**Code Snippet:**")
            parts.append(f"```\n{self.snippet}\n```")
        
        # Add suggestion if available
        if self.suggestion:
            parts.append(f"\n**Suggestion:**")
            parts.append(f"{self.suggestion}")
        
        return "\n".join(parts)


class ReviewResult(BaseModel):
    """Model representing the overall code review result"""

    issues: list[ReviewIssue] = Field(description="List of identified issues during the code review")
    summary: str = Field(description="Summary of the code review findings in a paragraph format with bullet points")
    aggregated_suggestions: list[str] = Field(description="List of aggregated suggestions for improvement")

    def str_markdown__(self) -> str:
        parts = []

        # Add summary with markdown header
        parts.append("# Code Review Summary\n")
        parts.append(self.summary)

        # Add issues section
        parts.append("\n## Identified Issues\n")
        for i, issue in enumerate(self.issues, 1):
            parts.append(f"#### Issue {i}")
            parts.append(issue.str_markdown__())
            parts.append("")  # Empty line for spacing

        # Add suggestions section
        parts.append("\n## Suggestions for Improvement\n")
        for i, suggestion in enumerate(self.aggregated_suggestions, 1):
            parts.append(f"{i}. {suggestion}")

        return "\n".join(parts)