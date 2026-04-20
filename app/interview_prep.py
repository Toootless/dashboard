"""
Interview preparation content generator.

Given a company name and job position, this module produces:
  - Curated web search URLs for company research
  - Relevant tools / tech-stack suggestions derived from job title keywords
  - Stage-by-stage interview questions:
      Recruiter screen → Hiring manager round → Technical panel
"""

from __future__ import annotations
import urllib.parse
import re
from typing import Any


# ---------------------------------------------------------------------------
# Search URL builder
# ---------------------------------------------------------------------------

def _q(text: str) -> str:
    """URL-encode a query string."""
    return urllib.parse.quote_plus(text)


def generate_search_urls(company: str, position: str) -> dict[str, list[dict]]:
    """Return a structured dict of research links for the given company + role."""
    company_q   = company.strip()
    position_q  = position.strip()
    full_q      = f"{company_q} {position_q}".strip()

    return {
        "company_overview": [
            {
                "label": "Company Website",
                "icon": "fa-globe",
                "url": f"https://www.google.com/search?q={_q(company_q + ' official website')}",
                "color": "primary",
                "hint": "Find official site, about page, and mission statement",
            },
            {
                "label": "LinkedIn Company",
                "icon": "fa-brands fa-linkedin",
                "url": f"https://www.linkedin.com/company/{_q(company_q.lower().replace(' ', '-'))}",
                "color": "info",
                "hint": "Employee count, recent activity, leadership team",
            },
            {
                "label": "Glassdoor Reviews",
                "icon": "fa-star",
                "url": f"https://www.glassdoor.com/Search/results.htm?keyword={_q(company_q)}",
                "color": "warning",
                "hint": "Culture, salary data, interview experience reviews",
            },
            {
                "label": "Recent News",
                "icon": "fa-newspaper",
                "url": f"https://news.google.com/search?q={_q(company_q)}",
                "color": "success",
                "hint": "Press releases, layoffs, funding rounds, product launches",
            },
            {
                "label": "Crunchbase Profile",
                "icon": "fa-building",
                "url": f"https://www.crunchbase.com/search/organizations/field/organizations/facet_ids/company?query={_q(company_q)}",
                "color": "secondary",
                "hint": "Funding history, key investors, headcount growth",
            },
        ],
        "role_research": [
            {
                "label": "LinkedIn Job Posts",
                "icon": "fa-brands fa-linkedin",
                "url": f"https://www.linkedin.com/jobs/search/?keywords={_q(full_q)}",
                "color": "info",
                "hint": "See how this role is described across similar companies",
            },
            {
                "label": "Interview Questions (Glassdoor)",
                "icon": "fa-comments",
                "url": f"https://www.glassdoor.com/Interview/{_q(company_q)}-{_q(position_q)}-Interview-Questions-EI_IE.htm",
                "color": "warning",
                "hint": "Real questions asked at this company for this role",
            },
            {
                "label": "Role Salary Range",
                "icon": "fa-dollar-sign",
                "url": f"https://www.levels.fyi/jobs/?title={_q(position_q)}",
                "color": "success",
                "hint": "Compensation benchmarks for negotiation",
            },
            {
                "label": "Similar Job Descriptions",
                "icon": "fa-magnifying-glass",
                "url": f"https://www.google.com/search?q={_q(full_q + ' job description requirements')}",
                "color": "primary",
                "hint": "Map required skills across multiple postings",
            },
        ],
    }


# ---------------------------------------------------------------------------
# Tech-stack / tools inference
# ---------------------------------------------------------------------------

