import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Common tech skills list
TECH_SKILLS = [
    "python", "java", "javascript", "react", "node", "sql", "mysql",
    "postgresql", "mongodb", "aws", "azure", "gcp", "docker", "kubernetes",
    "git", "linux", "machine learning", "deep learning", "tensorflow",
    "pytorch", "pandas", "numpy", "scikit-learn", "flask", "django",
    "rest api", "microservices", "ci/cd", "devops", "agile", "scrum",
    "data analysis", "data science", "nlp", "computer vision", "html",
    "css", "typescript", "spring boot", "hibernate", "maven", "jenkins"
]

def extract_skills(text):
    text_lower = text.lower()
    found_skills = []
    for skill in TECH_SKILLS:
        if skill in text_lower:
            found_skills.append(skill)
    return list(set(found_skills))

def calculate_match_score(resume_text, job_description):
    # Calculate cosine similarity
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        match_score = round(similarity * 100, 2)
    except:
        match_score = 0

    # Extract skills
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    matched_skills = list(set(resume_skills) & set(jd_skills))
    missing_skills = list(set(jd_skills) - set(resume_skills))

    # ATS Score calculation
    ats_score = min(100, match_score + (len(matched_skills) * 3))

    return {
        "match_score": match_score,
        "ats_score": round(ats_score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills
    }

def get_recommendations(missing_skills, match_score):
    recommendations = []

    if match_score < 30:
        recommendations.append("Your resume needs significant updates to match this job.")
    elif match_score < 60:
        recommendations.append("Your resume partially matches. Add more relevant keywords.")
    else:
        recommendations.append("Great match! Your resume aligns well with this job.")

    if missing_skills:
        top_missing = missing_skills[:5]
        recommendations.append(f"Consider adding these skills: {', '.join(top_missing)}")

    if not missing_skills:
        recommendations.append("You have all the key skills mentioned in the job description!")

    return recommendations