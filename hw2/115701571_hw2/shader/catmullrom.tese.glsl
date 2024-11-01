#version 410 core

layout (isolines, equal_spacing, ccw) in;

uniform mat3 model;
uniform float windowWidth;
uniform float windowHeight;

vec2 catmull_rom(vec2 p0, vec2 p1, vec2 p2, vec2 p3, float t)
{
    float t2 = t * t;
    float t3 = t2 * t;
    
    return 0.5 * ((2.0 * p1) +
                  (-p0 + p2) * t +
                  (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2 +
                  (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3);
}

void main()
{
    float t = gl_TessCoord.x;

    vec2 p0 = gl_in[0].gl_Position.xy;
    vec2 p1 = gl_in[1].gl_Position.xy;
    vec2 p2 = gl_in[2].gl_Position.xy;
    vec2 p3 = gl_in[3].gl_Position.xy;

    vec2 pos = catmull_rom(p0, p1, p2, p3, t);

    vec3 transformed = model * vec3(2.0 * pos.x / windowWidth - 1.0,
                                    2.0 * pos.y / windowHeight - 1.0,
                                    1.0);

    gl_Position = vec4(transformed.xy, 0.0, 1.0);
}