# Keyword → (tools list, color)
_TOOL_RULES: list[tuple[list[str], list[dict], str]] = [
    (
        ['adas', 'autonomous', 'autonomous driving', 'self-driving', 'lidar', 'radar', 'camera', 'sensor fusion'],
        [
            {"name": "MATLAB / Simulink",  "category": "Simulation"},
            {"name": "Python",             "category": "Scripting"},
            {"name": "CANalyzer / CANoe",  "category": "CAN Bus Analysis"},
            {"name": "Vector Tools",       "category": "Automotive Protocols"},
            {"name": "dSPACE HIL",         "category": "Hardware-in-Loop"},
            {"name": "CarMaker / CarSim",  "category": "Vehicle Simulation"},
            {"name": "ROS / ROS2",         "category": "Robotics Middleware"},
            {"name": "OpenCV",             "category": "Computer Vision"},
            {"name": "JIRA / Confluence",  "category": "Project Management"},
            {"name": "Git / GitLab",       "category": "Version Control"},
        ],
        "primary",
    ),
    (
        ['calibration', 'cal', 'calibration engineer'],
        [
            {"name": "INCA / ETAS",        "category": "ECU Calibration"},
            {"name": "MDA (MATLAB)",       "category": "Data Analysis"},
            {"name": "CANape",             "category": "Measurement / Calibration"},
            {"name": "LabVIEW",            "category": "Data Acquisition"},
            {"name": "Python / pandas",    "category": "Data Processing"},
            {"name": "MATLAB",             "category": "Analysis"},
            {"name": "Vector CANoe",       "category": "Protocol Analysis"},
            {"name": "Jira",               "category": "Issue Tracking"},
        ],
        "warning",
    ),
    (
        ['software', 'swe', 'developer', 'backend', 'frontend', 'full stack', 'fullstack', 'python', 'java', 'embedded'],
        [
            {"name": "Python / C++",       "category": "Primary Languages"},
            {"name": "Git / GitHub",       "category": "Version Control"},
            {"name": "Docker / Kubernetes","category": "Containerization"},
            {"name": "Jenkins / CI/CD",    "category": "DevOps"},
            {"name": "REST APIs",          "category": "Integration"},
            {"name": "Jira / Confluence",  "category": "Agile"},
            {"name": "SQL / PostgreSQL",   "category": "Database"},
            {"name": "Linux / Bash",       "category": "OS / Scripting"},
        ],
        "success",
    ),
    (
        ['systems', 'systems engineer', 'systems integration', 'integration test'],
        [
            {"name": "IBM DOORS / DOORS Next", "category": "Requirements Management"},
            {"name": "MATLAB / Simulink",       "category": "System Modeling"},
            {"name": "PTC Integrity / Jira",    "category": "Test Management"},
            {"name": "FMEA / FTA tools",        "category": "Safety Analysis"},
            {"name": "CANoe / CANalyzer",       "category": "Vehicle Bus"},
            {"name": "Python / scripting",      "category": "Automation"},
            {"name": "Confluence",              "category": "Documentation"},
            {"name": "MS Project / Jira",       "category": "Project Planning"},
        ],
        "info",
    ),
    (
        ['electrical', 'electrical engineer', 'ee', 'pcb', 'hardware', 'circuit'],
        [
            {"name": "Altium Designer",    "category": "PCB Design"},
            {"name": "Mentor Graphics",    "category": "Schematics"},
            {"name": "LTSpice / PSpice",   "category": "Circuit Simulation"},
            {"name": "Oscilloscope / DMM", "category": "Lab Instruments"},
            {"name": "CANalyzer",          "category": "Vehicle Bus"},
            {"name": "MATLAB",             "category": "Analysis"},
            {"name": "Python",             "category": "Scripting"},
            {"name": "Jira",               "category": "Issue Tracking"},
        ],
        "warning",
    ),
    (
        ['validation', 'verification', 'test', 'testing', 'v&v', 'quality'],
        [
            {"name": "CANoe / CANalyzer",  "category": "Bus Analysis"},
            {"name": "Python / pytest",    "category": "Test Automation"},
            {"name": "MATLAB / Simulink",  "category": "MIL / SIL Testing"},
            {"name": "dSPACE HIL",         "category": "HIL Testing"},
            {"name": "Vector vTESTstudio", "category": "Test Scripting"},
            {"name": "Jira / Zephyr",      "category": "Test Management"},
            {"name": "Git",                "category": "Version Control"},
            {"name": "LabVIEW",            "category": "Data Acquisition"},
        ],
        "danger",
    ),
    (
        ['vehicle', 'prototype', 'vehicle integration', 'vehicle test', 'fleet'],
        [
            {"name": "CANoe / CANalyzer",     "category": "Vehicle Bus"},
            {"name": "VehicleSpy / PCAN",     "category": "Diagnostics"},
            {"name": "INCA / CANape",          "category": "ECU Calibration"},
            {"name": "Python / pandas",        "category": "Data Processing"},
            {"name": "GPS / IMU data tools",   "category": "Instrumentation"},
            {"name": "Jira",                   "category": "Issue Tracking"},
            {"name": "MS Office / Confluence", "category": "Documentation"},
        ],
        "teal",
    ),
]


