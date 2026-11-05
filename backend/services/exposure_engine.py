"""
PrivacyLens AI Exposure Reconstruction Engine (Core USP).
Grounds privacy risk reasoning strictly in observed evidence.
Distinguishes visible facts from potential inferences without exaggerating or inventing identities.
Explains how individual benign clues combine into composite exposure risks (The Mosaic Effect).
"""
from typing import Any, Dict, List


def _categorize_clues(findings: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Sort detected privacy clues into functional privacy facets."""
    facets: Dict[str, List[Dict[str, Any]]] = {
        'identity': [],
        'affiliation': [],
        'location': [],
        'routine': [],
        'credentials': [],
        'contact': [],
        'financial': [],
        'metadata': [],
        'network_qr': [],
    }

    for f in findings:
        cat = f.get('category', '').lower()
        if any(t in cat for t in ['face', 'personal name', 'name field', 'national id', 'nric', 'fin', 'ssn', 'identity document', 'name']):
            facets['identity'].append(f)
        if any(t in cat for t in ['school uniform', 'school badge', 'student', 'school', 'affiliation', 'vehicle identifier']):
            facets['affiliation'].append(f)
        if any(t in cat for t in ['address', 'street sign', 'location clue', 'gps metadata', 'possible address']):
            facets['location'].append(f)
        if any(t in cat for t in ['schedule', 'timetable', 'calendar', 'timestamp', 'schedule clue']):
            facets['routine'].append(f)
        if any(t in cat for t in ['password', 'credential', 'api key', 'token', 'private key']):
            facets['credentials'].append(f)
        if any(t in cat for t in ['email', 'phone']):
            facets['contact'].append(f)
        if any(t in cat for t in ['payment card', 'card number', 'possible payment card']):
            facets['financial'].append(f)
        if f.get('source') == 'metadata' or 'metadata' in cat:
            facets['metadata'].append(f)
        if any(t in cat for t in ['qr code', 'ip address']):
            facets['network_qr'].append(f)

    return facets


def explain_exposure(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Construct multi-clue exposure reconstruction insights from observed findings.
    Designed for educational guidance on the 'mosaic effect' of online sharing.
    """
    if not findings:
        return {
            'risk_level': 'low',
            'possible_connections': [],
            'exposure_scenarios': [],
            'actionable_recommendations': [
                'Always manually review images before posting, especially in public forums.'
            ],
            'educational_takeaways': [
                'Even if automated tools detect no risks, context and privacy remain user decisions.'
            ],
            'summary': 'No sensitive information patterns detected.'
        }

    facets = _categorize_clues(findings)
    scenarios: List[Dict[str, Any]] = []
    connections: List[str] = []
    recommendations: List[str] = []

    has_identity = len(facets['identity']) > 0
    has_affiliation = len(facets['affiliation']) > 0
    has_location = len(facets['location']) > 0
    has_routine = len(facets['routine']) > 0
    has_credentials = len(facets['credentials']) > 0
    has_contact = len(facets['contact']) > 0
    has_financial = len(facets['financial']) > 0
    has_metadata_gps = any('gps' in f.get('category', '').lower() for f in facets['metadata'])
    has_qr = any('qr' in f.get('category', '').lower() for f in facets['network_qr'])

    # 1. Identity + Physical Location (Doxing / Physical Location Vector)
    if has_identity and has_location:
        connections.append('Identity or affiliation clues combined with a location clue may reveal more than either alone.')
        scenarios.append({
            'title': 'Identity and Physical Location Association',
            'visible_evidence': 'A visible face, personal name, or ID document paired with an address or location clue.',
            'potential_inference': (
                'Correlating an identifiable person directly with a residential address or specific street marker '
                'removes geographic anonymity and can expose home or school whereabouts.'
            ),
            'educational_guidance': (
                'Youths often post photos of letters, deliveries, or neighborhood hangouts. '
                'Masking unit and street numbers ensures home privacy.'
            )
        })
        recommendations.append('Black out unit numbers, postal codes, and delivery labels.')

    # 2. Location + Schedule/Routine (Physical Transit / Habit Vector)
    if has_location and has_routine:
        connections.append('Location and schedule clues together may disclose parts of a routine.')
        scenarios.append({
            'title': 'Location and Routine Mapping',
            'visible_evidence': 'Location markers (address, street sign, or GPS) visible alongside schedules or timestamps.',
            'potential_inference': (
                'Combining physical locations with time-based schedules reveals predictable transit routines '
                'and when someone is likely present at a specific place.'
            ),
            'educational_guidance': (
                'Avoid pairing commute photos with schedule details that reveal when you travel alone.'
            )
        })
        recommendations.append('Cover specific times and location clues to safeguard your daily routine.')

    # 3. School Affiliation + Location or Routine (Youth Routine Vector)
    if has_affiliation and (has_location or has_routine):
        connections.append('School attire or badges combined with location or timetable clues may reveal institutional routine.')
        scenarios.append({
            'title': 'School Affiliation & Routine Profiling',
            'visible_evidence': 'School attire, emblems, or student credentials alongside location or routine clues.',
            'potential_inference': (
                'When school badges or distinctive uniforms appear together with location markers or class timetables, '
                'an observer can correlate which school a student attends with their daily transit routes.'
            ),
            'educational_guidance': (
                'Keep school badges and street signs separate to avoid revealing school commute routes.'
            )
        })
        recommendations.append('Blur or cover school crests and nearby street signs before sharing.')

    # 4. Identity + Direct Contact (Spear-Phishing / Impersonation Vector)
    if has_identity and has_contact:
        connections.append('Personal name or face paired with direct communication channels (phone/email).')
        scenarios.append({
            'title': 'Contact Information & Targeted Social Engineering',
            'visible_evidence': 'Personal identifiers (name or face) visible near a phone number or email address.',
            'potential_inference': (
                'When names and direct contacts are linked in public images, scammers can personalize deceptive messages, '
                'impersonate school officials, or initiate unwanted contact.'
            ),
            'educational_guidance': (
                'Never post registration forms or consent slips displaying phone numbers next to student names.'
            )
        })
        recommendations.append('Redact phone numbers and email addresses.')

    # 5. National ID / Student ID (Identity Theft & Account Verification Risk)
    national_ids = [f for f in facets['identity'] if any(t in f.get('category', '').lower() for t in ['national id', 'nric', 'fin', 'ssn', 'singapore id'])]
    if national_ids:
        connections.append('Government or national identification numbers visible.')
        scenarios.append({
            'title': 'Government Identification Exposure',
            'visible_evidence': 'A national identity format number (such as NRIC, FIN, or SSN) was detected.',
            'potential_inference': (
                'National ID numbers are persistent identifiers used for authentication across government, banking, and education portals. '
                'Exposing them facilitates identity theft, SIM-swapping, and fraudulent account recovery.'
            ),
            'educational_guidance': (
                'Identity cards should never be photographed or uploaded without fully blacking out all identity numbers.'
            )
        })
        recommendations.append('Permanently blackout all national identity numbers.')

    # 6. Credentials & Secrets (Account Takeover Risk)
    if has_credentials:
        connections.append('Exposed authentication credentials, API keys, or plaintext passwords.')
        scenarios.append({
            'title': 'Direct Credential Compromise',
            'visible_evidence': 'Plaintext password assignments or active API tokens visible in image content.',
            'potential_inference': (
                'Anyone viewing this image may gain unauthorized access to corresponding digital accounts, repositories, or services.'
            ),
            'educational_guidance': (
                'If a password or token appeared on screen during a screenshot, change or revoke it immediately.'
            )
        })
        recommendations.append('Rotate any exposed credentials immediately and blackout the credential field.')

    # 7. Financial Data (Payment Card Risk)
    if has_financial:
        connections.append('Valid payment card number visible in image.')
        scenarios.append({
            'title': 'Financial Card Exposure',
            'visible_evidence': 'A 13-19 digit number that matches payment card checksums was detected.',
            'potential_inference': (
                'Exposed payment card numbers can be used for fraudulent online transactions or social engineering.'
            ),
            'educational_guidance': (
                'Never share photographs of debit, credit, or student payment cards without obscuring numbers.'
            )
        })
        recommendations.append('Cover all digits of the payment card before sharing.')

    # 8. Hidden EXIF GPS Metadata (Invisible Geotagging)
    if has_metadata_gps:
        connections.append('Invisible EXIF GPS coordinates embedded in photo metadata.')
        scenarios.append({
            'title': 'Covert Geolocation Metadata',
            'visible_evidence': 'Embedded GPS latitude/longitude coordinates stored in the image header.',
            'potential_inference': (
                'Even if all visible landmarks are blacked out on the image, anyone who downloads the raw file '
                'can extract the exact GPS coordinates where the photo was taken.'
            ),
            'educational_guidance': (
                'Use PrivacyLens redaction export to automatically strip EXIF metadata from exported files.'
            )
        })
        recommendations.append('Export the photo with metadata stripping enabled.')

    # 9. QR Code + Personal Information
    if has_qr and (has_identity or has_contact or has_affiliation):
        connections.append('A visible QR code alongside identifying details may deserve extra review.')
        scenarios.append({
            'title': 'QR Code Destination Vulnerability',
            'visible_evidence': 'A QR code detected in the presence of personal information.',
            'potential_inference': (
                'QR codes on student passes, event badges, or documents frequently link to personal registration data or internal URLs.'
            ),
            'educational_guidance': (
                'Test and inspect QR code destinations before posting photos containing them.'
            )
        })
        recommendations.append('Cover QR codes that point to personal profiles, events, or portal links.')

    # Determine overall risk level
    if has_credentials or national_ids or has_financial:
        risk_level = 'critical'
    elif (has_affiliation and has_location) or (has_identity and has_location) or has_metadata_gps:
        risk_level = 'high'
    elif has_contact or has_affiliation or has_location or has_identity:
        risk_level = 'medium'
    else:
        risk_level = 'low'

    # Deduplicate recommendations
    deduped_recs = []
    for r in recommendations:
        if r not in deduped_recs:
            deduped_recs.append(r)
    if not deduped_recs:
        deduped_recs.append('Review detected items and redact any information you would not want public.')

    educational_takeaways = [
        "The Mosaic Effect: Digital investigators and malicious actors rarely rely on a single clue; they assemble innocuous pieces (a school logo, a road sign, a lunch schedule) into a complete profile.",
        "Boundary Setting: Setting online boundaries means deciding in advance what parts of your identity, location, and routine remain private.",
        "Verify Before Redacting: Automated tools provide suggestions. You maintain full control over which areas to obscure."
    ]

    summary_text = (
        f"Detected {len(findings)} privacy clue{'s' if len(findings) != 1 else ''}. "
        f"Identified {len(scenarios)} composite exposure scenario{'s' if len(scenarios) != 1 else ''} with {risk_level.upper()} overall exposure risk."
    )

    return {
        'risk_level': risk_level,
        'possible_connections': connections,
        'exposure_scenarios': scenarios,
        'actionable_recommendations': deduped_recs,
        'educational_takeaways': educational_takeaways,
        'summary': summary_text,
        'note': 'These are grounded exposure reconstructions based on observed evidence, not a determination of identity or location.'
    }
