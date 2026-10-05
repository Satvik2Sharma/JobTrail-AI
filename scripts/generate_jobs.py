#!/usr/bin/env python3
"""
Synthetic job dataset generator for JobTrail-AI.
Generates ~300 realistic prototype job/internship records spanning diverse tech domains.
All listings are synthetic prototype/demo data and not live employment listings.
"""

import json
import random
from pathlib import Path

random.seed(42)

COMPANIES = [
    "TechNova Solutions", "CloudScale Systems", "Nexus AI Labs", "QuantumByte",
    "Apex Dynamics", "Starlight Software", "BluePeak Technologies", "Vertex Dataworks",
    "Synthetix Core", "Aether Cloud", "PulseWave Digital", "Cortex Intelligence",
    "Hyperion Soft", "DataForge Analytics", "Krypton Cyber", "OmniStack Labs",
    "Prism Logic", "Cobalt Platforms", "Skyline Cloud", "Horizon Media Tech",
    "Optima Robotics", "Zenith Infotech", "Solstice Health Tech", "Strata Security",
    "Vanguard Edge", "BioMetrics AI", "InfiniStream Systems", "Solaris Networks",
    "EchoLink Communications", "IronClad Security", "Catalyst Micro", "TrueNorth DevOps",
    "NextGen FinTech", "Orbit Space Systems", "AlphaByte Engineering", "DeepMindset Analytics",
    "Lumina Interactive", "Beacon Data Systems", "AcroTech Studio", "Astra Digital"
]

LOCATIONS = [
    ("San Francisco, CA", False),
    ("New York, NY", False),
    ("Austin, TX", False),
    ("Seattle, WA", False),
    ("Boston, MA", False),
    ("Chicago, IL", False),
    ("Denver, CO", False),
    ("Bengaluru, India", False),
    ("Hyderabad, India", False),
    ("Pune, India", False),
    ("London, UK", False),
    ("Berlin, Germany", False),
    ("Toronto, Canada", False),
    ("Remote", True),
    ("Remote - US", True),
    ("Remote - Global", True),
]