def infer_tech_stack(position: str) -> list[dict]:
    """
    Return a list of tool dicts relevant to the given job position.
    Falls back to a generic engineering set if no keyword matches.
    """
    pos_lower = position.lower()
    matched: list[dict] = []
    color = "secondary"

    for keywords, tools, col in _TOOL_RULES:
        if any(kw in pos_lower for kw in keywords):
            matched = tools
            color   = col
            break

    if not matched:
        # Generic engineering fallback
        matched = [
            {"name": "MATLAB",             "category": "Analysis"},
            {"name": "Python",             "category": "Scripting"},
            {"name": "Jira / Confluence",  "category": "Project Tracking"},
            {"name": "Git",                "category": "Version Control"},
            {"name": "MS Office 365",      "category": "Documentation"},
        ]
        color = "secondary"

    return [{"color": color, **t} for t in matched]


# ---------------------------------------------------------------------------
# Interview question bank
# ---------------------------------------------------------------------------

_RECRUITER_QUESTIONS: list[str] = [
    "Tell me about yourself and your background.",
    "What motivated you to apply for this role at {company}?",
    "What are your salary expectations and are you flexible?",
    "What is your current notice period or availability to start?",
    "Are you interviewing with other companies? What is your timeline?",
    "Why are you leaving / looking to leave your current position?",
    "Can you confirm your authorization to work without sponsorship?",
    "What does your ideal work environment look like — remote, hybrid, or on-site?",
    "Walk me through a high-level summary of your most recent role.",
    "What are the top two or three things you're looking for in your next position?",
    "Have you worked in the automotive / aerospace / [industry] sector before?",
    "Is relocation an option if this role requires it?",
]

_HIRING_MANAGER_QUESTIONS: list[str] = [
    "Tell me about a complex project you led from requirements to delivery — what was your role and what was the outcome?",
    "Describe a situation where you had to push back on a technical decision made by leadership. How did you handle it?",
    "Give me an example of a time you identified a process inefficiency and drove an improvement.",
    "Tell me about a time a project failed or a milestone was missed. What did you learn?",
    "How do you prioritize competing demands when resources are constrained?",
    "Describe a time you had to work cross-functionally with teams that had conflicting goals.",
    "Where do you see yourself in 3–5 years and how does this role align with that vision?",
    "What is your approach to mentoring or developing junior engineers?",
    "Tell me about a time you had to rapidly upskill or learn a new technology for a project.",
    "How do you stay current with developments in your field?",
    "Describe a time you disagreed with a colleague and how you resolved it professionally.",
    "What does 'done' mean to you when delivering engineering work?",
]

