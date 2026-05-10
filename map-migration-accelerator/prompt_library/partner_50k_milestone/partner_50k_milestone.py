def get_milestone_prompt(services_summary, high_level_strategy):
    prompt = f"""
        As an AWS migration expert, develop a migration milestone analysis using the following inputs.
        Always use USD($) as currency. Use British English standards. Ensure all cost calculations are mathematically correct.

        AWS Services & Cost Data: {services_summary}
        Migration Strategy & Wave Plan: {high_level_strategy}

        Use exactly these ## headings in your response:

        ## High Level Wave Plan
        Create a table with columns: Wave | Description | Timeframe | Services/Workloads | Monthly Spend | Cumulative Spend
        Use the wave timeframes from the migration strategy (e.g. Weeks 1-8, Months 3-6). Do not invent new timeframes — align with the strategy wave plan.
        Include all waves with calculated cumulative USD($) spend.

        ## First $50,000 USD Milestone Prediction
        Using the wave timeframes and cumulative spend from the table above, identify the specific wave and calendar period where cumulative spend crosses $50,000 USD.
        Show the step-by-step calculation: Wave 1 spend + Wave 2 spend + ... = cumulative total.
        State the predicted month/period explicitly (e.g. "During Wave 2, approximately Month 5 based on the strategy timeline").

        ## Acceleration Strategy
        CONDITIONAL: Only include this section if the $50,000 milestone takes longer than 3 months to achieve.
        If the milestone IS achieved within 3 months, write only: "Not required — milestone achieved within 3 months."
        If the milestone takes longer than 3 months, recommend specific strategies to achieve $50,000 cumulative spend within 3 months. Use bullet points.

        ## Risks and Assumptions
        List risks and assumptions for the overall milestone timeline and any acceleration strategy. Use bullet points, 5-7 items max.

        ## Duration Rationale and Reasoning
        Provide rationale for the estimated duration of each wave, referencing the strategy timeframes. Use bullet points, one per wave.

        Format your response in markdown. Keep each section concise — bullet points preferred over paragraphs.
        """
    return prompt
