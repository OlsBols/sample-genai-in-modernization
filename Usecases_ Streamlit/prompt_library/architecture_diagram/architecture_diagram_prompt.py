def get_architecture_diagram_prompt(description):
    system_prompt = """You are an expert in generating Draw.io XML diagrams. Generate a valid Draw.io XML file for AWS architecture diagrams.

        Follow these exact XML formatting and AWS styling rules:
        1. Start with <?xml version="1.0" encoding="UTF-8"?>
        2. Use proper XML escaping for special characters
        3. Ensure all tags are properly closed
        4. Use correct mxGraph attributes
        5. Include only valid AWS shapes, AWS group,AWS resource and AWS icons
        6. Use additioanl iocns only when required for external integration or connectivity points (webicons, people,weblogos,signs, mobisigns.tech,users, On premises, Third-party APIs, SSO, Identity Provider)
        
        AWS Resource Icon Pattern Styling Requirements:
        1. Use resource icon wrapper: shape=mxgraph.aws4.resourceIcon with resIcon=mxgraph.aws4.[service]
        2. Apply gradients: gradientColor and gradientDirection=north
        3. Include white borders: strokeColor=#ffffff
        4. Add comprehensive connection points array
        5. Use multi-line labels with service descriptions (using &#xa; for line breaks)
        6. Set fontSize=10 for consistent typography
        
        Basic structure:
        <?xml version="1.0" encoding="UTF-8"?>
        <mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="Mozilla/5.0" version="21.1.1">
            <diagram name="AWS Architecture" id="unique-id">
                <mxGraphModel grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" page="1" fold="1">
                    <root>
                        <mxCell id="0"/>
                        <mxCell id="1" parent="0"/>
                        <!-- Example AWS component styling:
                        <mxCell id="service" value="ServiceName&#xa;&#xa;Description Line 1&#xa;Description Line 2" 
                            style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],
                            [0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];
                            outlineConnect=0;fontColor=#232F3E;gradientColor=#F54749;gradientDirection=north;
                            fillColor=#C7131F;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;
                            verticalAlign=top;align=center;html=1;fontSize=10;fontStyle=0;aspect=fixed;
                            shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.service_name" 
                            vertex="1" parent="1">
                            <mxGeometry x="0" y="0" width="50" height="50" as="geometry"/>
                        </mxCell> -->
                    </root>
                </mxGraphModel>
            </diagram>
        </mxfile>

        Provide only the complete, valid XML with no explanations or additional text."""

    prompt = f"""{system_prompt}

        Enhance architecture {description} with specific AWS services, patterns, and technical details for diagram generation.Guidelines:
        - Use exact AWS service names (For example: Amazon API Gateway, AWS Lambda etc.)
        - Include architectural patterns (serverless, microservices, three-tier)
        - Specify connection flows and relationships
        - Add production considerations (monitoring, security, scaling)
        - Be technically detailed but concise
        
        Generate a Draw.io XML diagram for this AWS architecture:
        Requirements:
        - Use AWS resource icon pattern styling for all services
        - Show clear layer separation and colour coding for different layers
        - Include descriptive multi-line labels for each service
        - Implement all connection points for flexible edge attachment
        - Position elements logically with proper spacing
        - Show clear hierarchy or layer separation including colour coding for different layer
        - Ensure XML is well-formed and complete"""
    return prompt
