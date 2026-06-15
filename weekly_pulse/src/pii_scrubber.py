import re

class PIIScrubber:
    """
    A simple regex-based PII scrubber for review text.
    Removes emails and common phone number patterns.
    """
    # Regex for common email formats
    EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    
    # Regex for common phone numbers (specifically targeting 10-digit formats common in India)
    PHONE_REGEX = re.compile(r'(\+91[\-\s]?)?[0]?(91)?[6789]\d{9}')
    
    @classmethod
    def scrub(cls, text: str) -> str:
        if not text:
            return text
            
        text = cls.EMAIL_REGEX.sub('[EMAIL_REDACTED]', text)
        text = cls.PHONE_REGEX.sub('[PHONE_REDACTED]', text)
        
        return text
