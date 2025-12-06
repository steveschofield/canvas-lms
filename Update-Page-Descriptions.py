#!/usr/bin/env python3
"""
Update Canvas pages for PenTest+ modules 1–10 using HTML formatted like:

Before we touch a single tool, we’re going to make sure you understand what a professional pentest...

Subsections in this module:
    1. 1.1: ...
       • description
    2. 1.2: ...
       • description
    ...

Assumptions:
- Canvas pages are already created.
- Each relevant page title contains the string "Module X" (e.g., "Module 1").
- Config file at etc/config.txt with section [canvas-lms-test]:
    [canvas-lms-test]
    COURSE_ID = 12345
    API_TOKEN = your_token_here
    CANVAS_DOMAIN_URL = https://yourinstitution.instructure.com
"""

import configparser
import requests

# --------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------

CONFIG_PATH = "etc/config.txt"
CONFIG_SECTION = "canvas-lms-test"

# Start in dry-run so you can preview HTML before updating Canvas.
DRY_RUN = False

# --------------------------------------------------------------------
# Load Canvas config
# --------------------------------------------------------------------

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

if CONFIG_SECTION not in config:
    raise KeyError(
        f"Section [{CONFIG_SECTION}] not found in {CONFIG_PATH}. "
        f"Available sections: {config.sections()}"
    )

COURSE_ID = int(config[CONFIG_SECTION]["COURSE_ID"])
API_TOKEN = config[CONFIG_SECTION]["API_TOKEN"]
CANVAS_DOMAIN_URL = config[CONFIG_SECTION]["CANVAS_DOMAIN_URL"].rstrip("/")

# --------------------------------------------------------------------
# Module metadata: title, intro, subsections with descriptions
# --------------------------------------------------------------------
# Each subsection is (code, title, description)

