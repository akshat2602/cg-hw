// Vertex Shader
#version 410 core

uniform mat4 MVPMatrix;
uniform mat4 MVMatrix;
uniform mat3 NormalMatrix;

layout (location = 0) in vec4 VertexPosition;
layout (location = 1) in vec3 VertexNormal;

out vec3 Normal;
out vec3 FragPos;

void main()
{
    // Transform vertex position and normal
    FragPos = vec3(MVMatrix * VertexPosition);
    Normal = normalize(NormalMatrix * VertexNormal);
    gl_Position = MVPMatrix * VertexPosition;
}

// Fragment Shader
#version 410 core

uniform vec3 LightPos;
uniform vec3 ViewPos;
uniform vec3 LightColor;
uniform vec3 ObjectColor;
uniform int DisplayMode; // 0: WIREFRAME, 1: FLAT, 2: SMOOTH

in vec3 Normal;
in vec3 FragPos;

out vec4 FragColor;

void main()
{
    // Base color for wireframe mode
    if (DisplayMode == 0) {
        FragColor = vec4(ObjectColor, 1.0);
        return;
    }

    // Phong lighting components
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * LightColor;

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(LightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * LightColor;

    float specularStrength = 0.5;
    vec3 viewDir = normalize(ViewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * LightColor;

    vec3 result = (ambient + diffuse + specular) * ObjectColor;
    FragColor = vec4(result, 1.0);
}