#version 410 core

layout (location = 0) in vec3 aPosition;
layout (location = 1) in vec3 aNormal;
layout (location = 2) in vec3 aColor;

out vec3 FragPos;
out vec3 Normal;
out vec3 Color;
flat out vec3 FlatNormal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform int displayMode;

void main()
{
    vec4 worldPos = model * vec4(aPosition, 1.0);
    FragPos = vec3(worldPos);
    
    mat3 normalMatrix = mat3(transpose(inverse(model)));
    vec3 transformedNormal = normalize(normalMatrix * aNormal);
    
    // For flat shading, use the face normal directly
    FlatNormal = transformedNormal;
    
    // For smooth shading, we'll let the normal be interpolated
    Normal = transformedNormal;
    
    Color = aColor;
    gl_Position = projection * view * worldPos;
}