MODULES = {
    1: {
        "code": "1.0",
        "title": "Penetration Testing – Before You Begin",
        "intro": (
            "Before we touch a single tool, we’re going to make sure you understand what a professional "
            "pentest actually looks like—ethics, scope, documentation, and how your work lands in front "
            "of a client. This module is about showing up as a trusted tester, not just someone who knows "
            "how to launch exploits."
        ),
        "subsections": [
            (
                "1.1",
                "Professional Conduct and Penetration Testing",
                "What a penetration test is, how ethics, legal and compliance requirements shape the work, "
                "and why authorization and documentation (rules of engagement, reports) matter before you "
                "touch a system.",
            ),
            (
                "1.2",
                "Collaboration and Communication",
                "How pentest teams coordinate, define roles and responsibilities, communicate with clients, "
                "escalate issues, and clearly articulate risk, severity, and business impact.",
            ),
            (
                "1.3",
                "Testing Frameworks and Methodologies",
                "How to anchor your work in recognized frameworks like OSSTMM, CREST, PTES, MITRE ATT&CK, "
                "OWASP (web and mobile), the Purdue model, and threat modeling approaches so your test isn't "
                "random hacking but a structured assessment.",
            ),
            (
                "1.4",
                "Introduction to Scripting for Penetration Testing",
                "Where scripting fits into recon and enumeration, with an emphasis on Bash, Python, and "
                "PowerShell, plus core logic constructs so you can start automating common tasks instead "
                "of doing everything by hand.",
            ),
        ],
    },
    2: {
        "code": "2.0",
        "title": "Applying Pre-Engagement Activities",
        "intro": (
            "Before you ever scan or exploit a target, you need a clean engagement up front—scope, rules "
            "of engagement, responsibilities, and legal guardrails. In this module we’ll treat pre-engagement "
            "work like part of the test, because if you get this wrong, nothing else really matters."
        ),
        "subsections": [
            (
                "2.1",
                "Define the Scope",
                "How regulations, frameworks, standards, rules of engagement, agreement types, and target "
                "selection define what you're allowed to touch and how you test.",
            ),
            (
                "2.2",
                "Compare Types of Assessments",
                "Differences between web/application, network, mobile, cloud, wireless, IoT, and IT vs OT "
                "assessments and when each type makes sense.",
            ),
            (
                "2.3",
                "Utilize the Shared Responsibility Model",
                "How hosting providers, customers, penetration testers, and third parties each own parts of "
                "security in shared or cloud environments.",
            ),
            (
                "2.4",
                "Identify Legal and Ethical Considerations",
                "Authorization letters, mandatory reporting requirements, tester risk, and documenting "
                "pre-engagement activities so you stay protected and compliant.",
            ),
        ],
    },
    3: {
        "code": "3.0",
        "title": "Enumeration and Reconnaissance",
        "intro": (
            "Recon and enumeration are where good pentests are won—this is where you quietly collect the "
            "data that makes later attacks almost boring. We’ll focus on turning random scanning into a "
            "deliberate plan for how you’re going to break into an environment."
        ),
        "subsections": [
            (
                "3.1",
                "Information Gathering Techniques",
                "Active and passive recon, OSINT, Shodan, certificate transparency logs, network sniffing, "
                "and other techniques to build a picture of the target without tipping your hand.",
            ),
            (
                "3.2",
                "Host and Service Discovery Techniques",
                "Using tools like Nmap for host discovery, scripting, banner grabbing, DNS enumeration, "
                "service discovery, and OS fingerprinting to map what’s actually running.",
            ),
            (
                "3.3",
                "Enumeration for Attack Planning",
                "Mapping attack paths, doing manual enumeration, pulling data from SNMP and other protocols, "
                "and documenting what you find so you can plan realistic attacks.",
            ),
            (
                "3.4",
                "Enumeration for Specific Assets",
                "Targeted techniques for directory, user, wireless, permission, secrets, and share enumeration, "
                "plus WAF probing, decoy scans, ICS assessments, and web crawling/scraping.",
            ),
        ],
    },
    4: {
        "code": "4.0",
        "title": "Scanning and Identifying Vulnerabilities",
        "intro": (
            "Here we turn raw recon into actual weaknesses you can act on by scanning for vulnerabilities, "
            "validating what you find, and separating signal from noise. We’ll look at both technical scans "
            "and the physical side, so you see how an attacker really looks at an environment end-to-end."
        ),
        "subsections": [
            (
                "4.1",
                "Vulnerability Discovery Techniques",
                "Tools and scan types for finding vulnerabilities across hosts, networks, apps, containers, "
                "wireless, and Linux, and how to validate your results instead of trusting a tool blindly.",
            ),
            (
                "4.2",
                "Analyzing Reconnaissance Scanning and Enumeration",
                "How to line up public exploits and scripting with your scan and recon data to confirm "
                "what is actually exploitable.",
            ),
            (
                "4.3",
                "Physical Security Concepts",
                "Tailgating, site surveys, dropped USBs, badge cloning, lock picking, and documenting "
                "physical weaknesses as part of a complete assessment.",
            ),
        ],
    },
    5: {
        "code": "5.0",
        "title": "Conducting Pentest Attacks",
        "intro": (
            "This is where we turn all that planning into actual attacks—prioritizing targets, selecting "
            "exploits, and using scripts to make repeatable moves. The goal isn’t to spray and pray, "
            "but to line up the right capability against the right weakness at the right time."
        ),
        "subsections": [
            (
                "5.1",
                "Prepare and Prioritize Attacks",
                "How to rank targets based on business value, EOL software, default configs, running services, "
                "weak crypto, defensive capabilities, scope limits, and dependencies before you fire a shot.",
            ),
            (
                "5.2",
                "Scripting Automation",
                "Using PowerShell, Bash, Python, and breach-and-attack simulation to automate attacks and "
                "make your workflow more consistent and repeatable.",
            ),
        ],
    },
    6: {
        "code": "6.0",
        "title": "Web-based Attacks",
        "intro": (
            "Most environments expose something over HTTP or in the cloud, so knowing how to break web "
            "apps and cloud workloads is non-negotiable. In this module we’ll walk through the core web "
            "attack patterns and then extend that mindset into modern cloud-based targets."
        ),
        "subsections": [
            (
                "6.1",
                "Web-based Attacks",
                "Common web attack patterns like brute force, directory traversal, injection, XSS, request "
                "forgery, deserialization, IDOR, session hijacking, file inclusions, and API/JWT abuse, plus "
                "hands-on labs like SQLMap and XSS.",
            ),
            (
                "6.2",
                "Cloud-based Attacks",
                "How to attack misconfigured cloud resources, metadata services, access management, logging, "
                "images/artifacts, supply chain links, runtime workloads, containers, trust relationships, "
                "and even use SYN floods in cloud contexts.",
            ),
        ],
    },
    7: {
        "code": "7.0",
        "title": "Enterprise Attacks",
        "intro": (
            "Now we shift into classic enterprise territory—network attacks, authentication abuse, and "
            "host-based techniques you’ll see in real corporate environments. Think of this as learning how "
            "an attacker actually lives inside an enterprise, not just popping a single box and leaving."
        ),
        "subsections": [
            (
                "7.1",
                "Perform Network Attacks",
                "Network-level attacks using default credentials, on-path techniques, misconfigured services, "
                "VLAN hopping, multihomed hosts, relays, IDS evasion, and tools like Nmap and Netcat.",
            ),
            (
                "7.2",
                "Perform Authentication Attacks",
                "Password and identity attacks including MFA fatigue, pass-the-hash/ticket/token, Kerberos "
                "abuse, LDAP injection, dictionary/brute-force/mask/spraying/stuffing attacks, and OIDC/SAML abuse.",
            ),
            (
                "7.3",
                "Perform Host-Based Attacks",
                "Host-focused techniques like privilege escalation, credential dumping, bypassing security tools, "
                "payload obfuscation, shell/kiosk escape, injection techniques, log tampering, and abusing LOLBins.",
            ),
        ],
    },
    8: {
        "code": "8.0",
        "title": "Specialized Attacks",
        "intro": (
            "Not everything you test will be a standard server or web app—wireless, people, and specialized "
            "systems all become attack paths. This module is about recognizing those edges and knowing how "
            "to approach them instead of mentally treating them as out of scope just because they’re different."
        ),
        "subsections": [
            (
                "8.1",
                "Wireless Attacks",
                "Wireless attack types and tools, including wardriving, Bluetooth abuse, evil twin setups, "
                "signal jamming, protocol fuzzing, packet crafting, deauth attacks, captive portals, and WPS/PIN attacks.",
            ),
            (
                "8.2",
                "Social Engineering Attacks",
                "Phishing, spear phishing, whaling, smishing, watering holes, credential harvesting, and "
                "using frameworks like SET to run controlled social engineering operations.",
            ),
            (
                "8.3",
                "Specialized System Attacks",
                "Attacks against mobile, AI-enabled, OT/ICS, RFID/NFC, Bluetooth and similar specialized "
                "systems, and how those fit into a broader penetration test.",
            ),
        ],
    },
    9: {
        "code": "9.0",
        "title": "Performing Penetration Testing Tasks",
        "intro": (
            "Once you’re in, the job shifts to staying in, moving around, quietly staging data, and then "
            "cleaning up without leaving a mess behind. Here we’ll look at persistence, lateral movement, "
            "staging, exfiltration, and responsible cleanup the way a professional tester handles it."
        ),
        "subsections": [
            (
                "9.1",
                "Establish and Maintain Persistence",
                "Persistence techniques like scheduled tasks/cron, service creation, reverse/bind shells, "
                "new accounts, credential theft, registry abuse, C2 frameworks, backdoors, rootkits, browser "
                "extensions, and tampering with security controls.",
            ),
            (
                "9.2",
                "Move Laterally through Environments",
                "Scanning from compromised hosts, using Metasploit/Zenmap, pivoting, relays, firewall bypasses, "
                "and Windows remoting (WMI/WinRM) to move across an environment.",
            ),
            (
                "9.3",
                "Staging and Exfiltration",
                "How to collect, hide, and move data using techniques like steganography, alternate data streams, "
                "and careful exfiltration paths that avoid detection.",
            ),
            (
                "9.4",
                "Cleanup and Restoration",
                "Cleanup, restoration, and documentation steps so you can remove artifacts, restore systems, "
                "and leave the environment in a known-good state after testing.",
            ),
        ],
    },
    10: {
        "code": "10.0",
        "title": "Reporting and Recommendations",
        "intro": (
            "The report is what your client actually lives with after you’re gone, so this module is about "
            "turning all your work into clear, prioritized findings and realistic recommendations. We’ll tie "
            "together risk scoring, controls, and communication so your reports drive change instead of just "
            "sitting in someone’s inbox."
        ),
        "subsections": [
            (
                "10.1",
                "Penetration Test Report Components",
                "How to build a complete penetration test report—executive summary, methodology, detailed "
                "findings, risk scoring, limitations, assumptions, and documentation standards.",
            ),
            (
                "10.2",
                "Analyze Findings and Remediation Recommendations",
                "How to turn raw findings into technical, administrative, operational, and physical control "
                "recommendations that are realistic for the client to implement.",
            ),
        ],
    },
}