# Role-specific technical question banks keyed by category
_TECH_QUESTIONS: dict[str, list[str]] = {
    "adas": [
        "Explain the sensor fusion approach you'd use to combine radar, lidar, and camera data for object detection.",
        "What is the difference between MIL, SIL, HIL, and PIL testing and when do you use each?",
        "How do you validate an AEB (Automatic Emergency Braking) system from requirements through to vehicle testing?",
        "Describe your experience with ISO 26262 functional safety requirements and ASIL decomposition.",
        "Walk me through how you would debug an unexpected false positive in a forward collision warning algorithm.",
        "What is the role of the Kalman filter in sensor fusion and what are its limitations?",
        "How do you handle latency and synchronization between heterogeneous sensor streams?",
        "What automotive communication protocols have you worked with (CAN, LIN, Ethernet, SOME/IP, FlexRay)?",
        "How would you design a test matrix for a new ADAS feature to ensure coverage across all operational design domains (ODD)?",
        "Explain the concept of a safety case and how it relates to V-model development.",
    ],
    "calibration": [
        "Walk me through your ECU calibration workflow using tools like INCA or CANape.",
        "How do you validate that a calibration change achieves the desired system behavior without regressions?",
        "Describe a calibration challenge you solved — what was the root cause and approach?",
        "What is DOE (Design of Experiments) and how have you applied it in a calibration context?",
        "How do you manage calibration datasets and ensure traceability back to requirements?",
        "Explain the difference between open-loop and closed-loop calibration strategies.",
        "What metrics do you use to assess the quality of a calibration on a vehicle test?",
        "How do you coordinate with software and hardware teams when a calibration issue turns out to be a software bug?",
    ],
    "systems": [
        "Walk me through your requirements management process from customer needs to system requirements.",
        "How do you perform a system-level FMEA and what tools do you use?",
        "Describe an integration challenge you solved between two or more subsystems.",
        "How do you handle requirements traceability and manage change requests in a large program?",
        "What is a V-model and how does it guide your development and verification activities?",
        "How do you allocate system-level requirements down to subsystem or component specifications?",
        "Describe your approach to writing an interface control document (ICD).",
        "What metrics do you track to measure system integration progress and risk?",
        "How do you manage a supplier who is behind schedule and impacting your integration milestone?",
        "Explain a trade study you conducted and how you structured the decision criteria.",
    ],
    "software": [
        "Walk me through your software development process — how do you go from requirement to code to deployment?",
        "How do you approach unit testing and what coverage level do you target?",
        "Describe a performace bottleneck you've identified and resolved in production code.",
        "What design patterns have you used and why did you choose them for a specific problem?",
        "How do you handle thread safety and concurrency bugs in multi-threaded systems?",
        "Walk me through how you would debug a memory leak in a C++ embedded application.",
        "What CI/CD tools have you used and how did they impact your team's velocity?",
        "How do you handle backward compatibility when releasing a new API version?",
        "What is your code review philosophy — what do you look for and what are deal-breakers?",
        "Describe your experience with real-time operating systems (RTOS) and scheduling constraints.",
    ],
    "validation": [
        "How do you develop a test plan from a set of system requirements?",
        "Describe your experience with HIL or SIL testing — what setup did you use and what did you test?",
        "Walk me through how you would create regression test suites and manage their execution.",
        "How do you handle a test that consistently produces intermittent failures?",
        "What is your approach to root-cause analysis when a test fails?",
        "Describe a defect you found that had a significant impact on the program timeline.",
        "How do you measure test coverage and know when you have tested enough?",
        "What is your experience with ISO 26262 product verification and validation activities?",
        "How do you coordinate test schedules with hardware and software dependencies?",
        "Describe your experience writing automated test scripts — what language and framework did you use?",
    ],
    "generic": [
        "Walk me through a complex technical problem you solved end-to-end.",
        "How do you approach a new technical area you are unfamiliar with?",
        "Describe your experience working with cross-functional teams in a fast-paced program.",
        "What development tools and workflows are you most comfortable with?",
        "How do you handle ambiguous requirements or incomplete specifications?",
        "Describe your quality assurance approach — how do you ensure correctness of your work?",
        "Tell me about a technical risk you identified early and how you mitigated it.",
        "What metrics do you use to demonstrate engineering progress to stakeholders?",
        "Describe your documentation practices and why they matter.",
        "How do you manage your workload when priorities shift frequently?",
    ],
}


def _detect_category(position: str) -> str:
    pos = position.lower()
    if any(k in pos for k in ['adas', 'autonomous', 'radar', 'lidar', 'camera', 'sensor']):
        return 'adas'
    if any(k in pos for k in ['calibration', 'cal engineer', 'inca', 'canape']):
        return 'calibration'
    if any(k in pos for k in ['systems', 'integration', 'systems engineer']):
        return 'systems'
    if any(k in pos for k in ['software', 'developer', 'swe', 'embedded', 'python', 'java']):
        return 'software'
    if any(k in pos for k in ['validation', 'verification', 'test', 'v&v', 'quality']):
        return 'validation'
    return 'generic'


def generate_interview_questions(company: str, position: str) -> dict[str, list[str]]:
    """
    Return stage-by-stage interview questions for the given company + position.
    Company name is interpolated into recruiter questions.
    """
    category = _detect_category(position)
    tech_qs  = _TECH_QUESTIONS.get(category, _TECH_QUESTIONS['generic'])

    recruiter_qs = [q.replace('{company}', company) for q in _RECRUITER_QUESTIONS]

    return {
        "recruiter":       recruiter_qs,
        "hiring_manager":  _HIRING_MANAGER_QUESTIONS,
        "technical":       tech_qs,
        "category":        category,
    }


# ---------------------------------------------------------------------------
# Master prep builder
# ---------------------------------------------------------------------------

def build_interview_prep(company: str, position: str) -> dict[str, Any]:
    """Return the complete interview prep payload for a job application."""
    return {
        "company":    company,
        "position":   position,
        "search":     generate_search_urls(company, position),
        "tech_stack": infer_tech_stack(position),
        "questions":  generate_interview_questions(company, position),
    }
