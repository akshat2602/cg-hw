#version 410 core

layout (quads, equal_spacing, ccw) in;

out vec3 Normal;
out vec3 FragPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform int shapeType;  // 0=sphere, 1=cylinder, 2=cone

const float PI = 3.14159265359;
const float TWO_PI = 2.0 * PI;

vec4 getSpherePosition(float u, float v)
{
    float phi = TWO_PI * u;
    float theta = PI * v;
    
    float x = sin(theta) * cos(phi);
    float y = sin(theta) * sin(phi);
    float z = cos(theta);
    
    return vec4(x, y, z, 1.0);
}

vec4 getCylinderPosition(float u, float v)
{
    float phi = TWO_PI * u;
    
    float x = cos(phi);
    float y = 2.0 * v - 1.0; // Height from -1 to 1
    float z = sin(phi);
    
    return vec4(x, y, z, 1.0);
}

vec4 getConePosition(float u, float v)
{
    float phi = TWO_PI * u;
    float h = 1.0 - v; // Height from 0 to 1
    
    float x = h * cos(phi);
    float y = v * 2.0 - 1.0; // Height from -1 to 1
    float z = h * sin(phi);
    
    return vec4(x, y, z, 1.0);
}

vec3 getSphereNormal(vec4 pos)
{
    return normalize(vec3(pos));
}

vec3 getCylinderNormal(float u)
{
    float phi = TWO_PI * u;
    return normalize(vec3(cos(phi), 0.0, sin(phi)));
}

vec3 getConeNormal(float u, float v)
{
    float phi = TWO_PI * u;
    float h = 1.0 - v;
    vec3 tangent = vec3(-h * sin(phi), 0.0, h * cos(phi));
    vec3 bitangent = vec3(cos(phi), 1.0, sin(phi));
    return normalize(cross(tangent, bitangent));
}

void main()
{
    float u = gl_TessCoord.x;
    float v = gl_TessCoord.y;

    vec4 pos;
    vec3 norm;

    if (shapeType == 0) {
        pos = getSpherePosition(u, v);
        norm = getSphereNormal(pos);
    }
    else if (shapeType == 1) {
        pos = getCylinderPosition(u, v);
        norm = getCylinderNormal(u);
    }
    else {
        pos = getConePosition(u, v);
        norm = getConeNormal(u, v);
    }

    FragPos = vec3(model * pos);
    Normal = mat3(transpose(inverse(model))) * norm;
    gl_Position = projection * view * model * pos;
}