# --------------------------------------------------------------------
# Canvas API helpers
# --------------------------------------------------------------------


def canvas_headers():
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }


def list_pages_for_course(course_id: int):
    pages = []
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/pages"
    params = {"per_page": 100}

    while url:
        r = requests.get(url, headers=canvas_headers(), params=params)
        r.raise_for_status()
        pages.extend(r.json())

        link = r.headers.get("Link", "")
        next_url = None
        for part in link.split(","):
            part = part.strip()
            if 'rel="next"' in part:
                start = part.find("<") + 1
                end = part.find(">")
                next_url = part[start:end]
                break

        url = next_url
        params = {}

    return pages


def find_page_for_module(course_id: int, module_number: int):
    """
    Find the Canvas page whose title contains 'Module X' (case-insensitive).
    """
    fragment = f"Module {module_number}".lower()
    for page in list_pages_for_course(course_id):
        title = page.get("title", "").lower()
        if fragment in title:
            return page
    return None


def update_canvas_page_body(course_id: int, page_url: str, html_body: str):
    """
    Update a Canvas wiki page body with HTML.
    """
    url = f"{CANVAS_DOMAIN_URL}/api/v1/courses/{course_id}/pages/{page_url}"
    payload = {"wiki_page[body]": html_body}
    r = requests.put(url, headers=canvas_headers(), data=payload)
    r.raise_for_status()
    return r.json()


