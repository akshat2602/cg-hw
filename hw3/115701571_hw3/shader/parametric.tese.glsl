#version 410 core

layout (quads, equal_spacing, ccw) in;

out vec3 Normal;
out vec3 FragPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform int shapeType;  // 0=sphere, 1=cylinder, 2=cone, 3=superquadric
uniform float e1;       // North-south exponent for superquadric
uniform float e2;       // East-west exponent for superquadric

const float PI = 3.14159265359;
const float TWO_PI = 2.0 * PI;

// Sign function that returns 1.0 for positive values and -1.0 for negative values
float sign(float x) {
    return x >= 0.0 ? 1.0 : -1.0;
}

// Power function that preserves sign
float spow(float x, float p) {
    return sign(x) * pow(abs(x), p);
}

vec4 getSuperquadricPosition(float u, float v) {
    float phi = TWO_PI * u - PI;      // Range: -π to π
    float theta = PI * v - PI/2.0;    // Range: -π/2 to π/2
    
    // Use reciprocal of exponents to get correct behavior:
    // - Small exponents (e.g. 0.3) -> cube-like
    // - Large exponents (e.g. 3.0) -> star-like
    float r_e1 = 1.0/e1;
    float r_e2 = 1.0/e2;
    
    float cosPhi = cos(phi);
    float cosTheta = cos(theta);
    float sinPhi = sin(phi);
    float sinTheta = sin(theta);
    
    float x = spow(cosTheta, r_e1) * spow(cosPhi, r_e2);
    float y = spow(cosTheta, r_e1) * spow(sinPhi, r_e2);
    float z = spow(sinTheta, r_e1);
    
    return vec4(x, y, z, 1.0);
}

vec3 getSuperquadricNormal(float u, float v) {
    float phi = TWO_PI * u - PI;
    float theta = PI * v - PI/2.0;
    
    float r_e1 = 1.0/e1;
    float r_e2 = 1.0/e2;
    
    float cosPhi = cos(phi);
    float cosTheta = cos(theta);
    float sinPhi = sin(phi);
    float sinTheta = sin(theta);
    
    float nx = (2.0*r_e2) * spow(cosTheta, 2.0-r_e1) * spow(cosPhi, 2.0-r_e2);
    float ny = (2.0*r_e2) * spow(cosTheta, 2.0-r_e1) * spow(sinPhi, 2.0-r_e2);
    float nz = (2.0*r_e1) * spow(sinTheta, 2.0-r_e1);
    
    return normalize(vec3(nx, ny, nz));
}

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
    else if (shapeType == 2) {
        pos = getConePosition(u, v);
        norm = getConeNormal(u, v);
    }
    else {  // superquadric
        pos = getSuperquadricPosition(u, v);
        norm = getSuperquadricNormal(u, v);
    }

    FragPos = vec3(model * pos);
    Normal = mat3(transpose(inverse(model))) * norm;
    gl_Position = projection * view * model * pos;
}