JOB_TEMPLATES = [
    {
        "category": "AI/ML",
        "titles": [
            "Machine Learning Engineer Intern", "Junior ML Engineer", "Machine Learning Engineer",
            "AI Research Engineer", "Deep Learning Intern", "Computer Vision Specialist",
            "NLP Engineer", "Applied AI Scientist Intern", "Generative AI Engineer"
        ],
        "primary_skills": ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-learn"],
        "extra_skills_pool": ["PyTorch", "TensorFlow", "Deep Learning", "NLP", "Computer Vision", "OpenCV", "Docker", "SQL", "MLOps", "Generative AI"],
        "degrees": ["B.Tech/B.E. in Computer Science, AI, or related STEM field", "Master's or Bachelor's in CS / Data Science", "B.Tech/B.E. in Computer Science or Mathematics"],
        "desc_template": "Join our AI research and deployment group to develop state-of-the-art predictive and deep learning models. You will preprocess diverse datasets, train neural architectures, and integrate algorithms into production microservices."
    },
    {
        "category": "Data Science & Analytics",
        "titles": [
            "Data Science Intern", "Junior Data Scientist", "Data Analyst Intern",
            "Data Analytics Associate", "Business Intelligence Analyst", "Statistical Modeling Specialist"
        ],
        "primary_skills": ["Python", "SQL", "Pandas", "Data Analysis"],
        "extra_skills_pool": ["NumPy", "Data Visualization", "Scikit-learn", "Machine Learning", "ETL", "PostgreSQL", "R", "Feature Engineering"],
        "degrees": ["B.Tech/B.E. in Computer Science, Statistics, or Information Technology", "Bachelor's in Mathematics, Economics, or CS"],
        "desc_template": "Work closely with product and engineering teams to transform raw operational data into actionable insights, automated KPI dashboards, and foundational machine learning experiments."
    },
    {
        "category": "Backend Development",
        "titles": [
            "Backend Engineer Intern", "Junior Backend Developer", "Python Backend Engineer",
            "FastAPI Developer", "Java Software Engineer", "Go Backend Engineer", "Distributed Systems Engineer"
        ],
        "primary_skills": ["Python", "REST API", "SQL", "Git"],
        "extra_skills_pool": ["FastAPI", "Django", "PostgreSQL", "Docker", "Redis", "Java", "Spring Boot", "Microservices", "Linux", "Kubernetes"],
        "degrees": ["B.Tech/B.E. in Computer Science, Software Engineering, or related technical field", "Bachelor's degree in Computer Science or equivalent practical experience"],
        "desc_template": "Architect and maintain robust, scalable backend APIs and data persistence layers. Collaborate on high-throughput microservices, optimize database queries, and ensure 99.9% service reliability."
    },
    {
        "category": "Frontend Development",
        "titles": [
            "Frontend Engineer Intern", "Junior React Developer", "Frontend Web Developer",
            "UI/UX Software Engineer", "Next.js Frontend Engineer", "Web Applications Developer"
        ],
        "primary_skills": ["JavaScript", "TypeScript", "React", "HTML", "CSS"],
        "extra_skills_pool": ["Next.js", "Tailwind CSS", "Redux", "REST API", "Git", "Zustand", "Vue.js", "Unit Testing"],
        "degrees": ["B.Tech/B.E. in Computer Science, Web Development, or equivalent", "Bachelor's in CS, IT, or Design Computing"],
        "desc_template": "Craft highly responsive, accessible, and visually stunning web interfaces for modern SaaS platforms. Collaborate with designers and backend engineers to integrate stateful client-side workflows."
    },
    {
        "category": "Full Stack",
        "titles": [
            "Full Stack Developer Intern", "Junior Full Stack Engineer", "Full Stack Software Engineer",
            "Web Development Specialist", "MERN Stack Engineer", "Python Full Stack Developer"
        ],
        "primary_skills": ["JavaScript", "TypeScript", "React", "Node.js", "SQL"],
        "extra_skills_pool": ["Python", "FastAPI", "PostgreSQL", "MongoDB", "Docker", "REST API", "Tailwind CSS", "Git", "Next.js"],
        "degrees": ["B.Tech/B.E. in Computer Science, IT, or related degree", "Bachelor's degree in Software Engineering or equivalent experience"],
        "desc_template": "Build end-to-end features spanning modern interactive frontends to resilient backend APIs. Own feature delivery from concept, database schema design, to CI/CD pipeline deployments."
    },
    {
        "category": "Cloud & DevOps",
        "titles": [
            "DevOps Engineer Intern", "Cloud Infrastructure Engineer", "Site Reliability Engineer (SRE)",
            "Cloud Security Associate", "Platform Engineering Intern", "CI/CD Automation Engineer"
        ],
        "primary_skills": ["Linux", "Docker", "Git", "CI/CD"],
        "extra_skills_pool": ["Kubernetes", "AWS", "Terraform", "Azure", "GCP", "Python", "Prometheus", "Nginx", "System Design"],
        "degrees": ["B.Tech/B.E. in Computer Science, Network Engineering, or Information Systems", "Bachelor's in CS or IT"],
        "desc_template": "Automate cloud deployment pipelines, manage containerized microservice clusters, and monitor infrastructure telemetry to ensure unmatched performance and zero-downtime releases."
    },
    {
        "category": "Cybersecurity",
        "titles": [
            "Cybersecurity Analyst Intern", "Junior Security Engineer", "Information Security Specialist",
            "Application Security Associate", "SOC Analyst Intern", "Penetration Testing Intern"
        ],
        "primary_skills": ["Cybersecurity", "Linux", "Computer Networks"],
        "extra_skills_pool": ["Penetration Testing", "Cryptography", "Python", "Docker", "Operating Systems", "Git", "AWS"],
        "degrees": ["B.Tech/B.E. in Cybersecurity, Computer Science, or Network Systems", "Bachelor's degree in Information Security or Computer Science"],
        "desc_template": "Identify application vulnerabilities, assess network perimeter security, implement cryptographic controls, and support incident response protocols across enterprise infrastructures."
    },
    {
        "category": "Mobile Development",
        "titles": [
            "Flutter Developer Intern", "Android App Engineer", "Mobile Applications Developer",
            "iOS Engineer Intern", "React Native Developer", "Junior Mobile Engineer"
        ],
        "primary_skills": ["Flutter", "Git", "REST API"],
        "extra_skills_pool": ["Android", "React Native", "iOS", "Firebase", "Kotlin", "Swift", "TypeScript", "Data Structures"],
        "degrees": ["B.Tech/B.E. in Computer Science, Mobile Computing, or Software Engineering", "Bachelor's in CS or relevant discipline"],
        "desc_template": "Develop smooth, native-feeling cross-platform and mobile applications. Integrate offline synchronization, push notifications, and high-performance user interfaces."
    },
    {
        "category": "Software Engineering & Systems",
        "titles": [
            "Software Development Engineer Intern (SDE)", "Junior Software Developer", "C++ Systems Engineer",
            "Java SDE Intern", "Core Platform Software Engineer", "Embedded & Systems Engineer"
        ],
        "primary_skills": ["Data Structures", "Algorithms", "Git"],
        "extra_skills_pool": ["C++", "Java", "Python", "Object-Oriented Programming", "Operating Systems", "System Design", "Linux", "SQL", "Unit Testing"],
        "degrees": ["B.Tech/B.E. in Computer Science, Electrical Engineering, or related discipline", "Bachelor's or Master's in Computer Science"],
        "desc_template": "Solve fundamental computational problems, optimize critical path algorithms, and engineer robust object-oriented system software capable of handling millions of transactions."
    }
]