# --------------------------------------------------------------------
# HTML generator using your desired formatting
# --------------------------------------------------------------------


def get_module_html(module_number: int) -> str:
    """
    Build HTML with:
    <p>intro...</p>
    <p><strong>Subsections in this module:</strong></p>
    <ol>
      <li>
        <p><strong>1.1: Title</strong></p>
        <p>&bull; Description...</p>
      </li>
      ...
    </ol>
    """
    if module_number not in MODULES:
        raise ValueError(f"Module {module_number} not defined.")

    m = MODULES[module_number]

    html = []
    # (Optional) You can add an h2 if you want a visible heading:
    html.append(f"<h2>Module {m['code']} – {m['title']}</h2>")
    html.append(f"<p>{m['intro']}</p>")
    html.append("<p><strong>Subsections in this module:</strong></p>")
    html.append("<ol>")

    for code, title, desc in m["subsections"]:
        html.append("  <li>")
        html.append(f"    <p><strong>{code}: {title}</strong></p>")
        html.append(f"    <p>&bull; {desc}</p>")
        html.append("  </li>")

    html.append("</ol>")

    return "\n".join(html)


# --------------------------------------------------------------------
# Main flow
# --------------------------------------------------------------------


def main():
    print(f"Running update for course {COURSE_ID} (DRY_RUN={DRY_RUN})")

    for module_number in range(1, 11):
        print("-" * 70)
        print(f"Processing Module {module_number}...")

        page = find_page_for_module(COURSE_ID, module_number)
        if not page:
            print(f"  [WARN] No Canvas page found with 'Module {module_number}' in title.")
            continue

        html = get_module_html(module_number)
        print(f"  Found page: {page['title']} (slug: {page['url']})")

        if DRY_RUN:
            print("  [DRY RUN] Would update with HTML:")
            print(html)
            continue

        update_canvas_page_body(COURSE_ID, page["url"], html)
        print("  [OK] Page updated.")


if __name__ == "__main__":
    main()