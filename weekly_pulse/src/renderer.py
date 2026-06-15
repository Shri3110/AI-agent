from typing import Dict, Any

class PulseRenderer:
    @staticmethod
    def render_doc_content(week_label: str, analysis_data: Dict[str, Any]) -> str:
        """Renders the full Markdown report for the Google Doc."""
        md = f"## Groww — Weekly Review Pulse\n"
        md += f"*Period: {week_label}*\n\n"
        
        md += "### Top themes\n"
        for theme in analysis_data.get('themes', []):
            md += f"- {theme}\n"
            
        md += "\n### Real user quotes\n"
        for quote in analysis_data.get('quotes', []):
            md += f"- \"{quote}\"\n"
            
        md += "\n### Action ideas\n"
        for action in analysis_data.get('actions', []):
            md += f"- {action}\n"
            
        return md

    @staticmethod
    def render_email_teaser(week_label: str, analysis_data: Dict[str, Any], doc_link: str) -> str:
        """Renders the HTML email teaser."""
        html = f"<h2>Groww — Weekly Review Pulse ({week_label})</h2>"
        html += "<h3>Top themes this week:</h3><ul>"
        
        for theme in analysis_data.get('themes', [])[:3]: # Only top 3 for teaser
            html += f"<li>{theme}</li>"
            
        html += "</ul>"
        html += f"<p><a href='{doc_link}'>Read the full report & verbatim quotes here</a></p>"
        
        return html
