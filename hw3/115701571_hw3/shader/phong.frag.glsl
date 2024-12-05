#version 410 core

in vec3 FragPos;
in vec3 Normal;
in vec3 Color;
flat in vec3 FlatNormal;

out vec4 FragColor;

uniform vec3 viewPos;
uniform vec3 lightPos;
uniform vec3 lightColor;
uniform int displayMode;  // 1=WIREFRAME, 2=FLAT, 3=SMOOTH

void main()
{
    vec3 norm;
    
    if (displayMode == 1) {
        // Wireframe mode - just use the color
        FragColor = vec4(Color, 1.0);
        return;
    }
    
    // Select normal based on display mode
    norm = (displayMode == 2) ? normalize(FlatNormal) : normalize(Normal);
    
    // Ambient
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * lightColor;
    
    // Diffuse
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    // Specular
    float specularStrength = 0.5;
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 halfwayDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(norm, halfwayDir), 0.0), 32.0);
    vec3 specular = specularStrength * spec * lightColor;
    
    // Combine results
    vec3 result = (ambient + diffuse + specular) * Color;
    FragColor = vec4(result, 1.0);
}