EXPERIENCE_LEVELS = [
    ("0-1 years", "Internship", (40000, 75000)),
    ("0-1 years", "Entry-level Full-time", (65000, 95000)),
    ("1-2 years", "Full-time", (85000, 115000)),
    ("0-1 years", "Internship", (35000, 70000)),
    ("0-2 years", "Associate / Junior", (70000, 100000)),
]

def generate_job_dataset(target_count=300):
    jobs = []
    
    # We want evenly distributed records across categories
    per_template = (target_count // len(JOB_TEMPLATES)) + 2
    
    job_id = 1
    for template in JOB_TEMPLATES:
        for _ in range(per_template):
            if len(jobs) >= target_count:
                break
                
            company = random.choice(COMPANIES)
            title = random.choice(template["titles"])
            loc_str, is_remote = random.choice(LOCATIONS)
            if "Remote" in loc_str:
                is_remote = True
            elif random.random() < 0.35:
                # hybrid/remote option
                is_remote = True
                
            exp_label, emp_type, sal_range = random.choice(EXPERIENCE_LEVELS)
            
            # Select skills: primary guaranteed + 2 to 4 extras
            num_extras = random.randint(2, 4)
            chosen_extras = random.sample(template["extra_skills_pool"], min(num_extras, len(template["extra_skills_pool"])))
            job_skills = list(dict.fromkeys(template["primary_skills"] + chosen_extras))
            
            education_req = random.choice(template["degrees"])
            
            salary_min = sal_range[0] + random.randint(-5, 10) * 1000
            salary_max = sal_range[1] + random.randint(0, 15) * 1000
            
            description = (
                f"{company} is looking for a talented and passionate {title} to join our engineering and technology team. "
                f"{template['desc_template']} "
                f"You will work in a collaborative agile environment, learning from senior engineers and shipping meaningful features to thousands of users."
            )
            
            requirements = (
                f"• {education_req}.\n"
                f"• Experience or academic project work with {', '.join(job_skills[:3])}.\n"
                f"• Solid foundation in Computer Science, algorithms, and software development methodologies.\n"
                f"• Passion for problem-solving, code quality, and continuous learning."
            )
            
            responsibilities = (
                f"• Develop, test, and document production-ready features using {', '.join(job_skills[:4])}.\n"
                f"• Collaborate with cross-functional peers including designers, product managers, and QA.\n"
                f"• Participate in code reviews, sprint planning, and architectural discussions.\n"
                f"• Debug issues, write automated tests, and improve overall system maintainability."
            )
            
            job = {
                "id": job_id,
                "title": title,
                "company": company,
                "location": loc_str,
                "remote": is_remote,
                "employment_type": emp_type,
                "experience_level": exp_label,
                "education_requirement": education_req,
                "category": template["category"],
                "skills": job_skills,
                "description": description,
                "requirements": requirements,
                "responsibilities": responsibilities,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "application_url": f"https://careers.{company.lower().replace(' ', '')}.com/jobs/{job_id}",
                "is_synthetic": True,
                "disclaimer": "The included jobs are synthetic prototype/demo records and are not live employment listings."
            }
            jobs.append(job)
            job_id += 1

    return jobs

if __name__ == "__main__":
    jobs = generate_job_dataset(305)
    out_path = Path("/home/user/Desktop/PROJECTS/JobTrail-AI/data/jobs.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)
    print(f"Successfully generated {len(jobs)} realistic prototype job records at {out_path}")
