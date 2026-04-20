def get_learning_pathway_prompt(
    training_data, target_role, target_experience, learning_duration
):
    prompt = f"""
    Using the provided training details {training_data}, design comprehensive AWS migration and modernisation training pathways for {target_role}, tailored to {target_experience} experience levels.

    Each pathway shall:
    - Build progressive expertise in AWS migration services, tools and methodologies
    - Calculate duration in minutes or hours, ensuring the combined total training duration does not exceed {learning_duration}. The total training duration per week must remain under forty hours
    - Focus on practical, role-relevant competencies
    - Incorporate both technical and business perspectives where appropriate

    The pathways must incorporate:
    - Latest AWS services
    - Best practices
    - Course links 
    - Real-world migration scenarios aligned with the AWS Migration Acceleration Programme (MAP)

    Present the results in a table format with the following columns:
    - Table header 'Learning Pathway'
     |Course Id| Training Name | Description | Duration (minutes) | 
     |------|-------------|----------------|---------------|
     |  | | | | |
    - Course id: Course id from the provided data
    - Training Name: Exact training title from the provided data
    - Description: Concise description from the provided data
    - Duration: Time in minutes
  

    Following the table, provide a detailed rationale addressing:
    1. Total duration (expressed in hours)
    2. Justification for selecting these specific trainings for the target role
    3. Alignment with the specified experience level
    4. Structure of the progressive learning journey
    5. Expected skills and outcomes upon completion

    Format the response in markdown for optimal readability and structure. Maintain British English standards throughout the document.
    """
    return prompt
